// ─────────────────────────────────────────────────────────────
//  RSD Qualify — POST /api/submit
//  Receives form data from Page 10, then:
//    1. Validates required fields
//    2. Fires payload to GHL webhook
//    3. Generates printable HTML report
//    4. Saves report to Google Drive (per-prospect folder)
//    5. Returns JSON with success + Drive link
// ─────────────────────────────────────────────────────────────

if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config();
}

const fetch               = require('node-fetch');
const { generateReport }  = require('../lib/reportGenerator');
const { saveReportToDrive } = require('../lib/googleDrive');

// ── Allowed origins ──────────────────────────────────────────
const ALLOWED_ORIGINS = [
  'https://qualify.rsddirect.com',
  'https://rsddirect.com',
  'http://localhost:3000',
];

// ── Raw body reader (fallback for unparsed stream requests) ──
function readRawBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', chunk => { data += chunk.toString(); });
    req.on('end',  ()    => resolve(data));
    req.on('error', err  => reject(err));
  });
}

module.exports = async function handler(req, res) {

  // ── Top-level safety net — never let an unhandled error return a raw 500 ──
  try {

  // CORS
  const origin = req.headers.origin || '';
  if (ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST')    return res.status(405).json({ error: 'Method not allowed' });

  // ── Parse body: handle auto-parsed object, JSON string, or raw stream ──
  let body = {};
  try {
    if (req.body !== undefined && req.body !== null) {
      if (typeof req.body === 'object' && !Buffer.isBuffer(req.body)) {
        // Already parsed by Vercel runtime
        body = req.body;
      } else {
        // String or Buffer
        const str = Buffer.isBuffer(req.body) ? req.body.toString('utf8') : req.body;
        body = str ? JSON.parse(str) : {};
      }
    } else {
      // Stream not yet read — read it manually
      const raw = await readRawBody(req);
      body = raw ? JSON.parse(raw) : {};
    }
  } catch (parseErr) {
    console.error('[Submit] Body parse failed:', parseErr.message);
    return res.status(400).json({ error: 'Invalid JSON body' });
  }

  // ── Safe destructure — never throws even if body is weird ──
  const {
    contact      = {},
    items        = [],
    pkg          = null,
    gf           = null,
    qual         = [],
    preCallQuestion = '',
  } = (body && typeof body === 'object') ? body : {};

  console.log('[Submit] Received — contact:', contact.firstName, contact.lastName, '| items:', items.length, '| pkg:', pkg);

  // ── Validation ─────────────────────────────────────────────
  const errors = [];
  if (!contact.firstName?.trim()) errors.push('First name is required.');
  if (!contact.lastName?.trim())  errors.push('Last name is required.');
  if (!contact.email?.trim())     errors.push('Email address is required.');
  if (!contact.phone?.trim() && !contact.mobile?.trim()) errors.push('At least one phone number is required.');

  if (errors.length) {
    return res.status(422).json({ error: errors.join(' ') });
  }

  // ── Build GHL payload ──────────────────────────────────────
  const fullName   = `${contact.firstName} ${contact.lastName}`.trim();
  const qualScore  = Array.isArray(qual) ? qual.reduce((a, b) => a + b, 0) : 0;

  // Compute totals for GHL custom fields
  const D_PRICE_MAP = {
    scan_base:1299,scan_guided:1799,vid_single:500,vid_pack:1200,drone_half:350,drone_full:600,
    vid_authority:1800,vid_testimonial:1800,photo_half:400,photo_full:800,
    lp_base:1800,lp_conv:2800,lp_about:500,lp_vt:250,lp_vid:100,lp_cal:120,lp_social:250,ao_page:997,ao_ai_base:49,ao_ai_heavy:99,
    gbp_setup:700,gbp_scale:550,gbp_support:350,meta_setup:900,meta_scale:650,meta_own:450,
    rev_roadmap:497,rev_referral:397,rev_mailer:297,rep_mkt:297,soc3:497,soc5:797,soc7:1097,
    ad_mgmt:497,mkt_active:1800,rr_recep:397,rr_text:197,rr_sms:297,rr_full:497,
  };
  const D_TYPE_MAP = {
    scan_base:'one',scan_guided:'one',vid_single:'one',vid_pack:'one',drone_half:'one',drone_full:'one',
    vid_authority:'one',vid_testimonial:'one',photo_half:'one',photo_full:'one',
    lp_base:'one',lp_conv:'one',lp_about:'one',lp_vt:'one',lp_vid:'one',lp_cal:'one',lp_social:'one',ao_page:'one',ao_ai_base:'mo',ao_ai_heavy:'mo',
    gbp_setup:'one',gbp_scale:'one',gbp_support:'one',meta_setup:'one',meta_scale:'one',meta_own:'one',
    rev_roadmap:'one',rev_referral:'one',rev_mailer:'one',rep_mkt:'mo',soc3:'mo',soc5:'mo',soc7:'mo',
    ad_mgmt:'mo',mkt_active:'mo',rr_recep:'mo',rr_text:'mo',rr_sms:'mo',rr_full:'mo',
  };
  const PKG_PRICE_MAP = { pkg_t2b:5549, pkg_ao:6549, pkg_os:9549 };
  const GF_DISC_MAP   = { gf1:0.05, gf2:0.10, gf3:0.15 };

  let oneTime = 0, monthly = 0;
  for (const id of items) {
    if (!D_PRICE_MAP[id]) continue;
    if (D_TYPE_MAP[id] === 'one') oneTime += D_PRICE_MAP[id];
    else                           monthly += D_PRICE_MAP[id];
  }
  if (pkg && PKG_PRICE_MAP[pkg]) oneTime += PKG_PRICE_MAP[pkg];
  const combined    = oneTime + monthly;
  const discRate    = gf ? GF_DISC_MAP[gf] || 0 : 0;
  const discount    = Math.round(combined * discRate);
  const downPayment = Math.round(oneTime * 0.25);

  // Tier routing
  const SOC_PACK  = ['soc3','soc5','soc7'];
  const WEB_ITEMS = ['lp_base','lp_conv','lp_about','ao_page','gbp_setup','gbp_scale'];
  const hasPkg    = !!pkg;
  const hasSoc    = SOC_PACK.some(id => items.includes(id));
  const hasWeb    = WEB_ITEMS.some(id => items.includes(id));
  const isQual    = hasPkg || (hasSoc && hasWeb);
  const isPromo   = !isQual && combined >= 6000;
  const tierRoute = isQual ? 'Guarantee Qualified' : isPromo ? 'Speed to Prosperity' : 'Building Foundation';

  // Qual criteria labels
  const QUAL_LABELS = [
    'Google Business Profile (claimed + verified)',
    'Meta Business Suite / Ad Manager account ownership',
    'Existing media (photos, video, or tour footage)',
    'Active website or landing page',
    'Working phone number and email for lead routing',
    'Clear service or product offering with pricing'
  ];
  const qualArr     = Array.isArray(qual) ? qual : [];
  const qualMet     = QUAL_LABELS.filter((_, i) => qualArr[i] === 1);
  const qualMissing = QUAL_LABELS.filter((_, i) => qualArr[i] !== 1);
  const qualSummary = `${qualMet.length} of 6 prerequisites met — ${tierRoute}`;

  // Item labels
  const ITEM_LABELS = {
    scan_base:'3D Matterport Scan — Base', scan_guided:'Virtual Guided Tour',
    vid_single:'1 Conversion Video', vid_pack:'Video Starter Pack',
    drone_half:'Drone — Half Day', drone_full:'Drone — Full Day',
    vid_authority:'Owner / Stakeholder Authority Video', vid_testimonial:'Testimonial Video',
    photo_half:'Product Photography — Half Day', photo_full:'Product Photography — Full Day',
    lp_base:'Base Landing Page', lp_conv:'Conversion Capture Page',
    ao_ai_base:'AI Access Membership — Foundational Scaling ($49/mo)', ao_ai_heavy:'AI Access Membership — Heavy User ($99/mo)',
    lp_about:'About / Story Page', lp_vt:'Virtual Tour Embed Page',
    lp_vid:'Video Embed Add-on', lp_cal:'Calendar / Booking Add-on',
    lp_social:'Social Proof Page', ao_page:'Authority Outreach Page',
    gbp_setup:'Google Business Profile Setup', gbp_scale:'GBP Scale Package',
    gbp_support:'GBP Monthly Support', meta_setup:'Meta Ads Setup',
    meta_scale:'Meta Ads Scale Package', meta_own:'Meta Ads Self-Management',
    rev_roadmap:'Reputation Roadmap', rev_referral:'Referral System',
    rev_mailer:'Review Mailer Campaign', rep_mkt:'Reputation Marketing (mo)',
    soc3:'Social Content — 3 posts/wk', soc5:'Social Content — 5 posts/wk',
    soc7:'Social Content — 7 posts/wk', ad_mgmt:'Ad Management (mo)',
    mkt_active:'Active Marketing + Ad Management (4 posts/wk + Meta & Google campaigns)',
    rr_recep:'Rapid Response — Reception', rr_text:'Rapid Response — Text',
    rr_sms:'Rapid Response — SMS Drip', rr_full:'Rapid Response — Full Suite'
  };
  const PKG_LABELS = {
    pkg_t2b:'The Total Business Package',
    pkg_ao:'Authority & Outreach Package',
    pkg_os:'Online Sovereignty Package'
  };
  const selectedItemsReadable = items.map(id => ITEM_LABELS[id] || id).join(', ');
  const selectedPkgReadable   = pkg ? `${PKG_LABELS[pkg] || pkg} ($${PKG_PRICE_MAP[pkg]?.toLocaleString() || ''})` : '';

  // ── GHL payload — contact fields at ROOT level for native mapping ──
  const ghlPayload = {
    firstName:    contact.firstName,
    lastName:     contact.lastName,
    email:        contact.email,
    phone:        contact.phone || contact.mobile || '',
    companyName:  contact.businessName || '',
    name:         fullName,
    mobile_number:             contact.mobile || '',
    sms_opt_in:                contact.smsOptIn ? 'Yes' : 'No',
    pre_call_question:         preCallQuestion || '',
    qual_score:                qualScore,
    qual_criteria:             qualArr.join(','),
    selected_package:          pkg || '',
    selected_items:            items.join(','),
    founder_lock:              gf || '',
    one_time_total:            oneTime,
    monthly_total:             monthly,
    combined_total:            combined,
    discount_applied:          discount,
    down_payment:              downPayment,
    pipeline_route:            tierRoute,
    source_url:                'qualify.rsddirect.com',
    submission_date:           new Date().toISOString(),
    qual_criteria_met:         qualMet.join(', '),
    qual_criteria_missing:     qualMissing.join(', '),
    qual_summary:              qualSummary,
    selected_items_readable:   selectedItemsReadable,
    selected_package_readable: selectedPkgReadable,
  };

  // ── Fire GHL Webhook ───────────────────────────────────────
  let ghlStatus = 'skipped';
  const ghlUrl = process.env.GHL_WEBHOOK_URL;

  console.log('[GHL] Webhook URL set:', !!ghlUrl);

  if (ghlUrl && ghlUrl !== 'REPLACE_WITH_YOUR_GHL_WEBHOOK_URL') {
    try {
      const ghlRes = await fetch(ghlUrl, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(ghlPayload),
        timeout: 8000,
      });
      ghlStatus = ghlRes.ok ? 'sent' : `error_${ghlRes.status}`;
      console.log('[GHL] Webhook status:', ghlStatus);
    } catch (err) {
      console.error('[GHL] Webhook failed:', err.message);
      ghlStatus = 'error';
    }
  } else {
    console.warn('[GHL] GHL_WEBHOOK_URL not configured — skipping. Set this env var in Vercel project settings.');
  }

  // ── Generate HTML Report ───────────────────────────────────
  let reportHtml = null, driveLink = null;
  try {
    reportHtml = generateReport({ contact, items, pkg, gf, qual: qualArr });
  } catch (err) {
    console.error('[Report] Generation failed:', err.message);
  }

  // ── Save to Google Drive ───────────────────────────────────
  if (reportHtml) {
    try {
      driveLink = await saveReportToDrive(reportHtml, contact);
    } catch (err) {
      console.error('[Drive] Save failed:', err.message);
    }
  }

  // ── Respond ────────────────────────────────────────────────
  return res.status(200).json({
    success:   true,
    message:   'Submission received. We\'ll be in touch within 24 hours.',
    ghlStatus,
    driveLink,
    tier:      tierRoute,
    totals: { oneTime, monthly, combined, discount, downPayment },
  });

  } catch (fatalErr) {
    // Safety net — log and return structured error instead of raw 500
    console.error('[Submit] Fatal unhandled error:', fatalErr.message, fatalErr.stack);
    return res.status(500).json({ error: 'Internal server error', detail: fatalErr.message });
  }
};
