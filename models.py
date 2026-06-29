from sqlalchemy import Column, Integer, String, Float, Text, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    id         = Column(Integer, primary_key=True)
    name       = Column(String, nullable=False)
    slug       = Column(String, unique=True, nullable=False)
    icon       = Column(String)
    subtitle   = Column(String)
    section    = Column(String)  # e.g. "Home & Living", "Daily Needs"
    sort_order = Column(Integer, default=0)
    products   = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id          = Column(Integer, primary_key=True)
    name        = Column(String, nullable=False)
    slug        = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    unit        = Column(String)
    tags        = Column(JSON, default=list)
    is_popular  = Column(Boolean, default=False)
    category    = relationship("Category", back_populates="products")
    prices      = relationship("PriceRecord",    back_populates="product")
    breakdowns  = relationship("CostBreakdown",  back_populates="product")
    questions   = relationship("VendorQuestion", back_populates="product")
    trends      = relationship("PriceTrend",     back_populates="product")
    insights    = relationship("Insight",        back_populates="product")

class PriceRecord(Base):
    __tablename__ = "price_records"
    id          = Column(Integer, primary_key=True)
    product_id  = Column(Integer, ForeignKey("products.id"))
    city        = Column(String, nullable=False)
    budget_min  = Column(Float); budget_max  = Column(Float)
    fair_min    = Column(Float); fair_max    = Column(Float)
    premium_min = Column(Float); premium_max = Column(Float)
    avg_price   = Column(Float)
    updated_at  = Column(DateTime, default=datetime.utcnow)
    product     = relationship("Product", back_populates="prices")

class CostBreakdown(Base):
    __tablename__ = "cost_breakdowns"
    id         = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    label      = Column(String, nullable=False)
    min_val    = Column(Float, nullable=True)
    max_val    = Column(Float, nullable=True)
    percent    = Column(Float, nullable=True)
    sort_order = Column(Integer, default=0)
    product    = relationship("Product", back_populates="breakdowns")

class VendorQuestion(Base):
    __tablename__ = "vendor_questions"
    id         = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    question   = Column(String, nullable=False)
    sort_order = Column(Integer, default=0)
    product    = relationship("Product", back_populates="questions")

class PriceTrend(Base):
    __tablename__ = "price_trends"
    id          = Column(Integer, primary_key=True)
    product_id  = Column(Integer, ForeignKey("products.id"))
    city        = Column(String, nullable=False)
    month_label = Column(String)
    price       = Column(Float)
    sort_order  = Column(Integer, default=0)
    product     = relationship("Product", back_populates="trends")

class Insight(Base):
    __tablename__ = "insights"
    id         = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    text       = Column(Text, nullable=False)
    sort_order = Column(Integer, default=0)
    product    = relationship("Product", back_populates="insights")

class TrendingSearch(Base):
    __tablename__ = "trending_searches"
    id         = Column(Integer, primary_key=True)
    query      = Column(String, nullable=False)
    city       = Column(String, nullable=True)
    count      = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)

class MarketHighlight(Base):
    __tablename__ = "market_highlights"
    id         = Column(Integer, primary_key=True)
    label      = Column(String, nullable=False)
    value      = Column(String, nullable=False)
    change     = Column(String)
    is_up      = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

class MoneyHack(Base):
    __tablename__ = "money_hacks"
    id         = Column(Integer, primary_key=True)
    category   = Column(String, nullable=False)   # ELECTRICITY, GROCERY, etc.
    headline   = Column(String, nullable=False)
    detail     = Column(Text, nullable=False)
    saving_amt = Column(String)                   # "₹800/mo", "₹1.2K/trip"
    saving_period = Column(String)                # "per month", "per year"
    sort_order = Column(Integer, default=0)

class PriceBulletin(Base):
    __tablename__ = "price_bulletins"
    id         = Column(Integer, primary_key=True)
    category   = Column(String, nullable=False)
    city       = Column(String, nullable=True)
    headline   = Column(String, nullable=False)
    detail     = Column(Text, nullable=False)
    change_pct = Column(Float, nullable=False)    # negative = drop, positive = rise
    period     = Column(String)                   # "THIS WEEK", "THIS MONTH"
    published_at = Column(DateTime, default=datetime.utcnow)
    sort_order = Column(Integer, default=0)

class PlanTemplate(Base):
    __tablename__ = "plan_templates"
    id             = Column(Integer, primary_key=True)
    plan_id        = Column(String, unique=True, nullable=False)
    label          = Column(String, nullable=False)
    subtitle       = Column(String)
    icon           = Column(String)
    color_hex      = Column(String)
    icon_color_hex = Column(String)
    section        = Column(String)   # "LIFE PLANNING", "WEALTH BUILDING", "BORROWING & PROTECTION"
    sort_order     = Column(Integer, default=0)
    questions      = relationship("PlanQuestion",   back_populates="plan")
    free_insights  = relationship("PlanFreeInsight", back_populates="plan")
    premium_items  = relationship("PlanPremiumItem", back_populates="plan")

