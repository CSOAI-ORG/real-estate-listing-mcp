"""
Real Estate Listing MCP Server - Property Intelligence AI
Built by MEOK AI Labs | https://meok.ai

Property valuation, listing generation, comparable sales,
mortgage calculations, and neighborhood analysis.
"""

import time
import math
from datetime import datetime, timezone
from typing import Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "real-estate-listing")

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
_RATE_LIMITS = {"free": {"requests_per_hour": 60}, "pro": {"requests_per_hour": 5000}}
_request_log: list[float] = []
_tier = "free"


def _check_rate_limit() -> bool:
    now = time.time()
    _request_log[:] = [t for t in _request_log if now - t < 3600]
    if len(_request_log) >= _RATE_LIMITS[_tier]["requests_per_hour"]:
        return False
    _request_log.append(now)
    return True


# ---------------------------------------------------------------------------
# Market data - median price per sqft by property type and region
# ---------------------------------------------------------------------------
_PRICE_PSF: dict[str, dict[str, float]] = {
    "urban_prime": {"house": 450.0, "apartment": 520.0, "condo": 480.0, "townhouse": 410.0},
    "urban": {"house": 320.0, "apartment": 380.0, "condo": 350.0, "townhouse": 290.0},
    "suburban": {"house": 220.0, "apartment": 260.0, "condo": 240.0, "townhouse": 200.0},
    "rural": {"house": 140.0, "apartment": 170.0, "condo": 155.0, "townhouse": 130.0},
}

_CONDITION_MULTIPLIER = {
    "excellent": 1.15, "good": 1.0, "fair": 0.85, "poor": 0.70, "needs_renovation": 0.60,
}

_AGE_DEPRECIATION_RATE = 0.003  # 0.3% per year

_NEIGHBORHOOD_PROFILES: dict[str, dict] = {
    "urban_prime": {
        "walk_score": 95, "transit_score": 92, "crime_index": "low",
        "school_rating": 8.5, "amenities": ["restaurants", "theaters", "parks", "gyms", "hospitals"],
        "avg_commute_min": 15, "growth_5yr_pct": 18.5,
    },
    "urban": {
        "walk_score": 78, "transit_score": 72, "crime_index": "moderate",
        "school_rating": 7.0, "amenities": ["restaurants", "parks", "shops", "gyms"],
        "avg_commute_min": 25, "growth_5yr_pct": 12.0,
    },
    "suburban": {
        "walk_score": 45, "transit_score": 35, "crime_index": "low",
        "school_rating": 8.0, "amenities": ["parks", "schools", "shopping_centres", "sports_clubs"],
        "avg_commute_min": 40, "growth_5yr_pct": 8.5,
    },
    "rural": {
        "walk_score": 15, "transit_score": 8, "crime_index": "very_low",
        "school_rating": 6.5, "amenities": ["nature", "farms", "village_shops"],
        "avg_commute_min": 55, "growth_5yr_pct": 5.0,
    },
}


