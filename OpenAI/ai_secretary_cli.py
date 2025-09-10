# --- GRADE SYSTEM: bronze, silver, gold ---
def get_employee_grade(sales_count: int, unique_models: int, unique_services: int) -> str:
    """
    Returns the grade for an employee based on simple thresholds:
    - Bronze: default
    - Silver: at least 10 sales and at least 3 unique models/services
    - Gold: at least 20 sales and at least 5 unique models/services
    """
    if sales_count >= 20 and (unique_models + unique_services) >= 5:
        return 'gold'
    elif sales_count >= 10 and (unique_models + unique_services) >= 3:
        return 'silver'
    else:
        return 'bronze'

import requests
import re
# ---------- DATA AGGREGATION UTILITY ----------
def fetch_all_core_data(api_base_url="http://localhost:8000/api"):
    """
    Preia datele brute din toate endpointurile principale pentru analiză completă.
    Returnează un dict cu toate tabelele relevante.
    """
    endpoints = {
        "dealerships": "dealerships",
        "vehicles": "vehicles",
        "service_items": "service-items",
        "sale_orders": "sale-orders",
        "car_sale_items": "car-sale-items",
        "employees": "employees",
        "customers": "customers"
    }
    all_data = {}
    for key, endpoint in endpoints.items():
        try:
            resp = requests.get(f"{api_base_url}/{endpoint}", timeout=60)
            resp.raise_for_status()
            all_data[key] = resp.json()
        except Exception as e:
            print(f"[WARN] Could not fetch {key}: {e}")
            all_data[key] = []
    return all_data

def summarize_for_openai(all_data: dict) -> dict:
    """
    Sumarizează local datele brute pentru a trimite doar statistici relevante la OpenAI.
    Returnează un dict cu sumaruri pentru fiecare tabel.
    """
    summary = {}
    # Exemplu sumarizare: număr entități, top 5, statistici simple
    for key, rows in all_data.items():
        summary[key] = {
            "count": len(rows),
            "sample": rows[:5] if isinstance(rows, list) else rows
        }
    # Poți adăuga aici calcule suplimentare: medii, topuri, outlieri etc.
    return summary
#!/usr/bin/env python3
import os, sys, json, datetime as dt, re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import numpy as np
import pandas as pd
import requests
from chromadb.config import Settings

# ---------- CONFIG ----------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "sales")

MODEL_RECOMMEND = os.getenv("OPENAI_MODEL_REC", "gpt-4o-mini")
MODEL_MESSAGE  = os.getenv("OPENAI_MODEL_MSG", "gpt-4o-mini")


ACTION_VERBS = [
    "increase","grow","improve","boost","raise","recover","reduce","decrease",
    "crește","cresc","îmbunătățește","reduce","recuperează"
]


def make_concrete_fallback(user_text: str) -> str:
    """
    Construiește o sugestie CONCRETĂ adaptată la structura reală a bazei de date (dealership, regiuni, vânzări, servicii, etc).
    """
    txt = (user_text or "").lower()

    # Domeniu: vânzări mașini, servicii, clienți, regiuni
    if any(k in txt for k in ["golf", "tiguan", "passat", "model", "vehicle", "mașină", "masina"]):
        domain = "vehicle sales"
    elif any(k in txt for k in ["serviciu", "service", "warranty", "casco", "sunroof", "oil"]):
        domain = "service sales"
    elif any(k in txt for k in ["client", "customer"]):
        domain = "customer engagement"
    else:
        domain = "dealership sales"

    # Regiune: dacă apare un nume de regiune din baza de date, îl folosim
    regions = ["NW", "NE", "Cluj-Napoca", "Iasi"]
    region_phrase = "in all regions"
    for reg in regions:
        if reg.lower() in txt:
            region_phrase = f"in region {reg}"
            break

    # metrică & orizont
    target_pct = "by 10%"
    horizon = "in the next 30 days"

    return f"Increase {domain} {region_phrase} {target_pct} {horizon}."

def validate_goal_with_ai(goal: str, horizon: int = None) -> dict:
    # Nu mai extragem automat perioada și regiunea cu regex, doar AI decide ce lipsește
    horizon = None
    region = None
    """
    Returnează dict cu chei: is_valid (bool), why (str), suggested (str – mereu concret).
    Promptul este adaptat la structura reală a bazei de date (dealership, regiuni, vânzări, servicii, etc).
    """
    system = (
        "You are a validator for business objectives for a car dealership network. "
        "Determine if the input is a concrete business goal suitable as LLM context. "
        "Accept any natural language goal that contains: "
        "- an action verb (accept any synonym or similar word: increase, improve, grow, boost, raise, expand, enhance, maximize, accelerate, develop, advance, strengthen, promote, escalate, elevate, reduce, decrease, cut, minimize, recover, fix, solve, address, optimize, stimulate, drive, push, achieve, reach, deliver, accomplish, etc.) "
        "- what to change (accept any business target: vehicle sales, service sales, casco, casco sales, insurance, customer engagement, revenue, profit, margin, leads, contracts, appointments, test drives, upsell, cross-sell, retention, satisfaction, etc.) "
        "- a scope (accept any region, city, dealership, employee, team, group, or 'all regions', 'all', 'entire', 'everywhere', 'national', 'local', 'area', 'zone', 'territory', etc., in any natural language form) "
        "- a time window/period (accept any natural language expression for period, e.g. 'in the last 30 days', 'in September', 'look at the last 60 days', 'previous 3 months', 'for the last quarter', 'in Q3', 'recently', 'this year', 'since January', 'in 2025', 'for the summer', etc.) "
        "If a time window/period is missing from the goal, but a period is provided separately (e.g. as a parameter or in the UI), consider the goal valid. "
        "If the input is not concrete, return STRICT JSON with keys: is_valid (true/false), why (short, enumerate ONLY what is missing: e.g. 'Missing time window, region'), suggested (empty string). Do NOT mention details that are already present. No extra text. "
        "Be very permissive with natural language, and accept any reasonable synonym or similar word for each element. All four elements must be present, but allow for creative or indirect phrasing."
    )
    # Trimite goal și perioada ca JSON structurat către LLM
    if horizon:
        user = json.dumps({"goal": goal.strip(), "period_days": horizon}, ensure_ascii=False)
    else:
        user = goal.strip()
    suggested = ""
    is_valid = False
    why = "Input is not a business goal."
    try:
        raw = _openai_chat(MODEL_RECOMMEND, system, user, temperature=0)
        s, e = raw.find("{"), raw.rfind("}") + 1
        data = json.loads(raw[s:e])
        is_valid = bool(data.get("is_valid", False))
        why = str(data.get("why", "")).strip() or why
        suggested = ""  # Nu mai sugerăm obiectiv complet
    except Exception:
        pass
    return {"is_valid": is_valid, "why": why, "suggested": suggested, "horizon": horizon, "region": region}



