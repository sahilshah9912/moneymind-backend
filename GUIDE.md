# MoneyMind v3 — Complete Guide
## From your desktop to Play Store

---

## YOUR FILES (put all in one folder on Desktop called moneymind_v3)

```
moneymind_v3/
├── backend/
│   ├── main.py          ← Server with all routes + lead capture + admin
│   ├── models.py        ← Database structure
│   ├── database.py      ← DB connection
│   ├── seed.py          ← Pricing data (already seeded in moneymind.db)
│   ├── moneymind.db     ← ✅ Ready — 1,062 cities, 38,233 records
│   └── requirements.txt ← Python packages
├── frontend/
│   ├── App.js           ← Complete app — 4 tabs, no profile, no UPI
│   ├── package.json     ← SDK 54 compatible
│   ├── app.json         ← Play Store config
│   ├── eas.json         ← Build profiles
│   └── babel.config.js  ← Build tools
└── admin/
    └── admin.html       ← Open in browser — full admin panel
```

---

## PART A — TEST ON YOUR PHONE (30 minutes)

### Step 1 — Start the backend

Open Command Prompt → navigate to backend folder:
```
cd %USERPROFILE%\Desktop\moneymind_v3\backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8770
```

Leave this window open. Test: open browser → http://localhost:8770/api/health
You should see: {"status":"ok","cities":1062}

### Step 2 — Update your IP in App.js

Find your IP: open new CMD → type `ipconfig` → look for IPv4 Address (e.g. 192.168.1.5)

Open App.js in Notepad → line 8:
```
const API_BASE = 'http://YOUR_IP_HERE:8770/api';
```
Replace YOUR_IP_HERE with your actual IP. Save.

### Step 3 — Run the app

Open new CMD window:
```
cd %USERPROFILE%\Desktop\moneymind_v3\frontend
npm install --legacy-peer-deps
npx expo start --clear
```

Scan QR code with Expo Go on your phone.

### Step 4 — Use the Admin Panel

Double-click admin/admin.html — opens in your browser.
- Backend URL: http://localhost:8770
- Admin Secret: moneymind_admin_2025
Click Login → you're in.

---

## PART B — DEPLOY BACKEND TO RAILWAY (free, 20 minutes)

Railway hosts your backend so the app works for everyone — not just your laptop.

### Step 1 — Create Railway account
Go to https://railway.app → Sign Up with Google (free)

### Step 2 — Install Railway tool
In CMD:
```
npm install -g @railway/cli
railway login
```
A browser opens → log in → come back to CMD.

### Step 3 — Deploy
```
cd %USERPROFILE%\Desktop\moneymind_v3\backend
railway init
```
Name it: moneymind-backend → press Enter

```
railway up
```
Wait 3-4 minutes. Railway gives you a URL like:
https://moneymind-backend-production.up.railway.app

### Step 4 — Add your admin secret on Railway
- Go to railway.app → your project → Variables tab
- Add variable: ADMIN_SECRET = moneymind_admin_2025
- (Change this to something only you know!)

### Step 5 — Update App.js with Railway URL
Open App.js → line 8:
```
const API_BASE = 'https://moneymind-backend-production.up.railway.app/api';
```
Replace with YOUR actual Railway URL. Save.

### Step 6 — Test live backend
Open browser → https://your-railway-url.railway.app/api/health
Should show: {"status":"ok","cities":1062}

### Step 7 — Use Admin Panel with live backend
Open admin.html → enter your Railway URL → Login
Now you can manage content from anywhere in the world!

---

## PART C — BUILD APK FOR PLAY STORE (30 minutes)

### Step 1 — Create Expo account
Go to https://expo.dev → Sign Up (free)

### Step 2 — Login and build
```
cd %USERPROFILE%\Desktop\moneymind_v3\frontend
eas login
```
Enter your Expo account details.

```
eas build --platform android --profile production
```

When asked "Generate a new keystore?" → type Y → press Enter
IMPORTANT: Expo will show you keystore details — screenshot and save them forever.
You need the same keystore for every future update.

Wait 15-20 minutes. Expo builds on their cloud servers.
When done → they give you a download link for your .aab file.

### Step 3 — Download the .aab file
Click the link → download moneymind-*.aab
This is your Play Store file.

---

## PART D — PUBLISH ON PLAY STORE (1-2 hours setup, 3-7 days review)

### Step 1 — Google Play Console account
Go to https://play.google.com/console
Sign in with Google → Create developer account
Pay $25 (one-time, ≈ ₹2,100)
Takes 1-2 days to verify.

### Step 2 — Create your app
Play Console → Create app
- App name: MoneyMind
- Default language: English (India)
- App or game: App
- Free or paid: Free
Click: Create app

### Step 3 — Fill Store Listing

SHORT DESCRIPTION (80 chars max — copy this exactly):
```
Know the right price for anything. 1,062 Indian cities. Free.
```

