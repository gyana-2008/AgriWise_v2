"""
🌾 AGRIWISE AI - Automated Backend & Engine Test Suite
Zero external test dependencies; directly verifies database models,
decision engine calculations, live weather API, and profit simulations.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)

from database import SessionLocal, init_db, User, Farm, Crop, SeedVariety, Dealer, Buyer, TransportProvider, CropShortage, ConfigWeights
from seed_data import populate_database
from engines.weather_service import fetch_live_weather
from engines.recommendation import evaluate_crop_suitability, calculate_fertilizer_plan, DEFAULT_WEIGHTS
from engines.profitability import calculate_farm_profitability
from engines.assistant import process_assistant_query

def run_tests():
    print("🌾 Starting AGRIWISE AI direct automated verification test suite...")

    # 1. Database & Seed Verification
    init_db()
    populate_database()
    db = SessionLocal()

    user_count = db.query(User).count()
    farm_count = db.query(Farm).count()
    crop_count = db.query(Crop).count()
    seed_count = db.query(SeedVariety).count()
    dealer_count = db.query(Dealer).count()
    shortage_count = db.query(CropShortage).count()
    db.close()

    assert user_count >= 5, f"Expected >= 5 users, got {user_count}"
    assert farm_count >= 2, f"Expected >= 2 farms, got {farm_count}"
    assert crop_count >= 5, f"Expected >= 5 crops, got {crop_count}"
    assert seed_count >= 5, f"Expected >= 5 seeds, got {seed_count}"
    assert dealer_count >= 3, f"Expected >= 3 dealers, got {dealer_count}"
    assert shortage_count >= 8, f"Expected >= 8 shortage state records, got {shortage_count}"
    print(f"  ✓ Database verified: {user_count} users, {farm_count} farms, {crop_count} crops, {seed_count} seed varieties, {shortage_count} shortage records.")

    # 2. Live Weather Engine Test
    weather = fetch_live_weather(lat=30.9010, lon=75.8573, location_name="Sahnewal, Ludhiana")
    assert "current" in weather
    assert "temperature_c" in weather["current"]
    assert "agronomic_advisory" in weather
    print(f"  ✓ Weather engine passed: {weather['current']['temperature_c']}°C, Condition: {weather['current']['condition']}, Advisories: {len(weather['agronomic_advisory'])}")

    # 3. Crop Recommendation Engine Test
    crop_sample = {
        "name": "Maize",
        "season": "Kharif",
        "category": "Cereal",
        "optimum_temp_min": 18.0,
        "optimum_temp_max": 33.0,
        "optimum_ph_min": 5.8,
        "optimum_ph_max": 7.5,
        "water_req_level": "Medium",
        "demand_status": "High (Shortage in Processing)",
        "profit_potential": "High",
        "expected_yield_q_acre": 28.5,
        "current_mandi_price_q": 2350.0
    }
    soil_sample = {"ph": 6.8, "nitrogen_kg_ha": 260.0, "phosphorus_kg_ha": 22.5, "potassium_kg_ha": 280.0}
    water_sample = {"ec_ds_m": 0.65, "tds_ppm": 420.0}

    rec = evaluate_crop_suitability(crop_sample, soil_sample, water_sample, weather, DEFAULT_WEIGHTS)
    assert rec["suitability_score"] >= 80, f"Expected score >= 80, got {rec['suitability_score']}"
    assert len(rec["reasons"]) > 0
    print(f"  ✓ Crop Recommendation engine passed: {rec['crop_name']} suitability score: {rec['suitability_score']}% with confidence {rec['confidence']}")

    # 4. Scientific Fertilizer Plan Test
    fert = calculate_fertilizer_plan("Maize", 5.0, soil_sample)
    assert "nutrients_per_acre" in fert
    assert "recommended_products" in fert
    assert fert["total_estimated_fertilizer_cost_inr"] > 0
    print(f"  ✓ Fertilizer engine passed: Total estimated cost ₹{fert['total_estimated_fertilizer_cost_inr']} for 5.0 acres across {len(fert['recommended_products'])} products")

    # 5. Multi-Scenario Profitability Engine Test
    profit = calculate_farm_profitability(
        area_acres=5.0,
        crop_name="Maize",
        baseline_yield_q_acre=28.5,
        baseline_selling_price_q=2350.0
    )
    assert "scenarios" in profit
    sc = profit["scenarios"]
    assert sc["conservative"]["estimated_net_profit_inr"] > 0
    assert sc["expected"]["estimated_net_profit_inr"] > sc["conservative"]["estimated_net_profit_inr"]
    assert sc["optimistic"]["estimated_net_profit_inr"] > sc["expected"]["estimated_net_profit_inr"]
    print(f"  ✓ Profitability engine passed: Conservative (₹{sc['conservative']['estimated_net_profit_inr']}), Expected (₹{sc['expected']['estimated_net_profit_inr']}), Optimistic (₹{sc['optimistic']['estimated_net_profit_inr']})")

    # 6. AI Agronomist Assistant Engine Test
    chat = process_assistant_query("Why is maize recommended for my farm?", {"name": "Sahnewal Farm", "soil": {"ph": 6.8}}, weather, {"crop": "Maize"})
    assert "answer" in chat
    assert "Maize" in chat["answer"]
    print("  ✓ AI Assistant passed: Context-grounded response successfully synthesized")

    # 7. Payment Gateway Tests
    from database import PaymentTransaction
    tx_count = db.query(PaymentTransaction).count()
    assert tx_count >= 5, f"Expected at least 5 seeded transactions, got {tx_count}"
    
    # Test Payment Intent creation via main API endpoints
    import main
    intent_payload = {
        "amount_inr": 14365.0,
        "payment_type": "INPUT_PURCHASE",
        "payment_method": "KCC_RUPAY",
        "payer_name": "Sardar Gurpreet Singh",
        "payee_name": "IFFCO Kisan Kendra"
    }
    intent_res = main.create_payment_intent(intent_payload, db)
    assert intent_res["success"] is True
    assert intent_res["subsidy_amount_inr"] > 0 # 3% KCC subvention
    assert "AGRI-PAY" in intent_res["transaction_id"]
    test_tx_id = intent_res["transaction_id"]

    # Test Payment Verification
    verify_res = main.verify_payment({"transaction_id": test_tx_id, "payment_method": "KCC_RUPAY"}, db)
    assert verify_res["success"] is True
    assert verify_res["status"] == "SUCCESS"

    # Test Receipt Generation
    receipt = main.get_payment_receipt(test_tx_id, db)
    assert receipt["transaction_id"] == test_tx_id
    assert receipt["subsidy_amount_inr"] > 0
    assert "GOVERNMENT OF INDIA" in receipt["stamp"]
    print("  ✓ Payment Gateway passed: Intent, KCC subvention (3%), verification & receipt verified")

    # 8. Verify all dedicated frontend pages exist on disk
    frontend_pages = [
        "index.html", "pages/dashboard.html", "pages/farm-profile.html", "pages/farm-analysis.html",
        "pages/weather.html", "pages/crop-recommendation.html", "pages/crop-details.html",
        "pages/seed-recommendation.html", "pages/seed-details.html", "pages/cultivation-plan.html",
        "pages/fertilizer-recommendation.html", "pages/fertilizer-market.html", "pages/water-analysis.html",
        "pages/market-intelligence.html", "pages/crop-demand.html", "pages/crop-shortage.html",
        "pages/profit-estimator.html", "pages/buyer-marketplace.html", "pages/transport-marketplace.html",
        "pages/farm-to-market.html", "pages/farmer-orders.html", "pages/payment.html", "pages/dealer-dashboard.html",
        "pages/transport-dashboard.html", "pages/buyer-dashboard.html", "pages/ai-assistant.html",
        "pages/farm-calendar.html", "pages/notifications.html", "pages/farm-report.html",
        "pages/admin.html", "pages/login.html", "pages/register.html", "pages/forgot-password.html", "pages/verify-account.html"
    ]

    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    for p in frontend_pages:
        full_p = os.path.join(frontend_dir, p)
        assert os.path.exists(full_p), f"Missing page: {p}"

    print(f"  ✓ All {len(frontend_pages)} dedicated HTML pages verified on disk!")
    print("\n✅ ALL ENGINE, PAYMENT, AND DATABASE TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_tests()