class PlanQuestion(Base):
    __tablename__ = "plan_questions"
    id         = Column(Integer, primary_key=True)
    plan_id    = Column(Integer, ForeignKey("plan_templates.id"))
    step_no    = Column(Integer, nullable=False)
    question   = Column(String, nullable=False)
    field_key  = Column(String, nullable=False)
    input_type = Column(String, default="choice")  # choice | range | text
    options    = Column(JSON, nullable=True)        # [{"label": "...", "hint": "...", "value": "..."}]
    plan       = relationship("PlanTemplate", back_populates="questions")

class PlanFreeInsight(Base):
    __tablename__ = "plan_free_insights"
    id         = Column(Integer, primary_key=True)
    plan_id    = Column(Integer, ForeignKey("plan_templates.id"))
    text       = Column(Text, nullable=False)
    sort_order = Column(Integer, default=0)
    plan       = relationship("PlanTemplate", back_populates="free_insights")

class PlanPremiumItem(Base):
    __tablename__ = "plan_premium_items"
    id         = Column(Integer, primary_key=True)
    plan_id    = Column(Integer, ForeignKey("plan_templates.id"))
    title      = Column(String, nullable=False)
    subtitle   = Column(String)
    sort_order = Column(Integer, default=0)
    plan       = relationship("PlanTemplate", back_populates="premium_items")

class ExpenseCategory(Base):
    __tablename__ = "expense_categories"
    id              = Column(Integer, primary_key=True)
    name            = Column(String, nullable=False)
    icon_key        = Column(String)
    color_hex       = Column(String)
    recommended_pct = Column(Float)          # % of income
    sort_order      = Column(Integer, default=0)
    rules           = relationship("ExpenseRule", back_populates="expense_cat")

class ExpenseRule(Base):
    __tablename__ = "expense_rules"
    id               = Column(Integer, primary_key=True)
    expense_cat_id   = Column(Integer, ForeignKey("expense_categories.id"))
    income_min       = Column(Float, nullable=True)
    income_max       = Column(Float, nullable=True)
    city_tier        = Column(String, nullable=True)  # "metro", "tier2", "any"
    advice           = Column(Text, nullable=False)
    expense_cat      = relationship("ExpenseCategory", back_populates="rules")

class SearchLog(Base):
    __tablename__ = "search_logs"
    id                 = Column(Integer, primary_key=True)
    query              = Column(String, nullable=False)
    city               = Column(String, nullable=True)
    matched_product_id = Column(Integer, nullable=True)
    timestamp          = Column(DateTime, default=datetime.utcnow)

class PlanUnlock(Base):
    __tablename__ = "plan_unlocks"
    id         = Column(Integer, primary_key=True)
    plan_id    = Column(String, nullable=False)
    device_id  = Column(String, nullable=False)
    amount     = Column(Float, default=1000.0)
    unlocked_at = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# NEW — added for the 50-calculator Planning rebuild + admin formula editor.
# Purely additive: does not touch or modify any model above.
# ═══════════════════════════════════════════════════════════════════════════════

class Calculator(Base):
    """
    Each row = one calculator (out of 50). Replaces the old hardcoded calc_results()
    function in main.py's PLANNING section — instead of a Python if/elif chain per
    plan_id, each calculator's math lives here as an admin-editable formula.

    `inputs`/`outputs` describe the fields shown to the user (label, default, min/max, unit).
    `formula`/`formula_steps` are evaluated server-side via formula_engine.py's safe
    AST-based evaluator — no eval(), no code-injection risk from the admin formula editor.
    """
    __tablename__ = "calculators"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False)       # e.g. "home-loan-emi"
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)                # "Loans", "Insurance", etc.
    icon = Column(String, default="🧮")
    description = Column(String, default="")
    is_featured = Column(Boolean, default=False)              # shows in "5 Major Planning Tools" on home
    featured_order = Column(Integer, default=0)
    featured_group = Column(String, nullable=True)             # calcs sharing a group collapse into ONE home tile (e.g. Fresh Loan + Refinance)
    sort_order = Column(Integer, default=0)
    active = Column(Boolean, default=True)

    inputs = Column(JSON, nullable=False, default=list)
    formula = Column(Text, nullable=False, default="")
    formula_steps = Column(JSON, nullable=True, default=list)
    outputs = Column(JSON, nullable=False, default=list)
    constants = Column(JSON, nullable=True, default=dict)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

