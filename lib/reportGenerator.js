// ─────────────────────────────────────────────────────────────
//  RSD Qualify — Report Generator
//  Builds a print-optimized HTML report from submission payload.
//  Saved to Google Drive. User can open + Ctrl+P → Save as PDF.
// ─────────────────────────────────────────────────────────────

const D_NAME = {
  scan_base:'Scan Your Space (≤3k sqft)',scan_guided:'Virtual Guided Tour',
  vid_single:'1 Conversion Video',vid_pack:'Video Starter Pack',
  drone_half:'Drone — Half Day',drone_full:'Drone — Full Day',
  lp_base:'Base Landing Page',lp_conv:'Conversion Capture Page',
  lp_about:'About Us Page',lp_vt:'Virtual Tour Integration',
  lp_vid:'Brand Video Embed',lp_cal:'Calendar Booking',
  lp_social:'Social Feed Integration',ao_page:'AlwaysOn Conversion Page',
  gbp_setup:'GBP Full Setup',gbp_scale:'GBP Scaling & Optimization',
  gbp_support:'GBP Ownership Support',meta_setup:'Meta Full Setup/Migration',
  meta_scale:'Meta Scaling & Audit',meta_own:'Meta Ownership Support',
  rev_roadmap:'Speed to 10+ Reviews Roadmap',rev_referral:'Referral Reputation System',
  rev_mailer:'QR-to-Google Review Mailer',rep_mkt:'Reputation Marketing',
  soc3:'Social Content — 3/Week',soc5:'Social Content — 5/Week',soc7:'Social Content — 7/Week',
  ad_mgmt:'Monthly Ad Management',rr_recep:'AI Receptionist Booking',
  rr_text:'Missed-Call Text Back',rr_sms:'SMS Q&A + Auto-Booking',
  rr_full:'Full Rapid Response Suite',
};

const D_PRICE = {
  scan_base:1299,scan_guided:1799,vid_single:500,vid_pack:1200,
  drone_half:350,drone_full:600,lp_base:550,lp_conv:800,lp_about:500,
  lp_vt:250,lp_vid:100,lp_cal:120,lp_social:250,ao_page:997,
  gbp_setup:350,gbp_scale:275,gbp_support:175,meta_setup:450,
  meta_scale:325,meta_own:225,rev_roadmap:497,rev_referral:397,
  rev_mailer:297,rep_mkt:297,soc3:497,soc5:797,soc7:1097,
  ad_mgmt:497,rr_recep:397,rr_text:197,rr_sms:297,rr_full:497,
};

const D_TYPE = {
  scan_base:'one',scan_guided:'one',vid_single:'one',vid_pack:'one',
  drone_half:'one',drone_full:'one',lp_base:'one',lp_conv:'one',
  lp_about:'one',lp_vt:'one',lp_vid:'one',lp_cal:'one',lp_social:'one',
  ao_page:'one',gbp_setup:'one',gbp_scale:'one',gbp_support:'one',
  meta_setup:'one',meta_scale:'one',meta_own:'one',rev_roadmap:'one',
  rev_referral:'one',rev_mailer:'one',rep_mkt:'mo',soc3:'mo',soc5:'mo',
  soc7:'mo',ad_mgmt:'mo',rr_recep:'mo',rr_text:'mo',rr_sms:'mo',rr_full:'mo',
};

const D_CAT = {
  scan_base:'capture',scan_guided:'capture',vid_single:'capture',vid_pack:'capture',
  drone_half:'capture',drone_full:'capture',lp_base:'web',lp_conv:'web',lp_about:'web',
  lp_vt:'web',lp_vid:'web',lp_cal:'web',lp_social:'web',ao_page:'web',
  gbp_setup:'rep',gbp_scale:'rep',gbp_support:'rep',meta_setup:'ads',
  meta_scale:'ads',meta_own:'ads',rev_roadmap:'rep',rev_referral:'rep',
  rev_mailer:'rep',rep_mkt:'rep',soc3:'social',soc5:'social',soc7:'social',
  ad_mgmt:'ads',rr_recep:'rapid',rr_text:'rapid',rr_sms:'rapid',rr_full:'rapid',
};

const CAT_LABEL = {
  capture:'Space Capture & Media',web:'Online Presence',
  rep:'Reputation & Reviews',social:'Social Content',
  ads:'Advertising & Meta',rapid:'Rapid Response',
};

const PKG_NAME  = { pkg_t2b:'Tour2Booking™', pkg_ao:'AlwaysOn Tour2Booking™', pkg_os:'AlwaysOn Digital Twin Conversion OS™' };
const PKG_PRICE = { pkg_t2b:5549, pkg_ao:6549, pkg_os:9549 };
const GF_NAME   = { gf1:'Starter Lock', gf2:'Growth Lock', gf3:'Dominate Lock' };
const GF_DISC   = { gf1:0.05, gf2:0.10, gf3:0.15 };

