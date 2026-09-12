"""
🌾 AGRIWISE AI - Transparent Multi-Scenario Agricultural Profitability Engine
Calculates itemized cultivation costs, gross revenues, net returns, and ROI percentages
across Conservative, Expected, and Optimistic scenario matrices.
"""

from typing import Dict, Any

def calculate_farm_profitability(
    area_acres: float = 5.0,
    crop_name: str = "Maize",
    seed_variety: str = "Pioneer P3396 Hybrid",
    seed_cost_inr: float = 10400.0,
    fertilizer_cost_inr: float = 15200.0,
    labour_cost_inr: float = 12500.0,
    irrigation_cost_inr: float = 6500.0,
    machinery_diesel_cost_inr: float = 11000.0,
    pest_management_cost_inr: float = 4800.0,
    transport_logistics_cost_inr: float = 5800.0,
    other_miscellaneous_cost_inr: float = 3000.0,
    baseline_yield_q_acre: float = 28.5,
    baseline_selling_price_q: float = 2350.0
) -> Dict[str, Any]:
    """
    Computes transparent multi-scenario investment and return profiles.
    Strictly follows agricultural safety guidelines to label all metrics as Model-Based Estimates.
    """
    # 1. Total Cultivation Investment
    total_cost = (
        seed_cost_inr +
        fertilizer_cost_inr +
        labour_cost_inr +
        irrigation_cost_inr +
        machinery_diesel_cost_inr +
        pest_management_cost_inr +
        transport_logistics_cost_inr +
        other_miscellaneous_cost_inr
    )
    cost_per_acre = round(total_cost / area_acres, 2)

    # 2. Scenario Analysis Matrix
    # Conservative: 85% of yield, 92% of price, +8% unforeseen costs
    # Expected: 100% of yield, 100% of price, baseline costs
    # Optimistic: 112% of yield, 106% of price, -4% cost optimization

    scenarios = {}

    # Conservative
    c_yield_acre = round(baseline_yield_q_acre * 0.85, 1)
    c_total_yield_q = round(c_yield_acre * area_acres, 1)
    c_price_q = round(baseline_selling_price_q * 0.92, 2)
    c_cost = round(total_cost * 1.08, 2)
    c_revenue = round(c_total_yield_q * c_price_q, 2)
    c_profit = round(c_revenue - c_cost, 2)
    c_roi = round((c_profit / c_cost) * 100, 1) if c_cost > 0 else 0.0

    scenarios["conservative"] = {
        "label": "Conservative Scenario",
        "description": "Lower seasonal rain / slight pest pressure / subdued wholesale spot demand",
        "yield_per_acre_q": c_yield_acre,
        "total_yield_quintals": c_total_yield_q,
        "selling_price_per_q_inr": c_price_q,
        "total_cost_inr": c_cost,
        "expected_revenue_inr": c_revenue,
        "estimated_net_profit_inr": c_profit,
        "roi_percentage": c_roi,
        "profit_per_acre_inr": round(c_profit / area_acres, 2)
    }

    # Expected (Baseline)
    e_yield_acre = round(baseline_yield_q_acre, 1)
    e_total_yield_q = round(e_yield_acre * area_acres, 1)
    e_price_q = round(baseline_selling_price_q, 2)
    e_cost = round(total_cost, 2)
    e_revenue = round(e_total_yield_q * e_price_q, 2)
    e_profit = round(e_revenue - e_cost, 2)
    e_roi = round((e_profit / e_cost) * 100, 1) if e_cost > 0 else 0.0

    scenarios["expected"] = {
        "label": "Expected Scenario (Model Baseline)",
        "description": "Recommended nutrient dosage + favorable weather forecast + steady mandi pricing",
        "yield_per_acre_q": e_yield_acre,
        "total_yield_quintals": e_total_yield_q,
        "selling_price_per_q_inr": e_price_q,
        "total_cost_inr": e_cost,
        "expected_revenue_inr": e_revenue,
        "estimated_net_profit_inr": e_profit,
        "roi_percentage": e_roi,
        "profit_per_acre_inr": round(e_profit / area_acres, 2)
    }

    # Optimistic
    o_yield_acre = round(baseline_yield_q_acre * 1.12, 1)
    o_total_yield_q = round(o_yield_acre * area_acres, 1)
    o_price_q = round(baseline_selling_price_q * 1.06, 2)
    o_cost = round(total_cost * 0.96, 2)
    o_revenue = round(o_total_yield_q * o_price_q, 2)
    o_profit = round(o_revenue - o_cost, 2)
    o_roi = round((o_profit / o_cost) * 100, 1) if o_cost > 0 else 0.0

    scenarios["optimistic"] = {
        "label": "Optimistic Scenario",
        "description": "Peak hybrid vigor + premium quality grade (<12% moisture) sold directly to industrial food mills",
        "yield_per_acre_q": o_yield_acre,
        "total_yield_quintals": o_total_yield_q,
        "selling_price_per_q_inr": o_price_q,
        "total_cost_inr": o_cost,
        "expected_revenue_inr": o_revenue,
        "estimated_net_profit_inr": o_profit,
        "roi_percentage": o_roi,
        "profit_per_acre_inr": round(o_profit / area_acres, 2)
    }

    # 3. Itemized Cost Breakdown Percentage
    cost_breakdown = [
        {"category": "Certified Hybrid Seed", "amount_inr": seed_cost_inr, "percentage": round((seed_cost_inr / total_cost) * 100, 1)},
        {"category": "Fertilizers & Nutrients", "amount_inr": fertilizer_cost_inr, "percentage": round((fertilizer_cost_inr / total_cost) * 100, 1)},
        {"category": "Farm Labor (Sowing, Weeding)", "amount_inr": labour_cost_inr, "percentage": round((labour_cost_inr / total_cost) * 100, 1)},
        {"category": "Irrigation & Power", "amount_inr": irrigation_cost_inr, "percentage": round((irrigation_cost_inr / total_cost) * 100, 1)},
        {"category": "Tractor, Diesel & Machinery", "amount_inr": machinery_diesel_cost_inr, "percentage": round((machinery_diesel_cost_inr / total_cost) * 100, 1)},
        {"category": "Crop Protection & Bio-sprays", "amount_inr": pest_management_cost_inr, "percentage": round((pest_management_cost_inr / total_cost) * 100, 1)},
        {"category": "Mandi Transport Logistics", "amount_inr": transport_logistics_cost_inr, "percentage": round((transport_logistics_cost_inr / total_cost) * 100, 1)},
        {"category": "Contingency & Miscellaneous", "amount_inr": other_miscellaneous_cost_inr, "percentage": round((other_miscellaneous_cost_inr / total_cost) * 100, 1)}
    ]

    return {
        "crop": crop_name,
        "seed_variety": seed_variety,
        "area_acres": area_acres,
        "total_investment_cost_inr": round(total_cost, 2),
        "cost_per_acre_inr": cost_per_acre,
        "scenarios": scenarios,
        "cost_breakdown": cost_breakdown,
        "safety_disclaimer": "CRITICAL AGRONOMIC NOTICE: Figures reflect estimated model projections under the stated mathematical assumptions. Actual agricultural yields and market sales are subject to climatic volatility, pest infestations, mandi supply fluctuations, and biological variables. AGRIWISE AI does not guarantee financial returns or crop yields."
    }
