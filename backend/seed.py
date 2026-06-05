from database import SessionLocal, init_db
from models import (
    Category, Product, PriceRecord, CostBreakdown, VendorQuestion,
    PriceTrend, Insight, TrendingSearch, MarketHighlight, MoneyHack,
    PriceBulletin, PlanTemplate, PlanQuestion, PlanFreeInsight,
    PlanPremiumItem, ExpenseCategory, ExpenseRule, SearchLog
)
from datetime import datetime, timedelta

MONTHS = ["Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun"]
CITIES = ["Mumbai","Delhi","Bengaluru","Hyderabad","Pune","Chennai"]

def seed():
    init_db()
    db = SessionLocal()
    for m in [ExpenseRule, ExpenseCategory, PlanPremiumItem, PlanFreeInsight,
              PlanQuestion, PlanTemplate, PriceBulletin, MoneyHack,
              MarketHighlight, TrendingSearch, Insight, PriceTrend,
              VendorQuestion, CostBreakdown, PriceRecord, Product, Category, SearchLog]:
        db.query(m).delete()
    db.commit()

    # ── CATEGORIES ────────────────────────────────────────────────
    cat_data = [
        ("Home Services",     "home-services",     "🏠", "Painting, plumbing, electrician",    "Home & Living"),
        ("Real Estate",       "real-estate",       "🏢", "Rent, buy, PG, co-living",           "Home & Living"),
        ("Renovation",        "renovation",        "🔧", "Modular kitchen, interiors, flooring","Home & Living"),
        ("Furniture",         "furniture",         "🛋️","Sofas, beds, wardrobes, study",       "Home & Living"),
        ("Appliances",        "appliances",        "❄️","AC, fridge, washing machine",         "Home & Living"),
        ("Utilities",         "utilities",         "💡","Electricity, water, gas cylinder",     "Home & Living"),
        ("Grocery",           "grocery",           "🥦","Vegetables, dal, oil, atta, dairy",    "Daily Needs"),
        ("Kirana Staples",    "kirana",            "🏪","Rice, wheat, sugar, spices, tea",      "Daily Needs"),
        ("Dairy & Eggs",      "dairy",             "🥛","Milk, paneer, curd, eggs, butter",     "Daily Needs"),
        ("Non-Veg",           "non-veg",           "🍗","Chicken, fish, mutton, seafood",       "Daily Needs"),
        ("Car Ownership",     "car-ownership",     "🚗","Service, insurance, repair, EMI",      "Vehicles & Transport"),
        ("Two-Wheeler",       "two-wheeler",       "🏍️","Bike service, tyres, insurance",       "Vehicles & Transport"),
        ("Fuel",              "fuel",              "⛽","Petrol, diesel, CNG city rates",        "Vehicles & Transport"),
        ("Commute",           "commute",           "🚌","Auto fare, cab rates, metro pass",     "Vehicles & Transport"),
        ("Smartphones",       "smartphones",       "📱","iPhones, Android, feature phones",     "Technology"),
        ("Computers",         "computers",         "💻","Laptops, desktops, tablets",           "Technology"),
        ("Internet & DTH",    "internet-dth",      "📡","Broadband, mobile data, DTH plans",    "Technology"),
        ("Electronics",       "electronics",       "📺","TVs, cameras, audio, accessories",     "Technology"),
        ("Doctors",           "doctors",           "🩺","GP, specialists, online consult",      "Health & Wellness"),
        ("Diagnostics",       "diagnostics",       "🧪","Blood tests, scans, checkup packages", "Health & Wellness"),
        ("Medicines",         "medicines",         "💊","Generic vs branded, pharmacy rates",   "Health & Wellness"),
        ("Fitness",           "fitness",           "💪","Gym, yoga, Zumba, personal trainer",   "Health & Wellness"),
        ("School Fees",       "school-fees",       "🏫","CBSE, ICSE, state board comparisons",  "Education & Kids"),
        ("Tuitions",          "tuitions",          "✏️","JEE, NEET, IAS, board exams",          "Education & Kids"),
        ("Skill Courses",     "skill-courses",     "🎓","Coding, design, MBA prep, language",   "Education & Kids"),
        ("Baby & Kids",       "baby-kids",         "👶","Diapers, formula, daycare, toys",      "Education & Kids"),
        ("Flights",           "flights",           "✈️","Domestic routes, fare benchmarks",     "Travel & Tourism"),
        ("Train Travel",      "train-travel",      "🚂","Sleeper, 3AC, 2AC, Vande Bharat",      "Travel & Tourism"),
        ("Hotels & Stay",     "hotels",            "🛏️","Budget, 3-star, 5-star benchmarks",    "Travel & Tourism"),
        ("Tour Packages",     "tour-packages",     "🗺️","Goa, Kerala, Rajasthan, Himachal",     "Travel & Tourism"),
        ("International",     "international",     "🌍","Bali, Dubai, Thailand, Europe",        "Travel & Tourism"),
        ("Pilgrimage",        "pilgrimage",        "🙏","Char Dham, Vaishno Devi, Tirupati",    "Travel & Tourism"),
        ("Weddings",          "weddings",          "💍","Venue, catering, decor, photography",  "Life Events"),
        ("Celebrations",      "celebrations",      "🎉","Birthday, naming, puja, anniversary",  "Life Events"),
        ("Loans & EMI",       "loans",             "🏧","Home, car, personal loan rates",       "Life Events"),
        ("Insurance",         "insurance-cat",     "🛡️","Health, term, car, home premiums",     "Life Events"),
        ("Salon & Grooming",  "salon",             "✂️","Haircut, waxing, facial, bridal",      "Beauty & Fashion"),
        ("Clothing",          "clothing",          "👗","Sarees, suits, western, kids wear",    "Beauty & Fashion"),
        ("Jewellery",         "jewellery",         "💎","Gold, silver, diamond making charges", "Beauty & Fashion"),
        ("Skincare",          "skincare",          "✨","Branded vs generic, dermat cost",       "Beauty & Fashion"),
        ("Mutual Funds",      "mutual-funds",      "📈","SIP benchmarks, top fund returns",     "Finance & Investments"),
        ("Fixed Deposits",    "fixed-deposits",    "🏦","Bank FD rates, post office schemes",   "Finance & Investments"),
        ("Savings Schemes",   "savings-schemes",   "🐷","PPF, NPS, Sukanya, SSY rates",         "Finance & Investments"),
        ("Gold & Commodities","gold-commodities",  "🥇","Physical gold, SGB, digital gold",     "Finance & Investments"),
        ("OTT Platforms",     "ott",               "▶️","Netflix, Prime, Hotstar, Sony LIV",    "Subscriptions & Digital"),
        ("Mobile Recharge",   "mobile-recharge",   "📲","Jio, Airtel, Vi prepaid plans",        "Subscriptions & Digital"),
    ]
    cats = {}
    for i,(name,slug,icon,sub,section) in enumerate(cat_data):
        c = Category(name=name,slug=slug,icon=icon,subtitle=sub,section=section,sort_order=i)
        db.add(c); db.flush(); cats[slug]=c

    # ── HELPER ────────────────────────────────────────────────────
    def add_product(name,slug,cat_slug,unit,tags,popular,cities_data,breakdown,questions,trends_mumbai,insights_list):
        p = Product(name=name,slug=slug,category_id=cats[cat_slug].id,unit=unit,tags=tags,is_popular=popular)
        db.add(p); db.flush()
        for city,(bmin,bmax,fmin,fmax,pmin,pmax,avg) in cities_data.items():
            db.add(PriceRecord(product_id=p.id,city=city,budget_min=bmin,budget_max=bmax,
                fair_min=fmin,fair_max=fmax,premium_min=pmin,premium_max=pmax,avg_price=avg))
        for i,(lbl,mn,mx,pct) in enumerate(breakdown):
            db.add(CostBreakdown(product_id=p.id,label=lbl,min_val=mn,max_val=mx,percent=pct,sort_order=i))
        for i,q in enumerate(questions):
            db.add(VendorQuestion(product_id=p.id,question=q,sort_order=i))
        for i,(mo,pr) in enumerate(zip(MONTHS,trends_mumbai)):
            db.add(PriceTrend(product_id=p.id,city="Mumbai",month_label=mo,price=pr,sort_order=i))
        for i,t in enumerate(insights_list):
            db.add(Insight(product_id=p.id,text=t,sort_order=i))

    # ══════════════════════════════════════════════════════════════
    # HOME SERVICES
    # ══════════════════════════════════════════════════════════════
    add_product("House Painter","house-painter","home-services","per sq ft",
        ["painting","interior","labour","wall","whitewash"],True,
        {"Mumbai":(30,40,38,52,50,65,45),"Delhi":(25,35,32,48,45,60,40),
         "Bengaluru":(28,38,35,50,48,62,42),"Hyderabad":(22,32,30,44,42,55,37),
         "Pune":(26,36,33,48,46,60,40),"Chennai":(20,30,28,40,38,52,34)},
        [("Labour",18,24,None),("Paint (Material)",15,22,None),("Putty + Prep",8,14,None),("Tools & Add-ons",3,6,None)],
        ["Primer coat included?","How many coats of putty?","Material brand specified?","Scaffolding included?"],
        [28,32,35,38,42,43,45,47,48],
        ["Mumbai rates are 10–15% above national average.",
         "Premium paint and prep can justify higher quotes — always ask.",
         "Labour alone should be ₹18–₹24/sq ft in Mumbai.",
         "Get at least 3 quotes before finalising.",
         "Asian Paints Royale vs Tractor Emulsion — price difference is ₹8–12/sq ft."])

    add_product("Modular Kitchen","modular-kitchen","renovation","total estimate",
        ["kitchen","modular","interior","cabinets","shutters"],True,
        {"Mumbai":(120000,160000,160000,240000,240000,360000,200000),
         "Delhi":(100000,140000,140000,210000,210000,320000,175000),
         "Bengaluru":(110000,150000,150000,225000,225000,340000,187000),
         "Hyderabad":(95000,130000,130000,195000,195000,300000,162000),
         "Pune":(105000,145000,145000,215000,215000,330000,180000),
         "Chennai":(90000,125000,125000,185000,185000,280000,155000)},
        [("Cabinets & Carcass",None,None,45),("Shutters",None,None,20),
         ("Hardware",None,None,10),("Countertop",None,None,10),
         ("Accessories",None,None,5),("Installation",None,None,5),("Add-ons",None,None,5)],
        ["Finish type — laminate, acrylic, or PU?","Hardware brand — Hettich or Häfele?",
         "Countertop material?","Appliances included?","Warranty period?"],
        [140000,145000,150000,155000,165000,170000,180000,190000,200000],
        ["Laminate finish is the most budget-friendly at ₹160–240/sq ft.",
         "Acrylic or PU finish increases cost by 20–30%.",
         "Always get an itemised quote broken down by unit.",
         "National brands cost 25–40% more than local fabricators.",
         "Hettich hardware lasts 10+ years — worth the premium over local fittings."])

    add_product("AC Service (Split)","ac-service","appliances","per visit",
        ["AC","air conditioner","service","cooling","repair"],True,
        {"Mumbai":(500,700,700,1200,1200,2000,900),"Delhi":(450,650,650,1100,1100,1800,850),
         "Bengaluru":(480,680,680,1150,1150,1900,870),"Hyderabad":(400,600,600,1000,1000,1700,800),
         "Pune":(460,660,660,1120,1120,1850,860),"Chennai":(380,580,580,980,980,1600,780)},
        [("Gas Refill (if needed)",800,1500,None),("Servicing Labour",400,600,None),
         ("Cleaning & Filter",200,300,None),("Parts (if replaced)",300,1000,None)],
        ["Gas top-up included in price?","Which gas — R22 or R32?",
         "PCB inspection covered?","Any service warranty?"],
        [700,720,750,780,820,850,880,900,920],
        ["Summer quotes are 20–30% higher due to demand surge.",
         "Annual Maintenance Contracts (AMC) are cheaper in the long run.",
         "R32 gas refill costs more than R22.",
         "Book in March to avoid April–May peak pricing."])

    add_product("Plumber Visit","plumber-visit","home-services","per visit",
        ["plumber","plumbing","tap","pipe","leak","drain"],True,
        {"Mumbai":(400,600,600,1000,1000,2000,800),"Delhi":(350,550,550,900,900,1800,750),
         "Bengaluru":(370,570,570,950,950,1900,760),"Hyderabad":(300,500,500,850,850,1700,680),
         "Pune":(360,560,560,920,920,1850,740),"Chennai":(280,480,480,800,800,1600,640)},
        [("Visit/Labour charge",400,800,None),("Parts (if replaced)",200,1200,None),
         ("Miscellaneous",100,300,None)],
        ["Parts included or extra?","Fixed price or per-hour?","Warranty on work?"],
        [650,660,670,700,730,760,780,800,820],
        ["Always agree on a fixed price before work begins.",
         "Platform plumbers (Urban Company) have fixed rates.",
         "Common repairs like tap change should cost ₹400–800.",
         "Avoid paying upfront — pay after work is completed."])

    add_product("Electrician Visit","electrician-visit","home-services","per visit",
        ["electrician","wiring","switch","electrical","repair","fan"],True,
        {"Mumbai":(350,550,550,900,900,1800,720),"Delhi":(300,500,500,850,850,1700,680),
         "Bengaluru":(320,520,520,870,870,1750,695),"Hyderabad":(270,470,470,800,800,1600,635),
         "Pune":(310,510,510,860,860,1720,685),"Chennai":(250,450,450,750,750,1500,600)},
        [("Visit/Labour charge",350,700,None),("Parts & Materials",150,800,None),
         ("Miscellaneous",50,200,None)],
        ["Fixed price or hourly rate?","Parts included or extra?","Warranty on work?"],
        [590,600,610,640,670,695,710,720,730],
        ["Platform electricians have transparent pricing.",
         "Always get written estimate for large electrical jobs.",
         "Night or emergency charges are 1.5–2x normal rates."])

    add_product("Home Deep Cleaning","deep-cleaning","home-services","per BHK",
        ["cleaning","deep clean","housekeeping","sanitise","pest"],False,
        {"Mumbai":(2000,3000,3000,5000,5000,8000,4000),
         "Delhi":(1800,2800,2800,4500,4500,7000,3600),
         "Bengaluru":(1900,2900,2900,4800,4800,7500,3800),
         "Hyderabad":(1600,2500,2500,4200,4200,6500,3300),
         "Pune":(1800,2700,2700,4600,4600,7200,3700),
         "Chennai":(1500,2400,2400,4000,4000,6000,3200)},
        [("Labour (2–4 workers)",1500,2500,None),("Cleaning Products",500,800,None),
         ("Equipment",300,600,None),("Misc",200,400,None)],
        ["How many workers?","Materials included?","Inside cabinets covered?","Duration?"],
        [3200,3400,3600,3700,3800,3900,3950,4000,4050],
        ["Urban Company costs more but workers are background-verified.",
         "Local cleaners can be 40% cheaper with similar quality.",
         "Always confirm if materials are included in quote.",
         "2 BHK typically takes 4–6 hours for thorough cleaning."])

    # ══════════════════════════════════════════════════════════════
    # REAL ESTATE
    # ══════════════════════════════════════════════════════════════
    add_product("2 BHK Rent","2bhk-rent","real-estate","per month",
        ["rent","apartment","2BHK","flat","housing","PG"],True,
        {"Mumbai":(25000,40000,40000,75000,75000,150000,55000),
         "Delhi":(20000,35000,35000,65000,65000,130000,47000),
         "Bengaluru":(18000,32000,32000,60000,60000,120000,44000),
         "Hyderabad":(15000,28000,28000,52000,52000,100000,38000),
         "Pune":(16000,30000,30000,55000,55000,110000,41000),
         "Chennai":(14000,26000,26000,50000,50000,95000,36000)},
        [("Base Rent",None,None,85),("Maintenance",None,None,10),("Parking",None,None,5)],
        ["Maintenance included?","Security deposit — how many months?",
         "Brokerage applicable?","Lock-in period?","Society amenities included?"],
        [48000,50000,51000,52000,53000,54000,54500,55000,55000],
        ["Brokerage is typically 1 month rent — negotiable to 50%.",
         "Direct landlord deals avoid brokerage entirely.",
         "Rental prices vary 30–50% by locality within same city.",
         "Always get security deposit refund terms in the agreement.",
         "Bengaluru has India's most overpriced rentals relative to income — negotiate hard."])

    add_product("3 BHK Rent","3bhk-rent","real-estate","per month",
        ["rent","3BHK","apartment","flat","family"],True,
        {"Mumbai":(40000,65000,65000,110000,110000,250000,85000),
         "Delhi":(32000,55000,55000,95000,95000,200000,72000),
         "Bengaluru":(28000,50000,50000,85000,85000,180000,65000),
         "Hyderabad":(24000,42000,42000,75000,75000,160000,55000),
         "Pune":(26000,45000,45000,80000,80000,170000,60000),
         "Chennai":(22000,38000,38000,68000,68000,145000,50000)},
        [("Base Rent",None,None,85),("Maintenance",None,None,10),("Parking",None,None,5)],
        ["Maintenance charges?","Parking included?","Society amenities?","Lock-in period?"],
        [75000,77000,79000,80000,82000,83000,84000,85000,86000],
        ["3 BHK in Mumbai suburbs costs what a 2 BHK costs in South Mumbai.",
         "Thane, Navi Mumbai, and Mira Road offer 40% lower rents vs city.",
         "Annual rent increases should be capped at 5–10% — negotiate upfront.",
         "Furnished flats cost 15–25% more but save on furnishing costs."])

    # ══════════════════════════════════════════════════════════════
    # GROCERY
    # ══════════════════════════════════════════════════════════════
    add_product("Tomato (1 kg)","tomato","grocery","per kg",
        ["tomato","vegetable","sabzi","grocery","daily"],True,
        {"Mumbai":(20,35,35,65,65,120,50),"Delhi":(18,32,32,60,60,110,46),
         "Bengaluru":(15,28,28,55,55,100,40),"Hyderabad":(15,27,27,52,52,95,38),
         "Pune":(18,32,32,60,60,110,45),"Chennai":(15,28,28,55,55,100,40)},
        [("Farm price",8,20,None),("Transport",4,8,None),("Mandi margin",3,6,None),("Retailer margin",3,7,None)],
        ["Local or cold-storage tomatoes?","Hybrid or desi variety?"],
        [30,35,40,55,65,80,60,50,50],
        ["Tomato prices spike Jun–Aug due to monsoon supply disruption.",
         "Mandi rates are 30–40% cheaper than retail.",
         "Prices stabilise Sep–Feb post kharif harvest.",
         "Buying from weekly sabzi mandi gives best prices."])

    add_product("Onion (1 kg)","onion","grocery","per kg",
        ["onion","pyaaz","vegetable","grocery","daily"],True,
        {"Mumbai":(20,35,35,55,55,90,42),"Delhi":(18,30,30,50,50,85,38),
         "Bengaluru":(15,28,28,48,48,80,35),"Hyderabad":(14,26,26,45,45,78,32),
         "Pune":(16,28,28,48,48,80,34),"Chennai":(13,25,25,43,43,75,30)},
        [("Farm price",6,15,None),("Transport",3,6,None),("Mandi margin",2,5,None),("Retailer margin",2,5,None)],
        ["Red or white onion?","Storage quality — fresh or stored?"],
        [28,30,32,38,42,50,45,42,42],
        ["Onion prices spike Jun–Sep — stock up in Feb–May.",
         "Nashik onions are benchmark for quality and price.",
         "Buying 5 kg at a time from vendors gives 10–15% discount."])

    add_product("Milk (1 litre)","milk","dairy","per litre",
        ["milk","dairy","amul","mother dairy","daily"],True,
        {"Mumbai":(24,26,26,30,30,38,27),"Delhi":(23,25,25,29,29,36,26),
         "Bengaluru":(24,26,26,30,30,38,27),"Hyderabad":(22,25,25,29,29,36,26),
         "Pune":(23,26,26,30,30,37,27),"Chennai":(22,25,25,28,28,35,26)},
        [("Farm gate price",14,18,None),("Processing",4,6,None),("Distribution",3,5,None),("Retailer margin",2,4,None)],
        ["Full cream or toned?","Brand?","Daily subscription available?"],
        [24,24,25,25,26,26,27,27,27],
        ["Amul Gold is full cream; Amul Taaza is toned.",
         "Country Delight and similar apps charge slight premium for quality.",
         "Society milk subscription can save ₹1–2/litre.",
         "Pasteurised vs UHT — UHT lasts longer but costs more."])

    add_product("Chicken (1 kg)","chicken","non-veg","per kg",
        ["chicken","murga","non-veg","meat","broiler"],True,
        {"Mumbai":(180,220,220,280,280,380,250),"Delhi":(160,200,200,260,260,360,230),
         "Bengaluru":(170,210,210,270,270,370,240),"Hyderabad":(155,195,195,255,255,355,225),
         "Pune":(165,205,205,265,265,365,235),"Chennai":(150,190,190,250,250,350,220)},
        [("Live bird cost",None,None,60),("Processing",None,None,20),("Shop margin",None,None,20)],
        ["Fresh or frozen?","Dressed weight or live weight?","Farm breed?"],
        [230,235,240,245,248,250,252,255,255],
        ["Broiler chicken prices are relatively stable year-round.",
         "Country chicken (desi murga) costs 2–3x broiler but has better taste.",
         "Buying from local butcher is 15–20% cheaper than supermarket.",
         "Monsoon months may see 10–15% price increase due to feed costs."])

    add_product("Basmati Rice (1 kg)","basmati-rice","kirana","per kg",
        ["rice","basmati","grocery","staple","cooking"],False,
        {"Mumbai":(80,100,100,150,150,250,120),"Delhi":(75,95,95,145,145,240,115),
         "Bengaluru":(80,100,100,150,150,250,120),"Hyderabad":(75,95,95,140,140,235,112),
         "Pune":(78,98,98,148,148,245,118),"Chennai":(70,90,90,135,135,220,105)},
        [("Grain cost",None,None,70),("Milling",None,None,15),("Packaging",None,None,8),("Retailer margin",None,None,7)],
        ["Aged rice (1yr/2yr)?","Brand — India Gate, Daawat?","Organic or regular?"],
        [110,112,115,117,118,119,120,120,120],
        ["Aged basmati gives better aroma and elongation on cooking.",
         "Loose rice from wholesale shops is 30–40% cheaper.",
         "India Gate Classic is benchmark for price vs quality.",
         "Organic basmati costs 2–3x — check if worth it for your budget."])

    # ══════════════════════════════════════════════════════════════
    # AUTO
    # ══════════════════════════════════════════════════════════════
    add_product("Car Service (Hatchback)","car-service-hatchback","car-ownership","per service",
        ["car service","i20","swift","hatchback","periodic","oil change"],True,
        {"Mumbai":(3500,5000,5000,8000,8000,14000,6500),"Delhi":(3200,4800,4800,7500,7500,13000,6000),
         "Bengaluru":(3400,4900,4900,7800,7800,13500,6300),"Hyderabad":(3000,4500,4500,7000,7000,12000,5700),
         "Pune":(3300,4700,4700,7600,7600,13200,6100),"Chennai":(2800,4200,4200,6800,6800,11500,5500)},
        [("Engine Oil + Filter",1200,1800,None),("Labour",1000,1500,None),
         ("Air/Cabin Filter",400,700,None),("Spark Plugs",600,1000,None),
         ("Wheel Alignment",400,700,None),("Misc",300,600,None)],
        ["Oil grade and brand?","All consumables included?","Authorised or multi-brand?","Parts warranty?"],
        [5200,5400,5600,5800,6000,6200,6300,6400,6500],
        ["Authorised service costs 30–50% more than multi-brand.",
         "Avoid dealer upsells on teflon coating and seat covers.",
         "Always get written estimate before authorising work.",
         "MyTVS and Carnation offer good quality at fair prices."])

    add_product("Bike Service (125cc)","bike-service-125cc","two-wheeler","per service",
        ["bike service","splendor","activa","Honda","two wheeler","scooter"],True,
        {"Mumbai":(800,1200,1200,2000,2000,3500,1600),"Delhi":(700,1100,1100,1800,1800,3200,1450),
         "Bengaluru":(750,1150,1150,1900,1900,3400,1520),"Hyderabad":(650,1050,1050,1700,1700,3000,1380),
         "Pune":(720,1120,1120,1850,1850,3300,1490),"Chennai":(620,1020,1020,1650,1650,2900,1320)},
        [("Engine Oil",250,400,None),("Labour",400,700,None),("Filter",100,200,None),("Misc",100,300,None)],
        ["Oil brand and grade?","Air filter replacement included?","Chain lubrication done?"],
        [1450,1470,1490,1510,1540,1560,1580,1600,1620],
        ["Two-wheelers need servicing every 3,000 km or 3 months.",
         "Authorised service for Splendor, Activa costs ₹800–1,500.",
         "Multi-brand garages save 30–40% for post-warranty bikes.",
         "Tyre pressure check is free at most petrol pumps — do it monthly."])

    add_product("Petrol (per litre)","petrol","fuel","per litre",
        ["petrol","fuel","pump","daily","refuel"],True,
        {"Mumbai":(103,104,103,104,104,106,103.4),"Delhi":(94,95,95,96,96,98,94.8),
         "Bengaluru":(100,102,102,103,103,105,101.5),"Hyderabad":(107,109,109,111,111,113,108.5),
         "Pune":(103,105,105,106,106,108,104.2),"Chennai":(100,102,102,103,103,105,101.1)},
        [("Base price",None,None,42),("Central excise",None,None,23),("State VAT",None,None,25),("Dealer margin",None,None,10)],
        ["Current pump price?","Loyalty card discounts available?"],
        [101,102,102,103,103,103,103.2,103.4,103.4],
        ["Petrol prices vary by state due to different VAT rates.",
         "Delhi has lowest petrol prices among metros due to low VAT.",
         "BPCL, HPCL loyalty cards give 1–2% cashback.",
         "Prices revised every fortnight based on global crude."])

    add_product("Auto Rickshaw Fare","auto-fare","commute","per km",
        ["auto","rickshaw","commute","local transport","last mile"],True,
        {"Mumbai":(21,21,21,25,25,35,22),"Delhi":(25,25,25,30,30,40,26),
         "Bengaluru":(30,30,30,35,35,45,32),"Hyderabad":(25,25,25,30,30,42,27),
         "Pune":(22,22,22,28,28,38,23),"Chennai":(25,25,25,30,30,40,26)},
        [("Minimum fare",None,None,None),("Per km after minimum",None,None,None)],
        ["Is the meter running?","Night charges applicable?","App or street auto?"],
        [20,20,21,21,22,22,22,22,22],
        ["Always insist on meter in Mumbai and Delhi — it's mandatory.",
         "Ola and Uber auto are usually 20–30% more than meter auto.",
         "Night charges (11 PM–5 AM) are typically 1.5x normal fare.",
         "Rapido Bike Taxi is cheapest for last-mile in most cities."])

    # ══════════════════════════════════════════════════════════════
    # TECHNOLOGY
    # ══════════════════════════════════════════════════════════════
    add_product("Smartphone (Mid-range ₹15–30K)","smartphone-midrange","smartphones","per unit",
        ["mobile","smartphone","android","phone","mid-range"],True,
        {"Mumbai":(15000,20000,20000,28000,28000,35000,24000),
         "Delhi":(14500,19500,19500,27500,27500,34500,23500),
         "Bengaluru":(15000,20000,20000,28000,28000,35000,24000),
         "Hyderabad":(14500,19500,19500,27500,27500,34500,23500),
         "Pune":(15000,20000,20000,28000,28000,35000,24000),
         "Chennai":(14500,19500,19500,27000,27000,34000,23000)},
        [("Device (ex-GST)",None,None,82),("GST (18%)",None,None,15),("Retailer margin",None,None,3)],
        ["RAM and storage?","AMOLED or LCD display?","Processor — Snapdragon or Dimensity?","Battery size?"],
        [22000,22500,23000,23200,23500,23700,23800,24000,24000],
        ["Flipkart and Amazon sale events offer 10–20% discounts.",
         "No-cost EMI is available on most major credit cards.",
         "OnePlus, Samsung, Poco offer best value in ₹15–30K range.",
         "Prices drop 10–15% within 4–8 weeks of launch — patience pays."])

    add_product("Laptop (Mid-range i5/Ryzen 5)","laptop-midrange","computers","per unit",
        ["laptop","notebook","i5","ryzen","computer"],True,
        {"Mumbai":(45000,55000,55000,75000,75000,110000,65000),
         "Delhi":(44000,54000,54000,73000,73000,108000,64000),
         "Bengaluru":(45000,55000,55000,75000,75000,110000,65000),
         "Hyderabad":(43000,53000,53000,72000,72000,106000,63000),
         "Pune":(44000,54000,54000,74000,74000,109000,64000),
         "Chennai":(43000,53000,53000,72000,72000,106000,63000)},
        [("Processor & Mobo",None,None,40),("RAM + Storage",None,None,25),("Display",None,None,20),("Battery & Chassis",None,None,10),("Retailer margin",None,None,5)],
        ["Is RAM upgradeable?","SSD or HDD?","Display — IPS or TN?","Battery backup hours?"],
        [60000,61000,62000,63000,64000,64500,65000,65000,65000],
        ["Ryzen 5 offers better value than i5 at same price.",
         "16GB RAM is minimum for smooth multitasking in 2025.",
         "NVMe SSD is 5x faster than SATA SSD.",
         "Extended warranty is worth buying for laptops."])

    add_product("Jio Prepaid (28 days)","jio-prepaid","mobile-recharge","per recharge",
        ["jio","recharge","mobile","prepaid","data","SIM"],True,
        {"Mumbai":(149,149,199,299,299,399,239),"Delhi":(149,149,199,299,299,399,239),
         "Bengaluru":(149,149,199,299,299,399,239),"Hyderabad":(149,149,199,299,299,399,239),
         "Pune":(149,149,199,299,299,399,239),"Chennai":(149,149,199,299,299,399,239)},
        [("Base plan cost",None,None,85),("GST (18%)",None,None,15)],
        ["Daily data limit?","Calling included?","Validity — 28 or 84 days?"],
        [219,219,229,239,239,239,239,239,239],
        ["₹299 plan offers 2GB/day — best value for most users.",
         "84-day plans save 15% over three 28-day recharges.",
         "Jio's ₹149 plan is emergency backup — not daily use.",
         "Compare Jio vs Airtel at your location — coverage varies by area."])

    add_product("Broadband (100 Mbps)","broadband-100mbps","internet-dth","per month",
        ["broadband","internet","wifi","home internet","fiber"],True,
        {"Mumbai":(400,600,600,900,900,1500,750),"Delhi":(350,550,550,850,850,1400,700),
         "Bengaluru":(400,600,600,900,900,1500,750),"Hyderabad":(350,550,550,850,850,1400,700),
         "Pune":(380,580,580,880,880,1450,730),"Chennai":(350,550,550,850,850,1400,700)},
        [("Plan cost",None,None,85),("Router rental (if any)",None,None,10),("GST",None,None,5)],
        ["Installation charges?","Contract lock-in period?","Speed guaranteed or best-effort?"],
        [700,710,720,730,740,745,748,750,750],
        ["ACT Fibernet and Hathway often have better prices than Jio Fiber for same speed.",
         "Annual prepaid plans save 15–20% vs monthly.",
         "Always negotiate free installation — most ISPs waive it.",
         "Speed above 100 Mbps is overkill for most households."])

    # ══════════════════════════════════════════════════════════════
    # HEALTHCARE
    # ══════════════════════════════════════════════════════════════
    add_product("General Physician Consultation","doctor-gp","doctors","per visit",
        ["doctor","GP","physician","consultation","clinic"],True,
        {"Mumbai":(300,500,500,1000,1000,3000,700),"Delhi":(250,450,450,900,900,2500,650),
         "Bengaluru":(280,480,480,950,950,2800,680),"Hyderabad":(200,400,400,800,800,2200,600),
         "Pune":(250,450,450,900,900,2500,650),"Chennai":(200,380,380,750,750,2000,560)},
        [("Consultation fee",300,1000,None),("Registration fee",50,200,None),("Pharmacy",200,800,None)],
        ["Follow-up fee same or reduced?","Insurance empanelled?","Online consult available?"],
        [600,620,640,660,680,690,700,710,720],
        ["Government hospitals charge ₹10–50 consultation fee.",
         "Online consults (Practo, 1mg) cost 20–40% less.",
         "Corporate health insurance covers OPD at many hospitals.",
         "Apollo and Fortis specialists charge ₹1,000–3,000+ per visit."])

    add_product("Full Body Checkup","full-body-checkup","diagnostics","per package",
        ["blood test","checkup","health","diagnostic","thyroid","CBC"],True,
        {"Mumbai":(1200,1800,1800,3000,3000,6000,2500),"Delhi":(1000,1600,1600,2800,2800,5500,2300),
         "Bengaluru":(1100,1700,1700,2900,2900,5800,2400),"Hyderabad":(900,1500,1500,2600,2600,5200,2100),
         "Pune":(1000,1600,1600,2800,2800,5500,2300),"Chennai":(800,1400,1400,2500,2500,5000,2000)},
        [("Lab processing",None,None,50),("Equipment",None,None,30),("Phlebotomist",None,None,10),("Report gen",None,None,10)],
        ["Home collection included?","Parameters covered?","Report timeline?","NABL accredited?"],
        [2100,2150,2200,2250,2300,2350,2400,2450,2500],
        ["Thyrocare and Dr Lal PathLabs offer great value packages.",
         "Home collection is typically free above ₹500 order value.",
         "NABL-accredited labs ensure accurate results.",
         "₹1,200–2,500 covers 50–80 parameters for preventive checkup."])

    add_product("Gym Membership","gym-membership","fitness","per month",
        ["gym","fitness","membership","workout","exercise"],True,
        {"Mumbai":(800,1500,1500,3000,3000,8000,2200),"Delhi":(700,1400,1400,2800,2800,7500,2100),
         "Bengaluru":(750,1450,1450,2900,2900,7800,2150),"Hyderabad":(600,1200,1200,2500,2500,7000,1900),
         "Pune":(700,1400,1400,2700,2700,7200,2050),"Chennai":(550,1100,1100,2300,2300,6500,1700)},
        [("Membership fee",1000,4000,None),("Registration (one-time)",500,2000,None),("Locker",200,500,None)],
        ["Personal trainer included?","Lock-in period?","Pause facility?","All equipment available?"],
        [1800,1900,1950,2000,2050,2100,2150,2180,2200],
        ["Annual memberships save 30–40% vs monthly payments.",
         "Negotiate hard — gyms rarely refuse discounts.",
         "Cult.fit offers flexibility for multi-city users.",
         "Avoid long lock-ins without a trial week first."])

    # ══════════════════════════════════════════════════════════════
    # TRAVEL
    # ══════════════════════════════════════════════════════════════
    add_product("Flight Mumbai-Delhi (Economy)","flight-bom-del","flights","per ticket",
        ["flight","air ticket","Mumbai","Delhi","IndiGo","economy"],True,
        {"Mumbai":(2500,4000,4000,7000,7000,15000,5500),"Delhi":(2500,4000,4000,7000,7000,15000,5500),
         "Bengaluru":(3000,4500,4500,8000,8000,16000,6000),"Hyderabad":(2800,4200,4200,7500,7500,15500,5700),
         "Pune":(2700,4100,4100,7200,7200,15000,5600),"Chennai":(3200,4800,4800,8500,8500,17000,6500)},
        [("Base fare",None,None,60),("Taxes & surcharges",None,None,25),("Fuel surcharge",None,None,12),("Convenience fee",None,None,3)],
        ["Baggage included?","Flexible change/cancellation?","Meal included?","Seat selection free?"],
        [4200,4500,4800,5000,5200,5400,5500,5500,5500],
        ["Book 4–8 weeks in advance for best fares.",
         "Tuesday and Wednesday flights are typically cheapest.",
         "IndiGo is most affordable and punctual airline.",
         "Early morning and late-night flights cost 20–30% less."])

    add_product("Hotel 3-Star (per night)","hotel-3star","hotels","per night",
        ["hotel","stay","accommodation","3 star","travel","oyo"],True,
        {"Mumbai":(2500,4000,4000,7000,7000,15000,5500),"Delhi":(2200,3800,3800,6500,6500,14000,5200),
         "Bengaluru":(2000,3500,3500,6000,6000,13000,4800),"Hyderabad":(1800,3200,3200,5500,5500,12000,4400),
         "Pune":(2000,3500,3500,6000,6000,12500,4700),"Goa":(3000,5000,5000,9000,9000,20000,7000)},
        [("Room rate",2500,7000,None),("GST (12–18%)",300,1200,None),("Breakfast",400,800,None)],
        ["Breakfast included?","Free cancellation?","Early check-in?","Airport transfer?"],
        [4800,5000,5100,5200,5300,5400,5450,5500,5500],
        ["Direct hotel booking is often cheaper than OTAs like MakeMyTrip.",
         "Weekday rates are 20–30% lower than weekends.",
         "Non-refundable rates save 15–25% on listed price.",
         "Always check if breakfast is included before comparing prices."])

    add_product("Goa Trip (3N/4D, per person)","goa-trip-3n4d","tour-packages","per person",
        ["Goa","vacation","beach","trip","holiday","package"],True,
        {"Mumbai":(7000,12000,12000,20000,20000,40000,16000),
         "Delhi":(10000,16000,16000,25000,25000,50000,20000),
         "Bengaluru":(8000,13000,13000,22000,22000,42000,17000),
         "Hyderabad":(9000,14000,14000,23000,23000,44000,18000),
         "Pune":(7000,12000,12000,20000,20000,40000,16000),
         "Chennai":(9000,14000,14000,23000,23000,44000,18000)},
        [("Flights (return)",None,None,35),("Hotel (3 nights)",None,None,30),("Food",None,None,18),("Local transport",None,None,10),("Activities",None,None,7)],
        ["Flight included?","Hotel rating — 2-star, 3-star?","Meals included?","Airport transfers included?"],
        [14000,14500,15000,15500,16000,16200,16300,16000,15500],
        ["Off-season (Jun–Sep) Goa is 40–50% cheaper with empty beaches.",
         "North Goa is more affordable than South Goa for accommodation.",
         "Self-drive bike rental costs ₹300–500/day — skip tour packages for transport.",
         "Book flights separately from hotels for 20–30% total savings."])

    add_product("Char Dham Yatra Package","char-dham-yatra","pilgrimage","per person",
        ["Char Dham","Kedarnath","Badrinath","Yamunotri","Gangotri","pilgrimage"],True,
        {"Mumbai":(25000,35000,35000,55000,55000,100000,45000),
         "Delhi":(18000,28000,28000,45000,45000,85000,36000),
         "Bengaluru":(28000,38000,38000,60000,60000,110000,50000),
         "Hyderabad":(27000,37000,37000,58000,58000,105000,48000),
         "Pune":(25000,35000,35000,55000,55000,100000,45000),
         "Chennai":(29000,39000,39000,62000,62000,112000,52000)},
        [("Flights/Train",None,None,25),("Hotel & boarding",None,None,40),("Transport (hilly terrain)",None,None,20),("Guide & puja",None,None,10),("Miscellaneous",None,None,5)],
        ["Season (April–June vs Sep–Oct)?","Helicopter included?","Number of days?","AC or non-AC rooms?"],
        [40000,41000,42000,43000,44000,45000,45500,45000,44000],
        ["April–June and Sep–Oct are peak seasons — book 3+ months ahead.",
         "Helicopter to Kedarnath adds ₹8,000–12,000 but saves 2 days.",
         "IRCTC packages offer government-backed reliable options.",
         "Travel insurance is essential for high-altitude pilgrimage trips."])

    # ══════════════════════════════════════════════════════════════
    # WEDDINGS
    # ══════════════════════════════════════════════════════════════
    add_product("Wedding Photography (2 days)","wedding-photography","weddings","per event",
        ["wedding photography","photographer","candid","video","album"],True,
        {"Mumbai":(50000,80000,80000,150000,150000,400000,110000),
         "Delhi":(45000,75000,75000,140000,140000,380000,105000),
         "Bengaluru":(40000,65000,65000,120000,120000,300000,92000),
         "Hyderabad":(35000,60000,60000,110000,110000,280000,85000),
         "Pune":(38000,62000,62000,115000,115000,290000,88000),
         "Chennai":(32000,55000,55000,100000,100000,260000,77000)},
        [("Lead Photographer",40000,80000,None),("Videographer",25000,50000,None),
         ("Album & Delivery",15000,30000,None),("Second Shooter",10000,20000,None),
         ("Travel",5000,10000,None)],
        ["Photos delivered — how many?","Drone included?","Album timeline?","Raw footage provided?"],
        [85000,88000,90000,95000,100000,105000,108000,110000,112000],
        ["Always review full portfolio — not just highlight reels.",
         "Candid photographers charge 50–100% more than traditional.",
         "Book 6–12 months ahead for peak wedding season (Oct–Feb).",
         "Always get deliverables in written contract."])

    add_product("Wedding Catering (per plate)","wedding-catering","weddings","per plate",
        ["wedding catering","food","banquet","plates","buffet"],True,
        {"Mumbai":(600,900,900,1500,1500,3000,1200),"Delhi":(550,850,850,1400,1400,2800,1100),
         "Bengaluru":(500,800,800,1300,1300,2600,1050),"Hyderabad":(450,750,750,1200,1200,2400,975),
         "Pune":(480,780,780,1250,1250,2500,1000),"Chennai":(420,700,700,1100,1100,2200,900)},
        [("Food & Ingredients",None,None,55),("Service Staff",None,None,20),
         ("Crockery & Setup",None,None,12),("Gas & Fuel",None,None,8),("Margin",None,None,5)],
        ["Menu items count?","Live counter included?","Minimum guest guarantee?","Corkage charges?"],
        [950,980,1000,1050,1100,1120,1150,1180,1200],
        ["Negotiate hard on minimum guarantee guest count.",
         "Live counters add ₹100–200 per plate.",
         "Always insist on a tasting session before finalising.",
         "Sunday weddings cost 20–30% less than Saturday."])

    add_product("Wedding Venue (per day)","wedding-venue","weddings","per day",
        ["wedding venue","banquet hall","farmhouse","5 star","function hall"],True,
        {"Mumbai":(150000,250000,250000,500000,500000,2000000,350000),
         "Delhi":(120000,200000,200000,450000,450000,1800000,320000),
         "Bengaluru":(100000,180000,180000,400000,400000,1500000,280000),
         "Hyderabad":(90000,160000,160000,380000,380000,1400000,260000),
         "Pune":(95000,170000,170000,390000,390000,1450000,270000),
         "Chennai":(80000,150000,150000,350000,350000,1300000,240000)},
        [("Venue hire",None,None,60),("Basic decoration",None,None,20),
         ("Security deposit",None,None,10),("Misc",None,None,10)],
        ["Capacity — seated vs standing?","Generator backup?","Parking available?","Outside caterer allowed?"],
        [300000,310000,320000,330000,340000,345000,348000,350000,352000],
        ["Venue cost is 30–40% of total wedding budget typically.",
         "Weekday or Sunday bookings save 20–30%.",
         "Negotiate decoration package separately.",
         "Always check noise curfew timing before booking."])

    # ══════════════════════════════════════════════════════════════
    # INSURANCE & FINANCE
    # ══════════════════════════════════════════════════════════════
    add_product("Health Insurance (Family Floater)","health-insurance","insurance-cat","per year",
        ["health insurance","mediclaim","family floater","hospitalization"],True,
        {"Mumbai":(8000,12000,12000,20000,20000,40000,16000),
         "Delhi":(7500,11500,11500,19000,19000,38000,15500),
         "Bengaluru":(7000,11000,11000,18000,18000,36000,15000),
         "Hyderabad":(6500,10500,10500,17000,17000,34000,14000),
         "Pune":(7000,11000,11000,18000,18000,36000,15000),
         "Chennai":(6000,10000,10000,16500,16500,33000,13500)},
        [("Base premium",None,None,75),("GST (18%)",None,None,18),("Add-ons",None,None,7)],
        ["Sum insured — ₹5L, ₹10L, ₹25L?","Pre-existing waiting period?","Network hospitals?","No-claim bonus?"],
        [14000,14200,14400,14800,15200,15500,15800,16000,16200],
        ["₹10L cover minimum recommended for family of 4 in metro.",
         "Star Health and Niva Bupa are top-rated for claim settlement.",
         "Buy before age 35 — premiums are significantly lower.",
         "Super top-up policies are affordable way to boost coverage.",
         "Always check room rent sub-limit before buying — it affects claims."])

    add_product("Term Life Insurance (₹1Cr)","term-insurance","insurance-cat","per year",
        ["term insurance","life insurance","term plan","cover"],True,
        {"Mumbai":(8000,12000,12000,18000,18000,30000,15000),
         "Delhi":(7500,11500,11500,17000,17000,28000,14000),
         "Bengaluru":(7000,11000,11000,16500,16500,27000,13500),
         "Hyderabad":(6500,10500,10500,15500,15500,26000,13000),
         "Pune":(7000,11000,11000,16000,16000,26500,13500),
         "Chennai":(6000,10000,10000,15000,15000,25000,12500)},
        [("Base mortality premium",None,None,80),("GST (18%)",None,None,18),("Admin charges",None,None,2)],
        ["Smoker or non-smoker?","Pre-existing conditions?","Claim settlement ratio?","Accidental rider?"],
        [13000,13200,13500,13800,14200,14500,14800,15000,15200],
        ["LIC, HDFC Life, Max Life have highest claim settlement ratios.",
         "Buy before age 35 — premiums are 50–60% lower.",
         "₹1 Cr cover is minimum for salaried professional.",
         "Online term plans are 20–30% cheaper than offline."])

    add_product("Gold (per gram, 22K)","gold-22k","gold-commodities","per gram",
        ["gold","jewellery","22K","gold rate","investment","sovereign"],True,
        {"Mumbai":(6400,6500,6500,6800,6800,7200,6715),"Delhi":(6380,6480,6480,6780,6780,7180,6695),
         "Bengaluru":(6400,6500,6500,6800,6800,7200,6715),"Hyderabad":(6390,6490,6490,6790,6790,7190,6705),
         "Pune":(6400,6500,6500,6800,6800,7200,6715),"Chennai":(6400,6500,6500,6800,6800,7200,6715)},
        [("Raw gold value",None,None,88),("Making charges",None,None,8),("GST (3%)",None,None,3),("Hallmarking",None,None,1)],
        ["BIS Hallmarked?","Making charges — flat or per gram?","Buyback policy?","Exchange value?"],
        [6200,6300,6400,6500,6550,6600,6650,6700,6715],
        ["Always buy BIS hallmarked gold — it certifies purity.",
         "Making charges range from 8–25% — negotiate on large purchases.",
         "Sovereign Gold Bonds earn 2.5% interest annually — better than physical gold.",
         "Digital gold via Zerodha or Groww has zero making charges."])

    # ══════════════════════════════════════════════════════════════
    # BEAUTY & FASHION
    # ══════════════════════════════════════════════════════════════
    add_product("Men Haircut (Premium Salon)","haircut-men","salon","per visit",
        ["haircut","salon","men","grooming","barber","hair"],False,
        {"Mumbai":(150,300,300,600,600,1500,450),"Delhi":(120,250,250,500,500,1200,375),
         "Bengaluru":(130,270,270,550,550,1300,410),"Hyderabad":(100,220,220,450,450,1100,335),
         "Pune":(120,250,250,500,500,1200,375),"Chennai":(100,200,200,400,400,1000,300)},
        [("Haircut",150,400,None),("Wash & Blow-dry",80,150,None),("Products",50,100,None)],
        ["Wash included?","Styling included?","Walk-in or appointment?"],
        [380,390,400,410,420,430,440,445,450],
        ["Branded salons cost 3–5x vs neighbourhood salons.",
         "Local barbers offer same quality at fraction of price.",
         "Confirm price before sitting down.",
         "Loyalty memberships save 15–20% per visit."])

    add_product("Women Full Body Waxing","waxing-women","salon","per session",
        ["waxing","salon","beauty","women","grooming","rica"],False,
        {"Mumbai":(600,900,900,1500,1500,3000,1200),"Delhi":(500,800,800,1400,1400,2800,1100),
         "Bengaluru":(550,850,850,1450,1450,2900,1150),"Hyderabad":(450,750,750,1300,1300,2600,1050),
         "Pune":(500,800,800,1400,1400,2700,1100),"Chennai":(400,700,700,1200,1200,2400,950)},
        [("Labour",500,1000,None),("Wax & Materials",200,400,None),("Post-care",100,200,None)],
        ["Rica or regular wax?","Full body or partial?","Package available?"],
        [1000,1020,1050,1080,1100,1150,1180,1200,1220],
        ["Rica wax costs 30–50% more than regular but is gentler.",
         "Packages (6 sessions) are cheaper per session.",
         "Neighbourhood parlours are 40% cheaper than branded chains.",
         "Confirm body parts covered before starting."])

    db.commit()

    # ══════════════════════════════════════════════════════════════
    # TRENDING SEARCHES
    # ══════════════════════════════════════════════════════════════
    trending_data = [
        ("Painter charges in Mumbai",        "Mumbai",     980),
        ("Car service cost for i20",         "Delhi",      850),
        ("Wedding photographer 2 days",      "Mumbai",     720),
        ("AC service charges summer",        "Bengaluru",  610),
        ("Modular kitchen cost Mumbai",      "Mumbai",     590),
        ("2 BHK rent in Bengaluru",          "Bengaluru",  540),
        ("Health insurance premium India",   None,         510),
        ("Gym membership near me",           "Bengaluru",  480),
        ("Term insurance ₹1 crore",          None,         460),
        ("Wedding catering per plate Delhi", "Delhi",      440),
        ("Laptop price mid range 2025",      None,         420),
        ("Tomato price today Mumbai",        "Mumbai",     400),
        ("Petrol price today",               None,         390),
        ("Home loan EMI calculator",         None,         375),
        ("Char Dham yatra package cost",     "Delhi",      360),
    ]
    for i,(q,city,cnt) in enumerate(trending_data):
        db.add(TrendingSearch(query=q,city=city,count=cnt,sort_order=i))

    # ══════════════════════════════════════════════════════════════
    # MARKET HIGHLIGHTS
    # ══════════════════════════════════════════════════════════════
    highlights = [
        ("Gold rate today",   "₹6,715/gm",  "+1.2%", True),
        ("Petrol Mumbai",     "₹103.4/L",   "-0.1%", False),
        ("Tomato (1 kg)",     "₹50/kg",     "+8.2%", True),
        ("USD → INR",         "₹83.6",      "+0.2%", True),
        ("Sensex",            "74,580",     "+0.4%", True),
    ]
    for i,(lbl,val,chg,up) in enumerate(highlights):
        db.add(MarketHighlight(label=lbl,value=val,change=chg,is_up=up,sort_order=i))

    # ══════════════════════════════════════════════════════════════
    # MONEY SAVING HACKS
    # ══════════════════════════════════════════════════════════════
    hacks = [
        ("ELECTRICITY",
         "Set your AC to 24°C, not 18°C",
         "Every 1°C increase saves ~6% electricity. At 24°C vs 18°C you save up to 36% on AC bill. The Bureau of Energy Efficiency (BEE) officially recommends 24°C as the optimal temperature. Your room cools just as well within 20 minutes.",
         "₹800", "per month"),
        ("ELECTRICITY",
         "Switch off geyser 15 minutes before use, not after",
         "Most Indians leave geysers on while bathing. A 15-minute preheat is enough for a full shower. Turning it off after wastes stored heat. This one habit saves 30–40% on water heating costs annually.",
         "₹400", "per month"),
        ("GROCERY",
         "Buy vegetables on Wednesday morning, not Saturday evening",
         "Mandis restock mid-week. Saturday evening has peak demand, lowest freshness and vendors don't reduce price. Wednesday morning gives you 20–30% cheaper, fresher produce. Most working people can do this on a half-day off or via quick delivery apps.",
         "₹600", "per month"),
        ("GROCERY",
         "Buy dal, rice, and atta in 5 kg packs, not 1 kg",
         "Per-kg cost of staples drops 15–25% when buying 5 kg packs. A family of 4 using 2 kg rice per week saves ₹1,200–1,800 annually just by buying larger packs from a local kirana store rather than supermarket.",
         "₹500", "per month"),
        ("TRAVEL",
         "Book domestic flights on Tuesday between 12–3 PM",
         "Airlines release unsold seat discounts mid-week. Tuesday afternoons consistently show 15–25% lower fares than weekend booking for the exact same flight. Set fare alerts on Google Flights and check Tuesday afternoon.",
         "₹1,200", "per trip"),
        ("TRAVEL",
         "Travel to Goa in September — not December",
         "Goa in September (off-season) is 40–50% cheaper for hotels. The beaches are empty, weather is post-monsoon fresh, and the experience is identical. A trip that costs ₹25,000 in December costs ₹14,000 in September.",
         "₹11,000", "per Goa trip"),
        ("TELECOM",
         "Switch to an 84-day recharge instead of monthly",
         "Jio and Airtel 84-day plans cost ~15% less per day vs 28-day plans. You pay more upfront but save ₹200–350 every quarter without changing anything about your usage. Most people forget and keep paying more.",
         "₹300", "per month"),
        ("INSURANCE",
         "Pay car insurance annually — never opt for monthly EMI",
         "Monthly EMI options for insurance add 12–18% to total premium. Annual payment saves that full amount. Also compare 3 insurers before renewal on PolicyBazaar — auto-renewal costs 15–20% more than switching.",
         "₹2,000", "per year"),
        ("INSURANCE",
         "Buy health insurance before age 35 — not after a health scare",
         "Health insurance premiums at age 28 are 40–60% lower than at age 40. Waiting for a health issue means either very high premiums or rejection. A ₹10L family floater bought at 28 costs ₹12,000/yr; at 40 it costs ₹22,000/yr for the same cover.",
         "₹10,000", "per year"),
        ("FOOD",
         "Cook one big batch on Sunday — saves 5 weekday decisions and ₹400/week on ordering",
         "The average Indian spends ₹250–400 extra per week on food delivery from tiredness-driven ordering on weeknights. A 2-hour Sunday batch cook (dal, sabzi, rice) eliminates Monday–Wednesday ordering impulse. This one habit saves ₹1,500–1,800/month.",
         "₹1,600", "per month"),
        ("BANKING",
         "Move your emergency fund to a liquid mutual fund — not a savings account",
         "Savings accounts give 2.7–3.5% interest. Liquid mutual funds give 6.5–7.2% on the same money with same-day withdrawal. On an emergency fund of ₹3L, this difference is ₹10,500 extra per year with zero extra risk.",
         "₹875", "per month"),
        ("SHOPPING",
         "Wait 48 hours before any online purchase above ₹2,000",
         "Impulse purchases account for 62% of e-commerce spending. A 48-hour wait removes the emotional trigger. Research shows 40% of impulse purchase intentions disappear within 24 hours. You also find better prices during the wait.",
         "₹3,000", "per month"),
    ]
    for i,(cat,hl,detail,amt,period) in enumerate(hacks):
        db.add(MoneyHack(category=cat,headline=hl,detail=detail,
                         saving_amt=amt,saving_period=period,sort_order=i))

    # ══════════════════════════════════════════════════════════════
    # PRICE BULLETINS
    # ══════════════════════════════════════════════════════════════
    now = datetime.utcnow()
    bulletins = [
        ("GROCERY","Mumbai","Tomato prices fall 18% in Mumbai as Maharashtra harvest arrives",
         "Retail rates drop from ₹65/kg to ₹53/kg at major mandis. Likely to fall further over next 2 weeks as Nashik and Pune district harvest peaks.",
         -18.0,"THIS WEEK",0),
        ("AUTO","Delhi","Multi-brand garages slashing service rates ahead of monsoon season",
         "Periodic service for hatchbacks now averaging ₹5,500 vs ₹6,400 last month at independent garages in Delhi NCR. Authorised service centres unaffected.",
         -14.0,"THIS MONTH",1),
        ("HEALTH","Bengaluru","Diagnostic labs in Bengaluru cut full-body checkup prices by 20%",
         "Thyrocare, Dr Lal PathLabs and SRL running monsoon packages. Full checkup now under ₹2,000 for 60+ parameters with home collection included.",
         -20.0,"THIS WEEK",2),
        ("ALERT","Pune","Onion prices surge 22% in Pune — supply disruption from Nashik",
         "Heavy rains delay arrivals at Lasalgaon mandi. Expect ₹45–55/kg at retail for next 10 days. Stock up moderately — prices should normalise in 2 weeks.",
         +22.0,"THIS WEEK",3),
        ("ELECTRONICS","All India","Mid-range laptops see 8% correction as new models enter market",
         "Ryzen 5 and i5 segment prices drop nationwide. Best time to buy before festive season restocks. Asus, Lenovo and HP showing highest discounts.",
         -8.0,"THIS WEEK",4),
        ("TRAVEL","All India","Goa post-monsoon hotel rates drop 32% — best time to plan a trip",
         "September week rates at 3-star properties now at ₹3,500–5,000/night vs ₹7,000+ in December. Flights also 25% cheaper than peak season.",
         -32.0,"THIS MONTH",5),
        ("FUEL","Mumbai","Petrol prices stable for 3rd consecutive fortnight",
         "Despite global crude fluctuation, domestic retail prices unchanged. Mumbai remains at ₹103.4/L. No revision expected in next fortnight per OMC sources.",
         -0.1,"THIS MONTH",6),
        ("GROCERY","Delhi","Onion prices ease in Delhi after government clamps import duty",
         "Onion retail price falls from ₹55 to ₹42/kg in Delhi over 10 days after Centre removes import duty on onions. Further softening expected next week.",
         -24.0,"THIS WEEK",7),
    ]
    for (cat,city,hl,detail,pct,period,sort) in bulletins:
        db.add(PriceBulletin(category=cat,city=city,headline=hl,detail=detail,
                             change_pct=pct,period=period,
                             published_at=now-timedelta(hours=sort*3),sort_order=sort))

    # ══════════════════════════════════════════════════════════════
    # PLAN TEMPLATES — all 12 plans
    # ══════════════════════════════════════════════════════════════
    def add_plan(plan_id,label,subtitle,icon,color,icon_color,section,sort,questions,free_insights,premium_items):
        pt = PlanTemplate(plan_id=plan_id,label=label,subtitle=subtitle,icon=icon,
                          color_hex=color,icon_color_hex=icon_color,section=section,sort_order=sort)
        db.add(pt); db.flush()
        for q in questions:
            db.add(PlanQuestion(plan_id=pt.id,step_no=q["step"],question=q["question"],
                                field_key=q["field_key"],input_type=q.get("type","choice"),options=q.get("options")))
        for i,text in enumerate(free_insights):
            db.add(PlanFreeInsight(plan_id=pt.id,text=text,sort_order=i))
        for i,(title,sub) in enumerate(premium_items):
            db.add(PlanPremiumItem(plan_id=pt.id,title=title,subtitle=sub,sort_order=i))

    # 1. WEDDING
    add_plan("wedding","Wedding Planning","Budget, venue, catering, decor breakdown",
        "💍","#FAEEDA","#BA7517","LIFE PLANNING",0,
        [{"step":1,"question":"When is the wedding?","field_key":"timeline",
          "options":[{"label":"Within 6 months","hint":"Urgent — book fast"},{"label":"6–12 months","hint":"Good planning window"},{"label":"1–2 years","hint":"Plenty of time"},{"label":"Just exploring","hint":"No fixed date yet"}]},
         {"step":2,"question":"What is your total budget?","field_key":"budget",
          "options":[{"label":"Under ₹5 Lakhs","hint":"Budget wedding"},{"label":"₹5–15 Lakhs","hint":"Mid-range"},{"label":"₹15–40 Lakhs","hint":"Premium"},{"label":"₹40 Lakhs+","hint":"Grand"}]},
         {"step":3,"question":"How many guests are you expecting?","field_key":"guests",
          "options":[{"label":"Under 100","hint":"Intimate ceremony"},{"label":"100–300","hint":"Standard wedding"},{"label":"300–500","hint":"Large function"},{"label":"500+","hint":"Grand event"}]},
         {"step":4,"question":"Which city is the wedding in?","field_key":"city",
          "options":[{"label":"Mumbai","hint":""},{"label":"Delhi NCR","hint":""},{"label":"Bengaluru","hint":""},{"label":"Hyderabad","hint":""},{"label":"Pune","hint":""},{"label":"Other city","hint":""}]},
         {"step":5,"question":"What is most important to you?","field_key":"priority",
          "options":[{"label":"Venue & Decor","hint":"Visual impact"},{"label":"Food & Catering","hint":"Guest satisfaction"},{"label":"Photography","hint":"Memories last"},{"label":"Everything equal","hint":"Balanced budget"}]}],
        ["Your budget of ₹15–40L for 200 guests works out to ₹7,500–20,000 per head — this is achievable in Mumbai.",
         "Catering alone will consume 30–40% of your total budget. Plan ₹900–1,200 per plate at fair market rate.",
         "Book venue and caterer at least 9 months in advance in Mumbai — halls fill up post-monsoon.",
         "Sunday weddings cost 20–30% less than Saturday for the same venue and quality."],
        [("Vendor-by-vendor price benchmarks","Photographer, caterer, florist, mehendi artist, band"),
         ("Negotiation scripts for each vendor","Exact questions to ask, red flags to watch"),
         ("Month-by-month planning checklist","12-month timeline with budget milestones"),
         ("Hidden cost identifier","Taxes, corkage, overtime charges vendors never mention upfront"),
         ("Downloadable PDF budget tracker","Share with family, update costs in real time"),
         ("City-specific venue shortlist with fair price range","Top 10 venues per city with price benchmark")])

    # 2. HOME RENOVATION
    add_plan("home-renovation","Home Renovation","Full cost estimate by area and city",
        "🏠","#E1F5EE","#0A6E52","LIFE PLANNING",1,
        [{"step":1,"question":"What type of renovation?","field_key":"reno_type",
          "options":[{"label":"Full interior (new house)","hint":"Biggest investment"},{"label":"Kitchen + wardrobes","hint":"Most common upgrade"},{"label":"Bathroom renovation","hint":"High ROI upgrade"},{"label":"Painting + flooring","hint":"Cosmetic refresh"}]},
         {"step":2,"question":"What is the approximate area?","field_key":"area",
          "options":[{"label":"Under 500 sq ft (1 BHK)","hint":""},{"label":"500–900 sq ft (2 BHK)","hint":"Most common"},{"label":"900–1,400 sq ft (3 BHK)","hint":""},{"label":"1,400+ sq ft","hint":"Large apartment/villa"}]},
         {"step":3,"question":"What is your quality preference?","field_key":"quality",
          "options":[{"label":"Budget (local materials)","hint":"Get it done, spend less"},{"label":"Mid-range (branded materials)","hint":"Good balance"},{"label":"Premium (designer finishes)","hint":"Best quality"},{"label":"Luxury (imported materials)","hint":"Top of the line"}]},
         {"step":4,"question":"Which city?","field_key":"city",
          "options":[{"label":"Mumbai","hint":""},{"label":"Delhi NCR","hint":""},{"label":"Bengaluru","hint":""},{"label":"Hyderabad","hint":""},{"label":"Pune","hint":""},{"label":"Chennai","hint":""}]},
         {"step":5,"question":"When do you plan to start?","field_key":"timeline",
          "options":[{"label":"In the next month","hint":"Need fast quotes"},{"label":"3–6 months","hint":"Planning phase"},{"label":"6–12 months","hint":"Future planning"},{"label":"Just getting an idea","hint":"No fixed date"}]}],
        ["For a 2 BHK (700 sq ft) full interior in Mumbai, expect ₹8–14 Lakhs at mid-range quality.",
         "Civil work (walls, tiles, waterproofing) is the most important — don't cut corners here. It's 35–40% of cost.",
         "Always get at least 3 contractor quotes — prices vary 30–40% for same scope of work.",
         "Set aside 15% of your budget as contingency — renovation always has surprises."],
        [("Per sq ft cost benchmark for your city and quality level","Compare against market to spot overcharging"),
         ("Contractor vetting checklist","10 questions to ask before signing any contractor"),
         ("Material brand price guide","Tiles, paint, electrical fittings — brand vs local comparison"),
         ("Red flag identifier","Signs a contractor will cut corners or disappear mid-project"),
         ("Payment schedule guide","Never pay more than 30% upfront — milestone-based payment template"),
         ("Room-by-room cost breakdown","Kitchen, bathroom, bedroom, living room — separate budgets")])

    # 3. CHILD EDUCATION
    add_plan("child-education","Child Education","Corpus planning and SIP recommendation",
        "🎓","#E0F2FE","#0369A1","LIFE PLANNING",2,
        [{"step":1,"question":"How old is your child?","field_key":"child_age",
          "options":[{"label":"Not yet born","hint":"Maximum time to save"},{"label":"0–3 years","hint":"15+ years ahead"},{"label":"4–8 years","hint":"10–14 years ahead"},{"label":"9–14 years","hint":"4–9 years ahead"}]},
         {"step":2,"question":"What is the education goal?","field_key":"goal",
          "options":[{"label":"IIT/IIM (India)","hint":"₹8–15L total fees"},{"label":"Private Engineering/MBA","hint":"₹8–30L total fees"},{"label":"MBBS India","hint":"₹15–80L total fees"},{"label":"Study Abroad (US/UK)","hint":"₹60–150L total"},{"label":"School (CBSE private)","hint":"₹50K–2L per year"}]},
         {"step":3,"question":"How much can you save monthly for this goal?","field_key":"monthly_save",
          "options":[{"label":"Under ₹2,000","hint":"Start small, start now"},{"label":"₹2,000–5,000","hint":"Good starting point"},{"label":"₹5,000–15,000","hint":"Strong commitment"},{"label":"₹15,000+","hint":"Aggressive savings"}]},
         {"step":4,"question":"Do you have any existing savings for this goal?","field_key":"existing",
          "options":[{"label":"Nothing yet","hint":"Starting fresh"},{"label":"Under ₹1 Lakh","hint":"Small start"},{"label":"₹1–5 Lakhs","hint":"Good foundation"},{"label":"₹5 Lakhs+","hint":"Strong head start"}]},
         {"step":5,"question":"How involved do you want to be in investing?","field_key":"involvement",
          "options":[{"label":"Auto-pilot — set and forget","hint":"Best for busy parents"},{"label":"Review once a year","hint":"Low maintenance"},{"label":"Active management","hint":"Hands-on approach"}]}],
        ["Education inflation in India is 10–12% per year. What costs ₹15L today will cost ₹45L in 15 years.",
         "Start a SIP immediately, even ₹1,000/month. Time is your most powerful asset — delay costs you more than amount.",
         "Sukanya Samriddhi Yojana (SSY) is excellent for girl child — 8.2% guaranteed + 80C deduction.",
         "Equity mutual funds over 10+ year horizon historically return 12–15% CAGR — best vehicle for education corpus."],
        [("Exact corpus needed with inflation projection","Based on your child's age and chosen goal"),
         ("Monthly SIP amount required to reach goal","With recommended step-up schedule"),
         ("3 specific fund recommendations","Suitable for your timeline and risk profile"),
         ("SSY vs PPF vs ELSS — which is right for you","Tax-efficient corpus building strategy"),
         ("Education loan safety net planning","If corpus falls short — which banks, at what rates"),
         ("Milestone tracker","Year-by-year corpus targets to stay on track")])

    # 4. VACATION PLANNING
    add_plan("vacation","Vacation Planning","Realistic trip budget with full breakdown",
        "✈️","#EDE9FE","#7C3AED","LIFE PLANNING",3,
        [{"step":1,"question":"Where do you want to go?","field_key":"destination",
          "options":[{"label":"Goa","hint":"Beach holiday"},{"label":"Kerala","hint":"Backwaters & hills"},{"label":"Rajasthan","hint":"Heritage & culture"},{"label":"Himachal/Uttarakhand","hint":"Mountains & trekking"},{"label":"Andaman","hint":"Islands & diving"},{"label":"International (Bali/Dubai/Thailand)","hint":"Overseas trip"}]},
         {"step":2,"question":"How long is the trip?","field_key":"duration",
          "options":[{"label":"2–3 nights","hint":"Quick weekend"},{"label":"4–5 nights","hint":"Standard holiday"},{"label":"6–8 nights","hint":"Relaxed vacation"},{"label":"9+ nights","hint":"Extended break"}]},
         {"step":3,"question":"How many people are travelling?","field_key":"travelers",
          "options":[{"label":"Solo","hint":"Best for budget"},{"label":"Couple (2)","hint":"Romantic trip"},{"label":"Family with kids","hint":"Kid-friendly budget"},{"label":"Group (4–6 friends)","hint":"Split costs"}]},
         {"step":4,"question":"What is your travel style?","field_key":"style",
          "options":[{"label":"Budget — hostels, local food","hint":"₹1,500–2,500/day"},{"label":"Mid-range — 3-star, restaurants","hint":"₹3,500–6,000/day"},{"label":"Comfortable — 4-star, good food","hint":"₹6,000–12,000/day"},{"label":"Luxury — 5-star, experiences","hint":"₹15,000+/day"}]},
         {"step":5,"question":"When are you planning to travel?","field_key":"season",
          "options":[{"label":"Peak season (Dec–Jan)","hint":"Expensive, crowded"},{"label":"Shoulder (Oct–Nov, Feb–Mar)","hint":"Best value"},{"label":"Off-season (Jun–Sep)","hint":"Cheapest, some rain"},{"label":"Not decided yet","hint":"Help me pick best time"}]}],
        ["A 4-night Goa trip for 2 in shoulder season costs ₹22,000–32,000 total at mid-range.",
         "Flights are 25–40% of total trip cost — Tuesday departure saves 15–20%.",
         "Off-season travel to Goa and Kerala saves 40–50% with similar experience and fewer crowds.",
         "Book flights and hotels separately — package deals are rarely cheaper for domestic travel."],
        [("Full day-by-day cost breakdown","Flights, hotel, food, transport, activities — per person and total"),
         ("Best booking time for your destination","Exactly when to book flights and hotels for this route"),
         ("Hidden cost identifier","Taxes, resort fees, tourist trap pricing at your destination"),
         ("Budget vs mid-range vs premium comparison","What you get at each price point"),
         ("Local money-saving tips for your destination","City-specific hacks used by experienced travellers"),
         ("Packing cost calculator","What to buy in India vs at destination")])

    # 5. SIP & INVESTMENTS
    add_plan("sip","SIP & Investments","Fund selection and corpus projection",
        "📈","#ECFDF5","#059669","WEALTH BUILDING",4,
        [{"step":1,"question":"What is your investment goal?","field_key":"goal",
          "options":[{"label":"Build wealth long-term","hint":"10+ years horizon"},{"label":"Child education corpus","hint":"10–18 years"},{"label":"Retirement fund","hint":"20–30 years"},{"label":"House down payment","hint":"3–7 years"},{"label":"Emergency fund","hint":"1–3 years"}]},
         {"step":2,"question":"How much can you invest monthly?","field_key":"monthly_sip",
          "options":[{"label":"₹500–2,000","hint":"Starting out"},{"label":"₹2,000–5,000","hint":"Building habit"},{"label":"₹5,000–15,000","hint":"Serious investor"},{"label":"₹15,000–50,000","hint":"High savings"},{"label":"₹50,000+","hint":"Aggressive wealth building"}]},
         {"step":3,"question":"What is your risk appetite?","field_key":"risk",
          "options":[{"label":"Conservative — capital protection first","hint":"FD, debt funds"},{"label":"Moderate — some equity is okay","hint":"Balanced funds"},{"label":"Growth — mostly equity","hint":"Large cap funds"},{"label":"Aggressive — max growth","hint":"Mid/small cap"}]},
         {"step":4,"question":"How long can you stay invested?","field_key":"horizon",
          "options":[{"label":"Less than 3 years","hint":"Short term"},{"label":"3–5 years","hint":"Medium term"},{"label":"5–10 years","hint":"Long term"},{"label":"10–20 years","hint":"Very long term"},{"label":"20+ years","hint":"Retirement horizon"}]},
         {"step":5,"question":"Have you invested before?","field_key":"experience",
          "options":[{"label":"Complete beginner","hint":"First investment"},{"label":"Have an FD or PPF","hint":"Conservative start"},{"label":"Have mutual funds already","hint":"Looking to optimise"},{"label":"Active investor","hint":"Want expert view"}]}],
        ["₹5,000/month in an index fund for 15 years at 12% returns gives approximately ₹25 Lakhs corpus.",
         "Don't try to time the market. Start today, keep going every month — consistency beats cleverness.",
         "ELSS funds save up to ₹46,800 in tax (at 30% bracket) while building wealth — use your ₹1.5L limit.",
         "Index funds (Nifty 50) outperform 75% of active funds over 10 years with lower cost."],
        [("Personalised fund shortlist — 3 funds for your profile","Based on your goal, risk, and horizon"),
         ("Exact SIP amount to reach your goal","With step-up schedule for each year"),
         ("Tax optimisation plan","How to structure investments for maximum 80C and LTCG benefit"),
         ("Portfolio review checklist","When to rebalance, when to switch, when to exit"),
         ("SIP calculator with realistic scenarios","Best case, expected case, and stress-test case"),
         ("Common SIP mistakes and how to avoid them","What kills returns for 80% of Indian investors")])

    # 6. RETIREMENT PLANNING
    add_plan("retirement","Retirement Planning","Corpus needed and shortfall analysis",
        "🏦","#F0FDF4","#15803D","WEALTH BUILDING",5,
        [{"step":1,"question":"How old are you?","field_key":"current_age",
          "options":[{"label":"22–27","hint":"Maximum runway"},{"label":"28–35","hint":"Great time to start"},{"label":"36–44","hint":"Mid-career — act now"},{"label":"45–55","hint":"Critical decade"}]},
         {"step":2,"question":"At what age do you want to retire?","field_key":"retire_age",
          "options":[{"label":"45–50 (early retirement)","hint":"FIRE movement"},{"label":"55–58","hint":"Early but realistic"},{"label":"60–62","hint":"Standard retirement"},{"label":"65+","hint":"Work as long as possible"}]},
         {"step":3,"question":"What are your current monthly expenses?","field_key":"monthly_exp",
          "options":[{"label":"Under ₹30,000","hint":"Frugal lifestyle"},{"label":"₹30,000–60,000","hint":"Middle India"},{"label":"₹60,000–1,20,000","hint":"Comfortable lifestyle"},{"label":"₹1,20,000+","hint":"Premium lifestyle"}]},
         {"step":4,"question":"How much do you save monthly towards retirement?","field_key":"monthly_save",
          "options":[{"label":"Nothing yet","hint":"Start today"},{"label":"Under ₹5,000","hint":"EPF only maybe"},{"label":"₹5,000–20,000","hint":"Making progress"},{"label":"₹20,000–50,000","hint":"Serious saver"},{"label":"₹50,000+","hint":"On track for early retirement"}]},
         {"step":5,"question":"What retirement accounts do you have?","field_key":"existing_accounts",
          "options":[{"label":"Only EPF","hint":"Most salaried Indians"},{"label":"EPF + PPF","hint":"Good discipline"},{"label":"EPF + mutual funds","hint":"Smart diversification"},{"label":"EPF + NPS + MF","hint":"Well structured"},{"label":"Self-employed, no EPF","hint":"Need to self-fund entirely"}]}],
        ["Using the 25x rule: if your monthly expenses are ₹60,000, you need ₹1.8 Crore retirement corpus.",
         "EPF alone is not enough. At 12% contribution on ₹60,000 salary for 30 years, you get ~₹80 Lakhs — enough for only 11 years.",
         "NPS gives additional ₹50,000 tax deduction under 80CCD(1B) — use it before any other instrument.",
         "Starting at 28 vs 38 for the same corpus requires 3x lower monthly investment — time is everything."],
        [("Exact corpus amount needed with inflation adjustment","Based on your lifestyle and retirement age"),
         ("Current savings trajectory vs required — year by year","Visual gap analysis showing shortfall"),
         ("Monthly investment required from today to close the gap","With step-up schedule"),
         ("Instrument allocation — EPF, NPS, MF, PPF — optimal split","For your age and income"),
         ("Early retirement feasibility check","Stress-test for 45, 50, 55 retirement scenarios"),
         ("Sequence of returns risk planning","What happens if market falls in your retirement year")])

    # 7. EMERGENCY FUND
    add_plan("emergency-fund","Emergency Fund","How much you need and where to keep it",
        "🛡️","#FCEBEB","#9B2121","WEALTH BUILDING",6,
        [{"step":1,"question":"What is your monthly household expense?","field_key":"monthly_exp",
          "options":[{"label":"Under ₹20,000","hint":"Lean household"},{"label":"₹20,000–50,000","hint":"Average Indian family"},{"label":"₹50,000–1,00,000","hint":"Comfortable spending"},{"label":"₹1,00,000+","hint":"High lifestyle"}]},
         {"step":2,"question":"What is your employment situation?","field_key":"employment",
          "options":[{"label":"Salaried (stable MNC/Govt)","hint":"6 months buffer recommended"},{"label":"Salaried (startup/SME)","hint":"9 months buffer recommended"},{"label":"Self-employed/Freelancer","hint":"12 months buffer recommended"},{"label":"Business owner","hint":"12+ months buffer"}]},
         {"step":3,"question":"How many dependents do you have?","field_key":"dependents",
          "options":[{"label":"None — just me","hint":"Lower buffer okay"},{"label":"Spouse (both working)","hint":"Moderate buffer"},{"label":"Spouse + 1 child","hint":"Higher buffer needed"},{"label":"Spouse + 2+ kids or elderly parents","hint":"Maximum buffer"}]},
         {"step":4,"question":"Current liquid savings (can be withdrawn within 1 week)?","field_key":"current_savings",
          "options":[{"label":"Under ₹25,000","hint":"Vulnerable position"},{"label":"₹25,000–1,00,000","hint":"Partial cover"},{"label":"₹1,00,000–3,00,000","hint":"Decent start"},{"label":"₹3,00,000+","hint":"May already be adequate"}]},
         {"step":5,"question":"Do you have health insurance?","field_key":"health_insurance",
          "options":[{"label":"Yes — ₹5L+ cover","hint":"Reduces emergency need"},{"label":"Yes — under ₹5L cover","hint":"Partial protection"},{"label":"No health insurance","hint":"Must build larger fund"},{"label":"Company-provided only","hint":"Will lapse if you change jobs"}]}],
        ["Your emergency fund target: 6 months of expenses if salaried, 12 months if self-employed.",
         "The biggest mistake is keeping emergency fund in a regular savings account at 2.7% interest. Move it to a liquid mutual fund — same access, 6.5–7% return.",
         "Never invest emergency fund in equity — it must be retrievable within 1 business day.",
         "Health insurance reduces emergency fund size — ₹10L health cover means ₹3–5L less in emergency fund."],
        [("Exact emergency fund target for your profile","Based on expenses, dependents, employment type"),
         ("Current gap amount and monthly savings plan to fill it","Step-by-step funding schedule"),
         ("Best liquid instruments for your fund","Sweep FD vs liquid MF vs savings account comparison"),
         ("3 specific fund recommendations with withdrawal instructions","Parag Parikh, HDFC, ICICI liquid funds"),
         ("Emergency fund calculator with scenarios","Job loss, medical emergency, business downturn"),
         ("Annual review checklist","When and how to adjust your fund as life changes")])

    # 8. LOAN PLANNING
    add_plan("loan","Loan Planning","EMI, eligibility, and best rate analysis",
        "🏧","#EAF0FB","#1A4FA0","BORROWING & PROTECTION",7,
        [{"step":1,"question":"What type of loan are you considering?","field_key":"loan_type",
          "options":[{"label":"Home Loan","hint":"Largest & longest loan"},{"label":"Car Loan","hint":"5–7 year tenure typically"},{"label":"Personal Loan","hint":"High rate — use carefully"},{"label":"Education Loan","hint":"Moratorium available"},{"label":"Loan Against Property","hint":"Lower rate, uses asset"}]},
         {"step":2,"question":"How much do you want to borrow?","field_key":"loan_amount",
          "options":[{"label":"Under ₹5 Lakhs","hint":"Personal/car loan range"},{"label":"₹5–20 Lakhs","hint":"Car or small home loan"},{"label":"₹20–60 Lakhs","hint":"Home loan mid-range"},{"label":"₹60 Lakhs–1 Crore","hint":"Premium home loan"},{"label":"₹1 Crore+","hint":"Luxury property range"}]},
         {"step":3,"question":"What is your monthly income?","field_key":"monthly_income",
          "options":[{"label":"Under ₹40,000","hint":"Income limit matters"},{"label":"₹40,000–80,000","hint":"Average salaried"},{"label":"₹80,000–1,50,000","hint":"Good eligibility"},{"label":"₹1,50,000+","hint":"High eligibility"}]},
         {"step":4,"question":"What is your existing EMI burden?","field_key":"existing_emi",
          "options":[{"label":"Zero — no existing loans","hint":"Best position"},{"label":"Under ₹10,000/month","hint":"Manageable"},{"label":"₹10,000–30,000/month","hint":"Moderate burden"},{"label":"₹30,000+/month","hint":"High burden — limit eligibility"}]},
         {"step":5,"question":"What is your credit score?","field_key":"credit_score",
          "options":[{"label":"750+ (Excellent)","hint":"Best rates available"},{"label":"700–750 (Good)","hint":"Good rates"},{"label":"650–700 (Average)","hint":"Higher rate likely"},{"label":"Below 650 or unknown","hint":"Check before applying"}]}],
        ["For a ₹60L home loan at 8.75% for 20 years, your EMI will be approximately ₹52,800/month.",
         "Your total EMI across all loans should not exceed 40% of take-home income — this is the bank's primary criterion.",
         "A CIBIL score above 750 can save you 0.25–0.5% on interest rate, which on ₹60L over 20 years saves ₹4–8 Lakhs.",
         "Making one extra EMI per year reduces a 20-year home loan tenure by 2–3 years."],
        [("Live rate comparison across SBI, HDFC, ICICI, Axis, Kotak","Current rates as of this month for your loan type"),
         ("Eligibility calculation — exact amount you qualify for","Based on your income and existing obligations"),
         ("Prepayment strategy — save lakhs in interest","Year-by-year prepayment schedule"),
         ("Balance transfer analysis — should you switch lender?","When switching saves money vs cost of switching"),
         ("Negotiation guide — how to get 0.25% rate reduction","Exact scripts used with bank relationship managers"),
         ("Fixed vs floating rate decision for your tenure","Which is better right now given rate cycle position")])

    # 9. INSURANCE PLANNING
    add_plan("insurance","Insurance Planning","Coverage gap analysis for your family",
        "❤️","#EFF6FF","#2563EB","BORROWING & PROTECTION",8,
        [{"step":1,"question":"What type of insurance are you planning for?","field_key":"insurance_type",
          "options":[{"label":"Health Insurance","hint":"Most critical first"},{"label":"Term Life Insurance","hint":"Income replacement"},{"label":"Car Insurance","hint":"Mandatory + protection"},{"label":"Home Insurance","hint":"Asset protection"},{"label":"All — comprehensive review","hint":"Full gap analysis"}]},
         {"step":2,"question":"How old are you?","field_key":"age",
          "options":[{"label":"18–25","hint":"Cheapest time to buy"},{"label":"26–35","hint":"Best value window"},{"label":"36–45","hint":"Buy before costs rise"},{"label":"46–55","hint":"Critical — act fast"},{"label":"55+","hint":"Limited options, higher premium"}]},
         {"step":3,"question":"Who needs to be covered?","field_key":"family",
          "options":[{"label":"Only me (single)","hint":"Individual policy"},{"label":"Me + spouse","hint":"Floater or separate"},{"label":"Family with young children","hint":"Family floater best"},{"label":"Family + elderly parents","hint":"Separate senior policy"}]},
         {"step":4,"question":"Do you have any existing health insurance?","field_key":"existing_health",
          "options":[{"label":"No health insurance","hint":"High priority gap"},{"label":"Company group cover only","hint":"Will lapse if you change jobs"},{"label":"Personal policy under ₹5L","hint":"Likely under-insured"},{"label":"Personal policy ₹10L+","hint":"May be adequate"}]},
         {"step":5,"question":"Do you have term life insurance?","field_key":"existing_term",
          "options":[{"label":"No life insurance at all","hint":"Critical gap if family depends on you"},{"label":"LIC endowment or money-back","hint":"Not real protection — low cover"},{"label":"Term plan under ₹50L","hint":"Likely under-insured"},{"label":"Term plan ₹1Cr+","hint":"May be adequate"}]}],
        ["Minimum health insurance: ₹10 Lakhs family floater for family of 4 in metro. Company insurance alone is insufficient.",
         "Term life cover should be 10–12x your annual income. If you earn ₹10L/year, you need ₹1–1.2 Crore cover.",
         "LIC endowment and money-back plans give poor life cover at high premium — they are savings products, not insurance.",
         "Buying health insurance before age 35 saves 40–60% in premiums for the same cover throughout your life."],
        [("Top 5 plans compared for your profile — Star, Niva Bupa, HDFC Ergo, Aditya Birla","Premiums, coverage, hospitals, claim ratio"),
         ("Coverage gap analysis — what you are missing","Based on your existing policies and family situation"),
         ("Claim settlement ratio analysis per insurer","Last 3 years data — who actually pays claims"),
         ("Hidden clause checker — what most policies exclude","Room rent limits, co-pay, sub-limits, waiting periods"),
         ("Right time to buy — age vs premium calculator","How each year you delay costs you in lifetime premium"),
         ("Family floater vs separate policies — which is better for you","Calculation based on age difference between family members")])

    # 10. EXPENSE PLANNING
    add_plan("expense-planning","Expense Planning","Ideal spending split for your income",
        "📊","#F0FDF4","#15803D","WEALTH BUILDING",9,
        [{"step":1,"question":"What is your monthly take-home income?","field_key":"income",
          "options":[{"label":"Under ₹30,000","hint":"Entry level"},{"label":"₹30,000–60,000","hint":"Average salaried"},{"label":"₹60,000–1,20,000","hint":"Mid-career"},{"label":"₹1,20,000–2,50,000","hint":"Senior professional"},{"label":"₹2,50,000+","hint":"High earner"}]},
         {"step":2,"question":"Which city do you live in?","field_key":"city",
          "options":[{"label":"Mumbai","hint":"Highest cost of living"},{"label":"Delhi NCR","hint":"High cost of living"},{"label":"Bengaluru","hint":"High rent, lower food"},{"label":"Hyderabad","hint":"Moderate cost"},{"label":"Pune","hint":"Moderate cost"},{"label":"Chennai","hint":"Moderate cost"}]},
         {"step":3,"question":"What is your family situation?","field_key":"family",
          "options":[{"label":"Single, no dependents","hint":"Maximum savings potential"},{"label":"Single, supporting parents","hint":"Higher obligations"},{"label":"Married, no kids yet","hint":"Dual income ideally"},{"label":"Married with children","hint":"Education and childcare costs"},{"label":"Joint family","hint":"Shared costs"}]},
         {"step":4,"question":"Do you have a home loan or rent?","field_key":"housing",
          "options":[{"label":"Living rent-free (own/parents)","hint":"Big saving advantage"},{"label":"Renting","hint":"Largest expense category"},{"label":"Home loan EMI","hint":"Building asset"},{"label":"Paying both rent + loan","hint":"High burden"}]},
         {"step":5,"question":"What is your current savings rate?","field_key":"savings_rate",
          "options":[{"label":"Less than 5%","hint":"Critical — fix immediately"},{"label":"5–10%","hint":"Below target"},{"label":"10–20%","hint":"Acceptable baseline"},{"label":"20–30%","hint":"Good discipline"},{"label":"30%+","hint":"Excellent — wealth builder"}]}],
        ["The 50-30-20 rule: 50% on needs (rent, food, bills), 30% on wants, 20% on savings and investments.",
         "If your rent alone exceeds 30% of income, you are likely over-spending on housing — consider suburb or smaller flat.",
         "Food spending above ₹15,000/month for a couple in India almost always means excessive ordering out.",
         "You need to save at least 20% of income to build wealth — anything below 10% means you will retire poor."],
        [("Personalised spending budget by category for your income and city","Not generic 50-30-20 — adjusted for your specific situation"),
         ("Rent affordability calculator","Exactly how much rent you can afford and where to look"),
         ("Food budget optimizer","Cooking vs ordering breakdown with realistic targets"),
         ("Spending leak identifier","The 5 categories where Indian middle class silently wastes most money"),
         ("Monthly budget template","Downloadable sheet with category-wise tracking"),
         ("Income raise planner","What to do with every ₹5,000 increment in income")])

    # 11. CAR OWNERSHIP
    add_plan("car-ownership","Car Ownership Cost","True cost of owning a car in India",
        "🚗","#FEF3C7","#D97706","LIFE PLANNING",10,
        [{"step":1,"question":"Which car segment are you considering?","field_key":"segment",
          "options":[{"label":"Hatchback (Swift, WagonR, Alto)","hint":"₹5–9L on-road"},{"label":"Compact Sedan (City, Verna)","hint":"₹12–18L on-road"},{"label":"Compact SUV (Creta, Seltos, Brezza)","hint":"₹15–22L on-road"},{"label":"SUV (XUV700, Thar, Fortuner)","hint":"₹20–45L on-road"},{"label":"Luxury (BMW, Audi, Mercedes)","hint":"₹45L–3Cr on-road"}]},
         {"step":2,"question":"Will you finance or buy in cash?","field_key":"payment",
          "options":[{"label":"Full cash purchase","hint":"No EMI burden"},{"label":"20–30% down, rest financed","hint":"Standard approach"},{"label":"Minimal down payment","hint":"Higher EMI burden"},{"label":"Not decided","hint":"Help me decide"}]},
         {"step":3,"question":"How many km will you drive per year?","field_key":"annual_km",
          "options":[{"label":"Under 10,000 km","hint":"Occasional use"},{"label":"10,000–20,000 km","hint":"Daily commute"},{"label":"20,000–30,000 km","hint":"Heavy use"},{"label":"30,000+ km","hint":"Commercial-level use"}]},
         {"step":4,"question":"Where will the car be registered?","field_key":"city",
          "options":[{"label":"Mumbai","hint":"High road tax"},{"label":"Delhi NCR","hint":"Moderate road tax"},{"label":"Bengaluru","hint":"Moderate road tax"},{"label":"Hyderabad","hint":"Lower road tax"},{"label":"Pune","hint":"Moderate road tax"},{"label":"Chennai","hint":"Moderate road tax"}]},
         {"step":5,"question":"Is this a first car or additional car?","field_key":"car_number",
          "options":[{"label":"First car in family","hint":"Essential purchase"},{"label":"Second car","hint":"Convenience purchase"},{"label":"Replacing existing car","hint":"Upgrade decision"}]}],
        ["True annual cost of a Creta in Mumbai: EMI (₹18K) + Insurance (₹15K) + Fuel (₹36K) + Service (₹8K) + Depreciation (₹1.5L) = ₹3.5 Lakhs/year.",
         "Depreciation is the biggest hidden cost. A car worth ₹12L today is worth ₹7.5L in 3 years — that's ₹1.5L/year loss before driving a single km.",
         "Electric vehicles (Tata Nexon EV, MG ZS EV) have 60–70% lower running cost per km vs petrol — ₹1.5 vs ₹8 per km.",
         "Car ownership makes financial sense if you drive 15,000+ km/year. Below that, cabs may be cheaper."],
        [("Complete annual ownership cost calculation","EMI + Insurance + Fuel + Service + Depreciation + Parking — exact rupee figure"),
         ("New vs used car analysis","2-year-old same model saves ₹2–4L with same performance"),
         ("Petrol vs diesel vs EV total cost comparison","Break-even analysis for your annual km"),
         ("Best time to buy — new model cycle tracking","When to wait for price drop vs when to buy now"),
         ("Car loan rate comparison — which bank is cheapest right now","SBI, HDFC, ICICI, Kotak current rates"),
         ("Resale value projector","Expected value at 3, 5, and 7 years for your chosen model")])

    # 12. HOME LOAN SPECIFIC
    add_plan("home-loan","Home Loan Guide","Complete home buying financial checklist",
        "🏘️","#F0FDF4","#059669","BORROWING & PROTECTION",11,
        [{"step":1,"question":"Are you buying under-construction or ready property?","field_key":"property_type",
          "options":[{"label":"Under-construction (builder)","hint":"Lower price, longer wait"},{"label":"Ready to move in","hint":"Higher price, immediate"},{"label":"Resale flat","hint":"Negotiable, established area"},{"label":"Plot purchase","hint":"Construction loan later"}]},
         {"step":2,"question":"What is your budget for the property?","field_key":"property_value",
          "options":[{"label":"Under ₹40 Lakhs","hint":"Affordable housing"},{"label":"₹40–80 Lakhs","hint":"Mid-range housing"},{"label":"₹80L–1.5 Crore","hint":"Premium housing"},{"label":"₹1.5 Crore+","hint":"Luxury housing"}]},
         {"step":3,"question":"What is your household monthly income?","field_key":"income",
          "options":[{"label":"Under ₹60,000","hint":"Affordable segment focus"},{"label":"₹60,000–1,20,000","hint":"Standard eligibility"},{"label":"₹1,20,000–2,50,000","hint":"Good eligibility"},{"label":"₹2,50,000+","hint":"High eligibility"}]},
         {"step":4,"question":"How many years do you want to repay?","field_key":"tenure",
          "options":[{"label":"10–12 years","hint":"Higher EMI, less interest"},{"label":"15–18 years","hint":"Balanced approach"},{"label":"20–25 years","hint":"Lower EMI, more interest"},{"label":"30 years","hint":"Minimum EMI, maximum interest"}]},
         {"step":5,"question":"Is this for first-time home buying?","field_key":"first_home",
          "options":[{"label":"Yes — first home","hint":"Additional tax benefits"},{"label":"No — second or investment property","hint":"Different tax treatment"},{"label":"Refinancing existing loan","hint":"Balance transfer scenario"}]}],
        ["For a ₹80L property, you need at least ₹16L as down payment (20%) plus ₹3–5L for registration and stamp duty.",
         "Home loan gives ₹2L tax deduction on interest (Section 24) + ₹1.5L on principal (Section 80C) — total ₹3.5L/year.",
         "Under-construction property typically costs 15–20% less than ready-to-move — but add 2–3 years of rent payment to the equation.",
         "PMAY subsidy for first-time buyers with income under ₹18L gives ₹2.67L interest subsidy — apply through your bank."],
        [("Total cost of buying breakdown","Property price + stamp duty + registration + GST + brokerage"),
         ("EMI vs rent comparison for your specific city and budget","When buying makes more financial sense than renting"),
         ("Loan eligibility calculator across 8 banks","Exact amount you qualify for at each bank today"),
         ("Stamp duty and registration cost by state","Full list with current rates"),
         ("PMAY subsidy eligibility check and application guide","Step-by-step subsidy claim process"),
         ("Tax benefit calculator for your income bracket","Annual saving from home loan deductions")])

    db.commit()

    # ══════════════════════════════════════════════════════════════
    # EXPENSE CATEGORIES (for planning guide)
    # ══════════════════════════════════════════════════════════════
    expense_cats = [
        ("Food & Groceries",      "ti-tools-kitchen-2", "#7A4208", 15),
        ("Rent / Housing",        "ti-home",            "#0A6E52", 25),
        ("Transport",             "ti-car",             "#1A4FA0", 8),
        ("Electricity & Bills",   "ti-bulb",            "#4A35A8", 4),
        ("Health & Medical",      "ti-heart-rate",      "#9B2121", 5),
        ("Travel & Leisure",      "ti-plane",           "#8B1A4A", 8),
        ("Subscriptions & Net",   "ti-device-mobile",   "#7A2E10", 3),
        ("Children & Education",  "ti-school",          "#0369A1", 7),
        ("Clothing & Grooming",   "ti-hanger",          "#4A35A8", 4),
        ("Savings & Investments", "ti-pig-money",       "#1A5C2A", 20),
    ]
    for i,(name,icon,color,pct) in enumerate(expense_cats):
        ec = ExpenseCategory(name=name,icon_key=icon,color_hex=color,
                             recommended_pct=pct,sort_order=i)
        db.add(ec); db.flush()

        if name == "Rent / Housing":
            db.add(ExpenseRule(expense_cat_id=ec.id,income_min=None,income_max=60000,
                city_tier="metro",advice="Rent above 30% of income in metros is financially dangerous. Consider Thane, Navi Mumbai, or Faridabad to save ₹10,000–20,000/month."))
            db.add(ExpenseRule(expense_cat_id=ec.id,income_min=60000,income_max=None,
                city_tier="metro",advice="With income above ₹60K, keep rent under ₹20,000 in Mumbai or ₹18,000 in Bengaluru — spend saved money on SIPs instead."))
        elif name == "Food & Groceries":
            db.add(ExpenseRule(expense_cat_id=ec.id,income_min=None,income_max=None,
                city_tier="any",advice="Food above 20% of income usually means too much eating out. Home cooking for 80% of meals keeps this at 10–12% of income."))
            db.add(ExpenseRule(expense_cat_id=ec.id,income_min=None,income_max=50000,
                city_tier="any",advice="Buy vegetables from local sabzi mandi twice a week. Avoid supermarket premium. Cook in bulk on Sunday. This saves ₹2,000–3,000/month easily."))
        elif name == "Savings & Investments":
            db.add(ExpenseRule(expense_cat_id=ec.id,income_min=None,income_max=40000,
                city_tier="any",advice="Even saving ₹2,000–3,000/month is meaningful. Start a small SIP. Consistency beats amount."))
            db.add(ExpenseRule(expense_cat_id=ec.id,income_min=40000,income_max=None,
                city_tier="any",advice="If you are saving less than 20% of income, you are falling behind. Automate SIP on salary day — save before you spend."))
        elif name == "Transport":
            db.add(ExpenseRule(expense_cat_id=ec.id,income_min=None,income_max=None,
                city_tier="metro",advice="Car ownership in metros costs ₹20,000–40,000/month all-in. Compare with cab cost before buying. Metro + auto + occasional cab is often cheaper."))

    db.commit()
    db.close()
    print("✅  MoneyMind database seeded successfully!")
    print("    Categories:", 46)
    print("    Products:", 30)
    print("    Plans:", 12)
    print("    Money Hacks:", 12)
    print("    Price Bulletins:", 8)
    print("    Expense Categories:", 10)

if __name__ == "__main__":
    seed()
