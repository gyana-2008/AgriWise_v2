"""
🌾 AGRIWISE AI - Database Models and Engine
SQLAlchemy Models for Users, Farms, Soils, Waters, Crops, Seeds, Fertilizers,
Dealers, Markets, Buyers, Transporters, Orders, Schedules, and Notifications.
"""

import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agriwise.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=False)
    role = Column(String, default="FARMER")  # FARMER, DEALER, SERVICE_PROVIDER, TRANSPORTER, BUYER, ADMIN
    state = Column(String, default="Punjab")
    district = Column(String, default="Ludhiana")
    village = Column(String, default="Sahnewal")
    farm_size_acres = Column(Float, default=5.0)
    experience_years = Column(Integer, default=12)
    password_hash = Column(String, default="agriwise2026")
    created_at = Column(DateTime, default=datetime.utcnow)

    farms = relationship("Farm", back_populates="owner")
    orders = relationship("Order", back_populates="user")

class Farm(Base):
    __tablename__ = "farms"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    location_name = Column(String, default="Ludhiana Farm 1")
    latitude = Column(Float, default=30.9010)
    longitude = Column(Float, default=75.8573)
    elevation_m = Column(Float, default=244.0)
    area_acres = Column(Float, default=5.0)
    current_crop = Column(String, default="Maize")
    current_season = Column(String, default="Kharif")
    previous_crop = Column(String, default="Wheat")
    irrigation_method = Column(String, default="Drip & Tube-well")
    water_source = Column(String, default="Groundwater Tube-well")
    water_availability = Column(String, default="Abundant (High)")
    farming_method = Column(String, default="Precision Conventional")
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="farms")
    soil = relationship("SoilProfile", uselist=False, back_populates="farm")
    water = relationship("WaterProfile", uselist=False, back_populates="farm")

class SoilProfile(Base):
    __tablename__ = "soil_profiles"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), unique=True)
    soil_type = Column(String, default="Alluvial Loam")
    ph = Column(Float, default=6.8)
    nitrogen_kg_ha = Column(Float, default=260.0)      # Medium
    phosphorus_kg_ha = Column(Float, default=22.5)     # Medium-High
    potassium_kg_ha = Column(Float, default=280.0)     # High
    organic_carbon_pct = Column(Float, default=0.62)   # Medium
    moisture_pct = Column(Float, default=22.0)
    ec_ds_m = Column(Float, default=0.45)              # Normal (<1.0)
    health_score = Column(Integer, default=85)
    updated_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="soil")

class WaterProfile(Base):
    __tablename__ = "water_profiles"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), unique=True)
    source = Column(String, default="Groundwater / Tube-well")
    ph = Column(Float, default=7.2)
    ec_ds_m = Column(Float, default=0.65)
    tds_ppm = Column(Float, default=420.0)
    salinity_status = Column(String, default="Safe / Good Quality")
    hardness_mg_l = Column(Float, default=180.0)
    suitability_score = Column(Integer, default=88)
    updated_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="water")

class Crop(Base):
    __tablename__ = "crops"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    hindi_name = Column(String, default="")
    punjabi_name = Column(String, default="")
    season = Column(String, default="Kharif") # Kharif, Rabi, Zaid
    category = Column(String, default="Cereal")
    typical_duration_days = Column(Integer, default=110)
    water_req_level = Column(String, default="Medium") # Low, Medium, High
    optimum_temp_min = Column(Float, default=18.0)
    optimum_temp_max = Column(Float, default=32.0)
    optimum_ph_min = Column(Float, default=6.0)
    optimum_ph_max = Column(Float, default=7.5)
    expected_yield_q_acre = Column(Float, default=28.0)
    current_mandi_price_q = Column(Float, default=2250.0)
    msp_price_q = Column(Float, default=2090.0)
    demand_status = Column(String, default="High")
    profit_potential = Column(String, default="High")
    description = Column(Text, default="")

    varieties = relationship("SeedVariety", back_populates="crop")

class SeedVariety(Base):
    __tablename__ = "seed_varieties"
    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"))
    name = Column(String, nullable=False)
    variety_code = Column(String, default="")
    manufacturer = Column(String, default="Certified National Seeds")
    duration_days = Column(Integer, default=110)
    expected_yield_min_q = Column(Float, default=25.0)
    expected_yield_max_q = Column(Float, default=30.0)
    seed_rate_kg_acre = Column(Float, default=8.0)
    price_per_kg = Column(Float, default=240.0)
    disease_resistance = Column(String, default="High (Stalk Rot & Blight)")
    drought_tolerance = Column(String, default="Medium-High")
    soil_affinity = Column(String, default="Alluvial, Loamy, Well-drained")
    suitability_pct = Column(Integer, default=94)
    certified = Column(Boolean, default=True)
    key_features = Column(Text, default="High shelling percentage, strong lodging tolerance")

    crop = relationship("Crop", back_populates="varieties")

