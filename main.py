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
    PlanPremiumItem, ExpenseCategory, ExpenseRule, SearchLog,
)

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