function fmt(n) { return '$' + n.toLocaleString('en-US'); }

function computeTotals(items, pkg, gf) {
  let oneTime = 0, monthly = 0;
  for (const id of items) {
    if (!D_PRICE[id]) continue;
    if (D_TYPE[id] === 'one') oneTime += D_PRICE[id];
    else                       monthly += D_PRICE[id];
  }
  if (pkg && PKG_PRICE[pkg]) oneTime += PKG_PRICE[pkg];
  const combined    = oneTime + monthly;
  const discRate    = gf ? GF_DISC[gf] || 0 : 0;
  const discount    = Math.round(combined * discRate);
  const downPayment = Math.round(oneTime * 0.25);
  return { oneTime, monthly, combined, discRate, discount, downPayment };
}

function getTierInfo(items, pkg) {
  const SOC_PACK  = ['soc3','soc5','soc7'];
  const WEB_ITEMS = ['lp_base','lp_conv','lp_about','ao_page','gbp_setup','gbp_scale'];
  const hasPkg    = !!pkg;
  const hasSoc    = SOC_PACK.some(id => items.includes(id));
  const hasWeb    = WEB_ITEMS.some(id => items.includes(id));
  let oneTime = 0, monthly = 0;
  for (const id of items) {
    if (!D_PRICE[id]) continue;
    if (D_TYPE[id] === 'one') oneTime += D_PRICE[id];
    else                       monthly += D_PRICE[id];
  }
  if (pkg && PKG_PRICE[pkg]) oneTime += PKG_PRICE[pkg];
  const combined   = oneTime + monthly;
  const isQual     = hasPkg || (hasSoc && hasWeb);
  const isPromo    = !isQual && combined >= 6000;
  if (isQual)  return { tier:'guarantee', label:'Guarantee Eligible',       color:'#5cb85c', bg:'#0d1f0d' };
  if (isPromo) return { tier:'promo',     label:'Speed to Prosperity — 15% Early Conviction Rate', color:'#c9a96e', bg:'#1a1505' };
  return           { tier:'foundation',  label:'Building Foundation',       color:'#5b9bd5', bg:'#0d1520' };
}

function buildLineItems(items, pkg) {
  const grouped = {};
  for (const id of items) {
    const cat = D_CAT[id] || 'other';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(id);
  }
  let html = '';
  if (pkg && PKG_NAME[pkg]) {
    html += `
      <tr class="cat-row"><td colspan="3">Core Package</td></tr>
      <tr>
        <td>${PKG_NAME[pkg]}</td>
        <td style="text-align:center">One-time</td>
        <td style="text-align:right">${fmt(PKG_PRICE[pkg])}</td>
      </tr>`;
  }
  for (const [cat, label] of Object.entries(CAT_LABEL)) {
    if (!grouped[cat]) continue;
    html += `<tr class="cat-row"><td colspan="3">${label}</td></tr>`;
    for (const id of grouped[cat]) {
      const nm = D_NAME[id] || id;
      const pr = D_PRICE[id] || 0;
      const tp = D_TYPE[id] === 'mo' ? '/mo' : 'One-time';
      html += `<tr>
        <td>${nm}</td>
        <td style="text-align:center">${tp}</td>
        <td style="text-align:right">${fmt(pr)}${D_TYPE[id]==='mo'?'/mo':''}</td>
      </tr>`;
    }
  }
  return html;
}

function qualScoreBar(qual) {
  const labels = ['Google Business','Meta Business Suite','Existing Media','Active Website','Working Contact','Clear Offering'];
  const total  = qual.reduce((a,b) => a+b, 0);
  return `
    <div style="margin:8px 0">
      <div style="font-size:11px;color:#9a9590;margin-bottom:6px">Qualification Score: <strong style="color:#c9a96e">${total}/6</strong></div>
      <div style="display:flex;gap:4px;flex-wrap:wrap">
        ${labels.map((l,i) => `
          <div style="font-size:9px;padding:3px 8px;border-radius:10px;border:1px solid ${qual[i]?'#5cb85c':'#262626'};background:${qual[i]?'rgba(92,184,92,.1)':'#141414'};color:${qual[i]?'#5cb85c':'#5e5955'}">${qual[i]?'✓':' '} ${l}</div>
        `).join('')}
      </div>
    </div>`;
}