FULL DESCRIPTION (copy this):
```
MoneyMind is India's smartest price intelligence platform.

PRICE DISCOVERY — 100% FREE FOREVER
Find fair market prices for anything — painting, kitchen renovation, AC service, car repairs, groceries, flights, hotels, weddings and more.

Prices for 1,062 cities across India — from Mumbai to small towns.
No guesswork. Real market data. Completely free.

MONEY SAVING HACKS
Daily practical tips that save ₹500–₹3,000 per month:
• Set your AC at 24°C and save ₹800/month on electricity
• Buy vegetables Wednesday morning — 25% cheaper than Saturday evening  
• Book flights on Tuesday afternoon — 20% lower fares
• Switch to 84-day recharge — save ₹300/month on mobile bill

PRICE BULLETIN
See what's changing today across India:
• Tomato prices down 18% in Mumbai
• Onion prices rising — stock up now
• Hotel rates in Goa 32% cheaper this month

FINANCIAL PLANNING — FREE EXPERT GUIDANCE
12 expert planners:
• Wedding planning — budget, venue, catering breakdown
• Home renovation — cost per sq ft for your city
• SIP & Investments — corpus projection
• Retirement planning — how much you need
• Home loan — EMI, eligibility, prepayment strategy
• Insurance — coverage gap analysis
• Car ownership — true annual cost
• Emergency fund, vacation, education planning

Answer questions → get free analysis → our team calls you with a personalised plan.

MoneyMind is 100% free. Price discovery is always free. No subscription. No hidden charges.

Built for the Indian middle class. Smart money decisions, made simple.
```

### Step 4 — Screenshots (required)
Take screenshots from your phone while using the app:
1. Home screen (Discover)
2. Price Check result (search "painter Mumbai")
3. Categories screen
4. Planning screen
Minimum 2 screenshots required.

### Step 5 — Privacy Policy (required by Google)

Create a free Google Site:
1. Go to sites.google.com → New site
2. Title: MoneyMind Privacy Policy
3. Add text:

MoneyMind Privacy Policy — Last updated: [today's date]

What we collect:
- Search queries (to improve our price database)
- Your city (to show relevant prices)  
- Phone number if you request a call back (optional)

What we do NOT collect:
- No account required
- No passwords stored
- No payment details stored
- We do not sell your data

Contact: your-email@gmail.com

4. Publish → copy the URL
5. Paste URL in Play Console → App Content → Privacy Policy

### Step 6 — Content Rating
Play Console → Policy → App Content → Content Rating
Start questionnaire → Category: Finance → answer No to everything → Submit
You'll get rating: Everyone

### Step 7 — Upload AAB
Production → Create new release → Upload → select your .aab file
Release notes: "Initial launch — Price intelligence for India"
Save → Review → Submit

### Wait
Google reviews in 3-7 business days.
You'll get an email when approved.

---

## PART E — ADMIN PANEL USAGE

Open admin/admin.html in Chrome → login with your Railway URL + secret key.

WHAT YOU CAN DO:

📊 Dashboard
- See total leads (people who requested a call)
- See how many searches have been done
- Recent leads with phone numbers

📞 Leads  
- Full list of all users who asked for a call back
- Export as CSV to Excel
- Call them directly!

🗂️ Categories
- Add new categories (e.g. "Wedding Catering", "Solar Panels")
- Edit existing category names, icons, subtitles
- Delete categories
- Sort order controls what appears first

💡 Money Hacks
- Add new saving tips
- Edit existing hacks
- Delete outdated tips
- Choose category tag (ELECTRICITY, GROCERY, TRAVEL, etc.)

📰 Price Bulletin  
- Add new price news (e.g. "Mango prices drop 20% this week")
- Edit existing bulletins
- Delete old news
- Set + or - percentage to show as green (drop) or red (rise)

📈 Market Ticker
- Edit the scrolling ticker values (Gold, Petrol, Tomato, etc.)
- Update prices daily if you want fresh data

🔥 Trending Searches
- Add popular search terms
- Remove outdated ones
- These appear as chips on the home screen

---

## COSTS — TOTAL TO LAUNCH

| Item | Cost |
|------|------|
| Google Play account | $25 one-time ≈ ₹2,100 |
| Railway hosting | Free (up to $5/month usage) |
| Expo EAS Build | Free (3 builds/month) |
| Admin panel | Free (just an HTML file!) |
| Domain (optional) | ₹800/year |
| TOTAL | ≈ ₹2,500 to launch |

Railway free tier is enough for hundreds of daily users.
Only upgrade if you get 1,000+ daily users (good problem to have!).

---

## CHANGING THE ADMIN SECRET

Default secret is: moneymind_admin_2025
Change it before going live!

On Railway: Variables → ADMIN_SECRET → change to your own secret
Keep it private — whoever has this key can edit your entire database.

---

## YOUR CHECKLIST

[ ] All files placed in moneymind_v3 folder on Desktop
[ ] Backend runs locally (http://localhost:8770/api/health works)  
[ ] App shows on phone via Expo Go
[ ] Admin panel opens and logs in
[ ] Railway account created
[ ] Backend deployed to Railway
[ ] App.js updated with Railway URL
[ ] Expo account created
[ ] EAS build completed — .aab downloaded
[ ] Play Console account created ($25 paid)
[ ] Store listing filled (description, screenshots, privacy policy)
[ ] AAB uploaded and submitted for review
[ ] 🚀 MoneyMind LIVE on Play Store!
