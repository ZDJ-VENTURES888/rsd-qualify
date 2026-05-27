// ============================================================
// RSD Funnel — Canonical Pricing Tables
// Single source of truth. All funnel pages import from here.
// Edit prices ONLY in this file. Pages auto-pick up changes.
// ============================================================

// Package prices (one-time, base before any tier discount)
window.PKG_PRICE = {
  pkg_t2b: 5549,   // Tour2Booking
  pkg_ao:  6549,   // AlwaysOn Tour2Booking
  pkg_os:  9549    // AlwaysOn Digital Twin Conversion OS
};

// A la carte item prices
window.D_PRICE = {
  // Page 03 - Capture
  scan_base: 1299, scan_guided: 1799, vid_single: 500, vid_pack: 1200,
  drone_half: 350, drone_full: 600,
  vid_authority: 1800, vid_testimonial: 1800,
  photo_half: 400, photo_full: 800,
  lp_prem: 3500, lp_extra_page: 450,
  photo_1_3: 350, photo_6_9: 850, photo_9_12: 1300,
  photo_vol20: 2200, photo_21_30: 1995,
  // Page 04 - Web Presence
  seas_spring: 1850, seas_summer: 1850, seas_harvest: 2150,
  seas_winter: 1650, seas_annual: 6800, seas_extra: 1450,
  lp_base: 1800, lp_conv: 2800, lp_about: 500,
  vt_250: 0,
  // Page 04/05 additions
  ao_page: 1499, ao_ai_base: 1995, ao_ai_voice: 2495, ao_ai_full: 2995,
  // Page 06 - Social
  soc1: 750, soc2: 1500, soc3: 2250,
  ad_mgmt: 1495, ad_local: 995, ad_meta: 1295,
  // Page 07 - Rapid Response
  rr_basic: 495, rr_full: 995, rr_premium: 1495,
  // Page 08 - Digital Twin Avatar (added per user request)
  dt_avatar: 9000
};

// Item billing type: 'one' (one-time) or 'mo' (monthly recurring)
window.D_TYPE = {
  // One-time items
  scan_base: 'one', scan_guided: 'one', vid_single: 'one', vid_pack: 'one',
  drone_half: 'one', drone_full: 'one',
  vid_authority: 'one', vid_testimonial: 'one',
  photo_half: 'one', photo_full: 'one',
  lp_prem: 'one', lp_extra_page: 'one',
  photo_1_3: 'one', photo_6_9: 'one', photo_9_12: 'one',
  photo_vol20: 'one', photo_21_30: 'one',
  seas_spring: 'one', seas_summer: 'one', seas_harvest: 'one',
  seas_winter: 'one', seas_annual: 'one', seas_extra: 'one',
  lp_base: 'one', lp_conv: 'one', lp_about: 'one',
  vt_250: 'one',
  // Monthly recurring
  ao_page: 'mo', ao_ai_base: 'mo', ao_ai_voice: 'mo', ao_ai_full: 'mo',
  soc1: 'mo', soc2: 'mo', soc3: 'mo',
  ad_mgmt: 'mo', ad_local: 'mo', ad_meta: 'mo',
  rr_basic: 'mo', rr_full: 'mo', rr_premium: 'mo',
  // One-time (Digital Twin Avatar)
  dt_avatar: 'one'
};

// Founder lock tier discount rates
window.GF_DISC = {
  gf1: 0.05,   // Starter Lock: 5% off
  gf2: 0.10,   // Growth Lock: 10% off + priority fee
  gf3: 0.15    // Dominate Lock: 15% off
};

// Growth Lock one-time priority access fee
window.PRIORITY_FEE = 497;

console.log('[RSD] Pricing loaded:', Object.keys(window.D_PRICE).length, 'items');
