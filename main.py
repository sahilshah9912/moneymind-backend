"""
MoneyMind API v3
- Price discovery (free, all cities)
- Planning with lead capture (phone number → team reaches out)
- Admin panel endpoints (manage categories, products, hacks, bulletins)
- No UPI/payment integration
"""
import os, json
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from database import get_db, init_db
from models import (
    Category, Product, PriceRecord, CostBreakdown, VendorQuestion,
    PriceTrend, Insight, TrendingSearch, MarketHighlight, MoneyHack,
    PriceBulletin, PlanTemplate, PlanQuestion, PlanFreeInsight,
    PlanPremiumItem, ExpenseCategory, ExpenseRule, SearchLog, Calculator,
)
from formula_engine import run_calculator, validate_formula_syntax, FormulaError

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "moneymind_admin_2025")

app = FastAPI(title="MoneyMind API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    # Auto-seed calculators on every startup so they persist even after Render
    # redeploys (which reset the SQLite file on the free tier).
    # seed() is safe to call multiple times — it updates existing rows, never duplicates.
    try:
        from seed_calculators import seed
        db = next(get_db())
        seed(db)
        db.close()
    except Exception as e:
        print(f"[startup] Calculator seed warning: {e}")
    # Create leads table if not exists
    from sqlalchemy import text
    from database import engine
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT NOT NULL,
                plan_id TEXT,
                plan_name TEXT,
                city TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """))
        conn.commit()

# ── Auth helper ───────────────────────────────────────────────────────────────
def verify_admin(x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_SECRET:
        raise HTTPException(401, "Invalid admin key")
    return True

# ── Format helper ─────────────────────────────────────────────────────────────
def fmt(v):
    if v is None: return None
    if v >= 10000000: return f"₹{v/10000000:.1f}Cr"
    if v >= 100000:   return f"₹{v/100000:.1f}L"
    if v >= 1000:     return f"₹{v/1000:.1f}K"
    return f"₹{int(v):,}"

def product_dict(p, city, db, user_price=None):
    price = (db.query(PriceRecord).filter_by(product_id=p.id, city=city).first()
             or db.query(PriceRecord).filter_by(product_id=p.id).first())
    breakdown = [{"label":b.label,"min_val":b.min_val,"max_val":b.max_val,"percent":b.percent}
                 for b in sorted(p.breakdowns, key=lambda x: x.sort_order)]
    questions = [q.question for q in sorted(p.questions, key=lambda x: x.sort_order)]
    insights  = [i.text for i in sorted(p.insights, key=lambda x: x.sort_order)]
    trends    = ([{"month":t.month_label,"price":t.price}
                  for t in sorted(p.trends, key=lambda x: x.sort_order) if t.city == city]
                 or [{"month":t.month_label,"price":t.price}
                     for t in sorted(p.trends, key=lambda x: x.sort_order)])
    verdict = verdict_label = None
    if user_price and price:
        if   user_price <= price.budget_max:  verdict,verdict_label = "low",   "Below market — great price!"
        elif user_price <= price.fair_max:    verdict,verdict_label = "fair",  "Within fair market range"
        elif user_price <= price.premium_min: verdict,verdict_label = "slightly_high","Slightly above average"
        else:                                 verdict,verdict_label = "high",  "Above premium — negotiate"
    return {
        "id":p.id,"name":p.name,"slug":p.slug,
        "category":p.category.name if p.category else None,
        "category_slug":p.category.slug if p.category else None,
        "unit":p.unit,"tags":p.tags or [],"is_popular":p.is_popular,"city":city,
        "price":{
            "budget_min":price.budget_min,"budget_max":price.budget_max,
            "fair_min":price.fair_min,"fair_max":price.fair_max,
            "premium_min":price.premium_min,"premium_max":price.premium_max,
            "avg_price":price.avg_price,
            "budget_min_fmt":fmt(price.budget_min),"budget_max_fmt":fmt(price.budget_max),
            "fair_min_fmt":fmt(price.fair_min),"fair_max_fmt":fmt(price.fair_max),
            "premium_min_fmt":fmt(price.premium_min),"premium_max_fmt":fmt(price.premium_max),
            "avg_price_fmt":fmt(price.avg_price),
        } if price else None,
        "breakdown":breakdown,"questions":questions,"insights":insights,"trends":trends,
        "user_price":user_price,"verdict":verdict,"verdict_label":verdict_label,
    }

def calc_results(plan_id, inputs):
    def si(key, default, mapping): return mapping.get(inputs.get(key,""), default)
    if plan_id == "wedding":
        budget=inputs.get("budget_num",1500000); guests=inputs.get("guests_num",200)
        bph=budget/guests if guests else 0
        return {"budget_per_head":round(bph),"venue_decor":round(budget*.30),
                "catering":round(budget*.35),"photography":round(budget*.12),
                "bridal_groom":round(budget*.10),"buffer":round(budget*.13),
                "catering_per_plate_fair":round(bph*.35),
                "verdict":"tight" if bph<800 else "reasonable" if bph<2000 else "comfortable"}
    elif plan_id == "home-renovation":
        area=si("area","500–900 sq ft (2 BHK)",{"Under 500 sq ft (1 BHK)":450,"500–900 sq ft (2 BHK)":700,"900–1,400 sq ft (3 BHK)":1100,"1,400+ sq ft":1600})
        rate=si("quality","Mid-range (branded materials)",{"Budget (local materials)":800,"Mid-range (branded materials)":1400,"Premium (designer finishes)":2200,"Luxury (imported materials)":3500})
        total=area*rate
        return {"estimated_total":round(total),"cost_per_sqft":rate,"civil_work":round(total*.38),"modular_furniture":round(total*.30),"electrical_plumbing":round(total*.12),"painting_flooring":round(total*.12),"contingency":round(total*.18),"area_sqft":area}
    elif plan_id == "sip":
        sip=si("monthly_sip","₹5,000–15,000",{"₹500–2,000":1000,"₹2,000–5,000":3500,"₹5,000–15,000":10000,"₹15,000–50,000":30000,"₹50,000+":75000})
        rate=si("risk","Growth — mostly equity",{"Conservative — capital protection first":7.5,"Moderate — some equity is okay":10.5,"Growth — mostly equity":12.5,"Aggressive — max growth":15.0})
        yrs=si("horizon","10–20 years",{"Less than 3 years":2.5,"3–5 years":4,"5–10 years":7.5,"10–20 years":15,"20+ years":25})
        r=rate/1200; n=int(yrs*12); corpus=sip*((pow(1+r,n)-1)/r)*(1+r); invested=sip*n
        return {"monthly_sip":sip,"years":yrs,"expected_return_pct":rate,"total_invested":round(invested),"estimated_corpus":round(corpus),"wealth_gained":round(corpus-invested),"wealth_multiplier":round(corpus/invested,2)}
    elif plan_id == "retirement":
        cur=si("current_age","28–35",{"22–27":25,"28–35":32,"36–44":40,"45–55":50})
        ret=si("retire_age","60–62",{"45–50 (early retirement)":47,"55–58":57,"60–62":61,"65+":65})
        exp=si("monthly_exp","₹60,000–1,20,000",{"Under ₹30,000":25000,"₹30,000–60,000":45000,"₹60,000–1,20,000":90000,"₹1,20,000+":175000})
        sav=si("monthly_save","₹5,000–20,000",{"Nothing yet":0,"Under ₹5,000":3000,"₹5,000–20,000":12000,"₹20,000–50,000":35000,"₹50,000+":75000})
        yrs=max(1,ret-cur); fut_exp=exp*pow(1.06,yrs); needed=fut_exp*12*25
        r=0.11/12; n=yrs*12; projected=sav*((pow(1+r,n)-1)/r)*(1+r) if sav>0 else 0
        monthly_req=(needed*r)/(pow(1+r,n)-1) if n>0 else needed/12
        return {"years_to_retire":yrs,"corpus_needed":round(needed),"projected_corpus":round(projected),"shortfall":round(max(0,needed-projected)),"on_track":projected>=needed,"monthly_investment_required":round(monthly_req),"future_monthly_expense":round(fut_exp)}
    elif plan_id == "loan":
        loan=si("loan_amount","₹20–60 Lakhs",{"Under ₹5 Lakhs":300000,"₹5–20 Lakhs":1200000,"₹20–60 Lakhs":4000000,"₹60 Lakhs–1 Crore":8000000,"₹1 Crore+":15000000})
        income=si("monthly_income","₹80,000–1,50,000",{"Under ₹40,000":30000,"₹40,000–80,000":60000,"₹80,000–1,50,000":115000,"₹1,50,000+":250000})
        ltype=inputs.get("loan_type","Home Loan")
        rate={"Home Loan":8.75,"Car Loan":9.5,"Personal Loan":15.0,"Education Loan":9.0,"Loan Against Property":10.5}.get(ltype,8.75)
        tenure={"Home Loan":20,"Car Loan":6,"Personal Loan":4,"Education Loan":10,"Loan Against Property":15}.get(ltype,20)
        r=rate/1200; n=tenure*12; emi=loan*r*pow(1+r,n)/(pow(1+r,n)-1); total=emi*n
        return {"loan_amount":loan,"monthly_emi":round(emi),"total_payment":round(total),"total_interest":round(total-loan),"tenure_years":tenure,"interest_rate":rate,"emi_pct_income":round((emi/income)*100,1),"is_affordable":emi<=income*0.40}
    elif plan_id == "insurance":
        age={"18–25":22,"26–35":30,"36–45":40,"46–55":50,"55+":58}.get(inputs.get("age","26–35"),30)
        members=4; income=1200000
        return {"recommended_health_cover":max(1000000,income*0.5*members),"recommended_term_cover":income*12,"estimated_health_premium_pa":round((age*200+members*2500)*12),"estimated_term_premium_pa":round(income*12*0.0038),"ideal_premium_budget_pa":round(income*0.04)}
    elif plan_id == "emergency-fund":
        exp=si("monthly_exp","₹20,000–50,000",{"Under ₹20,000":15000,"₹20,000–50,000":35000,"₹50,000–1,00,000":75000,"₹1,00,000+":150000})
        months=si("employment","Salaried (stable MNC/Govt)",{"Salaried (stable MNC/Govt)":6,"Salaried (startup/SME)":9,"Self-employed/Freelancer":12,"Business owner":15})
        exist=si("current_savings","Under ₹25,000",{"Under ₹25,000":12500,"₹25,000–1,00,000":62500,"₹1,00,000–3,00,000":200000,"₹3,00,000+":400000})
        target=exp*months; gap=max(0,target-exist)
        return {"target_fund":round(target),"current_savings":round(exist),"gap":round(gap),"months_covered":round(exist/exp,1) if exp else 0,"months_recommended":months,"monthly_save_to_fill":round(gap/6)}
    elif plan_id == "expense-planning":
        inc=si("income","₹60,000–1,20,000",{"Under ₹30,000":25000,"₹30,000–60,000":45000,"₹60,000–1,20,000":90000,"₹1,20,000–2,50,000":185000,"₹2,50,000+":350000})
        return {"monthly_income":inc,"food_grocery":round(inc*.15),"rent_housing":round(inc*.25),"transport":round(inc*.08),"utilities":round(inc*.04),"health":round(inc*.05),"travel_leisure":round(inc*.08),"subscriptions":round(inc*.03),"education_kids":round(inc*.07),"clothing_grooming":round(inc*.04),"savings_investment":round(inc*.20),"needs_50pct":round(inc*.50),"wants_30pct":round(inc*.30),"savings_20pct":round(inc*.20)}
    elif plan_id == "car-ownership":
        seg={"Hatchback (Swift, WagonR, Alto)":{"price":700000,"kmpl":18,"service":7000},"Compact Sedan (City, Verna)":{"price":1400000,"kmpl":14,"service":9000},"Compact SUV (Creta, Seltos, Brezza)":{"price":1800000,"kmpl":15,"service":12000},"SUV (XUV700, Thar, Fortuner)":{"price":3000000,"kmpl":12,"service":18000},"Luxury (BMW, Audi, Mercedes)":{"price":6000000,"kmpl":10,"service":50000}}
        km={"Under 10,000 km":8000,"10,000–20,000 km":15000,"20,000–30,000 km":25000,"30,000+ km":35000}.get(inputs.get("annual_km","10,000–20,000 km"),15000)
        s=seg.get(inputs.get("segment","Compact SUV (Creta, Seltos, Brezza)"),{"price":1800000,"kmpl":15,"service":12000})
        emi=round(s["price"]*0.8*0.02); ins=round(s["price"]*0.018); fuel=round(km*103/s["kmpl"]); dep=round(s["price"]*0.15)
        total_yr=(emi*12)+ins+fuel+s["service"]+dep
        return {"on_road_price":s["price"],"monthly_emi":emi,"annual_insurance":ins,"annual_fuel":fuel,"annual_service":s["service"],"depreciation_yr1":dep,"total_annual_cost":round(total_yr),"total_monthly_cost":round(total_yr/12),"cost_per_km":round(total_yr/km,1)}
    elif plan_id == "vacation":
        base=si("destination","Goa",{"Goa":4500,"Kerala":4200,"Rajasthan":3800,"Himachal/Uttarakhand":3200,"Andaman":6500,"International (Bali/Dubai/Thailand)":9000})
        nights=si("duration","4–5 nights",{"2–3 nights":2.5,"4–5 nights":4.5,"6–8 nights":7,"9+ nights":10})
        ppl=si("travelers","Couple (2)",{"Solo":1,"Couple (2)":2,"Family with kids":3,"Group (4–6 friends)":5})
        mult=si("style","Mid-range — 3-star, restaurants",{"Budget — hostels, local food":0.6,"Mid-range — 3-star, restaurants":1.0,"Comfortable — 4-star, good food":1.7,"Luxury — 5-star, experiences":2.8})
        total=base*mult*nights*ppl
        return {"estimated_total":round(total),"per_person":round(total/ppl),"flights":round(total*.30),"hotel":round(total*.33),"food":round(total*.18),"transport":round(total*.10),"activities":round(total*.09),"nights":nights,"people":ppl}
    elif plan_id == "child-education":
        age=si("child_age","0–3 years",{"Not yet born":0,"0–3 years":2,"4–8 years":6,"9–14 years":11})
        cost=si("goal","IIT/IIM (India)",{"IIT/IIM (India)":1200000,"Private Engineering/MBA":2000000,"MBBS India":5000000,"Study Abroad (US/UK)":8000000,"School (CBSE private)":1500000})
        sav=si("monthly_save","₹2,000–5,000",{"Under ₹2,000":1000,"₹2,000–5,000":3500,"₹5,000–15,000":10000,"₹15,000+":20000})
        yrs=max(1,18-age); future_cost=cost*pow(1.10,yrs); r=0.12/12; n=int(yrs*12)
        corpus=sav*((pow(1+r,n)-1)/r)*(1+r)
        return {"child_age":age,"years_to_goal":yrs,"current_cost":cost,"future_cost":round(future_cost),"projected_corpus":round(corpus),"gap":round(max(0,future_cost-corpus))}
    elif plan_id == "home-loan":
        val=si("property_value","₹40–80 Lakhs",{"Under ₹40 Lakhs":3500000,"₹40–80 Lakhs":6000000,"₹80L–1.5 Crore":11000000,"₹1.5 Crore+":20000000})
        ten=si("tenure","20–25 years",{"10–12 years":11,"15–18 years":17,"20–25 years":22,"30 years":30})
        loan=val*0.80; r=8.75/1200; n=ten*12; emi=loan*r*pow(1+r,n)/(pow(1+r,n)-1); total=emi*n
        return {"property_value":val,"loan_amount":round(loan),"down_payment":round(val*.20),"stamp_duty":round(val*.06),"registration":round(val*.01),"total_upfront":round(val*.27),"monthly_emi":round(emi),"total_interest":round(total-loan),"tenure":ten}
    return {}

# ═══════════════════════════════════════════════════════════════════════════════
# LEAD CAPTURE — when user wants planning help
# ═══════════════════════════════════════════════════════════════════════════════

class LeadRequest(BaseModel):
    phone: str
    plan_id: str
    plan_name: str
    city: Optional[str] = "Not specified"

@app.post("/api/leads")
def capture_lead(req: LeadRequest, db: Session = Depends(get_db)):
    from sqlalchemy import text
    from database import engine
    with engine.connect() as conn:
        conn.execute(text(
            "INSERT INTO leads (phone, plan_id, plan_name, city) VALUES (:phone, :plan_id, :plan_name, :city)"
        ), {"phone": req.phone, "plan_id": req.plan_id, "plan_name": req.plan_name, "city": req.city})
        conn.commit()
    return {"success": True, "message": "Thank you! Our team will call you within 24 hours."}

# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/discover")
def discover(city: str = "Mumbai", db: Session = Depends(get_db)):
    trending   = db.query(TrendingSearch).order_by(TrendingSearch.sort_order).limit(10).all()
    highlights = db.query(MarketHighlight).order_by(MarketHighlight.sort_order).all()
    popular    = db.query(Product).filter_by(is_popular=True).limit(8).all()
    cats       = db.query(Category).order_by(Category.sort_order).all()
    hacks      = db.query(MoneyHack).order_by(MoneyHack.sort_order).limit(6).all()
    bulletins  = db.query(PriceBulletin).order_by(PriceBulletin.sort_order).limit(8).all()
    sections   = {}
    for c in cats:
        sections.setdefault(c.section, []).append({"name":c.name,"slug":c.slug,"icon":c.icon,"subtitle":c.subtitle})
    return {
        "trending_searches":[{"query":t.query,"city":t.city} for t in trending],
        "market_highlights":[{"label":h.label,"value":h.value,"change":h.change,"is_up":h.is_up} for h in highlights],
        "popular_products":[{"name":p.name,"slug":p.slug,"unit":p.unit,"category":p.category.name if p.category else None} for p in popular],
        "category_sections":sections,
        "money_hacks":[{"category":h.category,"headline":h.headline,"detail":h.detail,"saving_amt":h.saving_amt,"saving_period":h.saving_period} for h in hacks],
        "price_bulletins":[{"category":b.category,"city":b.city,"headline":b.headline,"detail":b.detail,"change_pct":b.change_pct,"period":b.period} for b in bulletins],
    }

@app.get("/api/search")
def search(q: str, city: str = "Mumbai", user_price: Optional[float] = None, db: Session = Depends(get_db)):
    q_lower=q.lower().strip(); words=q_lower.split(); scored=[]
    for p in db.query(Product).all():
        score=0; name=p.name.lower(); tags=[t.lower() for t in (p.tags or [])]; cat=(p.category.name or "").lower() if p.category else ""
        for w in words:
            if w in name: score+=4
            if any(w in t for t in tags): score+=3
            if w in cat: score+=2
        if q_lower in name: score+=10
        if score>0: scored.append((score,p))
    scored.sort(key=lambda x:-x[0])
    matched_id=scored[0][1].id if scored else None
    db.add(SearchLog(query=q,city=city,matched_product_id=matched_id)); db.commit()
    if not scored: return {"results":[],"query":q,"city":city,"message":"No results found."}
    return {"results":[product_dict(p,city,db,user_price) for _,p in scored[:5]],"query":q,"city":city,"total":len(scored)}

@app.get("/api/autocomplete")
def autocomplete(q: str, db: Session = Depends(get_db)):
    if len(q)<2: return []
    ql=q.lower(); suggestions=[]
    for p in db.query(Product).all():
        if ql in p.name.lower() or any(ql in t.lower() for t in (p.tags or [])):
            suggestions.append({"label":p.name,"slug":p.slug,"category":p.category.name if p.category else "","type":"product"})
        if len(suggestions)>=5: break
    for t in db.query(TrendingSearch).all():
        if ql in t.query.lower(): suggestions.append({"label":t.query,"slug":None,"category":"Trending","type":"trending"})
        if len(suggestions)>=8: break
    return suggestions[:8]

@app.get("/api/product/{slug}")
def product_detail(slug: str, city: str = "Mumbai", user_price: Optional[float] = None, db: Session = Depends(get_db)):
    p=db.query(Product).filter_by(slug=slug).first()
    if not p: raise HTTPException(404,"Product not found")
    return product_dict(p,city,db,user_price)

@app.get("/api/categories")
def categories(db: Session = Depends(get_db)):
    cats=db.query(Category).order_by(Category.sort_order).all()
    sections={}
    for c in cats:
        sections.setdefault(c.section,[]).append({"name":c.name,"slug":c.slug,"icon":c.icon,"subtitle":c.subtitle,"product_count":len(c.products)})
    return {"sections":sections,"total":len(cats)}

@app.get("/api/plans")
def list_plans(db: Session = Depends(get_db)):
    plans=db.query(PlanTemplate).order_by(PlanTemplate.sort_order).all()
    sections={}
    for p in plans:
        sections.setdefault(p.section,[]).append({"plan_id":p.plan_id,"label":p.label,"subtitle":p.subtitle,"icon":p.icon,"color":p.color_hex,"icon_color":p.icon_color_hex})
    return {"sections":sections,"total":len(plans)}

@app.get("/api/plans/{plan_id}")
def plan_detail(plan_id: str, db: Session = Depends(get_db)):
    plan=db.query(PlanTemplate).filter_by(plan_id=plan_id).first()
    if not plan: raise HTTPException(404,"Plan not found")
    return {
        "plan_id":plan.plan_id,"label":plan.label,"subtitle":plan.subtitle,
        "icon":plan.icon,"color":plan.color_hex,"icon_color":plan.icon_color_hex,"section":plan.section,
        "questions":[{"step":q.step_no,"question":q.question,"field_key":q.field_key,"type":q.input_type,"options":q.options} for q in sorted(plan.questions,key=lambda x:x.step_no)],
        "free_insights":[fi.text for fi in sorted(plan.free_insights,key=lambda x:x.sort_order)],
        "premium_items":[{"title":pi.title,"subtitle":pi.subtitle} for pi in sorted(plan.premium_items,key=lambda x:x.sort_order)],
    }

class PlanCalcRequest(BaseModel):
    inputs: dict

@app.post("/api/plans/{plan_id}/calculate")
def calculate_plan(plan_id: str, req: PlanCalcRequest, db: Session = Depends(get_db)):
    plan=db.query(PlanTemplate).filter_by(plan_id=plan_id).first()
    if not plan: raise HTTPException(404,"Plan not found")
    results=calc_results(plan_id,req.inputs)
    free_tips=[fi.text for fi in sorted(plan.free_insights,key=lambda x:x.sort_order)]
    prem_items=[{"title":pi.title,"subtitle":pi.subtitle} for pi in sorted(plan.premium_items,key=lambda x:x.sort_order)]
    return {"plan_id":plan_id,"label":plan.label,"inputs":req.inputs,"results":results,"free_insights":free_tips,"premium_items":prem_items}

@app.get("/api/hacks")
def hacks(category: Optional[str]=None, db: Session = Depends(get_db)):
    q=db.query(MoneyHack).order_by(MoneyHack.sort_order)
    if category: q=q.filter(MoneyHack.category==category.upper())
    return [{"id":h.id,"category":h.category,"headline":h.headline,"detail":h.detail,"saving_amt":h.saving_amt,"saving_period":h.saving_period} for h in q.all()]

@app.get("/api/bulletins")
def bulletins(db: Session = Depends(get_db)):
    return [{"id":b.id,"category":b.category,"city":b.city,"headline":b.headline,"detail":b.detail,"change_pct":b.change_pct,"period":b.period} for b in db.query(PriceBulletin).order_by(PriceBulletin.sort_order).all()]

@app.get("/api/cities")
def cities(q: Optional[str]=None, db: Session = Depends(get_db)):
    from sqlalchemy import distinct as sqldistinct
    cq=db.query(sqldistinct(PriceRecord.city)).order_by(PriceRecord.city)
    if q: cq=cq.filter(PriceRecord.city.ilike(f"%{q}%"))
    return {"cities":[r[0] for r in cq.limit(50).all()],"total":db.query(PriceRecord.city).distinct().count()}

@app.get("/api/health")
def health():
    return {"status":"ok","app":"MoneyMind API","version":"3.0.0","cities":1062,"products":36,"plans":12}

# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS — protected by ADMIN_SECRET header
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/admin/stats")
def admin_stats(db: Session = Depends(get_db), _=Depends(verify_admin)):
    from sqlalchemy import text
    from database import engine
    with engine.connect() as conn:
        leads_count = conn.execute(text("SELECT COUNT(*) FROM leads")).scalar()
        recent_leads = conn.execute(text("SELECT phone, plan_name, city, created_at FROM leads ORDER BY created_at DESC LIMIT 20")).fetchall()
    searches = db.query(SearchLog).count()
    return {
        "total_leads": leads_count,
        "total_searches": searches,
        "recent_leads": [{"phone":r[0],"plan_name":r[1],"city":r[2],"created_at":r[3]} for r in recent_leads],
        "categories": db.query(Category).count(),
        "products": db.query(Product).count(),
        "hacks": db.query(MoneyHack).count(),
        "bulletins": db.query(PriceBulletin).count(),
        "cities": db.query(PriceRecord.city).distinct().count(),
    }

# ── Categories CRUD ───────────────────────────────────────────────────────────
@app.get("/api/admin/categories")
def admin_list_categories(db: Session = Depends(get_db), _=Depends(verify_admin)):
    cats=db.query(Category).order_by(Category.sort_order).all()
    return [{"id":c.id,"name":c.name,"slug":c.slug,"icon":c.icon,"subtitle":c.subtitle,"section":c.section,"sort_order":c.sort_order,"product_count":len(c.products)} for c in cats]

class CategoryCreate(BaseModel):
    name: str; slug: str; icon: str; subtitle: str; section: str; sort_order: int = 99

@app.post("/api/admin/categories")
def admin_create_category(data: CategoryCreate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    existing=db.query(Category).filter_by(slug=data.slug).first()
    if existing: raise HTTPException(400,f"Slug '{data.slug}' already exists")
    cat=Category(**data.dict()); db.add(cat); db.commit(); db.refresh(cat)
    return {"success":True,"id":cat.id,"name":cat.name}

class CategoryUpdate(BaseModel):
    name: Optional[str]=None; icon: Optional[str]=None; subtitle: Optional[str]=None; section: Optional[str]=None; sort_order: Optional[int]=None

@app.put("/api/admin/categories/{cat_id}")
def admin_update_category(cat_id: int, data: CategoryUpdate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    cat=db.query(Category).filter_by(id=cat_id).first()
    if not cat: raise HTTPException(404,"Category not found")
    for k,v in data.dict(exclude_none=True).items(): setattr(cat,k,v)
    db.commit()
    return {"success":True,"id":cat.id,"name":cat.name}

@app.delete("/api/admin/categories/{cat_id}")
def admin_delete_category(cat_id: int, db: Session = Depends(get_db), _=Depends(verify_admin)):
    cat=db.query(Category).filter_by(id=cat_id).first()
    if not cat: raise HTTPException(404,"Category not found")
    db.delete(cat); db.commit()
    return {"success":True}

# ── Money Hacks CRUD ──────────────────────────────────────────────────────────
class HackCreate(BaseModel):
    category: str; headline: str; detail: str; saving_amt: str; saving_period: str; sort_order: int = 99

@app.get("/api/admin/hacks")
def admin_list_hacks(db: Session = Depends(get_db), _=Depends(verify_admin)):
    """Added — the admin panel needs to list existing hacks before editing/deleting them."""
    return [{"id": h.id, "category": h.category, "headline": h.headline, "detail": h.detail,
             "saving_amt": h.saving_amt, "saving_period": h.saving_period, "sort_order": h.sort_order}
            for h in db.query(MoneyHack).order_by(MoneyHack.sort_order).all()]

@app.post("/api/admin/hacks")
def admin_create_hack(data: HackCreate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    hack=MoneyHack(**data.dict()); db.add(hack); db.commit(); db.refresh(hack)
    return {"success":True,"id":hack.id}

class HackUpdate(BaseModel):
    category: Optional[str]=None; headline: Optional[str]=None; detail: Optional[str]=None; saving_amt: Optional[str]=None; saving_period: Optional[str]=None

@app.put("/api/admin/hacks/{hack_id}")
def admin_update_hack(hack_id: int, data: HackUpdate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    hack=db.query(MoneyHack).filter_by(id=hack_id).first()
    if not hack: raise HTTPException(404,"Hack not found")
    for k,v in data.dict(exclude_none=True).items(): setattr(hack,k,v)
    db.commit()
    return {"success":True}

@app.delete("/api/admin/hacks/{hack_id}")
def admin_delete_hack(hack_id: int, db: Session = Depends(get_db), _=Depends(verify_admin)):
    hack=db.query(MoneyHack).filter_by(id=hack_id).first()
    if not hack: raise HTTPException(404,"Hack not found")
    db.delete(hack); db.commit()
    return {"success":True}

# ── Price Bulletins CRUD ──────────────────────────────────────────────────────
class BulletinCreate(BaseModel):
    category: str; city: Optional[str]=None; headline: str; detail: str; change_pct: float; period: str; sort_order: int = 99

@app.get("/api/admin/bulletins")
def admin_list_bulletins(db: Session = Depends(get_db), _=Depends(verify_admin)):
    """Added — the admin panel needs to list existing bulletins before editing/deleting them."""
    return [{"id": b.id, "category": b.category, "city": b.city, "headline": b.headline, "detail": b.detail,
             "change_pct": b.change_pct, "period": b.period, "sort_order": b.sort_order}
            for b in db.query(PriceBulletin).order_by(PriceBulletin.sort_order).all()]

@app.post("/api/admin/bulletins")
def admin_create_bulletin(data: BulletinCreate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    b=PriceBulletin(**data.dict()); db.add(b); db.commit(); db.refresh(b)
    return {"success":True,"id":b.id}

class BulletinUpdate(BaseModel):
    category: Optional[str]=None; city: Optional[str]=None; headline: Optional[str]=None; detail: Optional[str]=None; change_pct: Optional[float]=None; period: Optional[str]=None

@app.put("/api/admin/bulletins/{bulletin_id}")
def admin_update_bulletin(bulletin_id: int, data: BulletinUpdate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    b=db.query(PriceBulletin).filter_by(id=bulletin_id).first()
    if not b: raise HTTPException(404,"Bulletin not found")
    for k,v in data.dict(exclude_none=True).items(): setattr(b,k,v)
    db.commit()
    return {"success":True}

@app.delete("/api/admin/bulletins/{bulletin_id}")
def admin_delete_bulletin(bulletin_id: int, db: Session = Depends(get_db), _=Depends(verify_admin)):
    b=db.query(PriceBulletin).filter_by(id=bulletin_id).first()
    if not b: raise HTTPException(404,"Bulletin not found")
    db.delete(b); db.commit()
    return {"success":True}

# ── Market Highlights CRUD ────────────────────────────────────────────────────
class HighlightUpdate(BaseModel):
    label: Optional[str]=None; value: Optional[str]=None; change: Optional[str]=None; is_up: Optional[bool]=None

@app.get("/api/admin/highlights")
def admin_list_highlights(db: Session = Depends(get_db), _=Depends(verify_admin)):
    return [{"id":h.id,"label":h.label,"value":h.value,"change":h.change,"is_up":h.is_up} for h in db.query(MarketHighlight).order_by(MarketHighlight.sort_order).all()]

@app.put("/api/admin/highlights/{hid}")
def admin_update_highlight(hid: int, data: HighlightUpdate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    h=db.query(MarketHighlight).filter_by(id=hid).first()
    if not h: raise HTTPException(404,"Highlight not found")
    for k,v in data.dict(exclude_none=True).items(): setattr(h,k,v)
    db.commit()
    return {"success":True}

class HighlightCreate(BaseModel):
    label: str; value: str; change: str = ""; is_up: bool = True; sort_order: int = 99

@app.post("/api/admin/highlights")
def admin_create_highlight(data: HighlightCreate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    """Added — admin previously had no way to add a new ticker entry, only edit existing ones."""
    h = MarketHighlight(**data.dict())
    db.add(h); db.commit(); db.refresh(h)
    return {"success": True, "id": h.id}

@app.delete("/api/admin/highlights/{hid}")
def admin_delete_highlight(hid: int, db: Session = Depends(get_db), _=Depends(verify_admin)):
    """Added — admin previously had no way to remove a ticker entry."""
    h = db.query(MarketHighlight).filter_by(id=hid).first()
    if not h: raise HTTPException(404, "Highlight not found")
    db.delete(h); db.commit()
    return {"success": True}

# ── Trending Searches CRUD ────────────────────────────────────────────────────
class TrendingCreate(BaseModel):
    query: str; city: Optional[str]=None; count: int=100; sort_order: int=99

@app.get("/api/admin/trending")
def admin_list_trending(db: Session = Depends(get_db), _=Depends(verify_admin)):
    return [{"id":t.id,"query":t.query,"city":t.city,"count":t.count} for t in db.query(TrendingSearch).order_by(TrendingSearch.sort_order).all()]

@app.post("/api/admin/trending")
def admin_create_trending(data: TrendingCreate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    t=TrendingSearch(**data.dict()); db.add(t); db.commit(); db.refresh(t)
    return {"success":True,"id":t.id}

@app.delete("/api/admin/trending/{tid}")
def admin_delete_trending(tid: int, db: Session = Depends(get_db), _=Depends(verify_admin)):
    t=db.query(TrendingSearch).filter_by(id=tid).first()
    if not t: raise HTTPException(404,"Not found")
    db.delete(t); db.commit()
    return {"success":True}

# ── Leads ─────────────────────────────────────────────────────────────────────
@app.get("/api/admin/leads")
def admin_list_leads(_=Depends(verify_admin)):
    from sqlalchemy import text
    from database import engine
    with engine.connect() as conn:
        rows=conn.execute(text("SELECT id,phone,plan_id,plan_name,city,created_at FROM leads ORDER BY created_at DESC")).fetchall()
    return [{"id":r[0],"phone":r[1],"plan_id":r[2],"plan_name":r[3],"city":r[4],"created_at":r[5]} for r in rows]

# ── Price Edit endpoint (Admin) ───────────────────────────────────────────────
class PriceUpdateRequest(BaseModel):
    city: str
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    fair_min: Optional[float] = None
    fair_max: Optional[float] = None
    premium_min: Optional[float] = None
    premium_max: Optional[float] = None
    avg_price: Optional[float] = None

@app.put("/api/admin/prices/{product_slug}")
def admin_update_price(product_slug: str, data: PriceUpdateRequest,
                       db: Session = Depends(get_db), _=Depends(verify_admin)):
    p = db.query(Product).filter_by(slug=product_slug).first()
    if not p:
        raise HTTPException(404, "Product not found")
    pr = db.query(PriceRecord).filter_by(product_id=p.id, city=data.city).first()
    if not pr:
        pr = PriceRecord(product_id=p.id, city=data.city)
        db.add(pr)
    for field in ["budget_min","budget_max","fair_min","fair_max",
                  "premium_min","premium_max","avg_price"]:
        val = getattr(data, field)
        if val is not None:
            setattr(pr, field, val)
    db.commit()
    return {"success": True, "product": product_slug, "city": data.city}

# ── Admin Products list (for price manager) ───────────────────────────────────
@app.get("/api/admin/products")
def admin_list_products(city: str = "Mumbai", db: Session = Depends(get_db), _=Depends(verify_admin)):
    products = db.query(Product).order_by(Product.name).all()
    result = []
    for p in products:
        pr = (db.query(PriceRecord).filter_by(product_id=p.id, city=city).first()
              or db.query(PriceRecord).filter_by(product_id=p.id).first())
        result.append({
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "unit": p.unit,
            "category": p.category.name if p.category else "—",
            "is_popular": p.is_popular,
            "price": {
                "budget_min": pr.budget_min, "budget_max": pr.budget_max,
                "fair_min": pr.fair_min, "fair_max": pr.fair_max,
                "premium_min": pr.premium_min, "premium_max": pr.premium_max,
                "avg_price": pr.avg_price,
            } if pr else None
        })
    return {"products": result, "city": city, "total": len(result)}

# ══════════════════════════════════════════════════════════════════════════════
# PLANNING ADMIN ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

class PlanInfoUpdate(BaseModel):
    label: Optional[str]=None
    subtitle: Optional[str]=None
    icon: Optional[str]=None
    section: Optional[str]=None
    color_hex: Optional[str]=None
    sort_order: Optional[int]=None

class QuestionCreate(BaseModel):
    plan_id: str
    step_no: int
    question: str
    field_key: str
    input_type: str = "choice"
    options: Optional[list] = None

class QuestionUpdate(BaseModel):
    question: Optional[str]=None
    field_key: Optional[str]=None
    input_type: Optional[str]=None
    options: Optional[list]=None
    step_no: Optional[int]=None

class InsightCreate(BaseModel):
    plan_id: str
    text: str
    sort_order: int = 0

class InsightUpdate(BaseModel):
    text: str

class PremiumItemCreate(BaseModel):
    plan_id: str
    title: str
    subtitle: str
    sort_order: int = 0

class PremiumItemUpdate(BaseModel):
    title: Optional[str]=None
    subtitle: Optional[str]=None

# ── Plan list for admin ───────────────────────────────────────────────────────
@app.get("/api/admin/plans")
def admin_list_plans(db: Session = Depends(get_db), _=Depends(verify_admin)):
    plans = db.query(PlanTemplate).order_by(PlanTemplate.sort_order).all()
    return {"plans": [{
        "plan_id": p.plan_id, "label": p.label, "subtitle": p.subtitle,
        "icon": p.icon, "section": p.section, "color": p.color_hex,
        "sort_order": p.sort_order,
        "questions": len(p.questions),
        "free_insights": len(p.free_insights),
        "premium_items": len(p.premium_items),
    } for p in plans]}

# ── Full plan detail for admin ────────────────────────────────────────────────
@app.get("/api/admin/plan-detail/{plan_id}")
def admin_plan_detail(plan_id: str, db: Session = Depends(get_db), _=Depends(verify_admin)):
    p = db.query(PlanTemplate).filter_by(plan_id=plan_id).first()
    if not p: raise HTTPException(404, "Plan not found")
    return {
        "plan_id": p.plan_id, "label": p.label, "subtitle": p.subtitle,
        "icon": p.icon, "section": p.section, "color": p.color_hex,
        "sort_order": p.sort_order,
        "questions": [{"id":q.id,"step_no":q.step_no,"question":q.question,
                        "field_key":q.field_key,"input_type":q.input_type,"options":q.options}
                       for q in sorted(p.questions, key=lambda x: x.step_no)],
        "free_insights": [{"id":fi.id,"text":fi.text,"sort_order":fi.sort_order}
                           for fi in sorted(p.free_insights, key=lambda x: x.sort_order)],
        "premium_items": [{"id":pi.id,"title":pi.title,"subtitle":pi.subtitle,"sort_order":pi.sort_order}
                           for pi in sorted(p.premium_items, key=lambda x: x.sort_order)],
    }

# ── Update plan info ──────────────────────────────────────────────────────────
@app.put("/api/admin/plans/{plan_id}")
def admin_update_plan(plan_id: str, data: PlanInfoUpdate,
                       db: Session = Depends(get_db), _=Depends(verify_admin)):
    p = db.query(PlanTemplate).filter_by(plan_id=plan_id).first()
    if not p: raise HTTPException(404, "Plan not found")
    for k,v in data.dict(exclude_none=True).items(): setattr(p,k,v)
    db.commit()
    return {"success": True}

# ── Questions CRUD ────────────────────────────────────────────────────────────
@app.post("/api/admin/questions")
def admin_create_question(data: QuestionCreate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    p = db.query(PlanTemplate).filter_by(plan_id=data.plan_id).first()
    if not p: raise HTTPException(404, "Plan not found")
    q = PlanQuestion(plan_id=p.id, step_no=data.step_no, question=data.question,
                     field_key=data.field_key, input_type=data.input_type, options=data.options or [])
    db.add(q); db.commit(); db.refresh(q)
    return {"success": True, "id": q.id}

@app.put("/api/admin/questions/{q_id}")
def admin_update_question(q_id: int, data: QuestionUpdate,
                           db: Session = Depends(get_db), _=Depends(verify_admin)):
    q = db.query(PlanQuestion).filter_by(id=q_id).first()
    if not q: raise HTTPException(404, "Question not found")
    for k,v in data.dict(exclude_none=True).items(): setattr(q,k,v)
    db.commit()
    return {"success": True}

@app.delete("/api/admin/questions/{q_id}")
def admin_delete_question(q_id: int, db: Session = Depends(get_db), _=Depends(verify_admin)):
    q = db.query(PlanQuestion).filter_by(id=q_id).first()
    if not q: raise HTTPException(404)
    db.delete(q); db.commit()
    return {"success": True}

# ── Free Insights CRUD ────────────────────────────────────────────────────────
@app.post("/api/admin/insights")
def admin_create_insight(data: InsightCreate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    p = db.query(PlanTemplate).filter_by(plan_id=data.plan_id).first()
    if not p: raise HTTPException(404)
    fi = PlanFreeInsight(plan_id=p.id, text=data.text, sort_order=data.sort_order)
    db.add(fi); db.commit(); db.refresh(fi)
    return {"success": True, "id": fi.id}

@app.put("/api/admin/insights/{fi_id}")
def admin_update_insight(fi_id: int, data: InsightUpdate,
                          db: Session = Depends(get_db), _=Depends(verify_admin)):
    fi = db.query(PlanFreeInsight).filter_by(id=fi_id).first()
    if not fi: raise HTTPException(404)
    fi.text = data.text; db.commit()
    return {"success": True}

@app.delete("/api/admin/insights/{fi_id}")
def admin_delete_insight(fi_id: int, db: Session = Depends(get_db), _=Depends(verify_admin)):
    fi = db.query(PlanFreeInsight).filter_by(id=fi_id).first()
    if not fi: raise HTTPException(404)
    db.delete(fi); db.commit()
    return {"success": True}

# ── Premium Items CRUD ────────────────────────────────────────────────────────
@app.post("/api/admin/premium-items")
def admin_create_premium(data: PremiumItemCreate, db: Session = Depends(get_db), _=Depends(verify_admin)):
    p = db.query(PlanTemplate).filter_by(plan_id=data.plan_id).first()
    if not p: raise HTTPException(404)
    pi = PlanPremiumItem(plan_id=p.id, title=data.title, subtitle=data.subtitle, sort_order=data.sort_order)
    db.add(pi); db.commit(); db.refresh(pi)
    return {"success": True, "id": pi.id}

@app.put("/api/admin/premium-items/{pi_id}")
def admin_update_premium(pi_id: int, data: PremiumItemUpdate,
                          db: Session = Depends(get_db), _=Depends(verify_admin)):
    pi = db.query(PlanPremiumItem).filter_by(id=pi_id).first()
    if not pi: raise HTTPException(404)
    for k,v in data.dict(exclude_none=True).items(): setattr(pi,k,v)
    db.commit()
    return {"success": True}

@app.delete("/api/admin/premium-items/{pi_id}")
def admin_delete_premium(pi_id: int, db: Session = Depends(get_db), _=Depends(verify_admin)):
    pi = db.query(PlanPremiumItem).filter_by(id=pi_id).first()
    if not pi: raise HTTPException(404)
    db.delete(pi); db.commit()
    return {"success": True}

# ══════════════════════════════════════════════════════════════════════════════
# CALCULATOR CONFIG — enable/disable individual calculators from admin
# Stored as a JSON file on the server (no DB table needed)
# ══════════════════════════════════════════════════════════════════════════════
CALC_CONFIG_FILE = "calculator_config.json"

def load_calc_config():
    """Load calculator config from JSON file, return dict {calc_id: {enabled, label}}"""
    if os.path.exists(CALC_CONFIG_FILE):
        try:
            with open(CALC_CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_calc_config(config: dict):
    with open(CALC_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

class CalcConfigUpdate(BaseModel):
    calculator_id: str
    enabled: bool

class BulkCalcConfigUpdate(BaseModel):
    config: dict  # {calc_id: {"enabled": bool}}

@app.get("/api/calculators/config")
def get_calc_config():
    """Public endpoint — app reads this on load to know which calculators are enabled"""
    return {"config": load_calc_config()}

@app.put("/api/admin/calculators/config")
def update_calc_config_bulk(data: BulkCalcConfigUpdate, _=Depends(verify_admin)):
    """Save full calculator config dict from admin panel"""
    save_calc_config(data.config)
    return {"success": True, "saved": len(data.config)}

@app.put("/api/admin/calculators/{calc_id}/toggle")
def toggle_calculator(calc_id: str, data: CalcConfigUpdate, _=Depends(verify_admin)):
    """Toggle a single calculator on or off"""
    config = load_calc_config()
    if calc_id not in config:
        config[calc_id] = {}
    config[calc_id]["enabled"] = data.enabled
    save_calc_config(config)
    return {"success": True, "calculator_id": calc_id, "enabled": data.enabled}


# ══════════════════════════════════════════════════════════════════════════════
# NEW — 50-calculator Planning rebuild with admin formula editor.
# Distinct from the CALC_CONFIG_FILE toggle system above (that's a simple
# enable/disable flag file; this is the actual calculator data + math, stored
# in the database via the new Calculator model). Purely additive — nothing
# above this line was changed.
# ══════════════════════════════════════════════════════════════════════════════

class CalculatorIn(BaseModel):
    slug: str
    name: str
    category: str
    icon: str = "🧮"
    description: str = ""
    is_featured: bool = False
    featured_order: int = 0
    featured_group: Optional[str] = None
    sort_order: int = 0
    active: bool = True
    inputs: list
    formula: str
    formula_steps: Optional[list] = []
    outputs: list
    constants: Optional[dict] = {}


class CalculatorRunRequest(BaseModel):
    values: dict


class FormulaValidateRequest(BaseModel):
    formula: str
    known_vars: list


# ── Public: list + run calculators ──────────────────────────────────────────
@app.get("/api/calculators")
def list_calculators(db: Session = Depends(get_db)):
    """
    All active calculators for the Planning screen, plus the 5 (or fewer) featured
    home-screen tiles. Calculators sharing a `featured_group` collapse into ONE tile
    with multiple modes (e.g. Fresh Loan + Refinance under one tile).
    """
    calcs = db.query(Calculator).filter(Calculator.active == True).order_by(Calculator.sort_order).all()
    featured = [c for c in calcs if c.is_featured]
    featured.sort(key=lambda c: c.featured_order)

    featured_tiles = []
    seen_groups = set()
    for c in featured:
        if c.featured_group:
            if c.featured_group in seen_groups:
                continue
            seen_groups.add(c.featured_group)
            modes = [fc for fc in featured if fc.featured_group == c.featured_group]
            featured_tiles.append({
                "tile_id": c.featured_group,
                "name": modes[0].name.split("(")[0].strip() if len(modes) > 1 else modes[0].name,
                "icon": modes[0].icon,
                "is_multi_mode": True,
                "modes": [{"slug": m.slug, "label": m.name, "icon": m.icon} for m in modes],
            })
        else:
            featured_tiles.append({
                "tile_id": c.slug, "name": c.name, "icon": c.icon,
                "is_multi_mode": False,
                "modes": [{"slug": c.slug, "label": c.name, "icon": c.icon}],
            })

    by_category = {}
    for c in calcs:
        by_category.setdefault(c.category, []).append({
            "slug": c.slug, "name": c.name, "icon": c.icon,
            "description": c.description, "category": c.category,
        })

    return {"featured": featured_tiles, "categories": by_category, "total": len(calcs)}


@app.get("/api/calculators/{slug}")
def get_calculator(slug: str, db: Session = Depends(get_db)):
    c = db.query(Calculator).filter(Calculator.slug == slug, Calculator.active == True).first()
    if not c:
        raise HTTPException(404, "Calculator not found")
    return {
        "slug": c.slug, "name": c.name, "icon": c.icon, "category": c.category,
        "description": c.description, "inputs": c.inputs, "outputs": c.outputs,
    }


@app.post("/api/calculators/{slug}/run")
def run_calculator_endpoint(slug: str, payload: CalculatorRunRequest, db: Session = Depends(get_db)):
    c = db.query(Calculator).filter(Calculator.slug == slug, Calculator.active == True).first()
    if not c:
        raise HTTPException(404, "Calculator not found")

    values = {}
    for inp in c.inputs:
        key = inp["key"]
        values[key] = payload.values.get(key, inp.get("default", 0))

    try:
        result_vars = run_calculator(values, c.formula_steps, c.formula, c.constants)
    except FormulaError as e:
        raise HTTPException(500, f"Calculation error: {e}")

    outputs = {out["key"]: result_vars.get(out["key"]) for out in c.outputs}
    return {"slug": slug, "inputs_used": values, "outputs": outputs}


# ── Admin: full CRUD + formula editor support ───────────────────────────────
@app.get("/api/admin/calculators-v2")
def admin_list_calculators_v2(db: Session = Depends(get_db), _=Depends(verify_admin)):
    """
    Named -v2 to avoid any collision with the existing /api/admin/calculators/config
    toggle-file system above. Returns full calculator data incl. formulas, for the
    admin panel's formula editor.
    """
    calcs = db.query(Calculator).order_by(Calculator.category, Calculator.sort_order).all()
    return [{
        "id": c.id, "slug": c.slug, "name": c.name, "category": c.category, "icon": c.icon,
        "description": c.description, "is_featured": c.is_featured, "featured_order": c.featured_order,
        "featured_group": c.featured_group, "sort_order": c.sort_order, "active": c.active,
        "inputs": c.inputs, "formula": c.formula, "formula_steps": c.formula_steps,
        "outputs": c.outputs, "constants": c.constants,
    } for c in calcs]


@app.get("/api/admin/calculators-v2/{slug}")
def admin_get_calculator_v2(slug: str, db: Session = Depends(get_db), _=Depends(verify_admin)):
    c = db.query(Calculator).filter(Calculator.slug == slug).first()
    if not c:
        raise HTTPException(404, "Calculator not found")
    return {
        "id": c.id, "slug": c.slug, "name": c.name, "category": c.category, "icon": c.icon,
        "description": c.description, "is_featured": c.is_featured, "featured_order": c.featured_order,
        "featured_group": c.featured_group, "sort_order": c.sort_order, "active": c.active,
        "inputs": c.inputs, "formula": c.formula, "formula_steps": c.formula_steps,
        "outputs": c.outputs, "constants": c.constants,
    }


@app.put("/api/admin/calculators-v2/{slug}")
def admin_update_calculator_v2(slug: str, payload: CalculatorIn, db: Session = Depends(get_db), _=Depends(verify_admin)):
    c = db.query(Calculator).filter(Calculator.slug == slug).first()
    if not c:
        raise HTTPException(404, "Calculator not found")

    known_vars = [i["key"] for i in payload.inputs] + list((payload.constants or {}).keys())
    for step in (payload.formula_steps or []):
        known_vars.append(step.get("var"))

    for step in (payload.formula_steps or []):
        check = validate_formula_syntax(step["expr"], known_vars)
        if not check["valid"]:
            raise HTTPException(400, f"Invalid formula in step '{step.get('var')}': {check['error']}")
    final_check = validate_formula_syntax(payload.formula, known_vars)
    if not final_check["valid"]:
        raise HTTPException(400, f"Invalid final formula: {final_check['error']}")

    for field, value in payload.dict().items():
        setattr(c, field, value)
    db.commit()
    return {"success": True, "slug": c.slug}


@app.post("/api/admin/calculators-v2")
def admin_create_calculator_v2(payload: CalculatorIn, db: Session = Depends(get_db), _=Depends(verify_admin)):
    existing = db.query(Calculator).filter(Calculator.slug == payload.slug).first()
    if existing:
        raise HTTPException(400, "A calculator with this slug already exists")

    known_vars = [i["key"] for i in payload.inputs] + list((payload.constants or {}).keys())
    for step in (payload.formula_steps or []):
        known_vars.append(step.get("var"))
    final_check = validate_formula_syntax(payload.formula, known_vars)
    if not final_check["valid"]:
        raise HTTPException(400, f"Invalid formula: {final_check['error']}")

    c = Calculator(**payload.dict())
    db.add(c)
    db.commit()
    return {"success": True, "slug": c.slug}


@app.delete("/api/admin/calculators-v2/{slug}")
def admin_delete_calculator_v2(slug: str, db: Session = Depends(get_db), _=Depends(verify_admin)):
    c = db.query(Calculator).filter(Calculator.slug == slug).first()
    if not c:
        raise HTTPException(404, "Calculator not found")
    db.delete(c)
    db.commit()
    return {"success": True}


@app.post("/api/admin/calculators-v2/validate-formula")
def admin_validate_formula_v2(payload: FormulaValidateRequest, _=Depends(verify_admin)):
    return validate_formula_syntax(payload.formula, payload.known_vars)


@app.post("/api/admin/calculators-v2/{slug}/test-run")
def admin_test_run_calculator_v2(slug: str, payload: CalculatorRunRequest, db: Session = Depends(get_db), _=Depends(verify_admin)):
    c = db.query(Calculator).filter(Calculator.slug == slug).first()
    if not c:
        raise HTTPException(404, "Calculator not found")
    try:
        result_vars = run_calculator(payload.values, c.formula_steps, c.formula, c.constants)
    except FormulaError as e:
        raise HTTPException(400, str(e))
    return {"all_variables": result_vars}


# ══════════════════════════════════════════════════════════════════════════════
# ONE-TIME SEED TRIGGER — visit this URL once in a browser to populate the
# `calculators` table on Render's free tier, which has no Shell access.
# Safe to call multiple times (seed() updates existing rows rather than
# duplicating them). Safe to delete this endpoint after you've used it once.
# Usage: https://your-backend.onrender.com/api/admin/seed-calculators?key=YOUR_ADMIN_SECRET
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/api/admin/seed-calculators")
def trigger_seed_calculators(key: str, db: Session = Depends(get_db)):
    if key != ADMIN_SECRET:
        raise HTTPException(401, "Invalid key")
    from seed_calculators import seed
    seed(db)
    count = db.query(Calculator).count()
    return {"success": True, "message": f"Seeded calculators. Total now in database: {count}"}
