#!/usr/bin/env python3
import os, sys, json, datetime as dt, re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import numpy as np
import pandas as pd
import requests


# ========= AI TARGETING (no email) & NOTIFICATIONS =========

def ai_select_underperformers(preview: List[Dict[str, Any]], goal: str, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Folosește LLM ca să aleagă cine e sub prag în mod inteligent.
    Returnează listă de dict: {dealer_id, reason}
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
        # fallback determinist, dacă LLM e indisponibil
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
    Construiește payloadul de notificare pe care frontend-ul îl poate consuma.
    """
    conv = f"{item.get('conversion',0)*100:.1f}%"
    payload = {
        "type": "sales_nudge",
        "audience": "individual",
        "dealer_id": item.get("dealer_id"),
        "region": item.get("region"),
        "tier": item.get("tier"),
        "title": "Atenție: oportunitate de îmbunătățire",
        "body": (
            f"Obiectiv: {goal}\n"
            f"În ultimele {horizon_days} zile: conversie {conv}, "
            f"venit {int(item.get('revenue',0))}, puncte {int(item.get('points',0))}."
            "\nSugestie: aplică direcțiile din anunțul managerului (follow-up rapid, evidențiază promoțiile, etc.)."
        ),
        "reason": reason,  # de ce a fost selectat
        "metrics": {
            "conversion": float(item.get("conversion", 0)),
            "revenue": float(item.get("revenue", 0)),
            "points": float(item.get("points", 0)),
            "risk_of_underperform": float(item.get("risk_of_underperform", 0)),
            "trend_revenue_30d": float(item.get("trend_revenue_30d", 0)),
        },
        "actions": [
            {"type": "open_dashboard", "label": "Deschide dashboard"},
            {"type": "ack", "label": "Am înțeles"}
        ],
    }
    return payload



# ---------- CONFIG ----------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "sales")

MODEL_RECOMMEND = os.getenv("OPENAI_MODEL_REC", "gpt-4o-mini")
MODEL_MESSAGE = os.getenv("OPENAI_MODEL_MSG", "gpt-4o-mini")

# ---------- CHROMA ----------
import chromadb
from chromadb.config import Settings

class SalesRepository:
    def __init__(self, path: str, collection: str):
        self.client = chromadb.PersistentClient(path=path, settings=Settings(allow_reset=True))
        self.col = self.client.get_or_create_collection(collection)

    def fetch_sales(self, since_days: int = 30, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        IMPORTANT: We do NOT filter by date in Chroma (where 'date' is stored as ISO string).
        Only simple filters are applied (e.g., region). Time windows are applied in Pandas (KPIService).
        """
        filters = filters or {}
        where: Dict[str, Any] = {}
        for k, v in filters.items():
            if isinstance(v, (str, int, float, bool)):
                where[k] = v

        res = self.col.get(where=where if where else None, include=["metadatas"])
        metas = res.get("metadatas", []) or []

        rows = []
        for m in metas:
            if not m:
                continue
            try:
                rows.append({
                    "dealer_id": m.get("dealer_id", "UNKNOWN"),
                    "date": m["date"],  # string ISO "YYYY-MM-DD"
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

# ---------- KPI ----------
class KPIService:
    def compute(self, rows: List[Dict[str, Any]], since_days: int):
        if not rows:
            return pd.DataFrame(), []

        df = pd.DataFrame(rows)

    # Accepts both ISO string ("2025-07-15") and timestamp (fallback)
        try:
            df["date"] = pd.to_datetime(df["date"]).dt.date
        except Exception:
            df["date"] = pd.to_datetime(df["date"], unit="s").dt.date

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
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages":[{"role":"system","content":system_msg},{"role":"user","content":user_msg}], "temperature": temperature}
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

@dataclass
class ManagerPrompt:
    goal: str
    horizon_days: int = 30
    constraints: List[str] = None
    filters: Dict[str, Any] = None

def generate_recommendations(kpis_preview: List[Dict[str,Any]], prompt: ManagerPrompt):
    system = (
        "You are an AI Sales Coach for FRONT-LINE sales advisors. "
        "Return a STRICT JSON array with 2-4 items. Each item must have keys: "
        "id, title, explanation, impact (0-1), effort (0-1), feasibility (0-1). "
        "IMPORTANT: Recommendations must be SIMPLE ACTIONS that sales advisors can do directly, "
        "like: faster follow-up calls, upsell related products, highlight promotions, track daily targets, "
        "confirm next-step commitments, shorten response times. "
        "DO NOT suggest marketing campaigns, SEO, pricing strategy, or management tasks. "
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
    kpis_preview: Optional[List[Dict[str,Any]]] = None
) -> str:
    # 1) Identified issues (strictly from data) – top 3 at risk
    issues_lines: List[str] = []
    if kpis_preview:
        top = sorted(kpis_preview, key=lambda x: x.get("risk_of_underperform", 0), reverse=True)[:3]
        for r in top:
            try:
                conv_pct = f"{float(r.get('conversion', 0))*100:.1f}%"
                trend_rev_pct = f"{float(r.get('trend_revenue_30d', 0))*100:+.0f}%"
                risc_pct = f"{float(r.get('risk_of_underperform', 0))*100:.0f}%"
                issues_lines.append(
                    f"- {r.get('dealer_id','UNKNOWN')} ({r.get('region','-')}, {r.get('tier','-')}): "
                    f"conversion {conv_pct}, revenue trend {trend_rev_pct}, risk {risc_pct}"
                )
            except Exception:
                continue
    if not issues_lines:
        issues_lines = ["(No issues identified from data for the selected period.)"]

    # 2) Allowed actions – only what advisors can do (from selected recommendations)
    allowed_actions = [
        {"title": s.get("title","").strip(), "explanation": s.get("explanation","").strip()}
        for s in (selected or []) if s.get("title")
    ]

    system = (
        "Write a SHORT ANNOUNCEMENT for sales advisors, IN ENGLISH.\n"
        "STRICT rules:\n"
        "- The target audience is the sales team (front-line). Tone: professional and motivational.\n"
        "- Include a section 'Identified issues (from data)' using ONLY the items from 'specific_issues'. "
        "Do not add other causes, do not invent explanations.\n"
        "- After that, offer 2–3 'Immediate directions for the team', based ONLY on the actions from 'allowed_actions'. "
        "These must be simple and concrete steps that salespeople can take directly (e.g.: rapid follow-up, upsell/cross-sell, clear presentation of benefits, confirmation of next steps, shortening response time).\n"
        "- DO NOT mention marketing, SEO, pricing, promotional campaigns, or management analysis.\n"
        "- End with a short phrase 'Why it matters' to motivate the team.\n"
        "- Return only plain text, no 'Subject', no automatic signature."
    )

    user = json.dumps({
        "goal": goal,
        "style": style,
        "specific_issues": issues_lines,   # facts from KPI
        "allowed_actions": allowed_actions # actions for advisors
    }, ensure_ascii=False)

    return _openai_chat(MODEL_MESSAGE, system, user, 0.2).strip()

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


    # reset colecția pentru seed curat
    try:
        repo.client.reset()
        col = repo.client.get_or_create_collection(CHROMA_COLLECTION)
    except Exception:
        pass
    col.add(ids=ids, documents=docs, metadatas=metas)

# ---------- MAIN ----------
def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--seed":
        repo = SalesRepository(CHROMA_PATH, CHROMA_COLLECTION)
        optional_seed(repo)
        print("Seed OK.")
        return

    goal = input("Objective (e.g.: 'Increase sales'): ").strip()
    horizon_in = input("Time window (last ... days, e.g. 30): ").strip()
    horizon = int(horizon_in) if horizon_in else 30
    region = input("Region filter (e.g. DE, Enter for all): ").strip() or None

    repo = SalesRepository(CHROMA_PATH, CHROMA_COLLECTION)
    rows = repo.fetch_sales(since_days=horizon, filters={"region": region} if region else {})
    if not rows:
        print("No records found in Chroma for the given window/filters.")
        print("You can run once:  python ai_secretary_cli.py --seed   for synthetic data.")
        sys.exit(1)

    kpisvc = KPIService()
    _kpi_df, preview = kpisvc.compute(rows, since_days=horizon)

    print("\n=== KPI PREVIEW (top risk) ===")
    if not preview:
        print("(Nothing to display — check the period or run --seed.)")
    else:
        for r in preview[:8]:
            print(f"{r['dealer_id']} | conv={r['conversion']:.3f} | rev={r['revenue']:.0f} | "
                  f"trend_rev={r['trend_revenue_30d']:.2f} | risk={r['risk_of_underperform']:.2f}")

    def champion_grade(pts: float) -> str:
        if pts >= 300:
            return "GOLD"
        if pts >= 150:
            return "SILVER"
        if pts >= 100:
            return "BRONZE"
        return "-"

    champs_df = _kpi_df[["dealer_id","region","tier","points"]].copy()
    champs_df["grade"] = champs_df["points"].apply(champion_grade)

    print("\n=== CHAMPIONS (points and grade) ===")
    for _, r in champs_df.sort_values("points", ascending=False).iterrows():
        print(f"- {r['dealer_id']} ({r['region']}, {r['tier']}): {int(r['points'])} points → {r['grade']}")

    # Identified issues (from data)
    print("\n=== IDENTIFIED ISSUES FROM DATA ===")
    if not preview:
        print("No data exists for the selected period.")
    else:
        for r in preview[:5]:
            conv = f"{r['conversion']*100:.1f}%" if r.get("conversion") is not None else "n/a"
            trend = f"{r['trend_revenue_30d']*100:+.0f}%" if r.get("trend_revenue_30d") is not None else "n/a"
            risk = f"{r['risk_of_underperform']*100:.0f}%" if r.get("risk_of_underperform") is not None else "n/a"
            print(f"- {r['dealer_id']} ({r['region']}, {r['tier']}): conversion {conv}, revenue trend {trend}, risk {risk}")

    # Recommendations (only actions for sales advisors)
    prompt = ManagerPrompt(goal=goal, horizon_days=horizon, constraints=["max 4 simple frontline actions"], filters={"region": region} if region else {})
    recs = generate_recommendations(preview, prompt)

    print("\n=== Proposed recommendations (choose IDs) ===")
    for r in recs:
        score = r["impact"] * r["feasibility"] / (0.2 + r["effort"])
        print(f"[{r['id']}] {r['title']}  | score={score:.2f}\n    {r['explanation']}\n")

    ids_raw = input("Selected ideas (e.g.: 1,3): ").strip()
    chosen_ids = {int(x) for x in re.findall(r"\d+", ids_raw)}
    selected = [r for r in recs if r["id"] in chosen_ids]
    if not selected:
        print("No valid options selected. Exiting.")
        sys.exit(1)

    style = input("Message style (professional/motivational) [professional]: ").strip() or "professional"
    msg = compose_message(goal, selected, style, kpis_preview=preview)

    # (optional) add a PS with the Champions ranking
    top3 = champs_df.sort_values("points", ascending=False).head(3)
    if not top3.empty:
        champions_note = "\n\nPS: Champions ranking: " + ", ".join(
            [f"{r['dealer_id']} {int(r['points'])}p ({r['grade']})" for _, r in top3.iterrows()]
        )
        msg = msg + champions_note


    print("\n================= DRAFT MESSAGE TO EMPLOYEES =================")
    print(msg)
    print("==============================================================\n")

    action = input("Manager, check the message. Type [A]pprove / [R]edo / [E]dit manually: ").strip().lower()
    if action.startswith("r"):
        new_style = input("Alternative style (professional/motivational): ").strip() or style
        msg = compose_message(goal, selected, new_style, kpis_preview=preview)
        print("\n===== NEW DRAFT MESSAGE =====")
        print(msg)
        print("===========================\n")
    elif action.startswith("e"):
        print("\nWrite your desired message (line by line, finish with double Enter):")
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        msg = "\n".join(lines)

    print("\n================= FINAL MESSAGE TO EMPLOYEES =================")
    print(msg)
    print("==============================================================\n")

    # (optional) save to files
    try:
        with open("mesaj_final.txt", "w", encoding="utf-8") as f:
            f.write(msg)
        with open("kpi_preview.json", "w", encoding="utf-8") as f:
            json.dump(preview, f, ensure_ascii=False, indent=2)
        print("✅ Saved: mesaj_final.txt, kpi_preview.json")
    except Exception:
        pass

         # === AI targeting -> NOTIFICATIONS JSON (no email) ===
    auto = input("Generez notificări pentru cei identificați de AI ca sub prag? (da/nu) [nu]: ").strip().lower() or "nu"
    if auto.startswith("d"):
        targets_ai = ai_select_underperformers(preview, goal, top_n=10)
        if not targets_ai:
            print("Nu am ținte de la AI. Nu generez notificări.")
        else:
            # map rapid: dealer_id -> rând KPI (din preview)
            kpi_by_id = {str(r["dealer_id"]): r for r in preview}
            notifications = []
            for t in targets_ai:
                did = str(t["dealer_id"])
                row = kpi_by_id.get(did)
                if not row:
                    continue
                notif = build_notification(row, goal, horizon, reason=t.get("reason",""))
                notifications.append(notif)

            os.makedirs("notifbox", exist_ok=True)
            # 2 variante utile: (a) one big file, (b) fișiere pe user

            # (a) Toate într-un singur JSON
            with open("notifbox/notifications.json", "w", encoding="utf-8") as f:
                json.dump({"generated_at": dt.datetime.now().isoformat(), "items": notifications},
                          f, ensure_ascii=False, indent=2)

            # (b) Un fișier pe dealer_id (ușor de servit pe frontend direct)
            for n in notifications:
                did = n.get("dealer_id", "UNKNOWN")
                with open(f"notifbox/{did}.json", "w", encoding="utf-8") as f:
                    json.dump(n, f, ensure_ascii=False, indent=2)

            print(f"✅ Notificări generate în folderul 'notifbox' "
                  f"({len(notifications)} iteme). Frontend-ul le poate consuma direct.")

    
if __name__ == "__main__":
    main()