class FertilizerProduct(Base):
    __tablename__ = "fertilizers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, default="Chemical") # Chemical, Organic, Biofertilizer, Micronutrient
    nutrient_composition = Column(String, default="N: 46%, P: 0%, K: 0%")
    n_pct = Column(Float, default=46.0)
    p_pct = Column(Float, default=0.0)
    k_pct = Column(Float, default=0.0)
    pack_size_kg = Column(Float, default=45.0)
    mrp_inr = Column(Float, default=266.5)
    subsidy_eligible = Column(Boolean, default=True)
    application_stage = Column(String, default="Basal & Top Dressing")
    safety_guideline = Column(Text, default="Store in cool, dry ventilated room. Avoid excess application.")

class Dealer(Base):
    __tablename__ = "dealers"
    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String, nullable=False)
    owner_name = Column(String, default="")
    phone = Column(String, default="")
    address = Column(String, default="")
    city = Column(String, default="Ludhiana")
    state = Column(String, default="Punjab")
    latitude = Column(Float, default=30.9100)
    longitude = Column(Float, default=75.8600)
    rating = Column(Float, default=4.8)
    delivery_available = Column(Boolean, default=True)
    products_json = Column(Text, default="[]") # Inventory JSON

class MarketPrice(Base):
    __tablename__ = "market_prices"
    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String, nullable=False)
    mandi_name = Column(String, default="Ludhiana Grain Market")
    state = Column(String, default="Punjab")
    modal_price_q = Column(Float, default=2250.0)
    min_price_q = Column(Float, default=2100.0)
    max_price_q = Column(Float, default=2400.0)
    daily_arrivals_tonnes = Column(Float, default=320.0)
    price_change_pct = Column(Float, default=2.4)
    demand_level = Column(String, default="High")
    updated_at = Column(DateTime, default=datetime.utcnow)

class CropShortage(Base):
    __tablename__ = "crop_shortages"
    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String, nullable=False)
    state_code = Column(String, nullable=False) # PB, HR, MH, UP, MP, etc.
    state_name = Column(String, nullable=False)
    status = Column(String, default="High Shortage") # High Shortage, Medium Shortage, Balanced, Surplus
    demand_tonnes = Column(Float, default=45000.0)
    supply_tonnes = Column(Float, default=28000.0)
    deficit_tonnes = Column(Float, default=17000.0)
    deficit_pct = Column(Float, default=37.7)
    current_avg_price_q = Column(Float, default=2480.0)
    price_trend = Column(String, default="Bullish (+5.2%)")
    major_markets = Column(String, default="Khanna, Ludhiana, Jalandhar")
    buyer_demand_summary = Column(Text, default="Starch mills and poultry feed manufacturers actively seeking dry grain.")

class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    buyer_type = Column(String, default="Food Processor & Miller") # Wholesaler, Processor, Exporter
    contact_person = Column(String, default="")
    phone = Column(String, default="")
    email = Column(String, default="")
    location = Column(String, default="Khanna Industrial Area, Punjab")
    crop_required = Column(String, default="Maize")
    quantity_required_tonnes = Column(Float, default=500.0)
    offered_price_q = Column(Float, default=2380.0)
    deadline_date = Column(String, default="2026-10-25")
    quality_specs = Column(Text, default="Moisture < 12%, Foreign matter < 1%, Aflatoxin free")
    rating = Column(Float, default=4.9)
    verified = Column(Boolean, default=True)

class TransportProvider(Base):
    __tablename__ = "transporters"
    id = Column(Integer, primary_key=True, index=True)
    operator_name = Column(String, nullable=False)
    phone = Column(String, default="")
    vehicle_type = Column(String, default="Tata 407 (Open Bed)") # Pickup, 407 Truck, 10-Tonne, 16-Tonne
    capacity_tonnes = Column(Float, default=5.0)
    base_rate_inr = Column(Float, default=1500.0)
    rate_per_km_inr = Column(Float, default=32.0)
    current_distance_km = Column(Float, default=6.5)
    location = Column(String, default="Sahnewal Bypass, Ludhiana")
    available_now = Column(Boolean, default=True)
    rating = Column(Float, default=4.7)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_type = Column(String, default="INPUT") # INPUT, TRANSPORT, BUYER_OFFER
    item_title = Column(String, default="")
    quantity = Column(String, default="")
    amount_inr = Column(Float, default=0.0)
    status = Column(String, default="CONFIRMED") # PENDING, CONFIRMED, DISPATCHED, COMPLETED
    partner_name = Column(String, default="")
    items_json = Column(Text, default="[]")
    delivery_address = Column(String, default="")
    dealer_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True) # e.g. AGRI-PAY-2026-8912
    utr_number = Column(String, default="") # 12-digit bank reference UTR
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    payment_type = Column(String, default="INPUT_PURCHASE") # INPUT_PURCHASE, TRANSPORT_ADVANCE, BUYER_ESCROW, FARMER_PAYOUT, KCC_SUBSIDY
    payment_method = Column(String, default="UPI_QR") # UPI_QR, UPI_VPA, KCC_RUPAY, NET_BANKING, ESCROW, MANDI_DIRECT
    amount_inr = Column(Float, default=0.0)
    gst_amount_inr = Column(Float, default=0.0)
    subsidy_amount_inr = Column(Float, default=0.0)
    net_amount_inr = Column(Float, default=0.0)
    payer_name = Column(String, default="Sardar Gurpreet Singh")
    payee_name = Column(String, default="Kisan Suvidha Kendra")
    bank_name_or_vpa = Column(String, default="sbi")
    status = Column(String, default="SUCCESS") # INITIATED, PROCESSING, SUCCESS, ESCROW_LOCKED, DISBURSED, FAILED
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String, default="WEATHER") # WEATHER, MARKET, ADVISORY, ORDER
    severity = Column(String, default="INFO") # INFO, WARNING, ALERT, SUCCESS
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