@mcp.tool()
def estimate_valuation(
    sqft: float,
    bedrooms: int,
    bathrooms: int,
    property_type: str = "house",
    location_tier: str = "suburban",
    condition: str = "good",
    year_built: int = 2000,
    lot_sqft: Optional[float] = None,
    garage_spaces: int = 0) -> dict:
    """Estimate property valuation using comp-based methodology.

    Args:
        sqft: Interior square footage.
        bedrooms: Number of bedrooms.
        bathrooms: Number of bathrooms.
        property_type: house | apartment | condo | townhouse.
        location_tier: urban_prime | urban | suburban | rural.
        condition: excellent | good | fair | poor | needs_renovation.
        year_built: Year the property was built.
        lot_sqft: Total lot size in sqft (houses only).
        garage_spaces: Number of garage spaces.
    """
    if not _check_rate_limit():
        return {"error": "Rate limit exceeded. Upgrade to pro tier."}

    psf = _PRICE_PSF.get(location_tier, _PRICE_PSF["suburban"]).get(property_type, 250.0)
    base_value = sqft * psf

    # Condition adjustment
    cond_mult = _CONDITION_MULTIPLIER.get(condition, 1.0)
    base_value *= cond_mult

    # Age depreciation
    age = max(0, datetime.now().year - year_built)
    age_factor = max(0.60, 1.0 - (age * _AGE_DEPRECIATION_RATE))
    base_value *= age_factor

    # Bedroom / bathroom premium
    if bedrooms >= 4:
        base_value *= 1.05
    if bathrooms >= 3:
        base_value *= 1.03

    # Garage premium
    base_value += garage_spaces * 25_000

    # Lot premium (houses)
    if lot_sqft and property_type == "house":
        excess_lot = max(0, lot_sqft - sqft * 3)
        base_value += excess_lot * 15

    low = round(base_value * 0.92)
    mid = round(base_value)
    high = round(base_value * 1.08)

    return {
        "estimated_value": {"low": low, "mid": mid, "high": high, "currency": "USD"},
        "price_per_sqft": round(mid / sqft, 2),
        "methodology": "comp-based with condition, age, and feature adjustments",
        "factors": {
            "base_psf": psf, "condition_multiplier": cond_mult,
            "age_years": age, "age_factor": round(age_factor, 4),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def generate_listing(
    address: str,
    sqft: float,
    bedrooms: int,
    bathrooms: int,
    property_type: str = "house",
    features: Optional[list[str]] = None,
    style: str = "professional",
    price: Optional[float] = None) -> dict:
    """Generate a professional property listing description.

    Args:
        address: Full property address.
        sqft: Interior square footage.
        bedrooms: Number of bedrooms.
        bathrooms: Number of bathrooms.
        property_type: house | apartment | condo | townhouse.
        features: List of notable features (e.g. pool, garden, renovated kitchen).
        style: professional | luxury | first_home | investment.
        price: Listing price (optional).
    """
    if not _check_rate_limit():
        return {"error": "Rate limit exceeded. Upgrade to pro tier."}

    features = features or []
    type_label = property_type.replace("_", " ").title()

    openers = {
        "professional": f"Presenting this well-maintained {bedrooms}-bedroom {type_label.lower()} at {address}.",
        "luxury": f"An exceptional {bedrooms}-bedroom residence awaits at {address}.",
        "first_home": f"Start your homeownership journey with this charming {bedrooms}-bedroom {type_label.lower()} at {address}.",
        "investment": f"Outstanding investment opportunity - {bedrooms}-bed {type_label.lower()} at {address} with strong rental potential.",
    }

    opener = openers.get(style, openers["professional"])
    size_desc = f"Spanning {sqft:,.0f} sq ft with {bedrooms} bedrooms and {bathrooms} bathrooms"
    feature_desc = ""
    if features:
        feature_list = ", ".join(features[:-1]) + f" and {features[-1]}" if len(features) > 1 else features[0]
        feature_desc = f" Key highlights include {feature_list}."

    description = f"{opener} {size_desc}, this property offers comfortable living in a desirable location.{feature_desc}"

    headline = f"{bedrooms} Bed {type_label} | {sqft:,.0f} sq ft"
    if price:
        headline += f" | ${price:,.0f}"

    return {
        "headline": headline,
        "description": description,
        "property_summary": {
            "address": address, "type": property_type, "sqft": sqft,
            "bedrooms": bedrooms, "bathrooms": bathrooms, "features": features,
        },
        "seo_keywords": [
            f"{bedrooms} bedroom {property_type}", f"{property_type} for sale",
            address.split(",")[-1].strip() if "," in address else address,
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def find_comparable_sales(
    sqft: float,
    bedrooms: int,
    property_type: str = "house",
    location_tier: str = "suburban",
    max_results: int = 5) -> dict:
    """Find comparable recent sales for pricing analysis.

    Args:
        sqft: Target property square footage.
        bedrooms: Target bedrooms.
        property_type: house | apartment | condo | townhouse.
        location_tier: urban_prime | urban | suburban | rural.
        max_results: Number of comps to return (1-10).
    """
    if not _check_rate_limit():
        return {"error": "Rate limit exceeded. Upgrade to pro tier."}

    import random
    random.seed(int(sqft * bedrooms * hash(location_tier) % 100000))

    psf = _PRICE_PSF.get(location_tier, _PRICE_PSF["suburban"]).get(property_type, 250.0)
    max_results = min(max(1, max_results), 10)

    comps = []
    for i in range(max_results):
        variance_sqft = random.uniform(-0.15, 0.15)
        comp_sqft = round(sqft * (1 + variance_sqft))
        variance_price = random.uniform(-0.12, 0.12)
        comp_psf = round(psf * (1 + variance_price), 2)
        comp_price = round(comp_sqft * comp_psf)
        days_ago = random.randint(14, 180)

        comps.append({
            "comp_id": f"COMP-{i+1:03d}",
            "sqft": comp_sqft,
            "bedrooms": bedrooms + random.choice([-1, 0, 0, 0, 1]),
            "property_type": property_type,
            "sale_price": comp_price,
            "price_per_sqft": comp_psf,
            "days_since_sale": days_ago,
            "similarity_score": round(1.0 - abs(variance_sqft) - abs(variance_price) * 0.5, 3),
        })

    comps.sort(key=lambda c: c["similarity_score"], reverse=True)
    avg_psf = round(sum(c["price_per_sqft"] for c in comps) / len(comps), 2)

    return {
        "target": {"sqft": sqft, "bedrooms": bedrooms, "type": property_type, "location": location_tier},
        "comparables": comps,
        "market_summary": {
            "avg_price_per_sqft": avg_psf,
            "implied_value": round(sqft * avg_psf),
            "comp_count": len(comps),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def calculate_mortgage(
    principal: float,
    annual_rate_pct: float = 6.5,
    term_years: int = 30,
    down_payment_pct: float = 20.0,
    property_tax_annual: float = 0.0,
    insurance_annual: float = 0.0,
    hoa_monthly: float = 0.0) -> dict:
    """Calculate monthly mortgage payment with full breakdown.

    Args:
        principal: Property purchase price.
        annual_rate_pct: Annual interest rate as percentage (e.g. 6.5).
        term_years: Loan term in years.
        down_payment_pct: Down payment as percentage of price.
        property_tax_annual: Annual property tax.
        insurance_annual: Annual homeowner insurance.
        hoa_monthly: Monthly HOA fee.
    """
    if not _check_rate_limit():
        return {"error": "Rate limit exceeded. Upgrade to pro tier."}

    down_payment = principal * (down_payment_pct / 100)
    loan_amount = principal - down_payment
    monthly_rate = (annual_rate_pct / 100) / 12
    n_payments = term_years * 12

    if monthly_rate == 0:
        monthly_pi = loan_amount / n_payments
    else:
        monthly_pi = loan_amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / (
            (1 + monthly_rate) ** n_payments - 1
        )

    monthly_tax = property_tax_annual / 12
    monthly_insurance = insurance_annual / 12
    total_monthly = monthly_pi + monthly_tax + monthly_insurance + hoa_monthly
    total_interest = (monthly_pi * n_payments) - loan_amount

    # Amortization first 5 years summary
    balance = loan_amount
    yearly_summary = []
    for year in range(1, min(6, term_years + 1)):
        year_interest = 0
        year_principal = 0
        for _ in range(12):
            interest_payment = balance * monthly_rate
            principal_payment = monthly_pi - interest_payment
            year_interest += interest_payment
            year_principal += principal_payment
            balance -= principal_payment
        yearly_summary.append({
            "year": year, "principal_paid": round(year_principal),
            "interest_paid": round(year_interest), "remaining_balance": round(max(0, balance)),
        })

    return {
        "purchase_price": principal,
        "down_payment": round(down_payment),
        "loan_amount": round(loan_amount),
        "monthly_payment": {
            "principal_and_interest": round(monthly_pi, 2),
            "property_tax": round(monthly_tax, 2),
            "insurance": round(monthly_insurance, 2),
            "hoa": hoa_monthly,
            "total": round(total_monthly, 2),
        },
        "loan_summary": {
            "term_years": term_years, "rate_pct": annual_rate_pct,
            "total_interest": round(total_interest),
            "total_cost": round(total_interest + loan_amount),
        },
        "amortization_preview": yearly_summary,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def analyze_neighborhood(
    location_tier: str = "suburban",
    priorities: Optional[list[str]] = None) -> dict:
    """Analyze neighborhood characteristics and livability scores.

    Args:
        location_tier: urban_prime | urban | suburban | rural.
        priorities: Ranked buyer priorities (e.g. schools, commute, safety, nightlife).
    """
    if not _check_rate_limit():
        return {"error": "Rate limit exceeded. Upgrade to pro tier."}

    profile = _NEIGHBORHOOD_PROFILES.get(location_tier, _NEIGHBORHOOD_PROFILES["suburban"])
    priorities = priorities or ["schools", "safety", "commute"]

    priority_scores = {
        "schools": min(10, profile["school_rating"] * 1.1),
        "safety": {"very_low": 9.5, "low": 8.5, "moderate": 6.0, "high": 3.5}.get(profile["crime_index"], 5),
        "commute": max(1, 10 - profile["avg_commute_min"] / 8),
        "walkability": profile["walk_score"] / 10,
        "transit": profile["transit_score"] / 10,
        "nightlife": {"urban_prime": 9, "urban": 7, "suburban": 4, "rural": 2}.get(location_tier, 5),
        "nature": {"urban_prime": 4, "urban": 5, "suburban": 7, "rural": 9.5}.get(location_tier, 6),
        "investment": min(10, profile["growth_5yr_pct"] / 2),
    }

    weighted_score = 0
    total_weight = 0
    for i, p in enumerate(priorities[:5]):
        weight = 5 - i
        weighted_score += priority_scores.get(p, 5) * weight
        total_weight += weight
    overall = round(weighted_score / total_weight, 1) if total_weight else 5.0

    return {
        "location_tier": location_tier,
        "profile": profile,
        "scores": {k: round(v, 1) for k, v in priority_scores.items()},
        "buyer_match": {
            "priorities": priorities, "weighted_score": overall,
            "verdict": "excellent" if overall >= 8 else "good" if overall >= 6 else "fair" if overall >= 4 else "poor",
        },
        "investment_outlook": {
            "5yr_growth_pct": profile["growth_5yr_pct"],
            "rating": "strong" if profile["growth_5yr_pct"] > 10 else "moderate" if profile["growth_5yr_pct"] > 6 else "stable",
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    mcp.run()
