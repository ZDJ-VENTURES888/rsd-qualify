// ─────────────────────────────────────────────────────────────
//  RSD Qualify — Local dev server
//  Run: node server.js
//  Production deploys via Vercel (vercel.json handles routing)
// ─────────────────────────────────────────────────────────────
require('dotenv').config();
const express = require('express');
const path    = require('path');
const submit  = require('./api/submit');

const app  = express();
const PORT = process.env.PORT || 3000;

app.use(express.json({ limit: '1mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// API routes
app.post('/api/submit', submit);

// Page routes — serve from public/pages/
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public/pages/rsd-funnel-page-01-hero.html'));
});
app.get('/pages/:page', (req, res) => {
  res.sendFile(path.join(__dirname, 'public/pages', req.params.page));
});

app.listen(PORT, () => {
  console.log(`\n  RSD Qualify running at http://localhost:${PORT}\n`);
});