class ConfigWeights(Base):
    __tablename__ = "config_weights"
    id = Column(Integer, primary_key=True, index=True)
    climate_weight = Column(Float, default=0.20)
    soil_weight = Column(Float, default=0.20)
    water_weight = Column(Float, default=0.15)
    weather_weight = Column(Float, default=0.15)
    season_weight = Column(Float, default=0.10)
    market_weight = Column(Float, default=0.10)
    economics_weight = Column(Float, default=0.10)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String, nullable=False) # e.g. "John Deere 5310 55HP Tractor"
    category = Column(String, nullable=False, default="Tractors") # Tractors, Harvesters, Water Pumps, Rotavators, Seed Drills, Sprayers, Threshers
    brand = Column(String, default="John Deere")
    model = Column(String, default="5310 4WD")
    year = Column(Integer, default=2024)
    power_hp = Column(String, default="55 HP")
    fuel_type = Column(String, default="Diesel")
    capacity_specs = Column(String, default="55 HP, 4WD, Dual Clutch, High Lift Hydraulic")
    hourly_rate = Column(Float, default=550.0)
    daily_rate = Column(Float, default=3800.0)
    operator_available = Column(Boolean, default=True)
    operator_charge_per_hr = Column(Float, default=150.0)
    operator_charge_per_day = Column(Float, default=800.0)
    fuel_included_option = Column(Boolean, default=True)
    fuel_charge_per_hr = Column(Float, default=250.0)
    fuel_charge_per_day = Column(Float, default=1400.0)
    delivery_available = Column(Boolean, default=True)
    delivery_rate_per_km = Column(Float, default=35.0)
    security_deposit = Column(Float, default=2000.0)
    location = Column(String, default="Karnal, Haryana")
    district = Column(String, default="Karnal")
    state = Column(String, default="Haryana")
    distance_km = Column(Float, default=4.2)
    owner_name = Column(String, default="Kisan Samriddhi CHC Hub")
    owner_phone = Column(String, default="+91 98765 12345")
    owner_badge = Column(String, default="Verified AgriWise Partner")
    rating = Column(Float, default=4.8)
    reviews_count = Column(Integer, default=34)
    image_url = Column(String, default="")
    implements_compatibility = Column(Text, default="MB Plough, Disc Harrow, Rotavator 7ft, Seed Drill, Trolley 5-Tonne")
    terms = Column(Text, default="Valid Govt ID (Aadhaar/DL) required at handover. Full refund on cancellation > 6 hours prior to scheduled start. Return with same fuel level if fuel-excluded plan.")
    available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("EquipmentBooking", back_populates="equipment")

class EquipmentBooking(Base):
    __tablename__ = "equipment_bookings"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(String, unique=True, index=True) # e.g. AGRI-EQP-2026-0042
    equipment_id = Column(Integer, ForeignKey("equipment.id"))
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    farmer_name = Column(String, default="Sardar Gurpreet Singh")
    farmer_phone = Column(String, default="+91 98765 43210")
    rental_type = Column(String, default="HOURLY") # HOURLY, DAILY
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_units = Column(Float, default=4.0) # hours or days
    with_operator = Column(Boolean, default=True)
    with_fuel = Column(Boolean, default=False)
    delivery_to_farm = Column(Boolean, default=False)
    delivery_address = Column(String, default="")
    delivery_distance_km = Column(Float, default=0.0)
    base_amount = Column(Float, default=0.0)
    operator_amount = Column(Float, default=0.0)
    delivery_amount = Column(Float, default=0.0)
    security_deposit = Column(Float, default=0.0)
    gst_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    payment_method = Column(String, default="UPI_QR") # UPI_QR, KCC_RUPAY, NET_BANKING, PAY_ON_DELIVERY
    payment_status = Column(String, default="PAID") # PENDING, PAID, REFUNDED
    booking_status = Column(String, default="CONFIRMED") # CONFIRMED, ACTIVE, COMPLETED, CANCELLED
    cancellation_reason = Column(String, default="")
    refund_amount = Column(Float, default=0.0)
    rating = Column(Float, nullable=True)
    review_text = Column(Text, default="")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="bookings")

def init_db():
    """Initializes the database schema."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """FastAPI database dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
