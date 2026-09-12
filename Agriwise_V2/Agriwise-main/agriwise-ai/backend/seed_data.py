"""
🌾 AGRIWISE AI - Realistic Seed Data for Indian Agriculture
Covers Crops, Seed Varieties, Fertilizers, Dealers, Buyers, Transporters,
Shortage Map States, Demo Users, and Config Weights.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import json
from datetime import datetime, timedelta
from database import (
    SessionLocal, init_db, User, Farm, SoilProfile, WaterProfile,
    Crop, SeedVariety, FertilizerProduct, Dealer, MarketPrice,
    CropShortage, Buyer, TransportProvider, Order, Notification, ConfigWeights,
    PaymentTransaction, Equipment, EquipmentBooking
)

def populate_database():
    init_db()
    db = SessionLocal()

    # If already seeded users, check if payments or equipment exist
    if db.query(User).count() > 0:
        if db.query(PaymentTransaction).count() == 0:
            seed_payments(db)
        if db.query(Equipment).count() == 0:
            seed_equipment(db)
        db.close()
        return

    print("🌾 Seeding AGRIWISE AI database with realistic Indian agriculture data...")

    # 1. Config Weights
    weights = ConfigWeights(
        climate_weight=0.20,
        soil_weight=0.20,
        water_weight=0.15,
        weather_weight=0.15,
        season_weight=0.10,
        market_weight=0.10,
        economics_weight=0.10
    )
    db.add(weights)

    # 2. Users (Roles: Farmer, Dealer, Transporter, Buyer, Admin)
    farmer_user = User(
        name="Gurpreet Singh",
        email="gurpreet.farmer@agriwise.ai",
        phone="+91 98765 43210",
        role="FARMER",
        state="Punjab",
        district="Ludhiana",
        village="Sahnewal",
        farm_size_acres=5.0,
        experience_years=14
    )
    dealer_user = User(
        name="Kisan Seva Kendra (Rajinder Kumar)",
        email="rajinder.dealer@agriwise.ai",
        phone="+91 98141 23456",
        role="DEALER",
        state="Punjab",
        district="Ludhiana",
        village="Sahnewal Mandi Road",
        farm_size_acres=0.0,
        experience_years=20
    )
    transporter_user = User(
        name="Balwinder Logistics",
        email="balwinder.transport@agriwise.ai",
        phone="+91 98722 89012",
        role="TRANSPORTER",
        state="Punjab",
        district="Ludhiana",
        village="GT Road Transport Nagar",
        farm_size_acres=0.0,
        experience_years=15
    )
    buyer_user = User(
        name="ABC Agro Foods & Mills",
        email="procurement@abcfoods.in",
        phone="+91 98555 67890",
        role="BUYER",
        state="Punjab",
        district="Ludhiana",
        village="Khanna Industrial Area",
        farm_size_acres=0.0,
        experience_years=18
    )
    admin_user = User(
        name="AgriWise System Administrator",
        email="admin@agriwise.ai",
        phone="+91 98000 11223",
        role="ADMIN",
        state="National",
        district="New Delhi",
        village="Pusa Agri Complex",
        farm_size_acres=0.0,
        experience_years=25
    )
    db.add_all([farmer_user, dealer_user, transporter_user, buyer_user, admin_user])
    db.commit()

    # 3. Demo Farms for Farmer
    farm1 = Farm(
        user_id=farmer_user.id,
        name="Sahnewal Golden Acre Farm",
        location_name="Sahnewal, Ludhiana, Punjab",
        latitude=30.9010,
        longitude=75.8573,
        elevation_m=244.0,
        area_acres=5.0,
        current_crop="Maize (Corn)",
        current_season="Kharif",
        previous_crop="Wheat (PBW 550)",
        irrigation_method="Subsurface Drip + Tube-well",
        water_source="Deep Tube-well (180 ft)",
        water_availability="Abundant (High)",
        farming_method="Precision Integrated Nutrient Management"
    )
    farm2 = Farm(
        user_id=farmer_user.id,
        name="Khamanon Canal Farm",
        location_name="Khamanon, Fatehgarh Sahib, Punjab",
        latitude=30.8200,
        longitude=76.2200,
        elevation_m=250.0,
        area_acres=3.5,
        current_crop="Basmati Rice",
        current_season="Kharif",
        previous_crop="Mustard",
        irrigation_method="Canal Siphon + Furrow",
        water_source="Sirhind Canal Distributary",
        water_availability="Seasonal Reliable",
        farming_method="Conventional Mechanized"
    )
    db.add_all([farm1, farm2])
    db.commit()

    # 4. Soil Profiles
    soil1 = SoilProfile(
        farm_id=farm1.id,
        soil_type="Alluvial Loam (Sandy Loam subsoil)",
        ph=6.8,
        nitrogen_kg_ha=260.0,
        phosphorus_kg_ha=22.5,
        potassium_kg_ha=280.0,
        organic_carbon_pct=0.62,
        moisture_pct=22.0,
        ec_ds_m=0.45,
        health_score=85
    )
    soil2 = SoilProfile(
        farm_id=farm2.id,
        soil_type="Clay Loam (Rich Alluvial)",
        ph=7.4,
        nitrogen_kg_ha=290.0,
        phosphorus_kg_ha=18.0,
        potassium_kg_ha=310.0,
        organic_carbon_pct=0.75,
        moisture_pct=28.0,
        ec_ds_m=0.52,
        health_score=88
    )
    db.add_all([soil1, soil2])

    # 5. Water Profiles
    water1 = WaterProfile(
        farm_id=farm1.id,
        source="Deep Groundwater Tube-well",
        ph=7.2,
        ec_ds_m=0.65,
        tds_ppm=420.0,
        salinity_status="Safe / Good Quality",
        hardness_mg_l=180.0,
        suitability_score=88
    )
    water2 = WaterProfile(
        farm_id=farm2.id,
        source="Canal Water",
        ph=7.1,
        ec_ds_m=0.40,
        tds_ppm=260.0,
        salinity_status="Excellent Quality (Low EC)",
        hardness_mg_l=140.0,
        suitability_score=94
    )
    db.add_all([water1, water2])
    db.commit()

    # 6. Crops
    crops_data = [
        {
            "name": "Maize",
            "hindi_name": "मक्का (Makka)",
            "punjabi_name": "ਮੱਕੀ (Makki)",
            "season": "Kharif",
            "category": "Cereal / Industrial Grain",
            "typical_duration_days": 105,
            "water_req_level": "Medium",
            "optimum_temp_min": 18.0,
            "optimum_temp_max": 33.0,
            "optimum_ph_min": 5.8,
            "optimum_ph_max": 7.5,
            "expected_yield_q_acre": 28.5,
            "current_mandi_price_q": 2350.0,
            "msp_price_q": 2090.0,
            "demand_status": "High (Shortage in Processing)",
            "profit_potential": "High",
            "description": "High market liquidity with surging demand from ethanol, poultry feed and starch processing plants."
        },
        {
            "name": "Soybean",
            "hindi_name": "सोयाबीन (Soybean)",
            "punjabi_name": "ਸੋਇਆਬੀਨ (Soybean)",
            "season": "Kharif",
            "category": "Oilseed / Legume",
            "typical_duration_days": 98,
            "water_req_level": "Medium-Low",
            "optimum_temp_min": 20.0,
            "optimum_temp_max": 32.0,
            "optimum_ph_min": 6.0,
            "optimum_ph_max": 7.5,
            "expected_yield_q_acre": 12.0,
            "current_mandi_price_q": 4650.0,
            "msp_price_q": 4600.0,
            "demand_status": "High (Crushing Demand)",
            "profit_potential": "High",
            "description": "Nitrogen-fixing legume requiring lower chemical fertilizers, providing excellent soil health restoration."
        },
        {
            "name": "Wheat",
            "hindi_name": "गेहूं (Gehun)",
            "punjabi_name": "ਕਣਕ (Kanak)",
            "season": "Rabi",
            "category": "Cereal / Staple",
            "typical_duration_days": 135,
            "water_req_level": "Medium",
            "optimum_temp_min": 12.0,
            "optimum_temp_max": 25.0,
            "optimum_ph_min": 6.0,
            "optimum_ph_max": 7.8,
            "expected_yield_q_acre": 22.0,
            "current_mandi_price_q": 2425.0,
            "msp_price_q": 2275.0,
            "demand_status": "Very High (Government & Milling)",
            "profit_potential": "Medium-High",
            "description": "Staple winter cereal with guaranteed procurement and steady open market premiums."
        },
        {
            "name": "Basmati Rice",
            "hindi_name": "बासमती धान (Basmati Dhan)",
            "punjabi_name": "ਬਾਸਮਤੀ ਚੌਲ (Basmati Chawal)",
            "season": "Kharif",
            "category": "Aromatic Cereal",
            "typical_duration_days": 125,
            "water_req_level": "High",
            "optimum_temp_min": 22.0,
            "optimum_temp_max": 35.0,
            "optimum_ph_min": 5.5,
            "optimum_ph_max": 7.2,
            "expected_yield_q_acre": 20.0,
            "current_mandi_price_q": 3850.0,
            "msp_price_q": 2183.0,
            "demand_status": "High (Export Demand)",
            "profit_potential": "High",
            "description": "Premium aromatic rice command strong export prices in Middle East and European markets."
        },
        {
            "name": "Cotton (Bt)",
            "hindi_name": "कपास (Kapas)",
            "punjabi_name": "ਕਪਾਹ (Kapas / Narma)",
            "season": "Kharif",
            "category": "Commercial Fiber",
            "typical_duration_days": 160,
            "water_req_level": "Medium-High",
            "optimum_temp_min": 21.0,
            "optimum_temp_max": 38.0,
            "optimum_ph_min": 6.0,
            "optimum_ph_max": 8.0,
            "expected_yield_q_acre": 10.5,
            "current_mandi_price_q": 7100.0,
            "msp_price_q": 6620.0,
            "demand_status": "Medium",
            "profit_potential": "High (Volatility)",
            "description": "High value cash crop suited for well-drained soils; requires proactive pest monitoring."
        },
        {
            "name": "Mustard",
            "hindi_name": "सरसों (Sarson)",
            "punjabi_name": "ਸਰ੍ਹੋਂ (Sarhon)",
            "season": "Rabi",
            "category": "Oilseed",
            "typical_duration_days": 115,
            "water_req_level": "Low",
            "optimum_temp_min": 10.0,
            "optimum_temp_max": 25.0,
            "optimum_ph_min": 6.0,
            "optimum_ph_max": 7.5,
            "expected_yield_q_acre": 9.5,
            "current_mandi_price_q": 5450.0,
            "msp_price_q": 5650.0,
            "demand_status": "High (Domestic Edible Oil)",
            "profit_potential": "High",
            "description": "Low water requirement, ideal for conserving groundwater in winter rotations."
        },
        {
            "name": "Tomato",
            "hindi_name": "टमाटर (Tamatar)",
            "punjabi_name": "ਟਮਾਟਰ (Tamatar)",
            "season": "Zaid / Kharif",
            "category": "Horticulture Vegetable",
            "typical_duration_days": 90,
            "water_req_level": "Medium",
            "optimum_temp_min": 18.0,
            "optimum_temp_max": 30.0,
            "optimum_ph_min": 6.0,
            "optimum_ph_max": 7.0,
            "expected_yield_q_acre": 140.0,
            "current_mandi_price_q": 1800.0,
            "msp_price_q": 0.0,
            "demand_status": "Extreme Volatility (High Demand)",
            "profit_potential": "Very High",
            "description": "Short duration high-yield vegetable crop giving rapid cash-flow cycles."
        }
    ]

    crop_objects = {}
    for c in crops_data:
        crop = Crop(**c)
        db.add(crop)
        crop_objects[c["name"]] = crop
    db.commit()

    # 7. Seed Varieties
    seeds_data = [
        # Maize Seeds
        {
            "crop_name": "Maize",
            "name": "Pioneer P3396 Hybrid",
            "variety_code": "PIO-3396",
            "manufacturer": "Corteva Agriscience",
            "duration_days": 108,
            "expected_yield_min_q": 27.0,
            "expected_yield_max_q": 32.0,
            "seed_rate_kg_acre": 8.0,
            "price_per_kg": 260.0,
            "disease_resistance": "High (Turcicum Leaf Blight & Downy Mildew)",
            "drought_tolerance": "High",
            "soil_affinity": "Alluvial, Loamy, Well-drained soils",
            "suitability_pct": 95,
            "certified": True,
            "key_features": "Heavy cob girth, stay-green trait, excellent shelling %"
        },
        {
            "crop_name": "Maize",
            "name": "Kaveri 50 Super Hybrid",
            "variety_code": "KAV-50",
            "manufacturer": "Kaveri Seed Company",
            "duration_days": 102,
            "expected_yield_min_q": 24.5,
            "expected_yield_max_q": 28.5,
            "seed_rate_kg_acre": 7.5,
            "price_per_kg": 220.0,
            "disease_resistance": "Medium-High",
            "drought_tolerance": "Medium",
            "soil_affinity": "Sandy Loam to Clay Loam",
            "suitability_pct": 89,
            "certified": True,
            "key_features": "Early maturity, uniform orange-yellow flint grains"
        },
        {
            "crop_name": "Maize",
            "name": "CP 333 Bold Kernel",
            "variety_code": "CP-333",
            "manufacturer": "Charoen Pokphand Seeds",
            "duration_days": 112,
            "expected_yield_min_q": 26.0,
            "expected_yield_max_q": 30.5,
            "seed_rate_kg_acre": 8.0,
            "price_per_kg": 245.0,
            "disease_resistance": "High (Stalk Rot resistant)",
            "drought_tolerance": "High",
            "soil_affinity": "Loamy soil with pH 6.0 - 7.5",
            "suitability_pct": 91,
            "certified": True,
            "key_features": "Dense starch content preferred by processing mills"
        },
        # Soybean Seeds
        {
            "crop_name": "Soybean",
            "name": "JS 335 Certified",
            "variety_code": "JS-335",
            "manufacturer": "Jawaharlal Nehru Krishi Vishwavidyalaya",
            "duration_days": 98,
            "expected_yield_min_q": 11.0,
            "expected_yield_max_q": 13.5,
            "seed_rate_kg_acre": 25.0,
            "price_per_kg": 85.0,
            "disease_resistance": "High (Yellow Mosaic Virus tolerant)",
            "drought_tolerance": "Medium",
            "soil_affinity": "Deep fertile black & alluvial soils",
            "suitability_pct": 88,
            "certified": True,
            "key_features": "High oil content (21%), non-shattering pods"
        },
        # Wheat Seeds
        {
            "crop_name": "Wheat",
            "name": "PBW 550 High Yield",
            "variety_code": "PBW-550",
            "manufacturer": "Punjab Agricultural University (PAU)",
            "duration_days": 132,
            "expected_yield_min_q": 21.0,
            "expected_yield_max_q": 24.5,
            "seed_rate_kg_acre": 40.0,
            "price_per_kg": 42.0,
            "disease_resistance": "High (Yellow Rust & Karnal Bunt resistant)",
            "drought_tolerance": "Medium",
            "soil_affinity": "Medium to heavy textured alluvial soils",
            "suitability_pct": 92,
            "certified": True,
            "key_features": "Lustrous amber grains, excellent chapati making quality"
        },
        # Basmati Rice Seeds
        {
            "crop_name": "Basmati Rice",
            "name": "Pusa Basmati 1121",
            "variety_code": "PB-1121",
            "manufacturer": "ICAR - IARI New Delhi",
            "duration_days": 128,
            "expected_yield_min_q": 19.0,
            "expected_yield_max_q": 22.0,
            "seed_rate_kg_acre": 6.0,
            "price_per_kg": 110.0,
            "disease_resistance": "Medium (Bacterial blight monitoring needed)",
            "drought_tolerance": "Low",
            "soil_affinity": "Clayey loam with good water retention",
            "suitability_pct": 86,
            "certified": True,
            "key_features": "Extra-long slender grain, world-renowned elongation ratio"
        }
    ]

    for s in seeds_data:
        crop_id = crop_objects[s["crop_name"]].id
        seed = SeedVariety(
            crop_id=crop_id,
            name=s["name"],
            variety_code=s["variety_code"],
            manufacturer=s["manufacturer"],
            duration_days=s["duration_days"],
            expected_yield_min_q=s["expected_yield_min_q"],
            expected_yield_max_q=s["expected_yield_max_q"],
            seed_rate_kg_acre=s["seed_rate_kg_acre"],
            price_per_kg=s["price_per_kg"],
            disease_resistance=s["disease_resistance"],
            drought_tolerance=s["drought_tolerance"],
            soil_affinity=s["soil_affinity"],
            suitability_pct=s["suitability_pct"],
            certified=s["certified"],
            key_features=s["key_features"]
        )
        db.add(seed)
    db.commit()

    # 8. Fertilizer Products
    fertilizers_data = [
        {
            "name": "Neem Coated Urea",
            "category": "Nitrogenous",
            "nutrient_composition": "N: 46%, P: 0%, K: 0%",
            "n_pct": 46.0, "p_pct": 0.0, "k_pct": 0.0,
            "pack_size_kg": 45.0,
            "mrp_inr": 266.5,
            "subsidy_eligible": True,
            "application_stage": "Basal & 2 Split Top Dressings",
            "safety_guideline": "Apply when soil has adequate moisture. Do not broadcast immediately before heavy rains."
        },
        {
            "name": "DAP (Di-Ammonium Phosphate 18:46:0)",
            "category": "Phosphatic",
            "nutrient_composition": "N: 18%, P: 46%, K: 0%",
            "n_pct": 18.0, "p_pct": 46.0, "k_pct": 0.0,
            "pack_size_kg": 50.0,
            "mrp_inr": 1350.0,
            "subsidy_eligible": True,
            "application_stage": "Basal Root Zone Placement at Sowing",
            "safety_guideline": "Place 3-5 cm below and to the side of seed furrow to avoid seedling burn."
        },
        {
            "name": "MOP (Muriate of Potash 0:0:60)",
            "category": "Potassic",
            "nutrient_composition": "N: 0%, P: 0%, K: 60%",
            "n_pct": 0.0, "p_pct": 0.0, "k_pct": 60.0,
            "pack_size_kg": 50.0,
            "mrp_inr": 1650.0,
            "subsidy_eligible": True,
            "application_stage": "Basal Application",
            "safety_guideline": "Improves drought tolerance, grain filling and disease resistance."
        },
        {
            "name": "IFFCO NPK Complex 19:19:19",
            "category": "Water Soluble NPK",
            "nutrient_composition": "N: 19%, P: 19%, K: 19%",
            "n_pct": 19.0, "p_pct": 19.0, "k_pct": 19.0,
            "pack_size_kg": 1.0,
            "mrp_inr": 185.0,
            "subsidy_eligible": False,
            "application_stage": "Foliar Spray at Vegetative Stage",
            "safety_guideline": "Spray during cool morning or evening hours. Do not mix with copper fungicides."
        },
        {
            "name": "Zinc Sulfate Heptahydrate (21% Zn)",
            "category": "Micronutrient",
            "nutrient_composition": "Zn: 21%, S: 10%",
            "n_pct": 0.0, "p_pct": 0.0, "k_pct": 0.0,
            "pack_size_kg": 10.0,
            "mrp_inr": 540.0,
            "subsidy_eligible": True,
            "application_stage": "Basal Soil Application",
            "safety_guideline": "Never mix directly with phosphatic fertilizers (DAP/SSP) in the same slurry."
        },
        {
            "name": "Organic Vermicompost Premium",
            "category": "Organic",
            "nutrient_composition": "Organic Carbon: 16%, N: 1.5%, P: 0.8%, K: 0.8%",
            "n_pct": 1.5, "p_pct": 0.8, "k_pct": 0.8,
            "pack_size_kg": 50.0,
            "mrp_inr": 450.0,
            "subsidy_eligible": False,
            "application_stage": "Land Preparation",
            "safety_guideline": "Incorporate thoroughly into top 15 cm soil layer 7 days before sowing."
        }
    ]

    for f in fertilizers_data:
        fert = FertilizerProduct(**f)
        db.add(fert)
    db.commit()

    # 9. Input Dealers
    dealers_data = [
        {
            "business_name": "Kisan Seva Kendra Sahnewal",
            "owner_name": "Rajinder Kumar Gupta",
            "phone": "+91 98141 23456",
            "address": "Shop 14, Main Mandi Road, Sahnewal",
            "city": "Ludhiana",
            "state": "Punjab",
            "latitude": 30.9045,
            "longitude": 75.8620,
            "rating": 4.9,
            "delivery_available": True,
            "products_json": json.dumps([
                {"name": "Pioneer P3396 Hybrid (4kg bag)", "price": 1040, "stock": "45 bags in stock", "category": "Seed"},
                {"name": "Neem Coated Urea (45kg)", "price": 266.5, "stock": "220 bags in stock", "category": "Fertilizer"},
                {"name": "DAP 18:46:0 (50kg)", "price": 1350, "stock": "80 bags in stock", "category": "Fertilizer"},
                {"name": "MOP 0:0:60 (50kg)", "price": 1650, "stock": "65 bags in stock", "category": "Fertilizer"},
                {"name": "Zinc Sulfate 21% (10kg)", "price": 520, "stock": "30 bags in stock", "category": "Micronutrient"}
            ])
        },
        {
            "business_name": "Ludhiana Agro Inputs & Seeds",
            "owner_name": "Harpreet Singh Dhillon",
            "phone": "+91 98780 44556",
            "address": "Near Old Grain Market, Gill Road",
            "city": "Ludhiana",
            "state": "Punjab",
            "latitude": 30.8910,
            "longitude": 75.8450,
            "rating": 4.7,
            "delivery_available": True,
            "products_json": json.dumps([
                {"name": "Kaveri 50 Super Hybrid (4kg bag)", "price": 880, "stock": "60 bags in stock", "category": "Seed"},
                {"name": "Neem Coated Urea (45kg)", "price": 266.5, "stock": "150 bags in stock", "category": "Fertilizer"},
                {"name": "DAP 18:46:0 (50kg)", "price": 1350, "stock": "110 bags in stock", "category": "Fertilizer"},
                {"name": "IFFCO NPK 19:19:19 (1kg)", "price": 180, "stock": "100 packs in stock", "category": "Foliar Fertilizer"}
            ])
        },
        {
            "business_name": "Khanna Farmers Agro Hub",
            "owner_name": "Manmohan Joshi",
            "phone": "+91 98150 99887",
            "address": "Asia's Largest Grain Market Compound",
            "city": "Khanna",
            "state": "Punjab",
            "latitude": 30.7050,
            "longitude": 76.2180,
            "rating": 4.8,
            "delivery_available": True,
            "products_json": json.dumps([
                {"name": "CP 333 Bold Kernel (4kg bag)", "price": 980, "stock": "50 bags in stock", "category": "Seed"},
                {"name": "Neem Coated Urea (45kg)", "price": 266.5, "stock": "350 bags in stock", "category": "Fertilizer"},
                {"name": "DAP 18:46:0 (50kg)", "price": 1350, "stock": "140 bags in stock", "category": "Fertilizer"},
                {"name": "Organic Vermicompost (50kg)", "price": 420, "stock": "120 bags in stock", "category": "Organic"}
            ])
        }
    ]

    for d in dealers_data:
        dealer = Dealer(**d)
        db.add(dealer)
    db.commit()

    # 10. Market Prices (Mandi Intelligence)
    market_data = [
        {
                "crop_name": "Maize",
                "mandi_name": "Khanna Grain Mandi (Asia's Largest)",
                "state": "Punjab",
                "modal_price_q": 2360.0,
                "min_price_q": 2200.0,
                "max_price_q": 2480.0,
                "daily_arrivals_tonnes": 480.0,
                "price_change_pct": 3.2,
                "demand_level": "Very High"
        },
        {
                "crop_name": "Maize",
                "mandi_name": "Ludhiana New Grain Market",
                "state": "Punjab",
                "modal_price_q": 2340.0,
                "min_price_q": 2180.0,
                "max_price_q": 2450.0,
                "daily_arrivals_tonnes": 310.0,
                "price_change_pct": 2.6,
                "demand_level": "High"
        },
        {
                "crop_name": "Maize",
                "mandi_name": "Karnal Mandi Complex",
                "state": "Haryana",
                "modal_price_q": 2380.0,
                "min_price_q": 2250.0,
                "max_price_q": 2510.0,
                "daily_arrivals_tonnes": 520.0,
                "price_change_pct": 4.1,
                "demand_level": "Very High"
        },
        {
                "crop_name": "Maize",
                "mandi_name": "Indore APMC Market",
                "state": "Madhya Pradesh",
                "modal_price_q": 2150.0,
                "min_price_q": 2050.0,
                "max_price_q": 2240.0,
                "daily_arrivals_tonnes": 850.0,
                "price_change_pct": -1.5,
                "demand_level": "Surplus Steady"
        },
        {
                "crop_name": "Maize",
                "mandi_name": "Davangere APMC Yard",
                "state": "Karnataka",
                "modal_price_q": 2180.0,
                "min_price_q": 2050.0,
                "max_price_q": 2290.0,
                "daily_arrivals_tonnes": 950.0,
                "price_change_pct": -1.8,
                "demand_level": "Surplus High"
        },
        {
                "crop_name": "Wheat",
                "mandi_name": "Khanna Grain Mandi",
                "state": "Punjab",
                "modal_price_q": 2440.0,
                "min_price_q": 2360.0,
                "max_price_q": 2520.0,
                "daily_arrivals_tonnes": 720.0,
                "price_change_pct": 1.2,
                "demand_level": "High"
        },
        {
                "crop_name": "Wheat",
                "mandi_name": "Ludhiana New Grain Market",
                "state": "Punjab",
                "modal_price_q": 2425.0,
                "min_price_q": 2350.0,
                "max_price_q": 2500.0,
                "daily_arrivals_tonnes": 650.0,
                "price_change_pct": 0.8,
                "demand_level": "Stable High"
        },
        {
                "crop_name": "Wheat",
                "mandi_name": "Karnal Mandi Complex",
                "state": "Haryana",
                "modal_price_q": 2450.0,
                "min_price_q": 2380.0,
                "max_price_q": 2530.0,
                "daily_arrivals_tonnes": 680.0,
                "price_change_pct": 1.4,
                "demand_level": "High"
        },
        {
                "crop_name": "Wheat",
                "mandi_name": "Kota APMC Yard",
                "state": "Rajasthan",
                "modal_price_q": 2410.0,
                "min_price_q": 2340.0,
                "max_price_q": 2480.0,
                "daily_arrivals_tonnes": 540.0,
                "price_change_pct": 0.5,
                "demand_level": "Moderate"
        },
        {
                "crop_name": "Wheat",
                "mandi_name": "Najafgarh Mandi",
                "state": "Delhi",
                "modal_price_q": 2470.0,
                "min_price_q": 2390.0,
                "max_price_q": 2550.0,
                "daily_arrivals_tonnes": 490.0,
                "price_change_pct": 1.8,
                "demand_level": "High"
        },
        {
                "crop_name": "Wheat",
                "mandi_name": "Coimbatore Flour Mill Cluster",
                "state": "Tamil Nadu",
                "modal_price_q": 2850.0,
                "min_price_q": 2750.0,
                "max_price_q": 2980.0,
                "daily_arrivals_tonnes": 180.0,
                "price_change_pct": 5.1,
                "demand_level": "Extreme Deficit"
        },
        {
                "crop_name": "Soybean",
                "mandi_name": "Indore Mandi (Crushing Capital)",
                "state": "Madhya Pradesh",
                "modal_price_q": 4720.0,
                "min_price_q": 4500.0,
                "max_price_q": 4900.0,
                "daily_arrivals_tonnes": 850.0,
                "price_change_pct": 1.8,
                "demand_level": "High"
        },
        {
                "crop_name": "Soybean",
                "mandi_name": "Latur APMC Market",
                "state": "Maharashtra",
                "modal_price_q": 4780.0,
                "min_price_q": 4550.0,
                "max_price_q": 4950.0,
                "daily_arrivals_tonnes": 780.0,
                "price_change_pct": 2.4,
                "demand_level": "Very High"
        },
        {
                "crop_name": "Soybean",
                "mandi_name": "Ujjain Grain Market",
                "state": "Madhya Pradesh",
                "modal_price_q": 4680.0,
                "min_price_q": 4450.0,
                "max_price_q": 4850.0,
                "daily_arrivals_tonnes": 620.0,
                "price_change_pct": 1.5,
                "demand_level": "High"
        },
        {
                "crop_name": "Soybean",
                "mandi_name": "Akola Oilseed Yard",
                "state": "Maharashtra",
                "modal_price_q": 4710.0,
                "min_price_q": 4480.0,
                "max_price_q": 4890.0,
                "daily_arrivals_tonnes": 450.0,
                "price_change_pct": 1.6,
                "demand_level": "High"
        },
        {
                "crop_name": "Soybean",
                "mandi_name": "Kota Mandi",
                "state": "Rajasthan",
                "modal_price_q": 4620.0,
                "min_price_q": 4400.0,
                "max_price_q": 4790.0,
                "daily_arrivals_tonnes": 390.0,
                "price_change_pct": 0.9,
                "demand_level": "Steady"
        },
        {
                "crop_name": "Basmati Rice",
                "mandi_name": "Amritsar Grain Mandi (Export Hub)",
                "state": "Punjab",
                "modal_price_q": 3890.0,
                "min_price_q": 3600.0,
                "max_price_q": 4150.0,
                "daily_arrivals_tonnes": 410.0,
                "price_change_pct": 2.1,
                "demand_level": "High"
        },
        {
                "crop_name": "Basmati Rice",
                "mandi_name": "Taraori Rice Mandi",
                "state": "Haryana",
                "modal_price_q": 3920.0,
                "min_price_q": 3650.0,
                "max_price_q": 4200.0,
                "daily_arrivals_tonnes": 480.0,
                "price_change_pct": 2.5,
                "demand_level": "Very High"
        },
        {
                "crop_name": "Basmati Rice",
                "mandi_name": "Karnal Basmati Exchange",
                "state": "Haryana",
                "modal_price_q": 3880.0,
                "min_price_q": 3620.0,
                "max_price_q": 4160.0,
                "daily_arrivals_tonnes": 510.0,
                "price_change_pct": 2.0,
                "demand_level": "High"
        },
        {
                "crop_name": "Basmati Rice",
                "mandi_name": "Kotkapura Mandi",
                "state": "Punjab",
                "modal_price_q": 3840.0,
                "min_price_q": 3550.0,
                "max_price_q": 4080.0,
                "daily_arrivals_tonnes": 290.0,
                "price_change_pct": 1.6,
                "demand_level": "Steady"
        },
        {
                "crop_name": "Mustard",
                "mandi_name": "Bharatpur APMC (Mustard Capital)",
                "state": "Rajasthan",
                "modal_price_q": 5450.0,
                "min_price_q": 5200.0,
                "max_price_q": 5650.0,
                "daily_arrivals_tonnes": 540.0,
                "price_change_pct": 2.4,
                "demand_level": "Very High"
        },
        {
                "crop_name": "Mustard",
                "mandi_name": "Alwar Mandi",
                "state": "Rajasthan",
                "modal_price_q": 5420.0,
                "min_price_q": 5180.0,
                "max_price_q": 5600.0,
                "daily_arrivals_tonnes": 480.0,
                "price_change_pct": 2.1,
                "demand_level": "High"
        },
        {
                "crop_name": "Mustard",
                "mandi_name": "Bathinda Grain Market",
                "state": "Punjab",
                "modal_price_q": 5380.0,
                "min_price_q": 5150.0,
                "max_price_q": 5550.0,
                "daily_arrivals_tonnes": 260.0,
                "price_change_pct": 1.7,
                "demand_level": "High"
        },
        {
                "crop_name": "Mustard",
                "mandi_name": "Sirsa Grain Mandi",
                "state": "Haryana",
                "modal_price_q": 5410.0,
                "min_price_q": 5190.0,
                "max_price_q": 5580.0,
                "daily_arrivals_tonnes": 390.0,
                "price_change_pct": 2.0,
                "demand_level": "High"
        },
        {
                "crop_name": "Cotton",
                "mandi_name": "Abohar Cotton Yard (White Gold Hub)",
                "state": "Punjab",
                "modal_price_q": 7020.0,
                "min_price_q": 6700.0,
                "max_price_q": 7380.0,
                "daily_arrivals_tonnes": 420.0,
                "price_change_pct": 1.8,
                "demand_level": "Very High"
        },
        {
                "crop_name": "Cotton",
                "mandi_name": "Mansa Mandi",
                "state": "Punjab",
                "modal_price_q": 6950.0,
                "min_price_q": 6600.0,
                "max_price_q": 7300.0,
                "daily_arrivals_tonnes": 380.0,
                "price_change_pct": 1.5,
                "demand_level": "High"
        },
        {
                "crop_name": "Cotton",
                "mandi_name": "Rajkot APMC Commercial Yard",
                "state": "Gujarat",
                "modal_price_q": 7150.0,
                "min_price_q": 6800.0,
                "max_price_q": 7450.0,
                "daily_arrivals_tonnes": 680.0,
                "price_change_pct": 2.2,
                "demand_level": "Very High"
        },
        {
                "crop_name": "Cotton",
                "mandi_name": "Sirsa Mandi",
                "state": "Haryana",
                "modal_price_q": 6910.0,
                "min_price_q": 6580.0,
                "max_price_q": 7250.0,
                "daily_arrivals_tonnes": 360.0,
                "price_change_pct": 1.3,
                "demand_level": "High"
        },
        {
                "crop_name": "Tomato",
                "mandi_name": "Delhi Azadpur Mandi",
                "state": "Delhi",
                "modal_price_q": 1950.0,
                "min_price_q": 1500.0,
                "max_price_q": 2300.0,
                "daily_arrivals_tonnes": 920.0,
                "price_change_pct": 8.5,
                "demand_level": "Very High"
        },
        {
                "crop_name": "Tomato",
                "mandi_name": "Ludhiana Sabzi Mandi",
                "state": "Punjab",
                "modal_price_q": 2100.0,
                "min_price_q": 1650.0,
                "max_price_q": 2450.0,
                "daily_arrivals_tonnes": 280.0,
                "price_change_pct": 9.2,
                "demand_level": "Extreme"
        },
        {
                "crop_name": "Tomato",
                "mandi_name": "Nashik Pimpalgaon APMC",
                "state": "Maharashtra",
                "modal_price_q": 1650.0,
                "min_price_q": 1300.0,
                "max_price_q": 1950.0,
                "daily_arrivals_tonnes": 1200.0,
                "price_change_pct": -3.5,
                "demand_level": "Surplus"
        },
        {
                "crop_name": "Tomato",
                "mandi_name": "Kalka Vegetable Market",
                "state": "Haryana",
                "modal_price_q": 1880.0,
                "min_price_q": 1450.0,
                "max_price_q": 2200.0,
                "daily_arrivals_tonnes": 340.0,
                "price_change_pct": 7.1,
                "demand_level": "High"
        }
]
    for m in market_data:
        db.add(MarketPrice(**m))
    db.commit()

    # 11. National Crop Shortages (For Interactive India Map)
    shortage_data = [
        {
                "crop_name": "Maize",
                "state_code": "PB",
                "state_name": "Punjab",
                "status": "High Shortage",
                "demand_tonnes": 55000.0,
                "supply_tonnes": 32000.0,
                "deficit_tonnes": 23000.0,
                "deficit_pct": 41.8,
                "current_avg_price_q": 2360.0,
                "price_trend": "Bullish (+4.2%)",
                "major_markets": "Khanna, Ludhiana, Jalandhar",
                "buyer_demand_summary": "Distilleries and starch mills running at 75% capacity due to grain deficit."
        },
        {
                "crop_name": "Maize",
                "state_code": "HR",
                "state_name": "Haryana",
                "status": "High Shortage",
                "demand_tonnes": 48000.0,
                "supply_tonnes": 30000.0,
                "deficit_tonnes": 18000.0,
                "deficit_pct": 37.5,
                "current_avg_price_q": 2380.0,
                "price_trend": "Bullish (+3.8%)",
                "major_markets": "Karnal, Ambala, Kaithal",
                "buyer_demand_summary": "Poultry feed clusters in Karnal offering premium spot cash for dry grain."
        },
        {
                "crop_name": "Maize",
                "state_code": "DL",
                "state_name": "Delhi",
                "status": "High Shortage",
                "demand_tonnes": 25000.0,
                "supply_tonnes": 2000.0,
                "deficit_tonnes": 23000.0,
                "deficit_pct": 92.0,
                "current_avg_price_q": 2440.0,
                "price_trend": "Bullish (+3.5%)",
                "major_markets": "Narela, Najafgarh",
                "buyer_demand_summary": "Urban milling & animal feed depots sourcing directly from neighboring states."
        },
        {
                "crop_name": "Maize",
                "state_code": "RJ",
                "state_name": "Rajasthan",
                "status": "Medium Shortage",
                "demand_tonnes": 62000.0,
                "supply_tonnes": 49000.0,
                "deficit_tonnes": 13000.0,
                "deficit_pct": 21.0,
                "current_avg_price_q": 2300.0,
                "price_trend": "Firm (+2.1%)",
                "major_markets": "Udaipur, Bhilwara, Jaipur",
                "buyer_demand_summary": "Cattle feed manufacturing plants operating with low buffer inventory."
        },
        {
                "crop_name": "Maize",
                "state_code": "UP",
                "state_name": "Uttar Pradesh",
                "status": "Balanced",
                "demand_tonnes": 62000.0,
                "supply_tonnes": 60000.0,
                "deficit_tonnes": 2000.0,
                "deficit_pct": 3.2,
                "current_avg_price_q": 2240.0,
                "price_trend": "Flat (0.0%)",
                "major_markets": "Kanpur, Bulandshahr, Bareilly",
                "buyer_demand_summary": "Local mill consumption balanced with arrivals."
        },
        {
                "crop_name": "Maize",
                "state_code": "GJ",
                "state_name": "Gujarat",
                "status": "Medium Shortage",
                "demand_tonnes": 58000.0,
                "supply_tonnes": 44000.0,
                "deficit_tonnes": 14000.0,
                "deficit_pct": 24.1,
                "current_avg_price_q": 2340.0,
                "price_trend": "Steady (+1.8%)",
                "major_markets": "Anand, Vadodara, Godhra",
                "buyer_demand_summary": "Dairy cooperative feed plants sourcing out-of-state yellow corn."
        },
        {
                "crop_name": "Maize",
                "state_code": "MP",
                "state_name": "Madhya Pradesh",
                "status": "Surplus",
                "demand_tonnes": 50000.0,
                "supply_tonnes": 72000.0,
                "deficit_tonnes": -22000.0,
                "deficit_pct": -44.0,
                "current_avg_price_q": 2150.0,
                "price_trend": "Softening (-2.1%)",
                "major_markets": "Chhindwara, Betul, Dhar",
                "buyer_demand_summary": "Hub for rail transport of corn to north Indian feed mills."
        },
        {
                "crop_name": "Maize",
                "state_code": "MH",
                "state_name": "Maharashtra",
                "status": "Medium Shortage",
                "demand_tonnes": 85000.0,
                "supply_tonnes": 68000.0,
                "deficit_tonnes": 17000.0,
                "deficit_pct": 20.0,
                "current_avg_price_q": 2310.0,
                "price_trend": "Stable (+1.2%)",
                "major_markets": "Aurangabad, Jalna, Sangli",
                "buyer_demand_summary": "Poultry and animal feed mills in western Maharashtra with active inquiries."
        },
        {
                "crop_name": "Maize",
                "state_code": "KA",
                "state_name": "Karnataka",
                "status": "Surplus",
                "demand_tonnes": 90000.0,
                "supply_tonnes": 115000.0,
                "deficit_tonnes": -25000.0,
                "deficit_pct": -27.8,
                "current_avg_price_q": 2180.0,
                "price_trend": "Softening (-1.5%)",
                "major_markets": "Davangere, Ranebennur, Shimoga",
                "buyer_demand_summary": "Heavy harvest arrivals pushing grain outward to northern deficit states."
        },
        {
                "crop_name": "Maize",
                "state_code": "AP",
                "state_name": "Andhra Pradesh",
                "status": "Balanced",
                "demand_tonnes": 52000.0,
                "supply_tonnes": 50000.0,
                "deficit_tonnes": 2000.0,
                "deficit_pct": 3.8,
                "current_avg_price_q": 2260.0,
                "price_trend": "Steady (+0.6%)",
                "major_markets": "Guntur, Kurnool, Vijayawada",
                "buyer_demand_summary": "Aquafeed & poultry sector demand meeting local coastal production."
        },
        {
                "crop_name": "Maize",
                "state_code": "TN",
                "state_name": "Tamil Nadu",
                "status": "High Shortage",
                "demand_tonnes": 68000.0,
                "supply_tonnes": 34000.0,
                "deficit_tonnes": 34000.0,
                "deficit_pct": 50.0,
                "current_avg_price_q": 2480.0,
                "price_trend": "Bullish (+4.6%)",
                "major_markets": "Namakkal, Erode, Coimbatore",
                "buyer_demand_summary": "Namakkal poultry belt running severe deficits; high truck freight absorption."
        },
        {
                "crop_name": "Maize",
                "state_code": "WB",
                "state_name": "West Bengal",
                "status": "Medium Shortage",
                "demand_tonnes": 45000.0,
                "supply_tonnes": 32000.0,
                "deficit_tonnes": 13000.0,
                "deficit_pct": 28.9,
                "current_avg_price_q": 2390.0,
                "price_trend": "Firm (+2.5%)",
                "major_markets": "Siliguri, Malda, Burdwan",
                "buyer_demand_summary": "East Indian poultry feed industry reliant on Bihar & Punjab dispatch rakes."
        },
        {
                "crop_name": "Maize",
                "state_code": "BR",
                "state_name": "Bihar",
                "status": "Surplus",
                "demand_tonnes": 42000.0,
                "supply_tonnes": 68000.0,
                "deficit_tonnes": -26000.0,
                "deficit_pct": -61.9,
                "current_avg_price_q": 2120.0,
                "price_trend": "Softening (-2.8%)",
                "major_markets": "Gulabbagh, Purnea, Begusarai",
                "buyer_demand_summary": "Peak Rabi maize export hub with massive wholesale rakes moving nationwide."
        },
        {
                "crop_name": "Maize",
                "state_code": "TS",
                "state_name": "Telangana",
                "status": "Medium Shortage",
                "demand_tonnes": 56000.0,
                "supply_tonnes": 45000.0,
                "deficit_tonnes": 11000.0,
                "deficit_pct": 19.6,
                "current_avg_price_q": 2290.0,
                "price_trend": "Steady (+1.4%)",
                "major_markets": "Warangal, Karimnagar, Nizamabad",
                "buyer_demand_summary": "Broiler feed producers requiring consistent moisture-checked supply."
        },
        {
                "crop_name": "Maize",
                "state_code": "OR",
                "state_name": "Odisha",
                "status": "Balanced",
                "demand_tonnes": 32000.0,
                "supply_tonnes": 30000.0,
                "deficit_tonnes": 2000.0,
                "deficit_pct": 6.2,
                "current_avg_price_q": 2230.0,
                "price_trend": "Flat (+0.2%)",
                "major_markets": "Nabarangpur, Cuttack, Sambalpur",
                "buyer_demand_summary": "Regional animal feed consumption matched by tribal belt cultivation."
        },
        {
                "crop_name": "Wheat",
                "state_code": "PB",
                "state_name": "Punjab",
                "status": "Surplus",
                "demand_tonnes": 75000.0,
                "supply_tonnes": 160000.0,
                "deficit_tonnes": -85000.0,
                "deficit_pct": -113.3,
                "current_avg_price_q": 2425.0,
                "price_trend": "Steady (+0.5%)",
                "major_markets": "Khanna, Rajpura, Moga",
                "buyer_demand_summary": "Central pool procurement buffer state; steady private miller interest."
        },
        {
                "crop_name": "Wheat",
                "state_code": "HR",
                "state_name": "Haryana",
                "status": "Surplus",
                "demand_tonnes": 65000.0,
                "supply_tonnes": 135000.0,
                "deficit_tonnes": -70000.0,
                "deficit_pct": -107.7,
                "current_avg_price_q": 2450.0,
                "price_trend": "Firm (+1.1%)",
                "major_markets": "Karnal, Sirsa, Kurukshetra",
                "buyer_demand_summary": "Heavy grain surplus; institutional millers loading rakes for western/southern depots."
        },
        {
                "crop_name": "Wheat",
                "state_code": "DL",
                "state_name": "Delhi",
                "status": "High Shortage",
                "demand_tonnes": 45000.0,
                "supply_tonnes": 6000.0,
                "deficit_tonnes": 39000.0,
                "deficit_pct": 86.7,
                "current_avg_price_q": 2470.0,
                "price_trend": "Firm (+1.8%)",
                "major_markets": "Najafgarh, Narela",
                "buyer_demand_summary": "High consumer & bakery demand requiring round-the-clock supply from Punjab."
        },
        {
                "crop_name": "Wheat",
                "state_code": "RJ",
                "state_name": "Rajasthan",
                "status": "Balanced",
                "demand_tonnes": 82000.0,
                "supply_tonnes": 85000.0,
                "deficit_tonnes": -3000.0,
                "deficit_pct": -3.7,
                "current_avg_price_q": 2410.0,
                "price_trend": "Steady (+0.4%)",
                "major_markets": "Kota, Sri Ganganagar, Hanumangarh",
                "buyer_demand_summary": "State consumption balanced; strong durum wheat premium in Hadoti region."
        },
        {
                "crop_name": "Wheat",
                "state_code": "UP",
                "state_name": "Uttar Pradesh",
                "status": "Surplus",
                "demand_tonnes": 140000.0,
                "supply_tonnes": 195000.0,
                "deficit_tonnes": -55000.0,
                "deficit_pct": -39.3,
                "current_avg_price_q": 2390.0,
                "price_trend": "Stable (+0.3%)",
                "major_markets": "Aligarh, Shahjahanpur, Bareilly",
                "buyer_demand_summary": "Largest production volume nationwide; abundant stock in western districts."
        },
        {
                "crop_name": "Wheat",
                "state_code": "GJ",
                "state_name": "Gujarat",
                "status": "Medium Shortage",
                "demand_tonnes": 72000.0,
                "supply_tonnes": 54000.0,
                "deficit_tonnes": 18000.0,
                "deficit_pct": 25.0,
                "current_avg_price_q": 2520.0,
                "price_trend": "Bullish (+2.2%)",
                "major_markets": "Rajkot, Ahmedabad, Gondal",
                "buyer_demand_summary": "High demand for Sharbati premium variety from industrial packaged atta brands."
        },
        {
                "crop_name": "Wheat",
                "state_code": "MP",
                "state_name": "Madhya Pradesh",
                "status": "Surplus",
                "demand_tonnes": 85000.0,
                "supply_tonnes": 145000.0,
                "deficit_tonnes": -60000.0,
                "deficit_pct": -70.6,
                "current_avg_price_q": 2400.0,
                "price_trend": "Steady (+0.7%)",
                "major_markets": "Sehore, Vidisha, Ujjain",
                "buyer_demand_summary": "Sharbati & Lok-1 wheat surplus dispatching to southern consumption hubs."
        },
        {
                "crop_name": "Wheat",
                "state_code": "MH",
                "state_name": "Maharashtra",
                "status": "High Shortage",
                "demand_tonnes": 110000.0,
                "supply_tonnes": 65000.0,
                "deficit_tonnes": 45000.0,
                "deficit_pct": 40.9,
                "current_avg_price_q": 2620.0,
                "price_trend": "Bullish (+3.4%)",
                "major_markets": "Pune, Mumbai, Nagpur",
                "buyer_demand_summary": "Extensive bakery and biscuit industrial deficit; importing rail rakes daily."
        },
        {
                "crop_name": "Wheat",
                "state_code": "KA",
                "state_name": "Karnataka",
                "status": "High Shortage",
                "demand_tonnes": 75000.0,
                "supply_tonnes": 22000.0,
                "deficit_tonnes": 53000.0,
                "deficit_pct": 70.7,
                "current_avg_price_q": 2740.0,
                "price_trend": "Bullish (+4.2%)",
                "major_markets": "Bengaluru, Belagavi, Hubballi",
                "buyer_demand_summary": "Roller flour mills operating on low stock; paying cash premiums for Punjab wheat."
        },
        {
                "crop_name": "Wheat",
                "state_code": "AP",
                "state_name": "Andhra Pradesh",
                "status": "High Shortage",
                "demand_tonnes": 58000.0,
                "supply_tonnes": 12000.0,
                "deficit_tonnes": 46000.0,
                "deficit_pct": 79.3,
                "current_avg_price_q": 2760.0,
                "price_trend": "Bullish (+4.0%)",
                "major_markets": "Guntur, Visakhapatnam",
                "buyer_demand_summary": "Southern non-wheat agrarian agrozone dependent on northern central rakes."
        },
        {
                "crop_name": "Wheat",
                "state_code": "TN",
                "state_name": "Tamil Nadu",
                "status": "High Shortage",
                "demand_tonnes": 65000.0,
                "supply_tonnes": 4000.0,
                "deficit_tonnes": 61000.0,
                "deficit_pct": 93.8,
                "current_avg_price_q": 2850.0,
                "price_trend": "Bullish (+5.1%)",
                "major_markets": "Coimbatore, Chennai, Madurai",
                "buyer_demand_summary": "South Indian roller flour mills relying heavily on northern rail rakes."
        },
        {
                "crop_name": "Wheat",
                "state_code": "WB",
                "state_name": "West Bengal",
                "status": "High Shortage",
                "demand_tonnes": 80000.0,
                "supply_tonnes": 35000.0,
                "deficit_tonnes": 45000.0,
                "deficit_pct": 56.2,
                "current_avg_price_q": 2580.0,
                "price_trend": "Firm (+2.8%)",
                "major_markets": "Kolkata, Siliguri, Burdwan",
                "buyer_demand_summary": "Maida and suji processing mills bidding for UP and Punjab grain dispatches."
        },
        {
                "crop_name": "Wheat",
                "state_code": "BR",
                "state_name": "Bihar",
                "status": "Medium Shortage",
                "demand_tonnes": 70000.0,
                "supply_tonnes": 58000.0,
                "deficit_tonnes": 12000.0,
                "deficit_pct": 17.1,
                "current_avg_price_q": 2460.0,
                "price_trend": "Steady (+1.2%)",
                "major_markets": "Patna, Muzaffarpur, Gaya",
                "buyer_demand_summary": "Moderate supply deficit in urban consumption clusters."
        },
        {
                "crop_name": "Wheat",
                "state_code": "TS",
                "state_name": "Telangana",
                "status": "High Shortage",
                "demand_tonnes": 62000.0,
                "supply_tonnes": 15000.0,
                "deficit_tonnes": 47000.0,
                "deficit_pct": 75.8,
                "current_avg_price_q": 2720.0,
                "price_trend": "Bullish (+3.9%)",
                "major_markets": "Hyderabad, Warangal",
                "buyer_demand_summary": "Hyderabad packaged food enterprises actively seeking interstate supply agreements."
        },
        {
                "crop_name": "Wheat",
                "state_code": "OR",
                "state_name": "Odisha",
                "status": "Medium Shortage",
                "demand_tonnes": 42000.0,
                "supply_tonnes": 18000.0,
                "deficit_tonnes": 24000.0,
                "deficit_pct": 57.1,
                "current_avg_price_q": 2610.0,
                "price_trend": "Firm (+2.4%)",
                "major_markets": "Bhubaneswar, Cuttack",
                "buyer_demand_summary": "Flour processing sector absorbing freight cost from MP & UP."
        },
        {
                "crop_name": "Soybean",
                "state_code": "PB",
                "state_name": "Punjab",
                "status": "Balanced",
                "demand_tonnes": 15000.0,
                "supply_tonnes": 14000.0,
                "deficit_tonnes": 1000.0,
                "deficit_pct": 6.7,
                "current_avg_price_q": 4680.0,
                "price_trend": "Steady (+0.8%)",
                "major_markets": "Ludhiana, Khanna",
                "buyer_demand_summary": "Poultry meal processors sourcing small quantities locally."
        },
        {
                "crop_name": "Soybean",
                "state_code": "HR",
                "state_name": "Haryana",
                "status": "Medium Shortage",
                "demand_tonnes": 22000.0,
                "supply_tonnes": 16000.0,
                "deficit_tonnes": 6000.0,
                "deficit_pct": 27.3,
                "current_avg_price_q": 4700.0,
                "price_trend": "Firm (+1.2%)",
                "major_markets": "Karnal, Ambala",
                "buyer_demand_summary": "High de-oiled cake demand from commercial dairy feed operators."
        },
        {
                "crop_name": "Soybean",
                "state_code": "DL",
                "state_name": "Delhi",
                "status": "Medium Shortage",
                "demand_tonnes": 18000.0,
                "supply_tonnes": 2000.0,
                "deficit_tonnes": 16000.0,
                "deficit_pct": 88.9,
                "current_avg_price_q": 4760.0,
                "price_trend": "Firm (+1.5%)",
                "major_markets": "Narela",
                "buyer_demand_summary": "Packaged soy milk and tofu processors with steady demand."
        },
        {
                "crop_name": "Soybean",
                "state_code": "RJ",
                "state_name": "Rajasthan",
                "status": "Medium Shortage",
                "demand_tonnes": 65000.0,
                "supply_tonnes": 52000.0,
                "deficit_tonnes": 13000.0,
                "deficit_pct": 20.0,
                "current_avg_price_q": 4620.0,
                "price_trend": "Steady (+0.9%)",
                "major_markets": "Kota, Baran, Jhalawar",
                "buyer_demand_summary": "Solvent extraction units operating at high capacity in southeastern region."
        },
        {
                "crop_name": "Soybean",
                "state_code": "UP",
                "state_name": "Uttar Pradesh",
                "status": "Balanced",
                "demand_tonnes": 38000.0,
                "supply_tonnes": 36000.0,
                "deficit_tonnes": 2000.0,
                "deficit_pct": 5.3,
                "current_avg_price_q": 4650.0,
                "price_trend": "Flat (0.0%)",
                "major_markets": "Jhansi, Lalitpur",
                "buyer_demand_summary": "Bundelkhand soybean output fulfilling local extraction requirements."
        },
        {
                "crop_name": "Soybean",
                "state_code": "GJ",
                "state_name": "Gujarat",
                "status": "Medium Shortage",
                "demand_tonnes": 48000.0,
                "supply_tonnes": 35000.0,
                "deficit_tonnes": 13000.0,
                "deficit_pct": 27.1,
                "current_avg_price_q": 4710.0,
                "price_trend": "Firm (+1.7%)",
                "major_markets": "Dahod, Vadodara",
                "buyer_demand_summary": "Crushing plants absorbing nearby Rajasthan & MP crop."
        },
        {
                "crop_name": "Soybean",
                "state_code": "MP",
                "state_name": "Madhya Pradesh",
                "status": "Medium Shortage",
                "demand_tonnes": 140000.0,
                "supply_tonnes": 115000.0,
                "deficit_tonnes": 25000.0,
                "deficit_pct": 17.9,
                "current_avg_price_q": 4720.0,
                "price_trend": "Firm (+1.9%)",
                "major_markets": "Indore, Ujjain, Dewas",
                "buyer_demand_summary": "High capacity crushing plants operating at good margins; intense miller competition."
        },
        {
                "crop_name": "Soybean",
                "state_code": "MH",
                "state_name": "Maharashtra",
                "status": "High Shortage",
                "demand_tonnes": 120000.0,
                "supply_tonnes": 82000.0,
                "deficit_tonnes": 38000.0,
                "deficit_pct": 31.7,
                "current_avg_price_q": 4780.0,
                "price_trend": "Bullish (+3.5%)",
                "major_markets": "Latur, Akola, Nagpur",
                "buyer_demand_summary": "Solvent extractors aggressively bidding up yellow soybean for meal export."
        },
        {
                "crop_name": "Soybean",
                "state_code": "KA",
                "state_name": "Karnataka",
                "status": "Surplus",
                "demand_tonnes": 35000.0,
                "supply_tonnes": 48000.0,
                "deficit_tonnes": -13000.0,
                "deficit_pct": -37.1,
                "current_avg_price_q": 4580.0,
                "price_trend": "Softening (-1.2%)",
                "major_markets": "Belagavi, Bidar",
                "buyer_demand_summary": "Northern Karnataka districts dispatching beans to Maharashtra solvent plants."
        },
        {
                "crop_name": "Soybean",
                "state_code": "AP",
                "state_name": "Andhra Pradesh",
                "status": "Medium Shortage",
                "demand_tonnes": 28000.0,
                "supply_tonnes": 20000.0,
                "deficit_tonnes": 8000.0,
                "deficit_pct": 28.6,
                "current_avg_price_q": 4690.0,
                "price_trend": "Firm (+1.4%)",
                "major_markets": "Adilabad, Kurnool",
                "buyer_demand_summary": "Poultry feed manufacturers securing non-GMO yellow soy contracts."
        },
        {
                "crop_name": "Soybean",
                "state_code": "TN",
                "state_name": "Tamil Nadu",
                "status": "High Shortage",
                "demand_tonnes": 42000.0,
                "supply_tonnes": 8000.0,
                "deficit_tonnes": 34000.0,
                "deficit_pct": 81.0,
                "current_avg_price_q": 4850.0,
                "price_trend": "Bullish (+3.8%)",
                "major_markets": "Coimbatore, Erode",
                "buyer_demand_summary": "Poultry integrator feed mills offering premium spot tariffs for high protein meal."
        },
        {
                "crop_name": "Soybean",
                "state_code": "WB",
                "state_name": "West Bengal",
                "status": "High Shortage",
                "demand_tonnes": 30000.0,
                "supply_tonnes": 5000.0,
                "deficit_tonnes": 25000.0,
                "deficit_pct": 83.3,
                "current_avg_price_q": 4790.0,
                "price_trend": "Firm (+2.2%)",
                "major_markets": "Kolkata, Siliguri",
                "buyer_demand_summary": "Aquafeed industries reliant on MP extraction plants."
        },
        {
                "crop_name": "Soybean",
                "state_code": "BR",
                "state_name": "Bihar",
                "status": "Medium Shortage",
                "demand_tonnes": 24000.0,
                "supply_tonnes": 14000.0,
                "deficit_tonnes": 10000.0,
                "deficit_pct": 41.7,
                "current_avg_price_q": 4710.0,
                "price_trend": "Firm (+1.6%)",
                "major_markets": "Purnea, Patna",
                "buyer_demand_summary": "Emerging feed compounding mills expanding procurement."
        },
        {
                "crop_name": "Soybean",
                "state_code": "TS",
                "state_name": "Telangana",
                "status": "Medium Shortage",
                "demand_tonnes": 40000.0,
                "supply_tonnes": 31000.0,
                "deficit_tonnes": 9000.0,
                "deficit_pct": 22.5,
                "current_avg_price_q": 4680.0,
                "price_trend": "Steady (+1.1%)",
                "major_markets": "Nizamabad, Adilabad",
                "buyer_demand_summary": "Soybean crushing plants bidding consistently in northern districts."
        },
        {
                "crop_name": "Soybean",
                "state_code": "OR",
                "state_name": "Odisha",
                "status": "Balanced",
                "demand_tonnes": 18000.0,
                "supply_tonnes": 17000.0,
                "deficit_tonnes": 1000.0,
                "deficit_pct": 5.6,
                "current_avg_price_q": 4640.0,
                "price_trend": "Flat (+0.3%)",
                "major_markets": "Koraput, Rayagada",
                "buyer_demand_summary": "Modest local demand aligned with production."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "PB",
                "state_name": "Punjab",
                "status": "Surplus",
                "demand_tonnes": 35000.0,
                "supply_tonnes": 95000.0,
                "deficit_tonnes": -60000.0,
                "deficit_pct": -171.4,
                "current_avg_price_q": 3890.0,
                "price_trend": "Firm (+2.1%)",
                "major_markets": "Amritsar, Tarn Taran, Kotkapura",
                "buyer_demand_summary": "Global export capital for Pusa 1121 & 1509; massive processing capacity."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "HR",
                "state_name": "Haryana",
                "status": "Surplus",
                "demand_tonnes": 30000.0,
                "supply_tonnes": 88000.0,
                "deficit_tonnes": -58000.0,
                "deficit_pct": -193.3,
                "current_avg_price_q": 3920.0,
                "price_trend": "Bullish (+2.5%)",
                "major_markets": "Taraori, Karnal, Kaithal",
                "buyer_demand_summary": "Historic Basmati belt with direct Middle-East & European export consignments."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "DL",
                "state_name": "Delhi",
                "status": "High Shortage",
                "demand_tonnes": 40000.0,
                "supply_tonnes": 5000.0,
                "deficit_tonnes": 35000.0,
                "deficit_pct": 87.5,
                "current_avg_price_q": 4120.0,
                "price_trend": "Bullish (+3.1%)",
                "major_markets": "Naya Bazar, Chandni Chowk",
                "buyer_demand_summary": "Premier domestic & export wholesale trading market operating on northern arrivals."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "RJ",
                "state_name": "Rajasthan",
                "status": "Medium Shortage",
                "demand_tonnes": 28000.0,
                "supply_tonnes": 18000.0,
                "deficit_tonnes": 10000.0,
                "deficit_pct": 35.7,
                "current_avg_price_q": 3980.0,
                "price_trend": "Steady (+1.4%)",
                "major_markets": "Kota, Bundi",
                "buyer_demand_summary": "Bundi Sugandh aromatic rice supplementing northern grain purchases."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "UP",
                "state_name": "Uttar Pradesh",
                "status": "Surplus",
                "demand_tonnes": 45000.0,
                "supply_tonnes": 72000.0,
                "deficit_tonnes": -27000.0,
                "deficit_pct": -60.0,
                "current_avg_price_q": 3820.0,
                "price_trend": "Firm (+1.7%)",
                "major_markets": "Bareilly, Pilibhit, Rampur",
                "buyer_demand_summary": "Western Terai region high output moving into Delhi wholesale channels."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "GJ",
                "state_name": "Gujarat",
                "status": "High Shortage",
                "demand_tonnes": 38000.0,
                "supply_tonnes": 12000.0,
                "deficit_tonnes": 26000.0,
                "deficit_pct": 68.4,
                "current_avg_price_q": 4080.0,
                "price_trend": "Bullish (+2.8%)",
                "major_markets": "Ahmedabad, Surat",
                "buyer_demand_summary": "Commercial hospitality & high-income household consumption driving demand."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "MP",
                "state_name": "Madhya Pradesh",
                "status": "Balanced",
                "demand_tonnes": 32000.0,
                "supply_tonnes": 34000.0,
                "deficit_tonnes": -2000.0,
                "deficit_pct": -6.2,
                "current_avg_price_q": 3850.0,
                "price_trend": "Steady (+0.9%)",
                "major_markets": "Raisen, Hoshangabad",
                "buyer_demand_summary": "Narmada basin aromatic paddy supplying central Indian millers."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "MH",
                "state_name": "Maharashtra",
                "status": "High Shortage",
                "demand_tonnes": 62000.0,
                "supply_tonnes": 15000.0,
                "deficit_tonnes": 47000.0,
                "deficit_pct": 75.8,
                "current_avg_price_q": 4150.0,
                "price_trend": "Bullish (+3.2%)",
                "major_markets": "Vashi (Navi Mumbai), Pune",
                "buyer_demand_summary": "Major seaport export hubs and metro retail consumption requiring continuous rakes."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "KA",
                "state_name": "Karnataka",
                "status": "High Shortage",
                "demand_tonnes": 35000.0,
                "supply_tonnes": 8000.0,
                "deficit_tonnes": 27000.0,
                "deficit_pct": 77.1,
                "current_avg_price_q": 4180.0,
                "price_trend": "Bullish (+3.5%)",
                "major_markets": "Bengaluru, Mangaluru",
                "buyer_demand_summary": "Premium dining & supermarket chains absorbing freight from Punjab."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "AP",
                "state_name": "Andhra Pradesh",
                "status": "Balanced",
                "demand_tonnes": 30000.0,
                "supply_tonnes": 28000.0,
                "deficit_tonnes": 2000.0,
                "deficit_pct": 6.7,
                "current_avg_price_q": 3950.0,
                "price_trend": "Steady (+0.8%)",
                "major_markets": "Nellore, Kakinada",
                "buyer_demand_summary": "South Indian non-basmati varieties dominate; Basmati market niche and steady."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "TN",
                "state_name": "Tamil Nadu",
                "status": "High Shortage",
                "demand_tonnes": 32000.0,
                "supply_tonnes": 6000.0,
                "deficit_tonnes": 26000.0,
                "deficit_pct": 81.2,
                "current_avg_price_q": 4220.0,
                "price_trend": "Bullish (+4.0%)",
                "major_markets": "Chennai, Madurai",
                "buyer_demand_summary": "High domestic biryani restaurant demand relying on Punjab rice mills."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "WB",
                "state_name": "West Bengal",
                "status": "Medium Shortage",
                "demand_tonnes": 36000.0,
                "supply_tonnes": 22000.0,
                "deficit_tonnes": 14000.0,
                "deficit_pct": 38.9,
                "current_avg_price_q": 4020.0,
                "price_trend": "Firm (+2.0%)",
                "major_markets": "Kolkata, Burdwan",
                "buyer_demand_summary": "Traditional rice consumer state expanding Basmati consumption."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "BR",
                "state_name": "Bihar",
                "status": "Balanced",
                "demand_tonnes": 25000.0,
                "supply_tonnes": 26000.0,
                "deficit_tonnes": -1000.0,
                "deficit_pct": -4.0,
                "current_avg_price_q": 3870.0,
                "price_trend": "Flat (+0.5%)",
                "major_markets": "Buxar, Rohtas",
                "buyer_demand_summary": "Katarni aromatic rice balanced with local procurement."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "TS",
                "state_name": "Telangana",
                "status": "High Shortage",
                "demand_tonnes": 34000.0,
                "supply_tonnes": 9000.0,
                "deficit_tonnes": 25000.0,
                "deficit_pct": 73.5,
                "current_avg_price_q": 4140.0,
                "price_trend": "Bullish (+3.3%)",
                "major_markets": "Hyderabad, Warangal",
                "buyer_demand_summary": "Famous Hyderabadi Biryani food cluster with year-round high Basmati requirements."
        },
        {
                "crop_name": "Basmati Rice",
                "state_code": "OR",
                "state_name": "Odisha",
                "status": "Balanced",
                "demand_tonnes": 20000.0,
                "supply_tonnes": 18000.0,
                "deficit_tonnes": 2000.0,
                "deficit_pct": 10.0,
                "current_avg_price_q": 3960.0,
                "price_trend": "Steady (+0.7%)",
                "major_markets": "Bhubaneswar, Cuttack",
                "buyer_demand_summary": "Local aromatic paddy fulfilling baseline demand."
        },
        {
                "crop_name": "Mustard",
                "state_code": "PB",
                "state_name": "Punjab",
                "status": "Medium Shortage",
                "demand_tonnes": 32000.0,
                "supply_tonnes": 24000.0,
                "deficit_tonnes": 8000.0,
                "deficit_pct": 25.0,
                "current_avg_price_q": 5380.0,
                "price_trend": "Firm (+1.7%)",
                "major_markets": "Bathinda, Mansa, Sangrur",
                "buyer_demand_summary": "Local expellers running at capacity for Kacchi Ghani mustard oil."
        },
        {
                "crop_name": "Mustard",
                "state_code": "HR",
                "state_name": "Haryana",
                "status": "Surplus",
                "demand_tonnes": 45000.0,
                "supply_tonnes": 68000.0,
                "deficit_tonnes": -23000.0,
                "deficit_pct": -51.1,
                "current_avg_price_q": 5410.0,
                "price_trend": "Firm (+2.0%)",
                "major_markets": "Sirsa, Hisar, Bhiwani",
                "buyer_demand_summary": "High acreage harvest yielding surplus oilseed for interstate oil mills."
        },
        {
                "crop_name": "Mustard",
                "state_code": "DL",
                "state_name": "Delhi",
                "status": "High Shortage",
                "demand_tonnes": 22000.0,
                "supply_tonnes": 1500.0,
                "deficit_tonnes": 20500.0,
                "deficit_pct": 93.2,
                "current_avg_price_q": 5520.0,
                "price_trend": "Bullish (+2.6%)",
                "major_markets": "Narela, Tilak Bazar",
                "buyer_demand_summary": "Heavy packaged edible oil bottling consumption."
        },
        {
                "crop_name": "Mustard",
                "state_code": "RJ",
                "state_name": "Rajasthan",
                "status": "Surplus",
                "demand_tonnes": 95000.0,
                "supply_tonnes": 165000.0,
                "deficit_tonnes": -70000.0,
                "deficit_pct": -73.7,
                "current_avg_price_q": 5450.0,
                "price_trend": "Bullish (+2.4%)",
                "major_markets": "Bharatpur, Alwar, Kota",
                "buyer_demand_summary": "National mustard capital; high-oil-content seed trading actively."
        },
        {
                "crop_name": "Mustard",
                "state_code": "UP",
                "state_name": "Uttar Pradesh",
                "status": "Medium Shortage",
                "demand_tonnes": 80000.0,
                "supply_tonnes": 65000.0,
                "deficit_tonnes": 15000.0,
                "deficit_pct": 18.8,
                "current_avg_price_q": 5390.0,
                "price_trend": "Steady (+1.3%)",
                "major_markets": "Agra, Mathura, Hathras",
                "buyer_demand_summary": "Agra-Mathura crushing corridor with intense daily seed demand."
        },
        {
                "crop_name": "Mustard",
                "state_code": "GJ",
                "state_name": "Gujarat",
                "status": "Medium Shortage",
                "demand_tonnes": 42000.0,
                "supply_tonnes": 32000.0,
                "deficit_tonnes": 10000.0,
                "deficit_pct": 23.8,
                "current_avg_price_q": 5480.0,
                "price_trend": "Firm (+1.9%)",
                "major_markets": "Deesa, Palanpur",
                "buyer_demand_summary": "Kacchi ghani extraction plants sourcing additional northern stock."
        },
        {
                "crop_name": "Mustard",
                "state_code": "MP",
                "state_name": "Madhya Pradesh",
                "status": "Surplus",
                "demand_tonnes": 48000.0,
                "supply_tonnes": 72000.0,
                "deficit_tonnes": -24000.0,
                "deficit_pct": -50.0,
                "current_avg_price_q": 5350.0,
                "price_trend": "Steady (+1.2%)",
                "major_markets": "Morena, Bhind, Gwalior",
                "buyer_demand_summary": "Chambal mustard belt generating high seed surplus."
        },
        {
                "crop_name": "Mustard",
                "state_code": "MH",
                "state_name": "Maharashtra",
                "status": "High Shortage",
                "demand_tonnes": 45000.0,
                "supply_tonnes": 12000.0,
                "deficit_tonnes": 33000.0,
                "deficit_pct": 73.3,
                "current_avg_price_q": 5600.0,
                "price_trend": "Bullish (+3.0%)",
                "major_markets": "Mumbai, Jalgaon",
                "buyer_demand_summary": "Edible oil refineries seeking north Indian mustard supplies."
        },
        {
                "crop_name": "Mustard",
                "state_code": "KA",
                "state_name": "Karnataka",
                "status": "High Shortage",
                "demand_tonnes": 25000.0,
                "supply_tonnes": 5000.0,
                "deficit_tonnes": 20000.0,
                "deficit_pct": 80.0,
                "current_avg_price_q": 5680.0,
                "price_trend": "Bullish (+3.4%)",
                "major_markets": "Bengaluru, Hubballi",
                "buyer_demand_summary": "Industrial culinary demand fulfilled by interstate arrivals."
        },
        {
                "crop_name": "Mustard",
                "state_code": "AP",
                "state_name": "Andhra Pradesh",
                "status": "High Shortage",
                "demand_tonnes": 22000.0,
                "supply_tonnes": 4000.0,
                "deficit_tonnes": 18000.0,
                "deficit_pct": 81.8,
                "current_avg_price_q": 5650.0,
                "price_trend": "Bullish (+3.1%)",
                "major_markets": "Vijayawada, Guntur",
                "buyer_demand_summary": "Specific culinary pickle and seasoning demand."
        },
        {
                "crop_name": "Mustard",
                "state_code": "TN",
                "state_name": "Tamil Nadu",
                "status": "High Shortage",
                "demand_tonnes": 24000.0,
                "supply_tonnes": 3000.0,
                "deficit_tonnes": 21000.0,
                "deficit_pct": 87.5,
                "current_avg_price_q": 5720.0,
                "price_trend": "Bullish (+3.7%)",
                "major_markets": "Chennai, Madurai",
                "buyer_demand_summary": "Retail mustard seed and oil packaging dependent on northern dispatch rakes."
        },
        {
                "crop_name": "Mustard",
                "state_code": "WB",
                "state_name": "West Bengal",
                "status": "High Shortage",
                "demand_tonnes": 75000.0,
                "supply_tonnes": 35000.0,
                "deficit_tonnes": 40000.0,
                "deficit_pct": 53.3,
                "current_avg_price_q": 5580.0,
                "price_trend": "Bullish (+2.9%)",
                "major_markets": "Kolkata, Siliguri, Burdwan",
                "buyer_demand_summary": "Premier state consumer of pungency-rich pure mustard oil; huge deficit."
        },
        {
                "crop_name": "Mustard",
                "state_code": "BR",
                "state_name": "Bihar",
                "status": "Medium Shortage",
                "demand_tonnes": 48000.0,
                "supply_tonnes": 32000.0,
                "deficit_tonnes": 16000.0,
                "deficit_pct": 33.3,
                "current_avg_price_q": 5460.0,
                "price_trend": "Firm (+1.8%)",
                "major_markets": "Patna, Muzaffarpur",
                "buyer_demand_summary": "Rural & urban household demand absorbing local and Rajasthan supply."
        },
        {
                "crop_name": "Mustard",
                "state_code": "TS",
                "state_name": "Telangana",
                "status": "High Shortage",
                "demand_tonnes": 20000.0,
                "supply_tonnes": 4500.0,
                "deficit_tonnes": 15500.0,
                "deficit_pct": 77.5,
                "current_avg_price_q": 5660.0,
                "price_trend": "Bullish (+3.2%)",
                "major_markets": "Hyderabad",
                "buyer_demand_summary": "Spices and edible oils segment sourcing northern raw seed."
        },
        {
                "crop_name": "Mustard",
                "state_code": "OR",
                "state_name": "Odisha",
                "status": "Medium Shortage",
                "demand_tonnes": 26000.0,
                "supply_tonnes": 14000.0,
                "deficit_tonnes": 12000.0,
                "deficit_pct": 46.2,
                "current_avg_price_q": 5540.0,
                "price_trend": "Firm (+2.1%)",
                "major_markets": "Cuttack, Balasore",
                "buyer_demand_summary": "High household mustard cooking preference driving consistent deficit."
        }
]
    for s in shortage_data:
        db.add(CropShortage(**s))
    db.commit()

    # 12. Wholesale Buyers & Demand Tenders
    buyers_data = [
        {
                "company_name": "ABC Agro Foods & Millers",
                "buyer_type": "Food Processor & Miller",
                "contact_person": "Vikram Ahuja (VP Procurement)",
                "phone": "+91 98555 67890",
                "email": "procurement@abcfoods.in",
                "location": "Khanna Industrial Area, Punjab (22 km away)",
                "crop_required": "Maize",
                "quantity_required_tonnes": 500.0,
                "offered_price_q": 2420.0,
                "deadline_date": "2026-10-06",
                "quality_specs": "Moisture < 12%, Foreign Matter < 1.0%, Broken grains < 2%, Aflatoxin compliant",
                "rating": 4.9,
                "verified": true
        },
        {
                "company_name": "Punjab Agro Industries Corp",
                "buyer_type": "State Procurement Agency",
                "contact_person": "Gursharan Singh (District Officer)",
                "phone": "+91 98760 12345",
                "email": "procure@punjabagro.gov.in",
                "location": "Ludhiana Mandi Complex, Punjab (12 km away)",
                "crop_required": "Maize",
                "quantity_required_tonnes": 1200.0,
                "offered_price_q": 2350.0,
                "deadline_date": "2026-10-21",
                "quality_specs": "Fair Average Quality (FAQ) norms, Moisture < 14%",
                "rating": 4.8,
                "verified": true
        },
        {
                "company_name": "Karnal Premium Poultry Feed Mills",
                "buyer_type": "Feed Manufacturer",
                "contact_person": "Ramesh Chawla",
                "phone": "+91 98960 55443",
                "email": "purchase@karnalfeed.com",
                "location": "GT Road, Karnal, Haryana (130 km away)",
                "crop_required": "Maize",
                "quantity_required_tonnes": 800.0,
                "offered_price_q": 2480.0,
                "deadline_date": "2026-09-26",
                "quality_specs": "Yellow maize, High protein (>8.5%), Dry kernels (<11.5% moisture)",
                "rating": 4.7,
                "verified": true
        },
        {
                "company_name": "ITC Choupal Fresh Flour Division",
                "buyer_type": "National Food Conglomerate",
                "contact_person": "Manish Sharma (Procurement Head)",
                "phone": "+91 98110 33445",
                "email": "procurement.wheat@itc.in",
                "location": "Khanna Mandi Hub, Punjab (20 km away)",
                "crop_required": "Wheat",
                "quantity_required_tonnes": 2500.0,
                "offered_price_q": 2520.0,
                "deadline_date": "2026-10-11",
                "quality_specs": "Protein > 11.5%, Hectolitre weight > 78 kg/hl, Moisture < 11.0%, Free from weevils",
                "rating": 5.0,
                "verified": true
        },
        {
                "company_name": "Britannia Industries Agri Supply",
                "buyer_type": "Industrial Bakery Manufacturer",
                "contact_person": "Anil Kulkarni",
                "phone": "+91 98450 67812",
                "email": "rawmaterials@britannia.co.in",
                "location": "Rajpura Industrial Cluster, Punjab (38 km away)",
                "crop_required": "Wheat",
                "quantity_required_tonnes": 1500.0,
                "offered_price_q": 2480.0,
                "deadline_date": "2026-10-03",
                "quality_specs": "Semi-hard flour milling grade, Gluten index > 80, Moisture < 12%",
                "rating": 4.9,
                "verified": true
        },
        {
                "company_name": "Adani Agri Logistics Modern Silos",
                "buyer_type": "Bulk Bulk Grain Storage & Logistics",
                "contact_person": "Deepak Verma",
                "phone": "+91 98250 99881",
                "email": "grain.silos@adani.com",
                "location": "Moga Automated Silo Terminal, Punjab (65 km away)",
                "crop_required": "Wheat",
                "quantity_required_tonnes": 5000.0,
                "offered_price_q": 2460.0,
                "deadline_date": "2026-10-26",
                "quality_specs": "FAQ specification, Direct pneumatic truck tipping accepted, Immediate digital receipt",
                "rating": 4.8,
                "verified": true
        },
        {
                "company_name": "Adani Wilmar Agri Crushing Hub",
                "buyer_type": "National Processor & Exporter",
                "contact_person": "Sanjay Deshmukh",
                "phone": "+91 98200 77665",
                "email": "agri.procurement@adaniwilmar.in",
                "location": "Indore Agri Park, Madhya Pradesh",
                "crop_required": "Soybean",
                "quantity_required_tonnes": 2500.0,
                "offered_price_q": 4820.0,
                "deadline_date": "2026-10-11",
                "quality_specs": "Oil content > 19.5%, Moisture < 10%, Sand/Silica < 0.5%",
                "rating": 5.0,
                "verified": true
        },
        {
                "company_name": "Ruchi Soya Industries (Patanjali)",
                "buyer_type": "Solvent Extraction & Edible Oils",
                "contact_person": "Vivek Agnihotri",
                "phone": "+91 98260 44556",
                "email": "procurement@ruchisoya.com",
                "location": "Pithampur SEZ, Madhya Pradesh",
                "crop_required": "Soybean",
                "quantity_required_tonnes": 1800.0,
                "offered_price_q": 4790.0,
                "deadline_date": "2026-10-01",
                "quality_specs": "Yellow soybean, Foreign matter < 2%, Damaged beans < 3%",
                "rating": 4.8,
                "verified": true
        },
        {
                "company_name": "KRBL Limited (India Gate Basmati)",
                "buyer_type": "Global Rice Miller & Exporter",
                "contact_person": "Pankaj Goel",
                "phone": "+91 98100 11223",
                "email": "paddy.purchase@krblindia.com",
                "location": "Alipur Rice Mill Complex, Delhi / Sonipat (190 km away)",
                "crop_required": "Basmati Rice",
                "quantity_required_tonnes": 3000.0,
                "offered_price_q": 3980.0,
                "deadline_date": "2026-10-16",
                "quality_specs": "Pusa 1121 & 1509 Paddy, Average grain length > 8.35mm, Moisture < 13%",
                "rating": 5.0,
                "verified": true
        },
        {
                "company_name": "LT Foods (Daawat Basmati Heritage)",
                "buyer_type": "Branded Exporter",
                "contact_person": "Sandeep Arora",
                "phone": "+91 98140 88990",
                "email": "sourcing@ltgroup.in",
                "location": "Amritsar Mandi Logistics Center, Punjab (110 km away)",
                "crop_required": "Basmati Rice",
                "quantity_required_tonnes": 2000.0,
                "offered_price_q": 3940.0,
                "deadline_date": "2026-10-09",
                "quality_specs": "Pure Basmati, No admixture of non-basmati grains, Certified export quality",
                "rating": 4.9,
                "verified": true
        },
        {
                "company_name": "Dhara Vegetable Oil Cooperative (NDDB)",
                "buyer_type": "National Edible Oil Brand",
                "contact_person": "Dr. R. K. Mathur",
                "phone": "+91 98290 77112",
                "email": "sourcing@dharaoils.coop",
                "location": "Bharatpur Industrial Area, Rajasthan",
                "crop_required": "Mustard",
                "quantity_required_tonnes": 1200.0,
                "offered_price_q": 5550.0,
                "deadline_date": "2026-10-01",
                "quality_specs": "Oil content > 40.0%, Moisture < 8.0%, Clean dry black sarson",
                "rating": 4.9,
                "verified": true
        },
        {
                "company_name": "Khandelwal Agro Crushing Mills",
                "buyer_type": "Regional Edible Oil Expeller",
                "contact_person": "Om Prakash Khandelwal",
                "phone": "+91 98280 55667",
                "email": "mustard@khandelwaloils.com",
                "location": "Alwar APMC Zone, Rajasthan",
                "crop_required": "Mustard",
                "quantity_required_tonnes": 600.0,
                "offered_price_q": 5500.0,
                "deadline_date": "2026-09-26",
                "quality_specs": "Pungency level high, Foreign seeds < 1.0%",
                "rating": 4.7,
                "verified": true
        },
        {
                "company_name": "Mother Dairy Safal Fresh Fruits & Veg",
                "buyer_type": "Retail Chain & Food Processor",
                "contact_person": "Rajeev Nanda",
                "phone": "+91 98118 77665",
                "email": "procurement@safalfresh.com",
                "location": "Delhi Azadpur Hub / Mangolpuri Cold Depot",
                "crop_required": "Tomato",
                "quantity_required_tonnes": 150.0,
                "offered_price_q": 2150.0,
                "deadline_date": "2026-09-18",
                "quality_specs": "Hybrid firm red, Uniform size (50-65mm), Crate packed, Free from pest puncture",
                "rating": 4.9,
                "verified": true
        },
        {
                "company_name": "Cremica Agro Foods (Sauce & Puree)",
                "buyer_type": "Industrial Food Processor",
                "contact_person": "Harvinder Bector",
                "phone": "+91 98765 43210",
                "email": "tomato.purchase@cremica.com",
                "location": "Phillaur Industrial Zone, Punjab (25 km away)",
                "crop_required": "Tomato",
                "quantity_required_tonnes": 400.0,
                "offered_price_q": 2050.0,
                "deadline_date": "2026-09-23",
                "quality_specs": "Processing grade (TSS > 4.5 Brix), High lycopene, Red ripe",
                "rating": 4.8,
                "verified": true
        }
]
    for b in buyers_data:
        db.add(Buyer(**b))
    db.commit()

    # 13. Transport Providers
    transporters_data = [
        {
            "operator_name": "Balwinder Singh Transport (Tata 407)",
            "phone": "+91 98722 89012",
            "vehicle_type": "Tata 407 (Medium Commercial Vehicle)",
            "capacity_tonnes": 4.5,
            "base_rate_inr": 1400.0,
            "rate_per_km_inr": 28.0,
            "current_distance_km": 4.5,
            "location": "Sahnewal GT Road Bypass",
            "available_now": True,
            "rating": 4.8
        },
        {
            "operator_name": "Khanna Express Truck Fleet (10-Tonne)",
            "phone": "+91 98140 33221",
            "vehicle_type": "Ashok Leyland 10-Tonne Truck",
            "capacity_tonnes": 10.0,
            "base_rate_inr": 2400.0,
            "rate_per_km_inr": 42.0,
            "current_distance_km": 9.0,
            "location": "Khanna Transport Nagar",
            "available_now": True,
            "rating": 4.9
        },
        {
            "operator_name": "Sher-e-Punjab Mahindra Bolero Maxi-Truck",
            "phone": "+91 98788 77665",
            "vehicle_type": "Mahindra Bolero Pickup",
            "capacity_tonnes": 1.7,
            "base_rate_inr": 750.0,
            "rate_per_km_inr": 18.0,
            "current_distance_km": 3.2,
            "location": "Sahnewal Focal Point",
            "available_now": True,
            "rating": 4.7
        }
    ]
    for t in transporters_data:
        db.add(TransportProvider(**t))
    db.commit()

    # 14. Initial Notifications
    notifications_data = [
        {
            "title": "🌧 Weather Advisory: Rainfall Expected in 48 Hours",
            "message": "Light to moderate pre-monsoon showers (18-25mm) forecasted. Avoid fertilizer broadcast or foliar sprays today to prevent leaching.",
            "category": "WEATHER",
            "severity": "WARNING",
            "created_at": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "title": "📈 Maize Price Surge in Khanna Mandi",
            "message": "Modal spot price crossed ₹2,360/quintal (+3.2%) due to tight industrial feed arrivals. Strong seller market.",
            "category": "MARKET",
            "severity": "INFO",
            "created_at": datetime.utcnow() - timedelta(hours=5)
        },
        {
            "title": "🌱 Sowing Stage Nutrient Alert",
            "message": "For your 5-acre Sahnewal farm, basal DAP (18:46:0) and MOP placement should be completed prior to seed drilling.",
            "category": "ADVISORY",
            "severity": "ALERT",
            "created_at": datetime.utcnow() - timedelta(days=1)
        }
    ]
    for n in notifications_data:
        db.add(Notification(**n))
    db.commit()

    # 15. Initial Demo Orders
    orders_data = [
        {
            "user_id": farmer_user.id,
            "order_type": "INPUT",
            "item_title": "Pioneer P3396 Hybrid Maize Seed (10 bags)",
            "quantity": "40 kg (10 bags of 4kg)",
            "amount_inr": 10400.0,
            "status": "CONFIRMED",
            "partner_name": "Kisan Seva Kendra Sahnewal",
            "created_at": datetime.utcnow() - timedelta(days=3)
        },
        {
            "user_id": farmer_user.id,
            "order_type": "TRANSPORT",
            "item_title": "Farm to Khanna Industrial Mill Transport",
            "quantity": "10 Tonnes Maize",
            "amount_inr": 3324.0,
            "status": "COMPLETED",
            "partner_name": "Balwinder Singh Transport",
            "created_at": datetime.utcnow() - timedelta(days=10)
        }
    ]
    for o in orders_data:
        db.add(Order(**o))
    db.commit()

    # 16. Seed Initial Demo Payments
    seed_payments(db)

    # 17. Seed Farm Equipment & Demo Bookings
    seed_equipment(db)

    db.close()
    print("✅ AGRIWISE AI database successfully seeded with realistic Indian agricultural data!")

def seed_payments(db):
    farmer_user = db.query(User).filter(User.role == "FARMER").first()
    farmer_id = farmer_user.id if farmer_user else 1

    payments_data = [
        {
            "transaction_id": "AGRI-PAY-2026-1049",
            "utr_number": "629108447192",
            "user_id": farmer_id,
            "payment_type": "INPUT_PURCHASE",
            "payment_method": "UPI_QR",
            "amount_inr": 10400.0,
            "gst_amount_inr": 520.0,
            "subsidy_amount_inr": 0.0,
            "net_amount_inr": 10400.0,
            "payer_name": "Sardar Gurpreet Singh",
            "payee_name": "Kisan Seva Kendra Sahnewal",
            "bank_name_or_vpa": "gurpreet@sbi",
            "status": "SUCCESS",
            "notes": "Purchase of Pioneer P3396 Hybrid Maize Seed (10 bags)",
            "created_at": datetime.utcnow() - timedelta(days=3),
            "completed_at": datetime.utcnow() - timedelta(days=3)
        },
        {
            "transaction_id": "AGRI-PAY-2026-1082",
            "utr_number": "629112998341",
            "user_id": farmer_id,
            "payment_type": "INPUT_PURCHASE",
            "payment_method": "KCC_RUPAY",
            "amount_inr": 14365.0,
            "gst_amount_inr": 718.25,
            "subsidy_amount_inr": 430.95,
            "net_amount_inr": 13934.05,
            "payer_name": "Sardar Gurpreet Singh",
            "payee_name": "IFFCO Farmer Service Centre",
            "bank_name_or_vpa": "SBI Agriculture Kisan Card (XXXX-4912)",
            "status": "SUCCESS",
            "notes": "Fertilizer seasonal package: Urea (10 bags), DAP (3 bags), MOP (2 bags) with 3% prompt subvention",
            "created_at": datetime.utcnow() - timedelta(days=2),
            "completed_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "transaction_id": "AGRI-PAY-2026-1104",
            "utr_number": "629115002914",
            "user_id": farmer_id,
            "payment_type": "TRANSPORT_ADVANCE",
            "payment_method": "UPI_VPA",
            "amount_inr": 1500.0,
            "gst_amount_inr": 0.0,
            "subsidy_amount_inr": 0.0,
            "net_amount_inr": 1500.0,
            "payer_name": "Sardar Gurpreet Singh",
            "payee_name": "Gurkirat Agri Logistics",
            "bank_name_or_vpa": "gurkirat.logistics@okaxis",
            "status": "SUCCESS",
            "notes": "50% advance dispatch fee for 10 Tonne Tata 407 transport to Khanna Mandi",
            "created_at": datetime.utcnow() - timedelta(days=1),
            "completed_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "transaction_id": "AGRI-PAY-2026-1150",
            "utr_number": "629118330911",
            "user_id": farmer_id,
            "payment_type": "BUYER_ESCROW",
            "payment_method": "ESCROW",
            "amount_inr": 238000.0,
            "gst_amount_inr": 0.0,
            "subsidy_amount_inr": 0.0,
            "net_amount_inr": 238000.0,
            "payer_name": "Godrej Agrovet Procurement Ltd",
            "payee_name": "Sardar Gurpreet Singh (AgriWise Smart Escrow Lock)",
            "bank_name_or_vpa": "ICICI Agri Escrow Vault",
            "status": "ESCROW_LOCKED",
            "notes": "Wholesale contract procurement escrow: 100 Quintals Yellow Maize at ₹2,380/Qtl. Pending APMC quality assay test.",
            "created_at": datetime.utcnow() - timedelta(hours=6),
            "completed_at": datetime.utcnow() - timedelta(hours=6)
        },
        {
            "transaction_id": "AGRI-PAY-2026-0980",
            "utr_number": "629088421098",
            "user_id": farmer_id,
            "payment_type": "FARMER_PAYOUT",
            "payment_method": "MANDI_DIRECT",
            "amount_inr": 194000.0,
            "gst_amount_inr": 0.0,
            "subsidy_amount_inr": 0.0,
            "net_amount_inr": 194000.0,
            "payer_name": "Khanna APMC Grain Exchange",
            "payee_name": "Sardar Gurpreet Singh",
            "bank_name_or_vpa": "Punjab National Bank (A/C: 084200010091)",
            "status": "DISBURSED",
            "notes": "Previous Rabi harvest settlement: 80 Quintals Sharbati Wheat direct DBT clearance",
            "created_at": datetime.utcnow() - timedelta(days=12),
            "completed_at": datetime.utcnow() - timedelta(days=12)
        }
    ]
    for p in payments_data:
        db.add(PaymentTransaction(**p))
    db.commit()
    print("💳 Pre-seeded realistic Indian agricultural payment transactions.")

def seed_equipment(db):
    farmer_user = db.query(User).filter(User.role == "FARMER").first()
    farmer_id = farmer_user.id if farmer_user else 1
    farmer_name = farmer_user.name if farmer_user else "Sardar Gurpreet Singh"
    farmer_phone = farmer_user.phone if farmer_user else "+91 98765 43210"

    equipment_list = [
        {
            "name": "John Deere 5310 55HP Tractor",
            "category": "Tractors",
            "brand": "John Deere",
            "model": "5310 GearPro 4WD",
            "year": 2024,
            "power_hp": "55 HP",
            "fuel_type": "Diesel",
            "capacity_specs": "55 HP, 4WD, 9F+3R GearPro, 2000 kg Hydraulic Lift, Dual Clutch",
            "hourly_rate": 550.0,
            "daily_rate": 3800.0,
            "operator_available": True,
            "operator_charge_per_hr": 150.0,
            "operator_charge_per_day": 800.0,
            "fuel_included_option": True,
            "fuel_charge_per_hr": 250.0,
            "fuel_charge_per_day": 1400.0,
            "delivery_available": True,
            "delivery_rate_per_km": 35.0,
            "security_deposit": 2000.0,
            "location": "Sahnewal / Ludhiana, Punjab",
            "district": "Ludhiana",
            "state": "Punjab",
            "distance_km": 3.8,
            "owner_name": "Gurpreet Singh CHC Machinery Hub",
            "owner_phone": "+91 98765 43210",
            "owner_badge": "Verified AgriWise Partner",
            "rating": 4.9,
            "reviews_count": 42,
            "image_url": "/images/equipment/john_deere_5310.jpg",
            "implements_compatibility": "MB Plough, 7-ft Rotavator, Disc Harrow, 9-Tyne Cultivator, 5-Tonne Hydraulic Trolley",
            "terms": "Valid Govt ID (Aadhaar/DL) required at handover. Full refund on cancellation > 6 hours prior to start. Fuel tank is provided full.",
            "available": True
        },
        {
            "name": "Mahindra Novo 655 DI 65HP Tractor 4WD",
            "category": "Tractors",
            "brand": "Mahindra",
            "model": "Arjun Novo 655 DI-i 4WD",
            "year": 2024,
            "power_hp": "65 HP",
            "fuel_type": "Diesel",
            "capacity_specs": "65 HP m-Boost Engine, 4WD, 15F+15R Synchromesh Shuttle, 2200 kg High Precision Hydraulics",
            "hourly_rate": 600.0,
            "daily_rate": 4200.0,
            "operator_available": True,
            "operator_charge_per_hr": 150.0,
            "operator_charge_per_day": 850.0,
            "fuel_included_option": True,
            "fuel_charge_per_hr": 280.0,
            "fuel_charge_per_day": 1550.0,
            "delivery_available": True,
            "delivery_rate_per_km": 38.0,
            "security_deposit": 2500.0,
            "location": "Karnal GT Road, Haryana",
            "district": "Karnal",
            "state": "Haryana",
            "distance_km": 5.2,
            "owner_name": "Kisan Samriddhi Custom Hiring Centre",
            "owner_phone": "+91 98123 77654",
            "owner_badge": "Verified AgriWise Partner",
            "rating": 4.8,
            "reviews_count": 38,
            "image_url": "/images/equipment/mahindra_novo_655.jpg",
            "implements_compatibility": "Heavy Laser Land Leveler, Subsoiler, Heavy Duty Rotavator, Multi-Crop Pneumatic Planter",
            "terms": "Security deposit refunded immediately upon return inspection. Standard diesel fuel policy applies.",
            "available": True
        },
        {
            "name": "Preet 987 Combine Harvester (Self-Propelled)",
            "category": "Harvesters",
            "brand": "Preet",
            "model": "987 Deluxe Self-Propelled",
            "year": 2023,
            "power_hp": "101 HP",
            "fuel_type": "Diesel",
            "capacity_specs": "101 HP Turbo Diesel, 14-ft Heavy Cutter Bar, Double Straw Walker, 2400 kg Grain Tank",
            "hourly_rate": 1800.0,
            "daily_rate": 14000.0,
            "operator_available": True,
            "operator_charge_per_hr": 300.0,
            "operator_charge_per_day": 1800.0,
            "fuel_included_option": True,
            "fuel_charge_per_hr": 750.0,
            "fuel_charge_per_day": 5500.0,
            "delivery_available": True,
            "delivery_rate_per_km": 55.0,
            "security_deposit": 5000.0,
            "location": "Patiala Rural Bypass, Punjab",
            "district": "Patiala",
            "state": "Punjab",
            "distance_km": 12.4,
            "owner_name": "Majha Malwa Combine Union",
            "owner_phone": "+91 98722 55432",
            "owner_badge": "Verified AgriWise Partner",
            "rating": 4.9,
            "reviews_count": 64,
            "image_url": "/images/equipment/preet_987_harvester.jpg",
            "implements_compatibility": "Paddy Cutter Bar, Wheat Reel Header, Straw Management System (SMS) attached",
            "terms": "Certified commercial harvester operator required and included. Minimum 2-hour booking.",
            "available": True
        },
        {
            "name": "Kirloskar 5HP Diesel Water Pump (Portable)",
            "category": "Water Pumps",
            "brand": "Kirloskar",
            "model": "Mega-T 5HP Portable Engine Pump",
            "year": 2024,
            "power_hp": "5 HP",
            "fuel_type": "Diesel",
            "capacity_specs": "5 HP 4-Stroke Air-Cooled Diesel, 1200 Litres/min High Discharge, 28m Total Head, Trolley Mounted",
            "hourly_rate": 150.0,
            "daily_rate": 900.0,
            "operator_available": True,
            "operator_charge_per_hr": 80.0,
            "operator_charge_per_day": 400.0,
            "fuel_included_option": True,
            "fuel_charge_per_hr": 90.0,
            "fuel_charge_per_day": 500.0,
            "delivery_available": True,
            "delivery_rate_per_km": 20.0,
            "security_deposit": 800.0,
            "location": "Meerut Industrial Area, Uttar Pradesh",
            "district": "Meerut",
            "state": "Uttar Pradesh",
            "distance_km": 2.5,
            "owner_name": "Chaudhary Tube-Well & Pump Rental",
            "owner_phone": "+91 94120 88765",
            "owner_badge": "Verified AgriWise Partner",
            "rating": 4.7,
            "reviews_count": 52,
            "image_url": "/images/equipment/kirloskar_water_pump.jpg",
            "implements_compatibility": "50-meter Flexible Delivery Hose, 10-meter Spiral Suction Pipe, Foot Valve & Strainer",
            "terms": "Supplied with suction pipe and clamps. Caution deposit refunded after water test run.",
            "available": True
        },
        {
            "name": "Shaktiman Semi-Champion Rotavator (7 Feet)",
            "category": "Rotavators",
            "brand": "Shaktiman",
            "model": "Semi-Champion 205 (7 Feet)",
            "year": 2024,
            "power_hp": "Requires 45-60 HP Tractor",
            "fuel_type": "PTO Driven",
            "capacity_specs": "7-ft Width, 48 Boron Steel L-Blades, Multi-Speed Heavy Duty Gearbox, Depth up to 7 inches",
            "hourly_rate": 300.0,
            "daily_rate": 2000.0,
            "operator_available": True,
            "operator_charge_per_hr": 120.0,
            "operator_charge_per_day": 600.0,
            "fuel_included_option": False,
            "fuel_charge_per_hr": 0.0,
            "fuel_charge_per_day": 0.0,
            "delivery_available": True,
            "delivery_rate_per_km": 25.0,
            "security_deposit": 1500.0,
            "location": "Nashik Agri Market, Maharashtra",
            "district": "Nashik",
            "state": "Maharashtra",
            "distance_km": 6.8,
            "owner_name": "Sahyadri Agro Machinery Bank",
            "owner_phone": "+91 98230 44556",
            "owner_badge": "Verified AgriWise Partner",
            "rating": 4.8,
            "reviews_count": 29,
            "image_url": "/images/equipment/shaktiman_rotavator.jpg",
            "implements_compatibility": "Connects to any standard 540 RPM PTO shaft. Fits 45-75 HP Category II tractors.",
            "terms": "Please verify PTO spline match (6-spline standard). Full refund if cancelled > 6 hrs prior.",
            "available": True
        },
        {
            "name": "National Seed-cum-Fertilizer Drill (11-Tyne)",
            "category": "Seed Drills",
            "brand": "National Agri",
            "model": "Automatic 11-Tyne Dual Box Drill",
            "year": 2023,
            "power_hp": "Requires 35-50 HP Tractor",
            "fuel_type": "Ground Wheel Driven",
            "capacity_specs": "11 Tynes, Dual Hopper (Seed 60kg + Fertilizer 65kg), Fluted Roller Seed Metering System",
            "hourly_rate": 250.0,
            "daily_rate": 1600.0,
            "operator_available": True,
            "operator_charge_per_hr": 100.0,
            "operator_charge_per_day": 550.0,
            "fuel_included_option": False,
            "fuel_charge_per_hr": 0.0,
            "fuel_charge_per_day": 0.0,
            "delivery_available": True,
            "delivery_rate_per_km": 25.0,
            "security_deposit": 1200.0,
            "location": "Indore Mandi Hub, Madhya Pradesh",
            "district": "Indore",
            "state": "Madhya Pradesh",
            "distance_km": 8.0,
            "owner_name": "Malwa Kisan Seed Tech CHC",
            "owner_phone": "+91 97555 33211",
            "owner_badge": "Verified AgriWise Partner",
            "rating": 4.7,
            "reviews_count": 23,
            "image_url": "/images/equipment/national_seed_drill.jpg",
            "implements_compatibility": "Calibrated for Wheat, Mustard, Gram, Soybeans, Maize with individual depth adjustments.",
            "terms": "Clean seed hoppers after use. Return in undamaged working order for instant deposit release.",
            "available": True
        },
        {
            "name": "Landforce Multi-Crop Thresher (PTO Driven)",
            "category": "Threshers",
            "brand": "Landforce",
            "model": "Multi-Crop Haramba Thresher 550",
            "year": 2023,
            "power_hp": "Requires 40+ HP Tractor",
            "fuel_type": "PTO Driven",
            "capacity_specs": "15-20 Quintals/hr Output, Double Blower Dust Separator, Sieves for Wheat/Maize/Soybean",
            "hourly_rate": 400.0,
            "daily_rate": 2800.0,
            "operator_available": True,
            "operator_charge_per_hr": 150.0,
            "operator_charge_per_day": 800.0,
            "fuel_included_option": False,
            "fuel_charge_per_hr": 0.0,
            "fuel_charge_per_day": 0.0,
            "delivery_available": True,
            "delivery_rate_per_km": 30.0,
            "security_deposit": 2000.0,
            "location": "Guntur Agriculture Market Yard, AP",
            "district": "Guntur",
            "state": "Andhra Pradesh",
            "distance_km": 11.5,
            "owner_name": "Coastal Andhra Farm Services",
            "owner_phone": "+91 98480 66789",
            "owner_badge": "Verified AgriWise Partner",
            "rating": 4.8,
            "reviews_count": 31,
            "image_url": "/images/equipment/landforce_thresher.jpg",
            "implements_compatibility": "Automatic Feeding Hopper, Elevator Bagging Chute, Variable Speed Pulleys",
            "terms": "Includes emergency stop mechanism. Operating instructions provided upon delivery.",
            "available": True
        },
        {
            "name": "Aspee HTP Tractor-Mounted Boom Sprayer (400L)",
            "category": "Sprayers",
            "brand": "Aspee",
            "model": "HTP 400L Boom Sprayer",
            "year": 2024,
            "power_hp": "Requires 30+ HP Tractor",
            "fuel_type": "PTO Driven",
            "capacity_specs": "400-Litre Heavy Tank, 30-ft Folding Boom, 22 Italian Ceramic Nozzles, 35 Bar Pressure Pump",
            "hourly_rate": 200.0,
            "daily_rate": 1400.0,
            "operator_available": True,
            "operator_charge_per_hr": 120.0,
            "operator_charge_per_day": 600.0,
            "fuel_included_option": False,
            "fuel_charge_per_hr": 0.0,
            "fuel_charge_per_day": 0.0,
            "delivery_available": True,
            "delivery_rate_per_km": 20.0,
            "security_deposit": 1000.0,
            "location": "Bathinda Cantt Road, Punjab",
            "district": "Bathinda",
            "state": "Punjab",
            "distance_km": 4.9,
            "owner_name": "Bathinda Precision Agro Implements",
            "owner_phone": "+91 98760 99881",
            "owner_badge": "Verified AgriWise Partner",
            "rating": 4.6,
            "reviews_count": 19,
            "image_url": "/images/equipment/aspee_boom_sprayer.jpg",
            "implements_compatibility": "Fits Category I & II tractors. Uniform micron-droplet coverage for pest & nutrient foliar spray.",
            "terms": "Flush tank thoroughly with clean water before return. Full deposit returned upon clean inspection.",
            "available": True
        },
        {
            "name": "Kubota DC-68G Paddy Combine Harvester",
            "category": "Harvesters",
            "brand": "Kubota",
            "model": "DC-68G Full-Feed Crawler",
            "year": 2024,
            "power_hp": "68 HP Turbo Charged",
            "fuel_type": "Diesel",
            "capacity_specs": "Rubber Track Crawler for Wet Fields, 2.0m Cutting Width, 1250L Grain Hopper, Hydrostatic HST",
            "hourly_rate": 2000.0,
            "daily_rate": 15500.0,
            "operator_available": True,
            "operator_charge_per_hr": 350.0,
            "operator_charge_per_day": 2000.0,
            "fuel_included_option": True,
            "fuel_charge_per_hr": 800.0,
            "fuel_charge_per_day": 6000.0,
            "delivery_available": True,
            "delivery_rate_per_km": 60.0,
            "security_deposit": 5000.0,
            "location": "Amritsar Rural, Punjab",
            "district": "Amritsar",
            "state": "Punjab",
            "distance_km": 14.2,
            "owner_name": "Golden Temple Agro Custom Centre",
            "owner_phone": "+91 98150 11223",
            "owner_badge": "Verified AgriWise Partner",
            "rating": 4.9,
            "reviews_count": 57,
            "image_url": "/images/equipment/kubota_dc68g_harvester.jpg",
            "implements_compatibility": "Special rubber tracks prevent field sinking in flooded paddy soils. Includes auto grain unloader.",
            "terms": "Driver & mechanical specialist provided. 100% money back if breakdown exceeds 2 hours.",
            "available": True
        },
        {
            "name": "Sonalika DI 745 III Sikander 50HP Tractor",
            "category": "Tractors",
            "brand": "Sonalika",
            "model": "DI 745 III Sikander HDM",
            "year": 2023,
            "power_hp": "50 HP",
            "fuel_type": "Diesel",
            "capacity_specs": "50 HP Heavy Duty Mileage Engine, 8F+2R Constant Mesh, 1800 kg Lift, Oil Immersed Brakes",
            "hourly_rate": 480.0,
            "daily_rate": 3400.0,
            "operator_available": True,
            "operator_charge_per_hr": 140.0,
            "operator_charge_per_day": 750.0,
            "fuel_included_option": True,
            "fuel_charge_per_hr": 240.0,
            "fuel_charge_per_day": 1350.0,
            "delivery_available": True,
            "delivery_rate_per_km": 32.0,
            "security_deposit": 2000.0,
            "location": "Muzaffarnagar Sugar Belt, UP",
            "district": "Muzaffarnagar",
            "state": "Uttar Pradesh",
            "distance_km": 7.5,
            "owner_name": "Kisan Shakti Tractor Pool",
            "owner_phone": "+91 94122 33445",
            "owner_badge": "Verified AgriWise Partner",
            "rating": 4.8,
            "reviews_count": 45,
            "image_url": "/images/equipment/sonalika_di745_tractor.jpg",
            "implements_compatibility": "Cultivator 9-Tyne, Rotavator 6ft, Disc Plough, Seed Drill, Heavy 5-Ton Trolley",
            "terms": "Fuel tank is filled to brim on dispatch. Return clean and fueled or pay fuel differential.",
            "available": True
        }
    ]

    created_items = []
    for eq in equipment_list:
        obj = Equipment(**eq)
        db.add(obj)
        created_items.append(obj)
    db.commit()

    # Pre-seed 3 realistic demo bookings for the farmer
    now = datetime.utcnow()
    # 1. Upcoming booking tomorrow
    booking_1 = EquipmentBooking(
        booking_id="AGRI-EQP-2026-0042",
        equipment_id=created_items[0].id, # John Deere 5310
        farmer_id=farmer_id,
        farmer_name=farmer_name,
        farmer_phone=farmer_phone,
        rental_type="HOURLY",
        start_time=now + timedelta(days=1, hours=3),
        end_time=now + timedelta(days=1, hours=7),
        duration_units=4.0,
        with_operator=True,
        with_fuel=False,
        delivery_to_farm=True,
        delivery_address="Sahnewal Farm 1, Khasra 412, Ludhiana",
        delivery_distance_km=3.8,
        base_amount=2200.0,
        operator_amount=600.0,
        delivery_amount=133.0,
        security_deposit=2000.0,
        gst_amount=146.65,
        total_amount=5079.65,
        payment_method="UPI_QR",
        payment_status="PAID",
        booking_status="CONFIRMED",
        notes="Ploughing and rotavator land preparation for Kharif sowing.",
        created_at=now - timedelta(hours=3)
    )

    # 2. Active booking ongoing today
    booking_2 = EquipmentBooking(
        booking_id="AGRI-EQP-2026-0038",
        equipment_id=created_items[4].id, # Shaktiman Rotavator
        farmer_id=farmer_id,
        farmer_name=farmer_name,
        farmer_phone=farmer_phone,
        rental_type="DAILY",
        start_time=now - timedelta(hours=2),
        end_time=now + timedelta(hours=8),
        duration_units=1.0,
        with_operator=True,
        with_fuel=False,
        delivery_to_farm=False,
        delivery_address="Self-pickup from Sahyadri CHC Yard",
        delivery_distance_km=0.0,
        base_amount=2000.0,
        operator_amount=600.0,
        delivery_amount=0.0,
        security_deposit=1500.0,
        gst_amount=130.0,
        total_amount=4230.0,
        payment_method="KCC_RUPAY",
        payment_status="PAID",
        booking_status="ACTIVE",
        notes="Active field tillage. Machine delivered and working smoothly.",
        created_at=now - timedelta(days=1)
    )

    # 3. Past completed booking 4 days ago
    booking_3 = EquipmentBooking(
        booking_id="AGRI-EQP-2026-0019",
        equipment_id=created_items[3].id, # Kirloskar Pump
        farmer_id=farmer_id,
        farmer_name=farmer_name,
        farmer_phone=farmer_phone,
        rental_type="HOURLY",
        start_time=now - timedelta(days=5, hours=4),
        end_time=now - timedelta(days=5),
        duration_units=4.0,
        with_operator=False,
        with_fuel=True,
        delivery_to_farm=True,
        delivery_address="Sahnewal Farm 1 Tube-well Well-Head 2",
        delivery_distance_km=2.5,
        base_amount=600.0,
        operator_amount=0.0,
        delivery_amount=50.0,
        security_deposit=800.0,
        gst_amount=32.5,
        total_amount=1482.5,
        payment_method="UPI_QR",
        payment_status="PAID",
        booking_status="COMPLETED",
        rating=5.0,
        review_text="Excellent water discharge rate, watered my 3-acre maize field within 4 hours. Prompt delivery and helpful owner!",
        notes="Completed successfully. Security deposit of ₹800 refunded.",
        created_at=now - timedelta(days=6)
    )

    db.add(booking_1)
    db.add(booking_2)
    db.add(booking_3)
    db.commit()
    print("🚜 Pre-seeded 10 realistic Indian farm equipment and 3 demo bookings.")

if __name__ == "__main__":
    populate_database()