# ========= AI TARGETING (no email) & NOTIFICATIONS =========

def ai_select_underperformers(preview: List[Dict[str, Any]], goal: str, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Uses LLM to intelligently select who is under the threshold.
    Returns a list of dicts: {dealer_id, reason}
    """
    if not preview:
        return []
    system = (
        "You are a sales analyst. From the given KPI preview rows, choose underperformers "
        "most in need of a corrective nudge. Consider low conversion, negative revenue trend, and high risk. "
        "Return STRICT JSON array of objects: {dealer_id, reason}. No prose, no extra text."
    )
    ranked = sorted(preview, key=lambda x: x.get("risk_of_underperform", 0), reverse=True)[:top_n]
    user = json.dumps({"goal": goal, "preview": ranked}, ensure_ascii=False)

    try:
        raw = _openai_chat(MODEL_RECOMMEND, system, user, 0.1)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            s, e = raw.find("["), raw.rfind("]") + 1
            data = json.loads(raw[s:e])
        out = []
        for it in data:
            did = str(it.get("dealer_id", "")).strip()
            if did:
                out.append({"dealer_id": did, "reason": str(it.get("reason","")).strip()})
        return out
    except Exception:
        # deterministic fallback if LLM is unavailable
        return [
            {
                "dealer_id": str(r.get("dealer_id","")),
                "reason": f"risk={r.get('risk_of_underperform',0):.2f}, "
                          f"conv={r.get('conversion',0):.3f}, "
                          f"trend_rev={r.get('trend_revenue_30d',0):.2f}"
            }
            for r in ranked
        ]


def build_notification(item: Dict[str, Any], goal: str, horizon_days: int, reason: str) -> Dict[str, Any]:
    """
    Builds the notification payload that the frontend can consume.
    """
    conv = f"{item.get('conversion',0)*100:.1f}%"
    payload = {
        "type": "sales_nudge",
        "audience": "individual",
        "dealer_id": item.get("dealer_id"),
        "region": item.get("region"),
        "tier": item.get("tier"),
        "title": "Attention: improvement opportunity",
        "body": (
            f"Goal: {goal}\n"
            f"In the last {horizon_days} days: conversion {conv}, "
            f"revenue {int(item.get('revenue',0))}, points {int(item.get('points',0))}."
            "\nSuggestion: apply the directions from the manager's announcement (quick follow-up, highlight promotions, etc.)."
        ),
        "reason": reason,  # why was this selected
        "metrics": {
            "conversion": float(item.get("conversion", 0)),
            "revenue": float(item.get("revenue", 0)),
            "points": float(item.get("points", 0)),
            "risk_of_underperform": float(item.get("risk_of_underperform", 0)),
            "trend_revenue_30d": float(item.get("trend_revenue_30d", 0)),
        },
        "actions": [
            {"type": "open_dashboard", "label": "Open dashboard"},
            {"type": "ack", "label": "Understood"}
        ],
    }
    return payload


class SalesRepository:
    def __init__(self, api_url: str = "http://localhost:8000/api/sales"):
        self.api_url = api_url

    def fetch_sales(self, since_days: int = 30, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Fetch sales data from a generic API endpoint. Filters and since_days are sent as query params.
        """
        params = {"since_days": since_days}
        if filters:
            params.update(filters)
        try:
            resp = requests.get(self.api_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # Expecting a list of dicts with required fields
            rows = []
            for m in data:
                try:
                    rows.append({
                        "dealer_id": m.get("dealer_id", "UNKNOWN"),
                        "date": m["date"],
                        "region": m.get("region"),
                        "tier": m.get("tier"),
                        "leads": float(m.get("leads", 0)),
                        "deals": float(m.get("deals", 0)),
                        "revenue": float(m.get("revenue", 0)),
                        "points": float(m.get("points", 0)),
                    })
                except Exception:
                    pass
            return rows
        except Exception as e:
            print(f"[ERROR] Could not fetch sales data from API: {e}")
            return []

# ---------- KPI ----------
class KPIService:
    def compute(self, rows: List[Dict[str, Any]], since_days: int):
        if not rows:
            return pd.DataFrame(), []

        df = pd.DataFrame(rows)

    # Accepts both ISO string ("2025-07-15") and timestamp (fallback)

        # Folosește 'order_date' dacă 'date' nu există
        date_col = None
        for c in df.columns:
            if c.lower() in ("date", "order_date", "created_at", "data", "timestamp"):
                date_col = c
                break
        if not date_col:
            raise ValueError(f"No date column found in input! Columns: {list(df.columns)}")
        try:
            df[date_col] = pd.to_datetime(df[date_col]).dt.date
        except Exception:
            df[date_col] = pd.to_datetime(df[date_col], unit="s").dt.date

        # redenumește pentru restul codului
        if date_col != "date":
            df["date"] = df[date_col]

    # time windows
        end = dt.date.today()
        start = end - dt.timedelta(days=since_days)
        prev_start = start - dt.timedelta(days=since_days)
        prev_end = start - dt.timedelta(days=1)

        curr = df[(df["date"] >= start) & (df["date"] <= end)].copy()
        prev = df[(df["date"] >= prev_start) & (df["date"] <= prev_end)].copy()

        if curr.empty:
            return pd.DataFrame(), []

    # stable aggregation on current window (no apply)
        g_curr = (
            curr.groupby(["dealer_id", "region", "tier"], as_index=False)
                .agg(
                    leads=("leads", "sum"),
                    deals=("deals", "sum"),
                    revenue=("revenue", "sum"),
                    points=("points", "sum"),
                )
        )
        g_curr["conversion"] = np.where(g_curr["leads"] > 0, g_curr["deals"] / g_curr["leads"], 0.0)

    # previous window (for trend)
        g_prev = (
            prev.groupby(["dealer_id"], as_index=False)
                .agg(
                    leads_prev=("leads", "sum"),
                    deals_prev=("deals", "sum"),
                    revenue_prev=("revenue", "sum"),
                    points_prev=("points", "sum"),
                )
        )
        g_prev["conversion_prev"] = np.where(
            g_prev["leads_prev"] > 0, g_prev["deals_prev"] / g_prev["leads_prev"], 0.0
        )

    # merge & fill
        kpis = g_curr.merge(g_prev, on="dealer_id", how="left")
        for col in ["leads_prev", "deals_prev", "revenue_prev", "points_prev", "conversion_prev"]:
            if col not in kpis:
                kpis[col] = 0.0
        kpis[["leads_prev","deals_prev","revenue_prev","points_prev","conversion_prev"]] = \
            kpis[["leads_prev","deals_prev","revenue_prev","points_prev","conversion_prev"]].fillna(0.0)

    # trends
        def trend(curr_val, prev_val):
            if prev_val == 0:
                return 0.0 if curr_val == 0 else 1.0
            return (curr_val - prev_val) / abs(prev_val)

        kpis["trend_revenue_30d"] = kpis.apply(lambda r: trend(r["revenue"], r["revenue_prev"]), axis=1)
        kpis["trend_conversion_30d"] = kpis.apply(lambda r: trend(r["conversion"], r["conversion_prev"]), axis=1)

    # simple risk 0..1
        conv_benchmark = max(0.05, float(kpis["conversion"].mean()) if len(kpis) else 0.08)
        risk = (
            ((conv_benchmark - kpis["conversion"]).clip(lower=0) / max(conv_benchmark, 1e-6))
            + (-kpis["trend_revenue_30d"]).clip(lower=0)
        ).clip(lower=0)
        kpis["risk_of_underperform"] = (risk / (risk.max() or 1)).fillna(0)

        preview_cols = [
            "dealer_id","region","tier","leads","deals","revenue","points","conversion",
            "trend_revenue_30d","trend_conversion_30d","risk_of_underperform"
        ]

        preview = kpis[preview_cols].sort_values("risk_of_underperform", ascending=False).head(15)
        return kpis, preview.to_dict(orient="records")

# ---------- LLM helpers ----------
def _openai_chat(model: str, system_msg: str, user_msg: str, temperature: float = 0.2) -> str:
    # Assistant API v2: persistent thread, agentic reasoning
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    import time
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }
    # 1. Creează asistentul (sau folosește unul existent)
    assistant_payload = {
        "instructions": system_msg,
        "model": model
    }
    a_resp = requests.post("https://api.openai.com/v1/assistants", headers=headers, json=assistant_payload, timeout=60)
    a_resp.raise_for_status()
    assistant_id = a_resp.json()["id"]
    # 2. Creează thread
    t_resp = requests.post("https://api.openai.com/v1/threads", headers=headers, timeout=60)
    t_resp.raise_for_status()
    thread_id = t_resp.json()["id"]
    # 3. Trimite mesajul user
    msg_payload = {"role": "user", "content": user_msg}
    m_resp = requests.post(f"https://api.openai.com/v1/threads/{thread_id}/messages", headers=headers, json=msg_payload, timeout=60)
    m_resp.raise_for_status()
    # 4. Rulează asistentul pe thread
    run_payload = {"assistant_id": assistant_id}
    run_resp = requests.post(f"https://api.openai.com/v1/threads/{thread_id}/runs", headers=headers, json=run_payload, timeout=60)
    run_resp.raise_for_status()
    run_id = run_resp.json()["id"]
    # 5. Polling pentru finalizare
    for _ in range(60):
        run_status = requests.get(f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}", headers=headers, timeout=60).json()
        if run_status["status"] == "completed":
            break
        time.sleep(2)
    # 6. Obține răspunsul final
    messages = requests.get(f"https://api.openai.com/v1/threads/{thread_id}/messages", headers=headers, timeout=60).json()
    for msg in messages["data"]:
        if msg["role"] == "assistant":
            # Extrage doar textul principal
            return msg["content"][0]["text"]["value"]
    raise RuntimeError("No assistant response received.")

@dataclass
class ManagerPrompt:
    goal: str
    horizon_days: int = 30
    constraints: List[str] = None
    filters: Dict[str, Any] = None

def generate_recommendations(kpis_preview: List[Dict[str,Any]], prompt: ManagerPrompt, ai_summary: str = None):
    system = (
        "You are an AI Sales Coach for FRONT-LINE sales advisors. "
        "You receive the following summary of business data and issues found in the data: "
        f"{ai_summary}\n"
        "Return a STRICT JSON array with 2-4 items. Each item must have keys: "
        "id, title, explanation. "
        "IMPORTANT: Recommendations must be ONLY SIMPLE, CONCRETE, and MEASURABLE ACTIONS that sales advisors (employees) can do directly and whose achievement can be evaluated (e.g., 'increase sales by 25%', 'contact 10 new leads per week', 'follow up with all test drive customers within 48 hours'). "
        "Recommendations MUST be based ONLY on the specific problems, statistics, and issues found in the summary above. Do NOT suggest generic actions. "
        "DO NOT suggest marketing campaigns, SEO, pricing strategy, management tasks, or anything that requires manager approval or company-level changes. "
        "Do NOT include general advice or analysis unless it results in a specific, trackable action (e.g., 'collect and review 20 customer feedback forms this month and implement at least one suggestion'). "
        "No prose, only JSON array."
    )
    user = json.dumps({
        "goal": prompt.goal,
        "horizon_days": prompt.horizon_days,
        "constraints": prompt.constraints or [],
        "filters": prompt.filters or {},
        "kpis_preview": kpis_preview[:10]
    }, ensure_ascii=False)
    raw = _openai_chat(MODEL_RECOMMEND, system, user, 0.2)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        s, e = raw.find("["), raw.rfind("]")+1
        data = json.loads(raw[s:e])
    # normalize & score
    for i, r in enumerate(data, 1):
        if "id" not in r: r["id"] = i
        r["impact"] = float(max(0, min(1, r.get("impact", 0.6))))
        r["effort"] = float(max(0, min(1, r.get("effort", 0.4))))
        r["feasibility"] = float(max(0, min(1, r.get("feasibility", 0.7))))
    data.sort(key=lambda x: -(x["impact"] * x["feasibility"] / (0.2 + x["effort"])))
    return data[:4]

def compose_message(
    goal: str,
    selected: List[Dict[str,Any]],
    style: str = "professional",
    kpis_preview: Optional[List[Dict[str,Any]]] = None,
    performance_level: str = None
) -> str:
    # 1) Identified issues (strictly from data) – top 3 at risk, but skip UNKNOWN or empty
    issues_lines: List[str] = []
    if kpis_preview:
        top = sorted(kpis_preview, key=lambda x: x.get("risk_of_underperform", 0), reverse=True)[:3]
        for r in top:
            dealer_id = r.get('dealer_id','').strip()
            region = r.get('region','').strip()
            tier = r.get('tier','').strip()
            # Skip if dealer_id is UNKNOWN or empty
            if not dealer_id or dealer_id.upper() == 'UNKNOWN':
                continue
            # Optionally, you can add a short description if you want, or just skip
            issues_lines.append(f"- Issue detected for {dealer_id} ({region}, {tier})")
    # If no real issues, do not add any line
    #if not issues_lines:
    #    issues_lines = ["(No issues identified from data for the selected period.)"]

    # 2) Allowed actions – only what advisors can do (from selected recommendations)
    allowed_actions = [
        {"title": s.get("title","").strip(), "explanation": s.get("explanation","").strip()}
        for s in (selected or []) if s.get("title")
    ]

    style_instructions = {
        "motivational": "Use an inspirational, energetic, and encouraging tone. Make the team feel empowered and excited to act.",
        "professional": "Use a formal, direct, and efficient tone. Focus on clarity, responsibility, and execution. Avoid exclamation marks and emotional language.",
        "friendly": "Use a warm, approachable, and supportive tone. Make the message feel personal and positive, as if talking to colleagues you appreciate.",
    }
    style = (locals().get('style') or 'motivational').lower()
    style_note = style_instructions.get(style, style_instructions['motivational'])
    perf_note = ""
    if performance_level:
        if performance_level == "high":
            perf_note = (
                " This message is for salespeople with HIGH sales results."
                " Use a celebratory and appreciative tone."
                " Explicitly praise their achievements and encourage them to share best practices with others."
                " The message should sound like a recognition and a push to maintain or exceed their current performance."
                " Example: 'Fantastic work! Your results are outstanding. Keep inspiring the team!'"
            )
        elif performance_level == "medium":
            perf_note = (
                " This message is for salespeople with MEDIUM/average sales results."
                " Use a supportive and motivating tone."
                " Acknowledge their effort, but encourage them to take specific steps to reach the next level."
                " The message should include practical tips and a call to action for improvement."
                " Example: 'Good job so far! With a few focused actions, you can achieve even more.'"
            )
        elif performance_level == "low":
            perf_note = (
                " This message is for salespeople with LOW/below-expectation sales results."
                " Use a constructive, direct, but empathetic tone."
                " Clearly state that improvement is needed, offer simple and concrete steps, and express confidence that they can recover."
                " The message should be honest about the situation, but also encouraging."
                " Example: 'Your results are currently below expectations. Focus on these actions to get back on track—we believe in your potential.'"
            )
    system = (
        "Write a SHORT, WELL-STRUCTURED ANNOUNCEMENT for sales advisors, IN ENGLISH.\n"
        "STRICT rules:\n"
        f"- The target audience is the sales team (front-line). {style_note}{perf_note}\n"
        "- Start with a brief, relevant introduction (1-2 sentences) that sets the context and tone, but do NOT use standard email formulas like 'Dear team' or 'Best regards'.\n"
        "- After the intro, present ALL actions from 'allowed_actions' as a clear, easy-to-read list (use bullet points or numbers). Reformulate each action in a clear, natural way, but keep all essential details (such as dealership names, models, numbers, etc.). Do NOT omit or merge any action.\n"
        "- Do NOT mention statistics, numbers, or generalities from the summary.\n"
        "- The message must focus ONLY on concrete, simple actions that each employee can do directly (e.g.: follow up with leads, ask for feedback, improve product presentation, respond faster to customer requests, etc.).\n"
        "- DO NOT include any actions or suggestions that require manager approval, company-level changes, or management analysis.\n"
        "- DO NOT mention marketing, SEO, pricing, promotional campaigns, or anything outside the direct control of a sales advisor.\n"
        "- The message should encourage teamwork, initiative, and customer focus.\n"
        "- End with a short, style-appropriate closing phrase (motivational, professional, or friendly, depending on 'style'). Optionally, you may close with a collective address such as 'Dear Team' or similar, to give the message a warm and unified feel.\n"
        "- Return only plain text, no 'Subject', no automatic signature."
    )

    user = json.dumps({
        "goal": goal,
        "style": style,
        "specific_issues": issues_lines,   # facts from KPI
        "allowed_actions": allowed_actions # actions for advisors
    }, ensure_ascii=False)

    return _openai_chat(MODEL_MESSAGE, system, user, 0.2).strip()

def ai_classify_employee_performance(all_data: dict, business_goal: str = None, period_days: int = 30) -> dict:
    """
    Trimite toate datele brute la Assistant API și cere să clasifice angajații în underperformers, average, overperformers.
    Returnează dict cu chei: underperformers, average, overperformers (fiecare listă de dict cu nume, id, dealership, motiv).
    """
    import json
    today_str = __import__('datetime').date.today().strftime('%B %d, %Y')
    system = (
        f"Today is {today_str}. "
        "You are an expert business analyst for a car dealership group. "
        "You receive ALL raw data tables (sale_orders, car_sale_items, service_sale_items, dealerships, employees, customers, vehicles, service_items). "
        f"{'The manager\'s business objective is: \'%s\'. ' % business_goal if business_goal else ''}"
        f"Analyze the most recent {period_days} days of data. "
        "Your task: Based strictly on the data, classify all employees (salespersons) into three groups: underperformers (below target), average, and overperformers (above target). "
        "For each employee, provide: id, name, dealership, region, and a short reason (e.g. 'sales 30% below avg', 'top 10% revenue', etc). "
        "If possible, estimate the target from the data (e.g. average or median sales). Do NOT use any local statistics, only what you deduce from the data. "
        "Return STRICT JSON with three keys: underperformers, average, overperformers. Each is a list of employee objects as described. No extra text, no explanations."
    )
    user = json.dumps({"all_data": all_data}, ensure_ascii=False)
    try:
        result = _openai_chat(MODEL_MESSAGE, system, user, 0.2)
        # Extrage JSON robust (code block sau direct)
        import re
        match = re.search(r"```json\\s*([\\s\\S]+?)```", result)
        if match:
            json_str = match.group(1).strip()
            return json.loads(json_str)
        # fallback: caută primul { ... }
        s, e = result.find("{"), result.rfind("}") + 1
        if s != -1 and e > s:
            return json.loads(result[s:e])
        raise ValueError("Could not extract JSON from response")
    except Exception as e:
        return {"error": str(e)}

# ---------- Seed synthetic data ----------
def optional_seed(repo: SalesRepository, dealers=6, days=60, region="DE"):
    """
    Generates synthetic data and stores date as ISO string (YYYY-MM-DD),
    so it passes Pandas filtering and appears in KPI PREVIEW.
    """
    col = repo.col
    np.random.seed(7)
    today = dt.date.today()
    ids, docs, metas = [], [], []
    for d in range(dealers):
        dealer = f"D{100+d}"
        tier = np.random.choice(["Bronze","Silver","Gold"], p=[0.4,0.4,0.2])
        base = np.random.uniform(9000, 22000) * (1.2 if tier=="Gold" else 1.0)
        for i in range(days):
            date = today - dt.timedelta(days=days - i)
            leads = max(1, int(np.random.poisson(12)))
            conv = np.clip(np.random.normal(0.09, 0.03), 0.02, 0.25)
            deals = max(0, int(leads * conv))
            revenue = float(np.random.normal(base, base*0.25))
            points = deals * (20 if tier=="Gold" else 10)
            ids.append(f"{dealer}_{date.isoformat()}_{i}")
            docs.append('{"note":"synthetic"}')
            metas.append({
                "dealer_id": dealer,                 # ex. D100
                "dealer_name": f"Salesperson {d+1}", # un nume sintetic
                "dealership_id": d + 1,              # ex. 1,2,3...
                "dealership_name": f"VW Dealer {d+1}",
                "region": region,
                "date": date.isoformat(),
                "tier": tier,
                "leads": leads,
                "deals": deals,
                "revenue": round(max(0, revenue), 2),
                "car_revenue": round(revenue * 0.8, 2),
                "service_revenue": round(revenue * 0.2, 2),
                "attach_rate": round((revenue * 0.2) / (revenue * 0.8), 4) if revenue > 0 else 0.0,
                "points": int(points)
            })


    # reset collection for a clean seed
    try:
        repo.client.reset()
        col = repo.client.get_or_create_collection(CHROMA_COLLECTION)
    except Exception:
        pass
    col.add(ids=ids, documents=docs, metadatas=metas)

# ---------- MAIN ----------
def main():
    all_data = fetch_all_core_data()
    if len(sys.argv) >= 2 and sys.argv[1] == "--seed":
        repo = SalesRepository(CHROMA_PATH, CHROMA_COLLECTION)
        optional_seed(repo)
        print("Seed OK.")
        return


    # === Nou flux: introduci obiectivul liber, AI-ul decide ce mai trebuie ===
    goal = None
    horizon = None
    region = None
    while True:
        goal_input = input("Enter your business objective (e.g., any business phrase): ").strip()
        if not goal_input:
            print("⚠️ Objective is required. Please enter something.")
            continue
        check = validate_goal_with_ai(goal_input)
        if check["is_valid"]:
            goal = goal_input
            # Automatically extract period (days) from the objective text
            import re
            horizon = None
            m = re.search(r'(\d{1,3})\s*(zile|days|day|săptămâni|weeks|luni|months)', goal_input, re.IGNORECASE)
            if m:
                val = int(m.group(1))
                unit = m.group(2).lower()
                if 'zile' in unit or 'day' in unit:
                    horizon = val
                elif 'săptămâni' in unit or 'week' in unit:
                    horizon = val * 7
                elif 'luni' in unit or 'month' in unit:
                    horizon = val * 30
            if horizon is None:
                # fallback: explicitly ask for the period if it could not be extracted
                while True:
                    horizon_in = input("Analysis period (days, 7–120): ").strip()
                    if horizon_in.isdigit():
                        horizon = int(horizon_in)
                        if 7 <= horizon <= 120:
                            break
                    print("⚠️ Please enter a number between 7 and 120.")
            break
        else:
            print(f"⚠️ Incomplete objective. Please add: {check['why']}")
            continue

    # Trimite toate datele brute la OpenAI pentru analiză și raport
    print("\n=== DATA SUMMARY (SELECTED PERIOD) ===")
    # Doar tabelele relevante pentru perioada selectată
    def filter_by_period(rows, date_keys, horizon):
        if not rows or not horizon:
            return rows
        end = dt.date.today()
        start = end - dt.timedelta(days=horizon)
        filtered = []
        for row in rows:
            for dk in date_keys:
                date_val = row.get(dk)
                if date_val:
                    try:
                        d = dt.datetime.strptime(str(date_val)[:10], "%Y-%m-%d").date()
                        if start <= d <= end:
                            filtered.append(row)
                            break
                    except Exception:
                        continue
        return filtered

    # Afișează doar tabelele cu date relevante pentru analiză pe perioadă
    period_tables = {
        "sale_orders": ["date", "order_date", "created_at", "data", "timestamp"],
        "car_sale_items": ["date", "order_date", "created_at", "data", "timestamp"],
        "service_items": ["date", "created_at", "timestamp"],
        "vehicles": ["date", "created_at", "timestamp"]
    }
    sales_counts = {}
    for key, val in all_data.items():
        if key in period_tables:
            filtered = filter_by_period(val, period_tables[key], horizon)
            print(f"{key}: {len(filtered)} records")
            sales_counts[key] = len(filtered)
    # Add service_sale_item to summary if present
    if 'service_sale_item' in all_data:
        filtered = filter_by_period(all_data['service_sale_item'], ["date", "order_date", "created_at", "data", "timestamp"], horizon)
        print(f"service_sale_item: {len(filtered)} records")
        sales_counts['service_sale_item'] = len(filtered)
    # Show combined total for all sales (car + service + service_sale_item)
    total_sales = sales_counts.get('car_sale_items', 0) + sales_counts.get('service_items', 0) + sales_counts.get('service_sale_item', 0)
    print(f"TOTAL SALES (car + service + service_sale_item): {total_sales} records")

    # Sumarizează și trimite la LLM
    summary = summarize_for_openai(all_data)
    print("\n=== LLM REPORT ===")
    # Poți folosi direct summary sau all_data pentru promptul LLM
    # Exemplu: trimite summary la OpenAI pentru analiză
    system = (
        "You are an expert business analyst for a car dealership group. "
        "You receive all raw data tables (sale_orders, car_sale_items, service_sale_items, dealerships, employees, customers, vehicles, service_items). "
        "Analyze all the data and generate a management report with the following structure: "
        "1. Identified Issues: List and explain the main problems, risks, or underperformers found in the data (regions, dealerships, employees, trends, etc). "
        "2. Recommendations for Manager: Give 2-4 concrete recommendations for improvement, addressed to the manager. DO NOT include a conclusion. Recommendations should be actionable at management level (e.g. training, marketing, inventory, process changes, etc.), not for front-line employees. "
        "Use all available data, do not ignore any table. "
        "Return a concise, actionable report in plain text."
    )
    user = json.dumps({"goal": goal, "horizon_days": horizon, "region": region, "summary": summary}, ensure_ascii=False)
    try:
        report = _openai_chat(MODEL_MESSAGE, system, user, 0.2)
        print(report)
    except Exception as e:
        print(f"[ERROR] LLM analysis failed: {e}")
    # === Recommendations and analysis based on ALL sales (car + service + service_sale_item) ===
    print("\n=== GENERATING RECOMMENDATIONS (ALL SALES TYPES) ===")
    # Merge car_sale_items, service_items, and service_sale_item for KPI and LLM analysis
    sales_rows = []
    for item in all_data.get("car_sale_items", []):
        try:
            sales_rows.append({
                "dealer_id": item.get("dealership_id", item.get("dealer_id", "UNKNOWN")),
                "date": item.get("date", item.get("order_date", dt.date.today().isoformat())),
                "region": item.get("region", "-"),
                "tier": item.get("tier", "-"),
                "leads": float(item.get("leads", 1)),
                "deals": float(item.get("deals", 1)),
                "revenue": float(item.get("revenue", item.get("amount", 0))),
                "points": float(item.get("points", 0)),
                "type": "car"
            })
        except Exception:
            pass
    for item in all_data.get("service_items", []):
        try:
            sales_rows.append({
                "dealer_id": item.get("dealership_id", item.get("dealer_id", "UNKNOWN")),
                "date": item.get("date", item.get("order_date", dt.date.today().isoformat())),
                "region": item.get("region", "-"),
                "tier": item.get("tier", "-"),
                "leads": float(item.get("leads", 1)),
                "deals": float(item.get("deals", 1)),
                "revenue": float(item.get("revenue", item.get("amount", 0))),
                "points": float(item.get("points", 0)),
                "type": "service"
            })
        except Exception:
            pass
    for item in all_data.get("service_sale_item", []):
        try:
            sales_rows.append({
                "dealer_id": item.get("dealership_id", item.get("dealer_id", "UNKNOWN")),
                "date": item.get("date", item.get("order_date", dt.date.today().isoformat())),
                "region": item.get("region", "-"),
                "tier": item.get("tier", "-"),
                "leads": float(item.get("leads", 1)),
                "deals": float(item.get("deals", 1)),
                "revenue": float(item.get("revenue", item.get("amount", 0))),
                "points": float(item.get("points", 0)),
                "type": "service_sale"
            })
        except Exception:
            pass
    kpi_service = KPIService()
    _, kpis_preview = kpi_service.compute(sales_rows, since_days=horizon)
    prompt = ManagerPrompt(goal=goal, horizon_days=horizon, filters={"region": region} if region else None)
    recommendations = generate_recommendations(kpis_preview, prompt)
    print("\nAvailable recommendations:")
    for idx, rec in enumerate(recommendations, 1):
        print(f"{idx}. {rec['title']}\n   {rec['explanation']}")

    # Selectare recomandări de către utilizator
    while True:
        sel = input("\nSelect the desired recommendations (e.g., 1,3): ").strip()
        if not sel:
            print("⚠️ You must select at least one.")
            continue
        try:
            idxs = [int(x)-1 for x in sel.split(",") if x.strip().isdigit() and 0 < int(x) <= len(recommendations)]
            if not idxs:
                raise ValueError
            selected = [recommendations[i] for i in idxs]
            break
        except Exception:
            print("⚠️ Please enter valid numbers separated by commas (e.g., 1,2)")

    # Alegere stil mesaj
    style = input("Message style (professional/motivational/friendly) [friendly]: ").strip() or "friendly"
    # Generate message with selected recommendations
    message = compose_message(goal, selected, style, kpis_preview=kpis_preview)
    print("\n=== TEAM MESSAGE ===\n")
    print(message)

    # Identify underperformers based on LLM report findings
    import re
    underperformer_names = set()
    # Try to extract dealership or region names from the LLM report's Identified Issues section
    if 'LLM REPORT' in report:
        issues_section = report.split('**1. Identified Issues:**')[-1].split('**2. Recommendations')[0]
        # Find all dealership/region mentions (simple heuristic: look for VW ... or region names)
        underperformer_names.update(re.findall(r'VW [A-Za-z ]+|NE region|NW region|Cluj-Napoca|Iasi', issues_section))
    # Map names to dealership_id using all_data['dealerships']
    name_to_id = {}
    for d in all_data.get('dealerships', []):
        if 'name' in d:
            name_to_id[d['name']] = d.get('dealership_id')
        if 'region' in d:
            name_to_id[d['region']] = d.get('dealership_id')
    # Build underperformers list
    underperformers = []
    print("\nIdentified underperformers from LLM report:")
    for name in underperformer_names:
        did = name_to_id.get(name)
        print(f"- {name}: dealership_id={did}")
        if did:
            underperformers.append({'dealer_id': did, 'reason': f'Flagged in LLM report: {name}'})

    # TEST: Forțează un underperformer manual pentru testare review-uri
    # Înlocuiește valorile cu unele reale din baza ta de date pentru test
    if not underperformers:
        print("[TEST] Forcing a test underperformer for review API demo.")
        underperformers = [{'dealer_id': 2, 'reason': 'Manual test underperformer'}]  # 2 = exemplu ID, modifică după caz

    if underperformers:
        print("\n=== SENDING MESSAGE TO UNDERPERFORMERS (LLM REPORT) ===")
        for up in underperformers:
            print(f"Message sent to dealer_id={up['dealer_id']}: {message}\nReason: {up['reason']}")
    else:
        print("No underperformers identified from LLM report.")

    # Accept/rewrite/edit and save message (for manager record)
    while True:
        act = input("\nManager, please review the message. Type [A]pprove / [R]egenerate / [E]dit manually / [G]roup send: ").strip().lower()
        if act.startswith("r"):
            new_style = input("Alternative style (professional/motivational): ").strip() or "professional"
            message = compose_message(goal, selected, new_style, kpis_preview=kpis_preview)
            print("\n===== NEW GENERATED MESSAGE =====")
            print(message)
            continue
        elif act.startswith("e"):
            print("\nWrite your desired message (line by line, finish with empty Enter):")
            lines = []
            while True:
                line = input()
                if line.strip() == "":
                    break
                lines.append(line)
            message = "\n".join(lines)
            print("\n===== MANUAL MESSAGE =====")
            print(message)
            continue
        elif act.startswith("g"):
            # === TRIMITERE GRUPATĂ ===
            print("\nSelect group to send: [L]ow / [M]edium / [H]igh / [A]ll")
            group_choice = input("Group: ").strip().lower()
            # Obține clasificarea angajaților
            performance = ai_classify_employee_performance(all_data, business_goal=goal, period_days=horizon)
            group_map = {"l": "underperformers", "m": "average", "h": "overperformers"}
            group_to_level = {"underperformers": "low", "average": "medium", "overperformers": "high"}
            groups = []
            if group_choice == "a":
                groups = ["underperformers", "average", "overperformers"]
            elif group_choice in group_map:
                groups = [group_map[group_choice]]
            else:
                print("Invalid group choice.")
                continue
            # Generează mesajele pentru fiecare grupă
            messages = {}
            for group in groups:
                level = group_to_level[group]
                messages[group] = compose_message(goal, selected, style=style, kpis_preview=kpis_preview, performance_level=level)
            # Trimite la fiecare angajat din grupă
            try:
                manager_id = int(input("Enter your manager_id for review records: ").strip())
            except Exception:
                manager_id = 1
            def send_review(manager_id, salesperson_id, review_text):
                url = "http://localhost:8000/api/reviews"
                payload = {
                    "manager_id": manager_id,
                    "salesperson_id": salesperson_id,
                    "review_text": review_text
                }
                try:
                    response = requests.post(url, json=payload)
                    if response.status_code in (200, 201):
                        print(f"✅ Review created for salesperson_id={salesperson_id}.")
                    else:
                        print(f"❌ Failed to create review for salesperson_id={salesperson_id}: {response.text}")
                except Exception as e:
                    print(f"❌ Error sending review for salesperson_id={salesperson_id}: {e}")
            for group in groups:
                msg = messages[group]
                for emp in performance.get(group, []):
                    salesperson_id = emp.get('id') or emp.get('employee_id') or emp.get('dealer_id')
                    name = emp.get('name') or emp.get('full_name') or salesperson_id
                    send_review(manager_id, salesperson_id, msg)
                    print(f"Message sent to {name} (id={salesperson_id}) [group: {group}]")
            print("\n✅ Group message(s) sent.")
            break
        elif act.startswith("a"):
            break
        else:
            print("Type A, R, E, or G.")

    # After approval, send the final message to all underperformers

    # === TRIMITE REVIEW-URI ÎN TABELA REVIEW PENTRU UNDERPERFORMERS ===
    def send_review(manager_id, salesperson_id, review_text):
        url = "http://localhost:8000/api/reviews"
        payload = {
            "manager_id": manager_id,
            "salesperson_id": salesperson_id,
            "review_text": review_text
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code in (200, 201):
                print(f"✅ Review created for salesperson_id={salesperson_id}.")
            else:
                print(f"❌ Failed to create review for salesperson_id={salesperson_id}: {response.text}")
        except Exception as e:
            print(f"❌ Error sending review for salesperson_id={salesperson_id}: {e}")

    if underperformers:
        print("\n=== FINAL MESSAGE SENT TO UNDERPERFORMERS ===")
        # TODO: Set manager_id corect (poate fi citit din context sau input)
        try:
            manager_id = int(input("Enter your manager_id for review records: ").strip())
        except Exception:
            manager_id = 1  # fallback
        for up in underperformers:
            # Caută salesperson_id asociat dealer_id (poate fi extins după nevoie)
            salesperson_id = up.get('dealer_id')  # Presupunem că dealer_id = salesperson_id, ajustează dacă e nevoie!
            review_text = f"Performance below expectations. {message} (Reason: {up['reason']})"
            send_review(manager_id, salesperson_id, review_text)
            print(f"Final message sent to dealer_id={up['dealer_id']}: {message}\nReason: {up['reason']}")
    else:
        print("No underperformers identified for final message.")

    # Save final message
    try:
        with open("final_message.txt", "w", encoding="utf-8") as f:
            f.write(message)
        print("✅ The message has been saved to final_message.txt")
    except Exception as e:
        print(f"Error saving message: {e}")

# Mesaj sumar pentru management
if __name__ == "__main__":
    main()