function generateReport(data) {
  const {
    contact, items = [], pkg = null, gf = null, qual = [0,0,0,0,0,0],
  } = data;

  const totals   = computeTotals(items, pkg, gf);
  const tierInfo = getTierInfo(items, pkg);
  const now      = new Date();
  const dateStr  = now.toLocaleDateString('en-US', { year:'numeric', month:'long', day:'numeric' });
  const timeStr  = now.toLocaleTimeString('en-US', { hour:'2-digit', minute:'2-digit' });

  const fullName  = `${contact.firstName || ''} ${contact.lastName || ''}`.trim();
  const bizName   = contact.businessName || '—';
  const smsStatus = contact.smsOptIn ? 'Yes — opted in' : 'No';

  const tierNextSteps = {
    guarantee:  'Your submission qualifies for the <strong>RSD 21-Day Performance Guarantee</strong>. A brief pre-launch audit will confirm your foundation before activation. Expect a reply within 24 hours.',
    promo:      'Your engagement qualifies for the <strong>15% Early Conviction Rate</strong>. This rate is valid for 7 business days from the date of your official RSD offer and is extended once. Lock in your plan forward.',
    foundation: 'Our team will review your selections and schedule a <strong>Foundation Fit Call</strong> to align your priorities. We'll scope the right starting point and build from there.',
  };

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RSD Fit Report — ${fullName} — ${dateStr}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
  :root{--gold:#c9a96e;--dark:#0b0b0b;--s1:#141414;--br:#262626;--tx:#1a1a1a;--td:#555}
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:#fff;color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.6;padding:40px}
  @media print{body{padding:0} .no-print{display:none!important} @page{margin:18mm 16mm}}

  /* Header */
  .rpt-header{display:flex;justify-content:space-between;align-items:flex-start;padding-bottom:20px;border-bottom:3px solid var(--gold);margin-bottom:24px}
  .rpt-brand{font-family:'Libre Baskerville',serif;font-size:20px;font-weight:700;color:var(--dark)}
  .rpt-tag{font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin-top:2px}
  .rpt-meta{text-align:right;font-size:10px;color:var(--td)}
  .rpt-meta strong{color:var(--tx);display:block;font-size:11px;margin-bottom:2px}

  /* Section */
  .sect{margin-bottom:22px}
  .sect-title{font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:var(--gold);margin-bottom:10px;padding-bottom:5px;border-bottom:1px solid #e0d9ce}

  /* Contact grid */
  .ct-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px 20px}
  .ct-row{display:flex;flex-direction:column;padding:5px 0;border-bottom:1px solid #f0ece6}
  .ct-lbl{font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--td);margin-bottom:1px}
  .ct-val{font-size:12px;color:var(--tx)}

  /* Score */
  .score-box{background:#faf9f7;border:1px solid #e8e4dc;border-radius:6px;padding:12px}

  /* Line items table */
  table{width:100%;border-collapse:collapse;font-size:11px}
  th{background:#f5f3ef;font-size:9px;letter-spacing:.08em;text-transform:uppercase;padding:7px 10px;text-align:left;color:var(--td);border-bottom:1px solid #e0d9ce}
  td{padding:6px 10px;border-bottom:1px solid #f0ece6}
  tr:last-child td{border:none}
  tr.cat-row td{background:#fdf9f4;font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--gold);padding:6px 10px;font-weight:700}

  /* Totals */
  .totals-box{background:#faf9f7;border:1px solid #e8e4dc;border-radius:6px;padding:14px;margin-top:12px}
  .tot-row{display:flex;justify-content:space-between;padding:4px 0;font-size:12px;border-bottom:1px solid #f0ece6}
  .tot-row:last-child{border:none;padding-top:10px;margin-top:6px;border-top:2px solid var(--gold)}
  .tot-row.final .l{font-family:'Libre Baskerville',serif;font-size:14px;font-weight:700}
  .tot-row.final .v{font-family:'Libre Baskerville',serif;font-size:18px;font-weight:700;color:var(--gold)}

  /* Tier badge */
  .tier-box{border-radius:8px;padding:16px 20px;margin-top:16px;text-align:center}
  .tier-label{font-family:'Libre Baskerville',serif;font-size:16px;font-weight:700;margin-bottom:6px}
  .tier-next{font-size:11px;color:var(--td);line-height:1.7;max-width:560px;margin:0 auto}

  /* Next steps */
  .ns-box{background:#faf9f7;border-left:3px solid var(--gold);padding:14px 16px;border-radius:0 6px 6px 0;margin-top:12px;font-size:11px;color:var(--td);line-height:1.8}
  .ns-box strong{color:var(--tx);font-weight:400}

  /* Footer */
  .rpt-footer{margin-top:32px;padding-top:16px;border-top:1px solid #e8e4dc;display:flex;justify-content:space-between;font-size:9px;color:var(--td)}

  /* Print button */
  .print-btn{display:inline-flex;align-items:center;gap:6px;background:var(--gold);color:#0b0b0b;border:none;padding:10px 24px;border-radius:6px;font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;margin-bottom:24px}
</style>
</head>
<body>

<button class="print-btn no-print" onclick="window.print()">🖨 Print / Save PDF</button>

<!-- Header -->
<div class="rpt-header">
  <div>
    <div class="rpt-brand">Real Space Digital</div>
    <div class="rpt-tag">Service-Fit Qualification Report</div>
  </div>
  <div class="rpt-meta">
    <strong>Submitted ${dateStr}</strong>
    ${timeStr} · qualify.rsddirect.com
  </div>
</div>

<!-- Contact Info -->
<div class="sect">
  <div class="sect-title">Prospect Information</div>
  <div class="ct-grid">
    <div class="ct-row"><span class="ct-lbl">Full Name</span><span class="ct-val">${fullName}</span></div>
    <div class="ct-row"><span class="ct-lbl">Business Name</span><span class="ct-val">${bizName}</span></div>
    <div class="ct-row"><span class="ct-lbl">Email</span><span class="ct-val">${contact.email || '—'}</span></div>
    <div class="ct-row"><span class="ct-lbl">Phone</span><span class="ct-val">${contact.phone || '—'}</span></div>
    <div class="ct-row"><span class="ct-lbl">Mobile / Cell</span><span class="ct-val">${contact.mobile || '—'}</span></div>
    <div class="ct-row"><span class="ct-lbl">SMS Opt-In</span><span class="ct-val">${smsStatus}</span></div>
  </div>
</div>

<!-- Qualification Score -->
<div class="sect">
  <div class="sect-title">Qualification Assessment</div>
  <div class="score-box">${qualScoreBar(qual)}</div>
</div>

<!-- Selected Services -->
<div class="sect">
  <div class="sect-title">Selected Services & Package</div>
  ${(items.length || pkg) ? `
  <table>
    <thead><tr><th>Service</th><th style="text-align:center">Type</th><th style="text-align:right">Price</th></tr></thead>
    <tbody>${buildLineItems(items, pkg)}</tbody>
  </table>` : '<p style="color:var(--td);font-size:12px;font-style:italic">No services selected.</p>'}

  ${gf ? `<div style="margin-top:10px;font-size:11px;color:var(--td)">Founder Lock: <strong style="color:var(--tx)">${GF_NAME[gf]||gf}</strong> — ${Math.round((GF_DISC[gf]||0)*100)}% rate lock applied</div>` : ''}
</div>

<!-- Totals -->
<div class="sect">
  <div class="sect-title">Investment Summary</div>
  <div class="totals-box">
    <div class="tot-row"><span class="l">One-Time Setup</span><span class="v">${fmt(totals.oneTime)}</span></div>
    <div class="tot-row"><span class="l">Monthly Recurring</span><span class="v">${fmt(totals.monthly)}/mo</span></div>
    ${totals.discount > 0 ? `<div class="tot-row"><span class="l">Founder Lock Discount (${Math.round(totals.discRate*100)}%)</span><span class="v" style="color:#5cb85c">− ${fmt(totals.discount)}</span></div>` : ''}
    <div class="tot-row"><span class="l">25% Down Payment Due</span><span class="v">${fmt(totals.downPayment)}</span></div>
    <div class="tot-row final"><span class="l">Combined Investment</span><span class="v">${fmt(totals.combined - totals.discount)}</span></div>
  </div>
</div>

<!-- Tier Badge -->
<div class="sect">
  <div class="sect-title">Qualification Tier</div>
  <div class="tier-box" style="background:${tierInfo.bg};border:1px solid ${tierInfo.color}30">
    <div class="tier-label" style="color:${tierInfo.color}">${tierInfo.label}</div>
    <div class="tier-next">${tierNextSteps[tierInfo.tier]}</div>
  </div>
</div>

<!-- Next Steps -->
<div class="sect">
  <div class="sect-title">Next Steps</div>
  <div class="ns-box">
    <strong>1. Fit Call Scheduling</strong> — RSD will reach out within 24 hours to schedule your Launch Your Marketing / Fit Your Market call.<br>
    <strong>2. Pre-Launch Audit</strong> — A brief system audit confirms your foundation before activation or proposal delivery.<br>
    <strong>3. Proposal Delivery</strong> — Genie Vee™ will generate your formal RSD proposal based on this assessment.<br>
    <strong>4. ${tierInfo.tier === 'promo' ? 'Rate Lock Window' : 'Activation'}</strong> — ${tierInfo.tier === 'promo' ? 'Your 15% Early Conviction Rate is valid 7 business days from your official RSD offer date.' : 'System is built and launched within 21 days of signed agreement and initial payment.'}
  </div>
</div>

<!-- Footer -->
<div class="rpt-footer">
  <span>Real Space Digital × ZDJ Ventures LLC · communications@zdj-ventures.com</span>
  <span>Digitizing Reality, Elevating Sales. · rsddirect.com</span>
</div>

</body>
</html>`;
}

module.exports = { generateReport };
