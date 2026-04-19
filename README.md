# RSD Qualify — qualify.rsddirect.com
### Service-Fit Qualification · Node.js · Vercel Deploy

> Real Space Digital · Digitizing Reality, Elevating Sales.

A standalone Node.js app that serves the 11-page RSD qualification funnel as a subdomain (`qualify.rsddirect.com`), **completely non-disruptive to the main rsddirect.com site**. On submission, it fires to GHL, generates a printable report, and saves it to Google Drive.

---

## Quick Start

### 1. Install dependencies
```bash
npm install
```

### 2. Configure environment
```bash
cp .env.example .env
# Fill in: GHL_WEBHOOK_URL, GOOGLE_CLIENT_EMAIL, GOOGLE_PRIVATE_KEY, GOOGLE_DRIVE_PARENT_FOLDER_ID
```

### 3. Run locally
```bash
npm start
# Open: http://localhost:3000
```

---

## Project Structure

```
qualify-node/
├── api/
│   └── submit.js              ← POST /api/submit — GHL + report + Drive
├── lib/
│   ├── reportGenerator.js     ← Builds printable HTML estimate report
│   └── googleDrive.js         ← Uploads report to Google Drive
├── public/
│   └── pages/
│       ├── rsd-funnel-page-01-hero.html
│       ├── rsd-funnel-page-02-qualify.html
│       ├── ...
│       ├── rsd-funnel-page-10-summary.html  ← Enhanced: mobile, SMS opt-in, /api/submit
│       └── rsd-funnel-page-11-confirm.html
├── server.js                  ← Local Express server
├── vercel.json                ← Vercel deployment config
├── .env.example               ← Environment variable template
└── package.json
```

---

## Deployment to Vercel (Subdomain)

### Step 1 — Push to GitHub
```bash
git init
git add -A
git commit -m "init: RSD qualify subdomain"
git remote add origin https://github.com/ZDJ-VENTURES888/rsd-qualify.git
git push -u origin main
```

### Step 2 — Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) → New Project
2. Import `ZDJ-VENTURES888/rsd-qualify`
3. Framework preset: **Other**
4. Click Deploy

### Step 3 — Add Environment Variables in Vercel
Vercel Dashboard → Project → Settings → Environment Variables. Add:

| Key | Value |
|---|---|
| `GHL_WEBHOOK_URL` | Your GHL webhook URL |
| `GOOGLE_CLIENT_EMAIL` | Service account email |
| `GOOGLE_PRIVATE_KEY` | Full private key (with `\n` escapes) |
| `GOOGLE_DRIVE_PARENT_FOLDER_ID` | Drive parent folder ID |

### Step 4 — Connect Subdomain
Vercel Dashboard → Project → Settings → Domains → Add `qualify.rsddirect.com`

In your DNS (wherever rsddirect.com is hosted — Hostinger, Namecheap, Cloudflare, etc.):
```
Type: CNAME
Name: qualify
Value: cname.vercel-dns.com
```

**That's it.** The main rsddirect.com is completely untouched.

---

## Google Drive Setup

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create or select a project
3. Enable **Google Drive API**
4. Go to **IAM & Admin → Service Accounts** → Create service account
5. Download the JSON key → copy `client_email` and `private_key` into `.env`
6. In Google Drive, create a folder: **"RSD Qualifications"**
7. Right-click → Share → paste the service account email (give it Editor access)
8. Copy the folder ID from the URL: `drive.google.com/drive/folders/`**`THIS_PART`**
9. Paste it into `.env` as `GOOGLE_DRIVE_PARENT_FOLDER_ID`

### Per-Prospect Folder Structure (Auto-Created)
```
RSD Qualifications/
└── John Smith — Smith Design Build — Apr 19 2026/
    └── RSD-Fit-Report-John-Smith-2026-04-19.html
```

---

## Submission Flow

```
Prospect fills Page 10 form
         ↓
POST /api/submit
         ├── → GHL Webhook (fires to pipeline: Guarantee Qualified / Speed to Prosperity / Building Foundation)
         ├── → Generate HTML report (contact info + qual score + selections + totals + tier)
         ├── → Upload to Google Drive (per-prospect folder)
         └── → Return { success, tier, driveLink } to browser
                  ↓
         Show Drive link + redirect to Page 11
```

---

## Enhanced Contact Fields (Page 10)

| Field | Required | Notes |
|---|---|---|
| First Name | Yes | |
| Last Name | Yes | |
| Business Name | No | |
| Email | Yes | |
| Phone / Office | Yes* | *Either phone or mobile required |
| Mobile / Cell | No | Recommended for SMS |
| SMS Opt-In | No | TCPA-compliant language included |

---

## GHL Pipeline Routing

The `pipeline_route` custom field in GHL receives one of three values:

| Value | Trigger Condition |
|---|---|
| `Guarantee Qualified` | Core Package selected OR Social Pack + Web presence |
| `Speed to Prosperity` | À la carte, combined total ≥ $6,000, no qualifying package |
| `Building Foundation` | All other submissions |

Build your GHL workflow with a condition branch on this field to route leads automatically.

---

*Real Space Digital × ZDJ Ventures LLC · communications@zdj-ventures.com*
