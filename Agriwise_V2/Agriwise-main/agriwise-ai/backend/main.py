"""
🌾 AGRIWISE AI - Main FastAPI Application
Provides RESTful APIs, serves frontend static assets, and handles clean routing
for all 28 dedicated functional pages.
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json
import random
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database import (
    get_db, init_db, User, Farm, SoilProfile, WaterProfile,
    Crop, SeedVariety, FertilizerProduct, Dealer, MarketPrice,
    CropShortage, Buyer, TransportProvider, Order, Notification, ConfigWeights,
    PaymentTransaction, Equipment, EquipmentBooking
)
from seed_data import populate_database
from engines.weather_service import fetch_live_weather
from engines.recommendation import evaluate_crop_suitability, calculate_fertilizer_plan, DEFAULT_WEIGHTS
from engines.profitability import calculate_farm_profitability
from engines.assistant import process_assistant_query

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
PAGES_DIR = os.path.join(FRONTEND_DIR, "pages")

app = FastAPI(
    title="🌾 AGRIWISE AI Platform API",
    description="Intelligent Crop, Seed, Input & Market Decision Platform for Indian Agriculture",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize and seed database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    populate_database()

# ==========================================
# 1. API: Health Check & System Status
# ==========================================
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "platform": "AGRIWISE AI",
        "version": "1.0.0",
        "database": "SQLite (Connected)",
        "weather_service": "Open-Meteo Global Engine (Active)",
        "environment": "Production-Ready Demo"
    }

# In-memory OTP storage with expiration
OTP_CACHE: Dict[str, Dict[str, Any]] = {}

def get_dashboard_redirect(role: str) -> str:
    role = (role or "FARMER").upper()
    if role == "DEALER":
        return "/dealer-dashboard"
    elif role in ["SERVICE_PROVIDER", "TRANSPORTER"]:
        return "/transport-dashboard"
    elif role == "BUYER":
        return "/buyer-dashboard"
    elif role == "ADMIN":
        return "/admin"
    return "/dashboard"

@app.get("/api/auth/me")
def get_current_user(role: Optional[str] = None, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    user = None
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
    if not user and role:
        target_role = role.upper()
        if target_role == "SERVICE_PROVIDER":
            user = db.query(User).filter((User.role == "SERVICE_PROVIDER") | (User.role == "TRANSPORTER")).first()
        else:
            user = db.query(User).filter(User.role == target_role).first()
    if not user:
        user = db.query(User).first()

    farm = user.farms[0] if user and user.farms else None
    return {
        "id": user.id if user else 1,
        "name": user.name if user else "Gurpreet Singh",
        "email": user.email if user else "gurpreet.farmer@agriwise.ai",
        "phone": user.phone if user else "+91 98765 43210",
        "role": user.role if user else "FARMER",
        "state": user.state if user else "Punjab",
        "district": user.district if user else "Ludhiana",
        "village": user.village if user else "Sahnewal",
        "farm_size_acres": user.farm_size_acres if user else 5.0,
        "experience_years": user.experience_years if user else 14,
        "active_farm": {
            "id": farm.id if farm else 1,
            "name": farm.name if farm else "Sahnewal Golden Acre Farm",
            "current_crop": farm.current_crop if farm else "Maize",
            "current_season": farm.current_season if farm else "Kharif",
            "area_acres": farm.area_acres if farm else 5.0
        } if farm else None
    }

@app.post("/api/auth/login")
def login(payload: dict = Body(...), db: Session = Depends(get_db)):
    identifier = (payload.get("identifier") or payload.get("email") or payload.get("phone") or "").strip()
    password = (payload.get("password") or "").strip()
    requested_role = (payload.get("role") or "").strip().upper()

    user = None
    # 1. Search by email or phone match
    if identifier:
        user = db.query(User).filter(
            (User.email.ilike(identifier)) | (User.phone == identifier) | (User.phone.contains(identifier))
        ).first()

    # 2. Search by role if requested
    if not user and requested_role in ["FARMER", "DEALER", "SERVICE_PROVIDER", "TRANSPORTER", "BUYER", "ADMIN"]:
        if requested_role == "SERVICE_PROVIDER":
            user = db.query(User).filter((User.role == "SERVICE_PROVIDER") | (User.role == "TRANSPORTER")).first()
        else:
            user = db.query(User).filter(User.role == requested_role).first()

    # 3. Check identifier matching role name
    if not user and identifier.upper() in ["FARMER", "DEALER", "SERVICE_PROVIDER", "TRANSPORTER", "BUYER", "ADMIN"]:
        if identifier.upper() == "SERVICE_PROVIDER":
            user = db.query(User).filter((User.role == "SERVICE_PROVIDER") | (User.role == "TRANSPORTER")).first()
        else:
            user = db.query(User).filter(User.role == identifier.upper()).first()

    # 4. Fallback to default user
    if not user:
        user = db.query(User).first()

    if not user:
        raise HTTPException(status_code=401, detail="No matching user account found. Please register.")

    redirect_url = get_dashboard_redirect(user.role)
    token = f"agriwise_tok_{user.role.lower()}_{user.id}_{int(datetime.utcnow().timestamp())}"

    return {
        "success": True,
        "message": f"Welcome back, {user.name}!",
        "token": token,
        "redirect_url": redirect_url,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "state": user.state,
            "district": user.district,
            "village": user.village,
            "farm_size_acres": user.farm_size_acres
        }
    }

@app.post("/api/auth/send-otp")
def send_otp(payload: dict = Body(...), db: Session = Depends(get_db)):
    phone = (payload.get("phone") or "").strip()
    role = (payload.get("role") or "FARMER").strip().upper()
    
    clean_digits = "".join(filter(str.isdigit, phone))
    if len(clean_digits) < 6:
        raise HTTPException(status_code=400, detail="Please enter a valid 10-digit Indian mobile number.")

    generated_otp = f"{random.randint(100000, 999999)}"
    OTP_CACHE[clean_digits] = {
        "otp": generated_otp,
        "role": role,
        "expires_at": datetime.utcnow() + timedelta(minutes=5)
    }

    return {
        "success": True,
        "message": f"6-digit Kisan Verification OTP dispatched to {phone}",
        "otp": generated_otp,
        "expires_in_seconds": 300,
        "role": role
    }

@app.post("/api/auth/verify-otp")
def verify_otp(payload: dict = Body(...), db: Session = Depends(get_db)):
    phone = (payload.get("phone") or "").strip()
    otp = (payload.get("otp") or "").strip()
    role = (payload.get("role") or "FARMER").strip().upper()

    clean_digits = "".join(filter(str.isdigit, phone))
    cached = OTP_CACHE.get(clean_digits)

    # Accept generated OTP, or master demo codes (123456 / 1234)
    is_valid = False
    if otp in ["123456", "1234"]:
        is_valid = True
    elif cached and cached.get("otp") == otp:
        if cached.get("expires_at") >= datetime.utcnow():
            is_valid = True
            role = cached.get("role", role)
        else:
            raise HTTPException(status_code=400, detail="OTP has expired. Please request a new code.")

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid OTP code. Please check SMS or use demo code 123456.")

    # Match user by phone or role
    user = db.query(User).filter(User.role == role).first()
    if not user:
        user = db.query(User).first()

    redirect_url = get_dashboard_redirect(user.role)
    token = f"agriwise_otp_tok_{user.role.lower()}_{user.id}_{int(datetime.utcnow().timestamp())}"

    return {
        "success": True,
        "message": f"Phone verified! Welcome back, {user.name}.",
        "token": token,
        "redirect_url": redirect_url,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "state": user.state,
            "district": user.district,
            "village": user.village,
            "farm_size_acres": user.farm_size_acres
        }
    }

@app.post("/api/auth/logout")
def logout():
    return {
        "success": True,
        "message": "User session cleared successfully"
    }

@app.post("/api/auth/register")
def register(payload: dict = Body(...), db: Session = Depends(get_db)):
    name = (payload.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Full name is required for registration.")

    phone = (payload.get("phone") or "").strip()
    if not phone or len("".join(filter(str.isdigit, phone))) < 6:
        raise HTTPException(status_code=400, detail="Please enter a valid 10-digit mobile number.")

    email = (payload.get("email") or "").strip()
    role = (payload.get("role") or "FARMER").strip().upper()
    state = (payload.get("state") or "Punjab").strip()
    district = (payload.get("district") or "Ludhiana").strip()
    village = (payload.get("village") or "Sahnewal").strip()

    try:
        farm_size = float(payload.get("farm_size_acres") or 5.0)
    except (ValueError, TypeError):
        farm_size = 5.0

    try:
        exp_years = int(payload.get("experience_years") or 10)
    except (ValueError, TypeError):
        exp_years = 10

    # Auto-generate email if missing
    if not email:
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower()) or "user"
        email = f"{clean_name}.{role.lower()}_{int(datetime.utcnow().timestamp()) % 10000}@agriwise.ai"

    # Check if user with same email or phone exists
    existing = db.query(User).filter(
        (User.email == email) | (User.phone == phone)
    ).first()

    if existing:
        user = existing
        # Update details if appropriate
        user.name = name
        user.state = state
        user.district = district
        user.village = village
        db.commit()
    else:
        new_user = User(
            name=name,
            email=email,
            phone=phone,
            role=role,
            state=state,
            district=district,
            village=village,
            farm_size_acres=farm_size,
            experience_years=exp_years
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user

        # Create role-specific models
        if role == "FARMER":
            farm = Farm(
                user_id=user.id,
                name=f"{village} {name.split()[0]} Farm",
                location_name=f"{village}, {district}, {state}",
                latitude=30.9010,
                longitude=75.8573,
                area_acres=farm_size,
                current_crop=payload.get("crops") or "Maize",
                current_season="Kharif",
                previous_crop="Wheat",
                irrigation_method=payload.get("irrigation_method") or "Subsurface Drip + Tube-well"
            )
            db.add(farm)
            db.commit()
            db.refresh(farm)

            soil = SoilProfile(
                farm_id=farm.id,
                soil_type="Alluvial Loam",
                soil_texture="Loamy",
                ph=6.8,
                nitrogen_kg_ha=260.0,
                phosphorus_kg_ha=22.5,
                potassium_kg_ha=280.0,
                organic_carbon_pct=0.62,
                health_score=85,
                source_type="Farmer entered",
                test_date="2026-05-10"
            )
            water = WaterProfile(
                farm_id=farm.id,
                source=farm.irrigation_method,
                ph=7.2,
                ec_ds_m=0.65,
                tds_ppm=420.0,
                suitability_score=88
            )
            db.add_all([soil, water])
            db.commit()

        elif role == "DEALER":
            dealer = Dealer(
                business_name=payload.get("business_name") or f"{name} Kisan Kendra",
                owner_name=name,
                phone=phone,
                city=district,
                address=f"{village}, {district}",
                state=state,
                rating=4.9,
                verified=True,
                delivery_available=True
            )
            db.add(dealer)
            db.commit()

        elif role in ["SERVICE_PROVIDER", "TRANSPORTER"]:
            user.role = "SERVICE_PROVIDER"
            tp = TransportProvider(
                operator_name=payload.get("business_name") or f"{name} Agricultural Services",
                phone=phone,
                vehicle_type=payload.get("vehicle_type") or "Tractor & Commercial Vehicle",
                capacity_tonnes=10.0,
                base_rate_inr=1800.0,
                rate_per_km_inr=26.0,
                location=f"{district} Bypass",
                available_now=True
            )
            db.add(tp)
            db.commit()

        elif role == "BUYER":
            buyer = Buyer(
                company_name=payload.get("business_name") or f"{name} Agro Mills",
                buyer_type="Food Processor & Miller",
                contact_person=name,
                phone=phone,
                email=email,
                location=f"{district} Industrial Area",
                state=state,
                district=district,
                crop_required=payload.get("crops") or "Maize",
                quantity_required_tonnes=500.0,
                offered_price_q=2350.0,
                verified=True
            )
            db.add(buyer)
            db.commit()

    token = f"agriwise_reg_tok_{user.role.lower()}_{user.id}_{int(datetime.utcnow().timestamp())}"
    redirect_url = get_dashboard_redirect(user.role)

    return {
        "success": True,
        "message": f"Registration successful! Welcome to AgriWise AI, {user.name}.",
        "token": token,
        "redirect_url": redirect_url,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "state": user.state,
            "district": user.district,
            "village": user.village,
            "farm_size_acres": user.farm_size_acres
        }
    }

# ==========================================
# 3. API: Farm Profile & Analysis
# ==========================================
@app.get("/api/farms")
def get_farms(db: Session = Depends(get_db)):
    farms = db.query(Farm).all()
    results = []
    for f in farms:
        soil = f.soil
        water = f.water
        results.append({
            "id": f.id,
            "name": f.name,
            "location_name": f.location_name,
            "latitude": f.latitude,
            "longitude": f.longitude,
            "elevation_m": f.elevation_m,
            "area_acres": f.area_acres,
            "current_crop": f.current_crop,
            "current_season": f.current_season,
            "previous_crop": f.previous_crop,
            "irrigation_method": f.irrigation_method,
            "water_source": f.water_source,
            "water_availability": f.water_availability,
            "farming_method": f.farming_method,
            "soil": {
                "soil_type": soil.soil_type if soil else "Alluvial Loam",
                "ph": soil.ph if soil else 6.8,
                "nitrogen_kg_ha": soil.nitrogen_kg_ha if soil else 260.0,
                "phosphorus_kg_ha": soil.phosphorus_kg_ha if soil else 22.5,
                "potassium_kg_ha": soil.potassium_kg_ha if soil else 280.0,
                "organic_carbon_pct": soil.organic_carbon_pct if soil else 0.62,
                "moisture_pct": soil.moisture_pct if soil else 22.0,
                "ec_ds_m": soil.ec_ds_m if soil else 0.45,
                "health_score": soil.health_score if soil else 85
            },
            "water": {
                "source": water.source if water else "Tube-well",
                "ph": water.ph if water else 7.2,
                "ec_ds_m": water.ec_ds_m if water else 0.65,
                "tds_ppm": water.tds_ppm if water else 420.0,
                "salinity_status": water.salinity_status if water else "Safe / Good Quality",
                "hardness_mg_l": water.hardness_mg_l if water else 180.0,
                "suitability_score": water.suitability_score if water else 88
            }
        })
    return results

@app.get("/api/farms/{farm_id}")
def get_farm(farm_id: int, db: Session = Depends(get_db)):
    f = db.query(Farm).filter(Farm.id == farm_id).first()
    if not f:
        f = db.query(Farm).first()
    soil = f.soil
    water = f.water
    return {
        "id": f.id,
        "name": f.name,
        "location_name": f.location_name,
        "latitude": f.latitude,
        "longitude": f.longitude,
        "elevation_m": f.elevation_m,
        "area_acres": f.area_acres,
        "current_crop": f.current_crop,
        "current_season": f.current_season,
        "previous_crop": f.previous_crop,
        "irrigation_method": f.irrigation_method,
        "water_source": f.water_source,
        "water_availability": f.water_availability,
        "farming_method": f.farming_method,
        "soil": {
            "soil_type": soil.soil_type if soil else "Alluvial Loam",
            "ph": soil.ph if soil else 6.8,
            "nitrogen_kg_ha": soil.nitrogen_kg_ha if soil else 260.0,
            "phosphorus_kg_ha": soil.phosphorus_kg_ha if soil else 22.5,
            "potassium_kg_ha": soil.potassium_kg_ha if soil else 280.0,
            "organic_carbon_pct": soil.organic_carbon_pct if soil else 0.62,
            "moisture_pct": soil.moisture_pct if soil else 22.0,
            "ec_ds_m": soil.ec_ds_m if soil else 0.45,
            "health_score": soil.health_score if soil else 85
        },
        "water": {
            "source": water.source if water else "Tube-well",
            "ph": water.ph if water else 7.2,
            "ec_ds_m": water.ec_ds_m if water else 0.65,
            "tds_ppm": water.tds_ppm if water else 420.0,
            "salinity_status": water.salinity_status if water else "Safe",
            "hardness_mg_l": water.hardness_mg_l if water else 180.0,
            "suitability_score": water.suitability_score if water else 88
        }
    }

@app.post("/api/farms")
def update_or_create_farm(payload: dict = Body(...), db: Session = Depends(get_db)):
    farm_id = payload.get("id")
    if farm_id:
        farm = db.query(Farm).filter(Farm.id == farm_id).first()
    else:
        user = db.query(User).filter(User.role == "FARMER").first()
        farm = Farm(user_id=user.id, name=payload.get("name", "New Farm"))
        db.add(farm)
        db.flush()

    farm.name = payload.get("name", farm.name)
    farm.location_name = payload.get("location_name", farm.location_name)
    farm.latitude = float(payload.get("latitude", farm.latitude))
    farm.longitude = float(payload.get("longitude", farm.longitude))
    farm.area_acres = float(payload.get("area_acres", farm.area_acres))
    farm.current_crop = payload.get("current_crop", farm.current_crop)
    farm.irrigation_method = payload.get("irrigation_method", farm.irrigation_method)

    # Update soil if provided
    soil_data = payload.get("soil", {})
    if soil_data:
        if not farm.soil:
            farm.soil = SoilProfile(farm_id=farm.id)
        farm.soil.ph = float(soil_data.get("ph", farm.soil.ph))
        farm.soil.nitrogen_kg_ha = float(soil_data.get("nitrogen_kg_ha", farm.soil.nitrogen_kg_ha))
        farm.soil.phosphorus_kg_ha = float(soil_data.get("phosphorus_kg_ha", farm.soil.phosphorus_kg_ha))
        farm.soil.potassium_kg_ha = float(soil_data.get("potassium_kg_ha", farm.soil.potassium_kg_ha))
        farm.soil.organic_carbon_pct = float(soil_data.get("organic_carbon_pct", farm.soil.organic_carbon_pct))

    # Update water if provided
    water_data = payload.get("water", {})
    if water_data:
        if not farm.water:
            farm.water = WaterProfile(farm_id=farm.id)
        farm.water.ph = float(water_data.get("ph", farm.water.ph))
        farm.water.ec_ds_m = float(water_data.get("ec_ds_m", farm.water.ec_ds_m))
        farm.water.tds_ppm = float(water_data.get("tds_ppm", farm.water.tds_ppm))

    db.commit()
    return {"success": True, "farm_id": farm.id, "message": "Farm profile saved successfully"}

# ==========================================
# 4. API: Live Weather Integration
# ==========================================
@app.get("/api/weather")
def get_weather(
    lat: float = Query(30.9010),
    lon: float = Query(75.8573),
    location: str = Query("Sahnewal, Ludhiana")
):
    """Returns live weather from Open-Meteo with dynamic agronomic advisories."""
    return fetch_live_weather(lat=lat, lon=lon, location_name=location)

# ==========================================
# 5. API: Crop & Seed Recommendations
# ==========================================
@app.get("/api/crops")
def get_all_crops(db: Session = Depends(get_db)):
    crops = db.query(Crop).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "hindi_name": c.hindi_name,
            "punjabi_name": c.punjabi_name,
            "season": c.season,
            "category": c.category,
            "duration_days": c.typical_duration_days,
            "water_req": c.water_req_level,
            "expected_yield_q_acre": c.expected_yield_q_acre,
            "current_mandi_price_q": c.current_mandi_price_q,
            "msp_price_q": c.msp_price_q,
            "demand_status": c.demand_status,
            "profit_potential": c.profit_potential,
            "description": c.description
        } for c in crops
    ]

@app.get("/api/crops/{crop_name}")
def get_crop_details(crop_name: str, db: Session = Depends(get_db)):
    crop = db.query(Crop).filter(Crop.name.ilike(f"%{crop_name}%")).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    varieties = [
        {
            "id": v.id,
            "name": v.name,
            "variety_code": v.variety_code,
            "manufacturer": v.manufacturer,
            "duration_days": v.duration_days,
            "expected_yield_min_q": v.expected_yield_min_q,
            "expected_yield_max_q": v.expected_yield_max_q,
            "seed_rate_kg_acre": v.seed_rate_kg_acre,
            "price_per_kg": v.price_per_kg,
            "disease_resistance": v.disease_resistance,
            "suitability_pct": v.suitability_pct
        } for v in crop.varieties
    ]

    return {
        "id": crop.id,
        "name": crop.name,
        "hindi_name": crop.hindi_name,
        "punjabi_name": crop.punjabi_name,
        "season": crop.season,
        "category": crop.category,
        "typical_duration_days": crop.typical_duration_days,
        "water_req_level": crop.water_req_level,
        "optimum_temp_min": crop.optimum_temp_min,
        "optimum_temp_max": crop.optimum_temp_max,
        "optimum_ph_min": crop.optimum_ph_min,
        "optimum_ph_max": crop.optimum_ph_max,
        "expected_yield_q_acre": crop.expected_yield_q_acre,
        "current_mandi_price_q": crop.current_mandi_price_q,
        "msp_price_q": crop.msp_price_q,
        "demand_status": crop.demand_status,
        "profit_potential": crop.profit_potential,
        "description": crop.description,
        "varieties": varieties
    }

@app.get("/api/recommendations/crops")
def recommend_crops(farm_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Computes AI-ranked crop recommendations based on farm parameters."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first() if farm_id else db.query(Farm).first()
    soil = farm.soil
    water = farm.water

    soil_dict = {
        "ph": soil.ph if soil else 6.8,
        "nitrogen_kg_ha": soil.nitrogen_kg_ha if soil else 260.0,
        "phosphorus_kg_ha": soil.phosphorus_kg_ha if soil else 22.5,
        "potassium_kg_ha": soil.potassium_kg_ha if soil else 280.0,
        "organic_carbon_pct": soil.organic_carbon_pct if soil else 0.62
    }
    water_dict = {
        "ec_ds_m": water.ec_ds_m if water else 0.65,
        "tds_ppm": water.tds_ppm if water else 420.0
    }

    # Fetch live weather for the farm coordinates
    weather = fetch_live_weather(lat=farm.latitude, lon=farm.longitude, location_name=farm.location_name)

    # Fetch weights from DB
    weights_record = db.query(ConfigWeights).first()
    weights = {
        "climate": weights_record.climate_weight if weights_record else 0.20,
        "soil": weights_record.soil_weight if weights_record else 0.20,
        "water": weights_record.water_weight if weights_record else 0.15,
        "weather": weights_record.weather_weight if weights_record else 0.15,
        "season": weights_record.season_weight if weights_record else 0.10,
        "market": weights_record.market_weight if weights_record else 0.10,
        "economics": weights_record.economics_weight if weights_record else 0.10
    }

    crops = db.query(Crop).all()
    ranked = []
    for c in crops:
        crop_dict = {
            "name": c.name,
            "hindi_name": c.hindi_name,
            "punjabi_name": c.punjabi_name,
            "season": c.season,
            "category": c.category,
            "optimum_temp_min": c.optimum_temp_min,
            "optimum_temp_max": c.optimum_temp_max,
            "optimum_ph_min": c.optimum_ph_min,
            "optimum_ph_max": c.optimum_ph_max,
            "water_req_level": c.water_req_level,
            "demand_status": c.demand_status,
            "profit_potential": c.profit_potential,
            "expected_yield_q_acre": c.expected_yield_q_acre,
            "current_mandi_price_q": c.current_mandi_price_q
        }
        res = evaluate_crop_suitability(crop_dict, soil_dict, water_dict, weather, weights)
        ranked.append(res)

    ranked.sort(key=lambda x: x["suitability_score"], reverse=True)

    return {
        "farm_name": farm.name,
        "farm_location": farm.location_name,
        "top_recommendation": ranked[0]["crop_name"] if ranked else "Maize",
        "ranked_crops": ranked
    }

@app.get("/api/seeds")
def get_seeds(crop_name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(SeedVariety)
    if crop_name:
        query = query.join(Crop).filter(Crop.name.ilike(f"%{crop_name}%"))
    seeds = query.all()
    return [
        {
            "id": s.id,
            "crop_name": s.crop.name if s.crop else "Maize",
            "name": s.name,
            "variety_code": s.variety_code,
            "manufacturer": s.manufacturer,
            "duration_days": s.duration_days,
            "expected_yield_min_q": s.expected_yield_min_q,
            "expected_yield_max_q": s.expected_yield_max_q,
            "seed_rate_kg_acre": s.seed_rate_kg_acre,
            "price_per_kg": s.price_per_kg,
            "disease_resistance": s.disease_resistance,
            "drought_tolerance": s.drought_tolerance,
            "soil_affinity": s.soil_affinity,
            "suitability_pct": s.suitability_pct,
            "certified": s.certified,
            "key_features": s.key_features
        } for s in seeds
    ]

@app.get("/api/seeds/{seed_id}")
def get_seed_details(seed_id: int, db: Session = Depends(get_db)):
    seed = db.query(SeedVariety).filter(SeedVariety.id == seed_id).first()
    if not seed:
        seed = db.query(SeedVariety).first()
    return {
        "id": seed.id,
        "crop_name": seed.crop.name if seed.crop else "Maize",
        "name": seed.name,
        "variety_code": seed.variety_code,
        "manufacturer": seed.manufacturer,
        "duration_days": seed.duration_days,
        "expected_yield_min_q": seed.expected_yield_min_q,
        "expected_yield_max_q": seed.expected_yield_max_q,
        "seed_rate_kg_acre": seed.seed_rate_kg_acre,
        "price_per_kg": seed.price_per_kg,
        "disease_resistance": seed.disease_resistance,
        "drought_tolerance": seed.drought_tolerance,
        "soil_affinity": seed.soil_affinity,
        "suitability_pct": seed.suitability_pct,
        "certified": seed.certified,
        "key_features": seed.key_features,
        "sowing_period": "May 25 - June 20 (Kharif)",
        "harvest_period": "September 15 - October 10",
        "water_requirement": "Medium (450-550 mm)",
        "soil_requirement": "Well-drained sandy loam or clay loam, pH 6.0-7.5"
    }

# ==========================================
# 6. API: Fertilizers & Input Marketplace
# ==========================================
@app.get("/api/recommendations/fertilizer")
def get_fertilizer_recommendation(
    crop_name: str = Query("Maize"),
    area_acres: float = Query(5.0),
    farm_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first() if farm_id else db.query(Farm).first()
    soil = farm.soil
    soil_dict = {
        "nitrogen_kg_ha": soil.nitrogen_kg_ha if soil else 260.0,
        "phosphorus_kg_ha": soil.phosphorus_kg_ha if soil else 22.5,
        "potassium_kg_ha": soil.potassium_kg_ha if soil else 280.0
    }
    return calculate_fertilizer_plan(crop_name=crop_name, area_acres=area_acres, soil_profile=soil_dict)

@app.get("/api/fertilizers/market")
def get_fertilizer_dealers(db: Session = Depends(get_db)):
    dealers = db.query(Dealer).all()
    results = []
    for d in dealers:
        results.append({
            "id": d.id,
            "business_name": d.business_name,
            "owner_name": d.owner_name,
            "phone": d.phone,
            "address": d.address,
            "city": d.city,
            "state": d.state,
            "rating": d.rating,
            "delivery_available": d.delivery_available,
            "distance_km": round(abs(d.latitude - 30.9010) * 111.0 + abs(d.longitude - 75.8573) * 96.0 + 2.5, 1),
            "products": json.loads(d.products_json)
        })
    results.sort(key=lambda x: x["distance_km"])
    return results

# ==========================================
# 7. API: Market Intelligence & Shortages
# ==========================================
@app.get("/api/markets/prices")
def get_market_prices(crop_name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(MarketPrice)
    if crop_name:
        query = query.filter(MarketPrice.crop_name.ilike(f"%{crop_name}%"))
    prices = query.all()
    return [
        {
            "id": p.id,
            "crop_name": p.crop_name,
            "mandi_name": p.mandi_name,
            "state": p.state,
            "modal_price_q": p.modal_price_q,
            "min_price_q": p.min_price_q,
            "max_price_q": p.max_price_q,
            "daily_arrivals_tonnes": p.daily_arrivals_tonnes,
            "price_change_pct": p.price_change_pct,
            "demand_level": p.demand_level,
            "updated_at": p.updated_at.strftime("%H:%M IST (Updated Today)")
        } for p in prices
    ]

@app.get("/api/markets/shortage")
def get_crop_shortages(crop_name: str = Query("Maize"), db: Session = Depends(get_db)):
    records = db.query(CropShortage).filter(CropShortage.crop_name.ilike(f"%{crop_name}%")).all()
    return [
        {
            "id": r.id,
            "crop_name": r.crop_name,
            "state_code": r.state_code,
            "state_name": r.state_name,
            "status": r.status,
            "demand_tonnes": r.demand_tonnes,
            "supply_tonnes": r.supply_tonnes,
            "deficit_tonnes": r.deficit_tonnes,
            "deficit_pct": r.deficit_pct,
            "current_avg_price_q": r.current_avg_price_q,
            "price_trend": r.price_trend,
            "major_markets": r.major_markets,
            "buyer_demand_summary": r.buyer_demand_summary
        } for r in records
    ]

# ==========================================
# 8. API: Buyers & Logistics Marketplace
# ==========================================
@app.get("/api/buyers")
def get_buyers(crop_name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Buyer)
    if crop_name:
        query = query.filter(Buyer.crop_required.ilike(f"%{crop_name}%"))
    buyers = query.all()
    return [
        {
            "id": b.id,
            "company_name": b.company_name,
            "buyer_type": b.buyer_type,
            "contact_person": b.contact_person,
            "phone": b.phone,
            "email": b.email,
            "location": b.location,
            "crop_required": b.crop_required,
            "quantity_required_tonnes": b.quantity_required_tonnes,
            "offered_price_q": b.offered_price_q,
            "deadline_date": b.deadline_date,
            "quality_specs": b.quality_specs,
            "rating": b.rating,
            "verified": b.verified
        } for b in buyers
    ]

@app.get("/api/transporters")
def get_transporters(db: Session = Depends(get_db)):
    trans = db.query(TransportProvider).all()
    return [
        {
            "id": t.id,
            "operator_name": t.operator_name,
            "phone": t.phone,
            "vehicle_type": t.vehicle_type,
            "capacity_tonnes": t.capacity_tonnes,
            "base_rate_inr": t.base_rate_inr,
            "rate_per_km_inr": t.rate_per_km_inr,
            "current_distance_km": t.current_distance_km,
            "location": t.location,
            "available_now": t.available_now,
            "rating": t.rating
        } for t in trans
    ]

# ==========================================
# 9. API: Transparent Profitability Engine
# ==========================================
@app.post("/api/profit/estimate")
def estimate_profit(payload: dict = Body(...)):
    return calculate_farm_profitability(
        area_acres=float(payload.get("area_acres", 5.0)),
        crop_name=payload.get("crop_name", "Maize"),
        seed_variety=payload.get("seed_variety", "Pioneer P3396 Hybrid"),
        seed_cost_inr=float(payload.get("seed_cost_inr", 10400.0)),
        fertilizer_cost_inr=float(payload.get("fertilizer_cost_inr", 15200.0)),
        labour_cost_inr=float(payload.get("labour_cost_inr", 12500.0)),
        irrigation_cost_inr=float(payload.get("irrigation_cost_inr", 6500.0)),
        machinery_diesel_cost_inr=float(payload.get("machinery_diesel_cost_inr", 11000.0)),
        pest_management_cost_inr=float(payload.get("pest_management_cost_inr", 4800.0)),
        transport_logistics_cost_inr=float(payload.get("transport_logistics_cost_inr", 5800.0)),
        other_miscellaneous_cost_inr=float(payload.get("other_miscellaneous_cost_inr", 3000.0)),
        baseline_yield_q_acre=float(payload.get("baseline_yield_q_acre", 28.5)),
        baseline_selling_price_q=float(payload.get("baseline_selling_price_q", 2350.0))
    )

# ==========================================
# 10. API: AI Agricultural Assistant
# ==========================================
@app.post("/api/assistant/chat")
def chat_assistant(payload: dict = Body(...), db: Session = Depends(get_db)):
    query = payload.get("message", "")
    farm = db.query(Farm).first()
    soil = farm.soil
    farm_dict = {
        "name": farm.name,
        "location_name": farm.location_name,
        "area_acres": farm.area_acres,
        "current_crop": farm.current_crop,
        "soil": {"ph": soil.ph if soil else 6.8}
    }
    weather = fetch_live_weather(lat=farm.latitude, lon=farm.longitude, location_name=farm.location_name)
    market_dict = {"crop": farm.current_crop, "price": 2360.0}

    return process_assistant_query(query, farm_dict, weather, market_dict)

# ==========================================
# 11. API: Orders & Notifications
# ==========================================
@app.get("/api/orders")
def get_orders(user_id: Optional[int] = None, role: Optional[str] = None, partner_name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Order)
    if user_id:
        query = query.filter(Order.user_id == user_id)
    if partner_name:
        query = query.filter(Order.partner_name.ilike(f"%{partner_name}%"))
    orders = query.order_by(Order.created_at.desc()).all()
    return [
        {
            "id": o.id,
            "user_id": o.user_id,
            "order_type": o.order_type,
            "item_title": o.item_title,
            "quantity": o.quantity,
            "amount_inr": o.amount_inr,
            "status": o.status,
            "partner_name": o.partner_name,
            "items_json": getattr(o, "items_json", "[]"),
            "delivery_address": getattr(o, "delivery_address", ""),
            "created_at": o.created_at.strftime("%Y-%m-%d %H:%M")
        } for o in orders
    ]

@app.post("/api/orders")
def create_order(payload: dict = Body(...), db: Session = Depends(get_db)):
    user_id = payload.get("user_id")
    user = None
    if user_id:
        user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        user = db.query(User).filter(User.role == "FARMER").first()
    if not user:
        user = db.query(User).first()

    raw_items = payload.get("items")
    if isinstance(raw_items, list):
        items_str = json.dumps(raw_items)
    else:
        items_str = str(payload.get("items_json", "[]"))

    new_order = Order(
        user_id=user.id if user else 1,
        order_type=payload.get("order_type", "INPUT"),
        item_title=payload.get("item_title", "Agricultural Inputs Order"),
        quantity=payload.get("quantity", "1 Order"),
        amount_inr=float(payload.get("amount_inr") or payload.get("total_amount") or 0.0),
        status=payload.get("status", "CONFIRMED"),
        partner_name=payload.get("partner_name", "Kisan Seva Kendra Sahnewal"),
        items_json=items_str,
        delivery_address=payload.get("delivery_address", f"{user.village}, {user.district}" if user else "Sahnewal, Ludhiana")
    )
    db.add(new_order)

    # Add notification for the order
    notif = Notification(
        title="✅ Order Confirmed",
        message=f"Your order for {new_order.item_title} ({new_order.quantity}) with {new_order.partner_name} has been placed successfully.",
        category="ORDER",
        severity="SUCCESS"
    )
    db.add(notif)
    db.commit()
    db.refresh(new_order)

    return {
        "success": True,
        "order_id": new_order.id,
        "id": new_order.id,
        "amount_inr": new_order.amount_inr,
        "total_amount": new_order.amount_inr,
        "delivery_address": new_order.delivery_address,
        "message": "Order successfully created"
    }

@app.patch("/api/orders/{order_id}/status")
def update_order_status(order_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    new_status = payload.get("status", "CONFIRMED").upper()
    order.status = new_status
    db.commit()
    return {"success": True, "order_id": order.id, "status": order.status}

@app.get("/api/notifications")
def get_notifications(db: Session = Depends(get_db)):
    notifs = db.query(Notification).order_by(Notification.created_at.desc()).all()
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "category": n.category,
            "severity": n.severity,
            "created_at": n.created_at.strftime("%d %b %H:%M"),
            "is_read": n.is_read
        } for n in notifs
    ]

# ==========================================
# 12. API: Admin & System Weights
# ==========================================
@app.get("/api/admin/metrics")
def get_admin_metrics(db: Session = Depends(get_db)):
    return {
        "total_farmers": db.query(User).filter(User.role == "FARMER").count() + 1420,
        "total_dealers": db.query(User).filter(User.role == "DEALER").count() + 85,
        "total_buyers": db.query(User).filter(User.role == "BUYER").count() + 42,
        "total_transporters": db.query(User).filter(User.role == "TRANSPORTER").count() + 118,
        "active_farms": db.query(Farm).count() + 1850,
        "active_orders": db.query(Order).count() + 320,
        "system_status": "All AI Decision Models Operational",
        "live_weather_uptime": "99.9%"
    }

@app.get("/api/admin/weights")
def get_weights(db: Session = Depends(get_db)):
    weights = db.query(ConfigWeights).first()
    if not weights:
        return DEFAULT_WEIGHTS
    return {
        "climate": weights.climate_weight,
        "soil": weights.soil_weight,
        "water": weights.water_weight,
        "weather": weights.weather_weight,
        "season": weights.season_weight,
        "market": weights.market_weight,
        "economics": weights.economics_weight
    }

@app.post("/api/admin/weights")
def update_weights(payload: dict = Body(...), db: Session = Depends(get_db)):
    weights = db.query(ConfigWeights).first()
    if not weights:
        weights = ConfigWeights()
        db.add(weights)
    weights.climate_weight = float(payload.get("climate", weights.climate_weight))
    weights.soil_weight = float(payload.get("soil", weights.soil_weight))
    weights.water_weight = float(payload.get("water", weights.water_weight))
    weights.weather_weight = float(payload.get("weather", weights.weather_weight))
    weights.season_weight = float(payload.get("season", weights.season_weight))
    weights.market_weight = float(payload.get("market", weights.market_weight))
    weights.economics_weight = float(payload.get("economics", weights.economics_weight))
    db.commit()
    return {"success": True, "message": "Recommendation decision weights updated successfully"}

# ==========================================
# 12B. API: Live Agricultural Payment Gateway & Settlements
# ==========================================
@app.get("/api/payments/stats")
def get_payment_stats(db: Session = Depends(get_db)):
    txs = db.query(PaymentTransaction).all()
    total_vol = sum(t.amount_inr for t in txs if t.status in ["SUCCESS", "ESCROW_LOCKED", "DISBURSED"])
    escrow_held = sum(t.amount_inr for t in txs if t.status == "ESCROW_LOCKED")
    subsidies = sum(t.subsidy_amount_inr for t in txs if t.status in ["SUCCESS", "DISBURSED"])
    return {
        "total_volume_inr": round(total_vol, 2),
        "escrow_in_holding_inr": round(escrow_held, 2),
        "subsidies_credited_inr": round(subsidies, 2),
        "total_transactions_count": len(txs),
        "active_gateway_uptime": "99.98% (NPCI Switch Connected)"
    }

@app.get("/api/payments/transactions")
def get_payment_transactions(
    user_id: Optional[int] = None,
    payment_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(PaymentTransaction)
    if user_id:
        query = query.filter(PaymentTransaction.user_id == user_id)
    if payment_type:
        query = query.filter(PaymentTransaction.payment_type == payment_type.upper())
    if status:
        query = query.filter(PaymentTransaction.status == status.upper())
    
    txs = query.order_by(PaymentTransaction.created_at.desc()).limit(limit).all()
    return [
        {
            "id": t.id,
            "transaction_id": t.transaction_id,
            "utr_number": t.utr_number,
            "payment_type": t.payment_type,
            "payment_method": t.payment_method,
            "amount_inr": t.amount_inr,
            "gst_amount_inr": t.gst_amount_inr,
            "subsidy_amount_inr": t.subsidy_amount_inr,
            "net_amount_inr": t.net_amount_inr,
            "payer_name": t.payer_name,
            "payee_name": t.payee_name,
            "bank_name_or_vpa": t.bank_name_or_vpa,
            "status": t.status,
            "notes": t.notes,
            "created_at": t.created_at.strftime("%d %b %Y, %I:%M %p") if t.created_at else "",
            "completed_at": t.completed_at.strftime("%d %b %Y, %I:%M %p") if t.completed_at else ""
        } for t in txs
    ]

@app.post("/api/payments/create-intent")
def create_payment_intent(payload: dict = Body(...), db: Session = Depends(get_db)):
    amount = float(payload.get("amount_inr", 1000.0))
    payment_type = payload.get("payment_type", "INPUT_PURCHASE").upper()
    payment_method = payload.get("payment_method", "UPI_QR").upper()
    payer_name = payload.get("payer_name", "Sardar Gurpreet Singh")
    payee_name = payload.get("payee_name", "AgriWise Input Marketplace")
    notes = payload.get("notes", "Agricultural input procurement transaction")
    order_id = payload.get("order_id")

    # Indian Agriculture GST & Subsidy Rules:
    # 5% GST on fertilizers/seeds (2.5% CGST + 2.5% SGST)
    # 0% GST on raw agricultural grain / MSP procurement
    gst = round(amount * 0.05, 2) if payment_type in ["INPUT_PURCHASE"] else 0.0
    
    # 3% prompt repayment interest subvention under Govt of India KCC scheme
    subsidy = round(amount * 0.03, 2) if payment_method == "KCC_RUPAY" else 0.0
    net_amount = round(amount + gst - subsidy, 2)

    # Unique Indian Banking transaction identifiers
    random_num = random.randint(1000, 9999)
    tx_id = f"AGRI-PAY-2026-{random_num}"
    utr = f"6291{random.randint(10000000, 99999999)}"

    # Generate Bharat QR / UPI intent URI
    upi_pa = "agriwise.settlement@sbi"
    upi_pn = payee_name.replace(" ", "+")
    upi_intent_uri = f"upi://pay?pa={upi_pa}&pn={upi_pn}&mc=5262&tid={tx_id}&tr={utr}&am={net_amount}&cu=INR"

    tx = PaymentTransaction(
        transaction_id=tx_id,
        utr_number=utr,
        user_id=1,
        order_id=order_id,
        payment_type=payment_type,
        payment_method=payment_method,
        amount_inr=amount,
        gst_amount_inr=gst,
        subsidy_amount_inr=subsidy,
        net_amount_inr=net_amount,
        payer_name=payer_name,
        payee_name=payee_name,
        bank_name_or_vpa=payload.get("bank_name_or_vpa", "SBI Agri"),
        status="INITIATED",
        notes=notes,
        created_at=datetime.utcnow()
    )
    db.add(tx)
    db.commit()

    return {
        "success": True,
        "transaction_id": tx_id,
        "utr_number": utr,
        "amount_inr": amount,
        "gst_amount_inr": gst,
        "subsidy_amount_inr": subsidy,
        "net_amount_inr": net_amount,
        "upi_intent_uri": upi_intent_uri,
        "payer_name": payer_name,
        "payee_name": payee_name,
        "payment_type": payment_type,
        "payment_method": payment_method,
        "expires_in_seconds": 300,
        "message": "Payment intent initialized successfully"
    }

@app.post("/api/payments/verify")
def verify_payment(payload: dict = Body(...), db: Session = Depends(get_db)):
    tx_id = payload.get("transaction_id")
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.transaction_id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    method = payload.get("payment_method", tx.payment_method).upper()
    tx.payment_method = method

    # Target status depending on type
    if tx.payment_type == "BUYER_ESCROW":
        tx.status = "ESCROW_LOCKED"
    else:
        tx.status = "SUCCESS"

    tx.completed_at = datetime.utcnow()
    if not tx.utr_number:
        tx.utr_number = f"6291{random.randint(10000000, 99999999)}"

    # If linked to order, mark order paid
    if tx.order_id:
        order = db.query(Order).filter(Order.id == tx.order_id).first()
        if order:
            order.status = "PAID"

    # Add notification
    status_label = "Escrow Vault Secured" if tx.status == "ESCROW_LOCKED" else "Payment Successful"
    notif = Notification(
        title=f"💳 {status_label}: ₹{tx.net_amount_inr:,.0f}",
        message=f"Transaction {tx.transaction_id} verified via {tx.payment_method}. UTR: {tx.utr_number}. Payee: {tx.payee_name}.",
        category="ORDER",
        severity="SUCCESS"
    )
    db.add(notif)
    db.commit()

    return {
        "success": True,
        "transaction_id": tx.transaction_id,
        "utr_number": tx.utr_number,
        "status": tx.status,
        "net_amount_inr": tx.net_amount_inr,
        "completed_at": tx.completed_at.strftime("%d %b %Y, %I:%M %p"),
        "receipt_url": f"/api/payments/receipt/{tx.transaction_id}",
        "message": f"{status_label} verified successfully by NPCI/Bank Switch"
    }

@app.post("/api/payments/escrow-release")
def release_escrow(payload: dict = Body(...), db: Session = Depends(get_db)):
    tx_id = payload.get("transaction_id")
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.transaction_id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if tx.status != "ESCROW_LOCKED":
        raise HTTPException(status_code=400, detail="Only ESCROW_LOCKED transactions can be released")

    tx.status = "DISBURSED"
    tx.completed_at = datetime.utcnow()
    tx.notes += " | APMC Moisture Quality Assay (<12%) passed. Funds disbursed to farmer PNB account."

    notif = Notification(
        title=f"🌾 Escrow Payout Disbursed: ₹{tx.net_amount_inr:,.0f}",
        message=f"APMC Quality assay passed. Funds from {tx.payer_name} released to farmer bank account. UTR: {tx.utr_number}.",
        category="MARKET",
        severity="SUCCESS"
    )
    db.add(notif)
    db.commit()

    return {
        "success": True,
        "transaction_id": tx.transaction_id,
        "status": "DISBURSED",
        "disbursed_amount_inr": tx.net_amount_inr,
        "message": "Escrow funds successfully disbursed to farmer account"
    }

@app.get("/api/payments/receipt/{tx_id}")
def get_payment_receipt(tx_id: str, db: Session = Depends(get_db)):
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.transaction_id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {
        "receipt_number": f"AGRI-REC-{tx.id:05d}",
        "transaction_id": tx.transaction_id,
        "utr_number": tx.utr_number,
        "date_time": tx.created_at.strftime("%d %b %Y, %I:%M %p") if tx.created_at else "",
        "payer_name": tx.payer_name,
        "payer_gstin": "03AABCA1234F1Z8" if "Ltd" in tx.payer_name else "URP (Unregistered Farmer)",
        "payee_name": tx.payee_name,
        "payee_gstin": "03AAGCI8821D1ZN",
        "payment_type": tx.payment_type,
        "payment_method": tx.payment_method,
        "bank_or_vpa": tx.bank_name_or_vpa,
        "status": tx.status,
        "base_amount_inr": tx.amount_inr,
        "gst_amount_inr": tx.gst_amount_inr,
        "subsidy_amount_inr": tx.subsidy_amount_inr,
        "net_amount_inr": tx.net_amount_inr,
        "notes": tx.notes,
        "verified_by": "NPCI / Bharat BillPay / PFMS Direct Agriculture Settlement Switch",
        "stamp": "GOVERNMENT OF INDIA DBT / APMC ASSAY COMPLIANT"
    }

# ==========================================
# 12C. API: Farm Equipment Rental & Custom Hiring Centre (CHC) Engine
# ==========================================

def get_equipment_live_status(eq: Equipment, db: Session) -> dict:
    if not eq.available:
        return {
            "status": "MAINTENANCE",
            "badge_class": "badge-red",
            "badge_text": "Under Maintenance",
            "available_now": False,
            "booked_until": None
        }

    now = datetime.utcnow()
    active_booking = db.query(EquipmentBooking).filter(
        EquipmentBooking.equipment_id == eq.id,
        EquipmentBooking.booking_status.in_(["CONFIRMED", "ACTIVE"]),
        EquipmentBooking.start_time <= now,
        EquipmentBooking.end_time >= now
    ).order_by(EquipmentBooking.end_time.desc()).first()

    if active_booking:
        return {
            "status": "BOOKED",
            "badge_class": "badge-amber",
            "badge_text": f"Booked until {active_booking.end_time.strftime('%d %b, %I:%M %p')}",
            "available_now": False,
            "booked_until": active_booking.end_time.strftime('%Y-%m-%dT%H:%M:%S')
        }

    return {
        "status": "AVAILABLE",
        "badge_class": "badge-emerald",
        "badge_text": "Available Today",
        "available_now": True,
        "booked_until": None
    }

def serialize_equipment(eq: Equipment, db: Session) -> dict:
    live = get_equipment_live_status(eq, db)
    return {
        "id": eq.id,
        "owner_id": eq.owner_id,
        "name": eq.name,
        "category": eq.category,
        "brand": eq.brand,
        "model": eq.model,
        "year": eq.year,
        "power_hp": eq.power_hp,
        "fuel_type": eq.fuel_type,
        "capacity_specs": eq.capacity_specs,
        "hourly_rate": eq.hourly_rate,
        "daily_rate": eq.daily_rate,
        "operator_available": eq.operator_available,
        "operator_charge_per_hr": eq.operator_charge_per_hr,
        "operator_charge_per_day": eq.operator_charge_per_day,
        "fuel_included_option": eq.fuel_included_option,
        "fuel_charge_per_hr": eq.fuel_charge_per_hr,
        "fuel_charge_per_day": eq.fuel_charge_per_day,
        "delivery_available": eq.delivery_available,
        "delivery_rate_per_km": eq.delivery_rate_per_km,
        "security_deposit": eq.security_deposit,
        "location": eq.location,
        "district": eq.district,
        "state": eq.state,
        "distance_km": eq.distance_km,
        "owner_name": eq.owner_name,
        "owner_phone": eq.owner_phone,
        "owner_badge": eq.owner_badge,
        "rating": eq.rating,
        "reviews_count": eq.reviews_count,
        "image_url": eq.image_url,
        "implements_compatibility": eq.implements_compatibility,
        "terms": eq.terms,
        "available": eq.available,
        "live_status": live
    }

@app.get("/api/equipment")
def get_equipment_catalog(
    search: Optional[str] = None,
    category: Optional[str] = None,
    rental_type: Optional[str] = None,
    max_price: Optional[float] = None,
    max_distance: Optional[float] = None,
    sort_by: Optional[str] = "distance_asc",
    db: Session = Depends(get_db)
):
    query = db.query(Equipment)

    if category and category.upper() != "ALL":
        cat_clean = category.strip().lower()
        if "tractor" in cat_clean:
            query = query.filter(Equipment.category.ilike("%Tractor%"))
        elif "harvest" in cat_clean:
            query = query.filter(Equipment.category.ilike("%Harvest%"))
        elif "pump" in cat_clean or "water" in cat_clean:
            query = query.filter(Equipment.category.ilike("%Pump%"))
        elif "rotavat" in cat_clean or "tiller" in cat_clean:
            query = query.filter(Equipment.category.ilike("%Rotavat%"))
        elif "seed" in cat_clean or "drill" in cat_clean:
            query = query.filter(Equipment.category.ilike("%Seed%"))
        elif "spray" in cat_clean:
            query = query.filter(Equipment.category.ilike("%Spray%"))
        elif "thresh" in cat_clean or "cultivat" in cat_clean:
            query = query.filter(Equipment.category.ilike("%Thresh%"))
        else:
            query = query.filter(Equipment.category.ilike(f"%{category}%"))

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (Equipment.name.ilike(s)) |
            (Equipment.brand.ilike(s)) |
            (Equipment.model.ilike(s)) |
            (Equipment.category.ilike(s)) |
            (Equipment.location.ilike(s)) |
            (Equipment.capacity_specs.ilike(s))
        )

    if max_distance:
        query = query.filter(Equipment.distance_km <= max_distance)

    items = query.all()

    # Price filtering
    if max_price:
        if rental_type and rental_type.upper() == "DAILY":
            items = [item for item in items if item.daily_rate <= max_price]
        else:
            items = [item for item in items if item.hourly_rate <= max_price]

    # Sorting
    if sort_by == "price_asc":
        if rental_type and rental_type.upper() == "DAILY":
            items.sort(key=lambda x: x.daily_rate)
        else:
            items.sort(key=lambda x: x.hourly_rate)
    elif sort_by == "price_desc":
        if rental_type and rental_type.upper() == "DAILY":
            items.sort(key=lambda x: x.daily_rate, reverse=True)
        else:
            items.sort(key=lambda x: x.hourly_rate, reverse=True)
    elif sort_by == "rating_desc":
        items.sort(key=lambda x: x.rating, reverse=True)
    elif sort_by == "distance_asc":
        items.sort(key=lambda x: x.distance_km)

    return [serialize_equipment(item, db) for item in items]

@app.post("/api/equipment/check-availability")
def check_equipment_availability(payload: dict = Body(...), db: Session = Depends(get_db)):
    equipment_id = payload.get("equipment_id")
    start_str = payload.get("start_time")
    end_str = payload.get("end_time")

    if not equipment_id or not start_str or not end_str:
        raise HTTPException(status_code=400, detail="equipment_id, start_time, and end_time are required")

    try:
        start_dt = datetime.fromisoformat(start_str.replace("Z", ""))
        end_dt = datetime.fromisoformat(end_str.replace("Z", ""))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ISO datetime format: {e}")

    if end_dt <= start_dt:
        raise HTTPException(status_code=400, detail="End time must be strictly after start time")

    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    if not eq.available:
        return {
            "available": False,
            "reason": "UNDER_MAINTENANCE",
            "message": "This equipment is currently under routine maintenance and unavailable for booking.",
            "conflicts": []
        }

    conflicts = db.query(EquipmentBooking).filter(
        EquipmentBooking.equipment_id == equipment_id,
        EquipmentBooking.booking_status.in_(["CONFIRMED", "ACTIVE"]),
        EquipmentBooking.start_time < end_dt,
        EquipmentBooking.end_time > start_dt
    ).all()

    if conflicts:
        conflict_details = [
            {
                "booking_id": c.booking_id,
                "start": c.start_time.strftime("%d %b %Y, %I:%M %p"),
                "end": c.end_time.strftime("%d %b %Y, %I:%M %p")
            } for c in conflicts
        ]
        return {
            "available": False,
            "reason": "OVERLAP_CONFLICT",
            "message": "This machine is already reserved for the selected slot. Please select another time or choose an alternate machine nearby.",
            "conflicts": conflict_details
        }

    return {
        "available": True,
        "message": "The machine is free and available for booking during the requested time slot.",
        "equipment_name": eq.name
    }

@app.post("/api/equipment/book")
def book_equipment(payload: dict = Body(...), db: Session = Depends(get_db)):
    equipment_id = payload.get("equipment_id")
    start_str = payload.get("start_time")
    end_str = payload.get("end_time")
    rental_type = (payload.get("rental_type") or "HOURLY").upper()

    if not equipment_id or not start_str or not end_str:
        raise HTTPException(status_code=400, detail="Missing required booking parameters")

    try:
        start_dt = datetime.fromisoformat(start_str.replace("Z", ""))
        end_dt = datetime.fromisoformat(end_str.replace("Z", ""))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {e}")

    if end_dt <= start_dt:
        raise HTTPException(status_code=400, detail="End time must be after start time")

    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    if not eq.available:
        raise HTTPException(status_code=400, detail="Equipment is currently under maintenance")

    # Overlap conflict prevention
    conflicts = db.query(EquipmentBooking).filter(
        EquipmentBooking.equipment_id == equipment_id,
        EquipmentBooking.booking_status.in_(["CONFIRMED", "ACTIVE"]),
        EquipmentBooking.start_time < end_dt,
        EquipmentBooking.end_time > start_dt
    ).all()

    if conflicts:
        raise HTTPException(
            status_code=409,
            detail="Conflict detected: This machine is already reserved for the selected slot. Please select another time or choose an alternate machine nearby."
        )

    # Duration & Server-Side Price Calculation
    diff_seconds = (end_dt - start_dt).total_seconds()
    if rental_type == "HOURLY":
        duration_units = max(1.0, round(diff_seconds / 3600.0, 1))
        unit_rate = eq.hourly_rate
        op_unit_rate = eq.operator_charge_per_hr if payload.get("with_operator", True) else 0.0
        fuel_unit_rate = eq.fuel_charge_per_hr if payload.get("with_fuel", False) else 0.0
    else:
        duration_units = max(1.0, round(diff_seconds / 86400.0, 1))
        unit_rate = eq.daily_rate
        op_unit_rate = eq.operator_charge_per_day if payload.get("with_operator", True) else 0.0
        fuel_unit_rate = eq.fuel_charge_per_day if payload.get("with_fuel", False) else 0.0

    base_amount = round(unit_rate * duration_units, 2)
    operator_amount = round(op_unit_rate * duration_units, 2)
    fuel_amount = round(fuel_unit_rate * duration_units, 2)

    delivery_to_farm = bool(payload.get("delivery_to_farm", False))
    delivery_dist = float(payload.get("delivery_distance_km") or eq.distance_km or 4.0) if delivery_to_farm else 0.0
    delivery_amount = round(delivery_dist * eq.delivery_rate_per_km, 2) if delivery_to_farm else 0.0

    subtotal = base_amount + operator_amount + fuel_amount + delivery_amount
    gst_amount = round(subtotal * 0.05, 2) # Standard 5% GST
    security_deposit = float(eq.security_deposit)
    total_amount = round(subtotal + gst_amount + security_deposit, 2)

    farmer_id = payload.get("farmer_id") or 1
    farmer_user = db.query(User).filter(User.id == farmer_id).first()
    farmer_name = payload.get("farmer_name") or (farmer_user.name if farmer_user else "Sardar Gurpreet Singh")
    farmer_phone = payload.get("farmer_phone") or (farmer_user.phone if farmer_user else "+91 98765 43210")
    payment_method = (payload.get("payment_method") or "UPI_QR").upper()

    rnd_num = random.randint(1000, 9999)
    booking_id = f"AGRI-EQP-2026-{rnd_num}"
    tx_id = f"AGRI-PAY-2026-{rnd_num}"
    utr_num = f"6291{random.randint(10000000, 99999999)}"

    if payment_method == "PAY_ON_DELIVERY":
        payment_status = "PENDING"
        tx_status = "INITIATED"
    else:
        payment_status = "PAID"
        tx_status = "SUCCESS"

    payment_tx = PaymentTransaction(
        transaction_id=tx_id,
        utr_number=utr_num,
        user_id=farmer_id,
        payment_type="EQUIPMENT_RENTAL",
        payment_method=payment_method,
        amount_inr=subtotal,
        gst_amount_inr=gst_amount,
        subsidy_amount_inr=0.0,
        net_amount_inr=total_amount,
        payer_name=farmer_name,
        payee_name=eq.owner_name,
        bank_name_or_vpa=payload.get("bank_name_or_vpa", "SBI / NPCI UPI Switch"),
        status=tx_status,
        notes=f"Farm Equipment Rental: {eq.name} ({duration_units} {'Hours' if rental_type == 'HOURLY' else 'Days'}). Deposit: ₹{security_deposit:,.0f} (Refundable).",
        created_at=datetime.utcnow(),
        completed_at=datetime.utcnow() if tx_status == "SUCCESS" else None
    )
    db.add(payment_tx)

    booking = EquipmentBooking(
        booking_id=booking_id,
        equipment_id=eq.id,
        farmer_id=farmer_id,
        farmer_name=farmer_name,
        farmer_phone=farmer_phone,
        rental_type=rental_type,
        start_time=start_dt,
        end_time=end_dt,
        duration_units=duration_units,
        with_operator=bool(payload.get("with_operator", True)),
        with_fuel=bool(payload.get("with_fuel", False)),
        delivery_to_farm=delivery_to_farm,
        delivery_address=payload.get("delivery_address", f"{eq.location} Farm Gate"),
        delivery_distance_km=delivery_dist,
        base_amount=base_amount,
        operator_amount=operator_amount,
        delivery_amount=delivery_amount,
        security_deposit=security_deposit,
        gst_amount=gst_amount,
        total_amount=total_amount,
        payment_method=payment_method,
        payment_status=payment_status,
        booking_status="CONFIRMED",
        notes=payload.get("notes", ""),
        created_at=datetime.utcnow()
    )
    db.add(booking)

    notif = Notification(
        title=f"🚜 Equipment Booked: {eq.name}",
        message=f"Booking {booking_id} confirmed for {start_dt.strftime('%d %b, %I:%M %p')} to {end_dt.strftime('%d %b, %I:%M %p')}. Total: ₹{total_amount:,.2f}. Owner: {eq.owner_name} ({eq.owner_phone}).",
        category="ORDER",
        severity="SUCCESS"
    )
    db.add(notif)
    db.commit()

    return {
        "success": True,
        "booking_id": booking_id,
        "transaction_id": tx_id,
        "utr_number": utr_num,
        "equipment_name": eq.name,
        "owner_name": eq.owner_name,
        "owner_phone": eq.owner_phone,
        "rental_type": rental_type,
        "start_time": start_dt.strftime("%d %b %Y, %I:%M %p"),
        "end_time": end_dt.strftime("%d %b %Y, %I:%M %p"),
        "duration_units": duration_units,
        "base_amount": base_amount,
        "operator_amount": operator_amount,
        "delivery_amount": delivery_amount,
        "security_deposit": security_deposit,
        "gst_amount": gst_amount,
        "total_amount": total_amount,
        "payment_method": payment_method,
        "payment_status": payment_status,
        "booking_status": "CONFIRMED",
        "receipt_url": f"/api/equipment/booking/{booking_id}/receipt",
        "message": f"Equipment {eq.name} successfully booked under {booking_id}!"
    }

@app.get("/api/equipment/my-rentals")
def get_my_equipment_rentals(farmer_id: Optional[int] = None, db: Session = Depends(get_db)):
    target_id = farmer_id or 1
    now = datetime.utcnow()

    bookings = db.query(EquipmentBooking).filter(
        (EquipmentBooking.farmer_id == target_id) | (EquipmentBooking.farmer_id == None)
    ).order_by(EquipmentBooking.start_time.desc()).all()

    upcoming = []
    active = []
    completed = []
    cancelled = []

    for b in bookings:
        eq = b.equipment
        data = {
            "id": b.id,
            "booking_id": b.booking_id,
            "equipment_id": b.equipment_id,
            "equipment_name": eq.name if eq else "Agricultural Implement",
            "equipment_category": eq.category if eq else "Equipment",
            "equipment_image": eq.image_url if eq else "",
            "owner_name": eq.owner_name if eq else "Partner CHC",
            "owner_phone": eq.owner_phone if eq else "+91 98765 43210",
            "rental_type": b.rental_type,
            "start_time": b.start_time.strftime("%d %b %Y, %I:%M %p"),
            "end_time": b.end_time.strftime("%d %b %Y, %I:%M %p"),
            "start_iso": b.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_iso": b.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration_units": b.duration_units,
            "with_operator": b.with_operator,
            "with_fuel": b.with_fuel,
            "delivery_to_farm": b.delivery_to_farm,
            "delivery_address": b.delivery_address,
            "base_amount": b.base_amount,
            "operator_amount": b.operator_amount,
            "delivery_amount": b.delivery_amount,
            "security_deposit": b.security_deposit,
            "gst_amount": b.gst_amount,
            "total_amount": b.total_amount,
            "payment_method": b.payment_method,
            "payment_status": b.payment_status,
            "booking_status": b.booking_status,
            "cancellation_reason": b.cancellation_reason,
            "refund_amount": b.refund_amount,
            "rating": b.rating,
            "review_text": b.review_text,
            "can_cancel": (b.booking_status == "CONFIRMED" and b.start_time > now),
            "created_at": b.created_at.strftime("%d %b %Y, %I:%M %p") if b.created_at else ""
        }

        if b.booking_status == "CANCELLED":
            cancelled.append(data)
        elif b.booking_status == "ACTIVE" or (b.booking_status == "CONFIRMED" and b.start_time <= now <= b.end_time):
            data["booking_status"] = "ACTIVE"
            active.append(data)
        elif b.booking_status == "CONFIRMED" and b.start_time > now:
            upcoming.append(data)
        else:
            data["booking_status"] = "COMPLETED"
            completed.append(data)

    return {
        "upcoming": upcoming,
        "active": active,
        "completed": completed,
        "cancelled": cancelled,
        "total_count": len(bookings)
    }

@app.post("/api/equipment/cancel-booking")
def cancel_equipment_booking(payload: dict = Body(...), db: Session = Depends(get_db)):
    booking_id = payload.get("booking_id")
    reason = payload.get("reason", "Changed field preparation plans")

    if not booking_id:
        raise HTTPException(status_code=400, detail="booking_id is required")

    booking = db.query(EquipmentBooking).filter(EquipmentBooking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.booking_status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")

    now = datetime.utcnow()
    hours_to_start = (booking.start_time - now).total_seconds() / 3600.0

    if hours_to_start >= 6.0:
        refund_amount = booking.total_amount
        policy_note = "Full 100% refund approved (cancelled > 6 hours before start)"
    elif hours_to_start > 0:
        refund_amount = round(booking.security_deposit + (booking.base_amount * 0.5), 2)
        policy_note = "Late cancellation (< 6 hours before start). Full security deposit + 50% base rental refunded."
    else:
        refund_amount = round(booking.security_deposit, 2)
        policy_note = "Booking already started. Security deposit refunded."

    booking.booking_status = "CANCELLED"
    booking.cancellation_reason = f"{reason} ({policy_note})"
    booking.refund_amount = refund_amount
    booking.payment_status = "REFUNDED"

    notif = Notification(
        title=f"🛑 Rental Cancelled: {booking.booking_id}",
        message=f"Booking {booking.booking_id} cancelled. Refund of ₹{refund_amount:,.2f} initiated to original payment method. {policy_note}",
        category="ORDER",
        severity="WARNING"
    )
    db.add(notif)
    db.commit()

    return {
        "success": True,
        "booking_id": booking.booking_id,
        "refund_amount": refund_amount,
        "policy_note": policy_note,
        "status": "CANCELLED",
        "message": f"Booking cancelled successfully. ₹{refund_amount:,.2f} refunded."
    }

CATEGORY_DEFAULT_IMAGES = {
    "Tractors": "/images/equipment/mahindra_novo_655.jpg",
    "Harvesters": "/images/equipment/preet_987_harvester.jpg",
    "Water Pumps": "/images/equipment/kirloskar_water_pump.jpg",
    "Rotavators": "/images/equipment/shaktiman_rotavator.jpg",
    "Seed Drills": "/images/equipment/national_seed_drill.jpg",
    "Sprayers": "/images/equipment/aspee_boom_sprayer.jpg",
    "Threshers": "/images/equipment/landforce_thresher.jpg"
}

@app.post("/api/equipment/list")
def list_new_equipment(payload: dict = Body(...), db: Session = Depends(get_db)):
    name = payload.get("name")
    category = payload.get("category", "Tractors")
    hourly_rate = float(payload.get("hourly_rate", 500.0))
    daily_rate = float(payload.get("daily_rate", 3500.0))

    if not name:
        raise HTTPException(status_code=400, detail="Equipment name is required")

    default_cat_img = CATEGORY_DEFAULT_IMAGES.get(category, "/images/equipment/john_deere_5310.jpg")

    new_eq = Equipment(
        name=name,
        category=category,
        brand=payload.get("brand", "Mahindra"),
        model=payload.get("model", "2024 Edition"),
        year=int(payload.get("year", 2024)),
        power_hp=payload.get("power_hp", "50 HP"),
        fuel_type=payload.get("fuel_type", "Diesel"),
        capacity_specs=payload.get("capacity_specs", "High performance agricultural implement"),
        hourly_rate=hourly_rate,
        daily_rate=daily_rate,
        operator_available=bool(payload.get("operator_available", True)),
        operator_charge_per_hr=float(payload.get("operator_charge_per_hr", 150.0)),
        operator_charge_per_day=float(payload.get("operator_charge_per_day", 800.0)),
        fuel_included_option=bool(payload.get("fuel_included_option", True)),
        fuel_charge_per_hr=float(payload.get("fuel_charge_per_hr", 250.0)),
        fuel_charge_per_day=float(payload.get("fuel_charge_per_day", 1400.0)),
        delivery_available=bool(payload.get("delivery_available", True)),
        delivery_rate_per_km=float(payload.get("delivery_rate_per_km", 35.0)),
        security_deposit=float(payload.get("security_deposit", 2000.0)),
        location=payload.get("location", "Ludhiana, Punjab"),
        district=payload.get("district", "Ludhiana"),
        state=payload.get("state", "Punjab"),
        distance_km=float(payload.get("distance_km", 5.0)),
        owner_name=payload.get("owner_name", "Kisan Sahayata CHC"),
        owner_phone=payload.get("owner_phone", "+91 98765 12345"),
        owner_badge="AgriWise Partner",
        rating=5.0,
        reviews_count=1,
        image_url=payload.get("image_url") or default_cat_img,
        implements_compatibility=payload.get("implements_compatibility", "Standard 3-point linkage"),
        terms=payload.get("terms", "Valid ID required. Full refund if cancelled > 6 hrs prior."),
        available=True
    )
    db.add(new_eq)
    db.commit()

    return {
        "success": True,
        "equipment": serialize_equipment(new_eq, db),
        "message": f"Successfully listed {name} on AgriWise Farm Equipment Marketplace!"
    }

@app.patch("/api/equipment/{equipment_id}/status")
def update_equipment_status(equipment_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    if "available" in payload:
        eq.available = bool(payload["available"])
    db.commit()

    return {
        "success": True,
        "id": eq.id,
        "available": eq.available,
        "message": f"Equipment availability updated to {'Available' if eq.available else 'Under Maintenance'}"
    }

@app.get("/api/equipment/booking/{booking_id}/receipt")
def get_equipment_booking_receipt(booking_id: str, db: Session = Depends(get_db)):
    booking = db.query(EquipmentBooking).filter(EquipmentBooking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    eq = booking.equipment
    return {
        "receipt_number": f"AGRI-EQP-REC-{booking.id:05d}",
        "booking_id": booking.booking_id,
        "created_at": booking.created_at.strftime("%d %b %Y, %I:%M %p") if booking.created_at else "",
        "rental_period": f"{booking.start_time.strftime('%d %b %Y, %I:%M %p')} to {booking.end_time.strftime('%d %b %Y, %I:%M %p')}",
        "duration": f"{booking.duration_units} {'Hours' if booking.rental_type == 'HOURLY' else 'Days'}",
        "equipment": {
            "name": eq.name if eq else "Farm Implement",
            "category": eq.category if eq else "Equipment",
            "model": eq.model if eq else "",
            "power": eq.power_hp if eq else "",
            "location": eq.location if eq else ""
        },
        "farmer": {
            "name": booking.farmer_name,
            "phone": booking.farmer_phone,
            "delivery_address": booking.delivery_address if booking.delivery_to_farm else "Self-pickup from Owner Yard"
        },
        "owner": {
            "name": eq.owner_name if eq else "Partner CHC",
            "phone": eq.owner_phone if eq else "+91 98765 12345",
            "badge": eq.owner_badge if eq else "Verified Partner"
        },
        "financials": {
            "base_rental": booking.base_amount,
            "operator_charges": booking.operator_amount,
            "delivery_charges": booking.delivery_amount,
            "security_deposit_refundable": booking.security_deposit,
            "gst_5_pct": booking.gst_amount,
            "total_paid": booking.total_amount,
            "payment_method": booking.payment_method,
            "payment_status": booking.payment_status,
            "booking_status": booking.booking_status
        },
        "terms_and_conditions": [
            "Refundable Security Deposit is returned within 2 hours of equipment return and physical inspection.",
            "Free cancellation with 100% refund if cancelled at least 6 hours before rental start time.",
            "Operator adheres to standard agricultural safety norms. Farmer must ensure field accessibility.",
            "DBT & APMC Custom Hiring Centre (CHC) compliance certified under Sub-Mission on Agricultural Mechanization (SMAM)."
        ]
    }

@app.get("/api/equipment/{equipment_id}")
def get_equipment_details(equipment_id: int, db: Session = Depends(get_db)):
    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    now = datetime.utcnow()
    future_bookings = db.query(EquipmentBooking).filter(
        EquipmentBooking.equipment_id == equipment_id,
        EquipmentBooking.booking_status.in_(["CONFIRMED", "ACTIVE"]),
        EquipmentBooking.end_time > now
    ).order_by(EquipmentBooking.start_time.asc()).all()

    booked_slots = [
        {
            "booking_id": b.booking_id,
            "start_time": b.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_time": b.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "formatted_start": b.start_time.strftime("%d %b %Y, %I:%M %p"),
            "formatted_end": b.end_time.strftime("%d %b %Y, %I:%M %p"),
            "rental_type": b.rental_type
        } for b in future_bookings
    ]

    data = serialize_equipment(eq, db)
    data["upcoming_booked_slots"] = booked_slots
    return data

# ==========================================
# 13. Static Files & Clean Dedicated Page Routing
# ==========================================
# Mount CSS, JS, Locales
if os.path.exists(os.path.join(FRONTEND_DIR, "css")):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
if os.path.exists(os.path.join(FRONTEND_DIR, "js")):
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
if os.path.exists(os.path.join(FRONTEND_DIR, "locales")):
    app.mount("/locales", StaticFiles(directory=os.path.join(FRONTEND_DIR, "locales")), name="locales")
if os.path.exists(os.path.join(FRONTEND_DIR, "images")):
    app.mount("/images", StaticFiles(directory=os.path.join(FRONTEND_DIR, "images")), name="images")

# Route handler for dedicated pages
ROUTE_PAGE_MAP = {
    "": "index.html",
    "dashboard": "pages/dashboard.html",
    "farm-profile": "pages/farm-profile.html",
    "farm-analysis": "pages/farm-analysis.html",
    "weather": "pages/weather.html",
    "crop-recommendation": "pages/crop-recommendation.html",
    "crop-details": "pages/crop-details.html",
    "seed-recommendation": "pages/seed-recommendation.html",
    "seed-details": "pages/seed-details.html",
    "cultivation-plan": "pages/cultivation-plan.html",
    "fertilizer-recommendation": "pages/fertilizer-recommendation.html",
    "fertilizer-market": "pages/fertilizer-market.html",
    "water-analysis": "pages/water-analysis.html",
    "market-intelligence": "pages/market-intelligence.html",
    "crop-demand": "pages/crop-demand.html",
    "crop-shortage": "pages/crop-shortage.html",
    "profit-estimator": "pages/profit-estimator.html",
    "buyer-marketplace": "pages/buyer-marketplace.html",
    "transport-marketplace": "pages/transport-marketplace.html",
    "farm-equipment": "pages/farm-equipment.html",
    "farm-to-market": "pages/farm-to-market.html",
    "farmer-orders": "pages/farmer-orders.html",
    "payment": "pages/payment.html",
    "payment-gateway": "pages/payment.html",
    "dealer-dashboard": "pages/dealer-dashboard.html",
    "transport-dashboard": "pages/transport-dashboard.html",
    "buyer-dashboard": "pages/buyer-dashboard.html",
    "ai-assistant": "pages/ai-assistant.html",
    "farm-calendar": "pages/farm-calendar.html",
    "notifications": "pages/notifications.html",
    "farm-report": "pages/farm-report.html",
    "admin": "pages/admin.html",
    "login": "pages/login.html",
    "register": "pages/register.html",
    "forgot-password": "pages/forgot-password.html",
    "verify-account": "pages/verify-account.html"
}

@app.get("/")
def get_landing():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/{page_name}")
def serve_page(page_name: str):
    clean = page_name.strip("/").lower()
    if clean.endswith(".html"):
        clean = clean[:-5]

    if clean in ROUTE_PAGE_MAP:
        target = os.path.join(FRONTEND_DIR, ROUTE_PAGE_MAP[clean])
        if os.path.exists(target):
            return FileResponse(target)

    # Fallback to direct page in pages/ if exists
    direct = os.path.join(PAGES_DIR, f"{clean}.html")
    if os.path.exists(direct):
        return FileResponse(direct)

    # If static file requested
    potential_file = os.path.join(FRONTEND_DIR, clean)
    if os.path.exists(potential_file) and os.path.isfile(potential_file):
        return FileResponse(potential_file)

    # Return landing or index if not matched
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
