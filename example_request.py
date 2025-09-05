from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, List
from openai import OpenAI
import os
import json

# ------------------------------
# Domain models
# ------------------------------

@dataclass
class Car:
    model: str
    car_class: str
    price: float

    def to_public(self) -> dict:
        # Keep numbers exact; the model must copy these if it returns prices
        return {"model": self.model, "class": self.car_class, "price": self.price}

@dataclass
class UserData:
    filters: List[str]
    clicks: List[str]
    hovers: Dict[str, float]  # seconds or count
    views: Dict[str, float]   # seconds
    rental_days: int

# ------------------------------
# Prompt builder (AI infers everything)
# ------------------------------

class PromptBuilder:
    def __init__(self, upsell_cap: float = 1.15):
        self.upsell_cap = upsell_cap

def build(self, user: UserData, cars: List[Car]) -> str:
    payload = {
        "user_data": asdict(user),
        "available_cars": [c.to_public() for c in cars],
    }
    return (
        "You are a rental car recommendation engine. Respond only in JSON.\n"
        "INPUT:\n"
        f"{json.dumps(payload, ensure_ascii=False)}\n\n"
        "TASK:\n"
        "- Analyze the user's behavior (clicks, hovers, views) and the available cars (with exact prices).\n"
        "- INFER the user's preferred daily price range directly from this data.\n"
        "- Treat LOW = lower bound and HIGH = upper bound of 'preferred_price_range'.\n"
        f"- Apply SALES STRATEGY during selection/ranking:\n"
        f"  • You MAY upsell only if strongly justified AND price ≤ HIGH * {self.upsell_cap}.\n"
        "  • Prefer options that increase perceived value without padding the list.\n"
        "- Recommend only cars within the inferred range or clearly justified by the SALES STRATEGY cap.\n"
        "- Number of recommendations is NOT fixed: choose the SMALLEST sufficient list; do NOT pad.\n"
        "- Do NOT exclude cars just because they are from the same class and similar price.\n"
        "- Use ONLY the prices from 'available_cars'. Do NOT invent or reformat prices.\n"
        "- If no cars meet the criteria, return an empty 'recommended_cars' list.\n\n"
        "OUTPUT (strict JSON schema):\n"
        "{\n"
        '  "preferred_price_range": "LOW-HIGH €/day",\n'
        '  "recommended_cars": [\n'
        '    {"model": "...", "class": "...", "price": NUMBER, "reason": "match_range|upsell_justified"}\n'
        "  ],\n"
        '  "excluded_cars": [\n'
        '    {"model": "...", "class": "...", "price": NUMBER, "reason": "wrong_class|low_interest|above_range"}\n'
        "  ]\n"
        "}\n\n"
        "CONSTRAINTS:\n"
        "- Return ONLY JSON (no extra text).\n"
        "- Copy prices exactly as numbers from 'available_cars'.\n"
        "- Format preferred_price_range with exactly two decimals on both bounds.\n"
    )



# ------------------------------
# OpenAI client
# ------------------------------

class RecommenderClient:
    def __init__(self, api_key_env: str = "OPENAI_API_KEY", model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=os.getenv(api_key_env))
        self.model = model

    def recommend(self, prompt: str) -> dict:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a rental car recommendation engine. Respond only in JSON. "
                        "Infer the user's preferred price range directly from the provided user behavior and the available cars' prices. "
                        "Primary goal: maximize conversion with relevant recommendations within the inferred price range. "
                        "Secondary goal: upsell slightly within a small cap if strongly justified. "
                        "Never invent prices; use only the prices given in the input. Be precise and consistent."
                    )
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=1000 
        )
        content = resp.choices[0].message.content
        try:
            return json.loads(content)
        except Exception:
            return {"raw": content}

# ------------------------------
# Orchestrator / Service
# ------------------------------

class RecommendationService:
    def __init__(self, prompt_builder: PromptBuilder, client: RecommenderClient):
        self.prompt_builder = prompt_builder
        self.client = client

    def run(self, user: UserData, cars: List[Car]) -> dict:
        prompt = self.prompt_builder.build(user, cars)  # AI infers everything
        result = self.client.recommend(prompt)
        return result

# ------------------------------
# Example usage
# ------------------------------

def main():
    user = UserData(
        filters=["Automat"],                 # keep your actual filter labels
        clicks=["BMW X5", "Audi Q7"],
        hovers={"Mercedes GLE": 25},
        views={"Mazda MX-5 Cabrio": 60},    # seconds
        rental_days=7,
    )

    available_cars = [
        Car("BMW X5", "SUV", 48),
        Car("Audi Q7", "SUV", 55),
        Car("Mercedes GLE", "SUV", 60),
        Car("Range Rover Evoque", "SUV", 52),
        Car("Mazda MX-5 Cabrio", "Cabrio", 45),
        Car("VW Transporter", "Minivan", 40),
        Car("Toyota Corolla", "Economy", 30),
        Car("Porsche 911", "Cabrio", 200),
    ]

    prompt_builder = PromptBuilder(upsell_cap=1.15)  # allow up to +15% above inferred high if strongly justified
    client = RecommenderClient(api_key_env="OPENAI_API_KEY", model="gpt-4o-mini")
    service = RecommendationService(prompt_builder, client)

    result = service.run(user, available_cars)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
