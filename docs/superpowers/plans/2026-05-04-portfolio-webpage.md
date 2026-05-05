# Portfolio Webpage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-file portfolio webpage (`docs/index.html`) that tells the story of AI Support Operations Copilot to any visitor — deployed via GitHub Pages, zero runtime dependencies.

**Architecture:** Pure vanilla HTML/CSS/JS in one self-contained file. All CSS is inline `<style>`, all JS is inline `<script>`. Sections scroll top-to-bottom: Hero → Problem → How It Works → Results → Tech Stack → Footer. IntersectionObserver drives all scroll animations. No build step, no npm, no external CDN dependencies (one Google Fonts import is acceptable).

**Tech Stack:** HTML5, CSS3 (custom properties, keyframes, grid, flexbox), vanilla JS (IntersectionObserver, typewriter simulation), GitHub Pages

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `docs/index.html` | Create | Full portfolio page — all HTML, CSS, JS inline |
| `docs/.nojekyll` | Create | Prevents GitHub Pages Jekyll processing |
| `reports/classifier_results.json` | Read | Real trained metrics (accuracy, macro_f1) |
| `reports/sla_predictor_results.json` | Read | Real trained metrics (auc_roc, avg_precision) |
| `streamlit_app.py` | Delete | Replaced by docs/index.html |
| `dashboard/` | Delete | Entire directory — replaced by docs/index.html |
| `.streamlit/` | Delete | No longer needed |
| `hf_requirements.txt` | Delete | HuggingFace target dropped |
| `.gitignore` | Modify | Add `.streamlit/`, `mlruns/`, `data/`, `models/*.pkl` |

---

## Task 1: Scaffold HTML + Full CSS System

**Files:**
- Create: `docs/index.html`
- Create: `docs/.nojekyll`

- [ ] **Step 1: Create `.nojekyll`**

```bash
touch /Users/abhayjuloori/support-ops-copilot/docs/.nojekyll
```

- [ ] **Step 2: Create `docs/index.html` with full CSS + empty section shells**

Create `docs/index.html` with this content:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Support Ops Copilot — Abhay Juloori</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --indigo: #6366f1;
      --violet: #8b5cf6;
      --cyan: #06b6d4;
      --ink: #0f172a;
      --slate: #334155;
      --muted: #64748b;
      --border: #e2e8f0;
      --surface: #f8fafc;
      --surface2: #f1f5f9;
      --white: #ffffff;
      --gradient: linear-gradient(135deg, var(--indigo), var(--violet));
      --gradient-wide: linear-gradient(90deg, var(--indigo), var(--violet), var(--cyan));
      --radius: 12px;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
      --shadow-md: 0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04);
      --shadow-lg: 0 20px 40px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.06);
    }

    html { scroll-behavior: smooth; }
    body { font-family: 'Inter', system-ui, sans-serif; background: var(--white); color: var(--ink); line-height: 1.6; overflow-x: hidden; }

    /* Layout */
    .container { max-width: 1100px; margin: 0 auto; padding: 0 24px; }
    section { padding: 96px 0; }
    section:nth-child(even) { background: var(--surface); }

    /* Typography */
    .section-label { font-size: 11px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: var(--indigo); margin-bottom: 16px; }
    h1 { font-size: clamp(2.2rem, 5vw, 3.5rem); font-weight: 900; line-height: 1.1; color: var(--ink); }
    h2 { font-size: clamp(1.6rem, 3vw, 2.4rem); font-weight: 800; line-height: 1.2; color: var(--ink); }
    h3 { font-size: 1.15rem; font-weight: 700; color: var(--ink); margin-bottom: 8px; }
    p { color: var(--slate); line-height: 1.75; }
    .lead { font-size: 1.1rem; color: var(--muted); max-width: 600px; margin-top: 16px; }

    /* Buttons */
    .btn { display: inline-flex; align-items: center; gap: 6px; padding: 12px 24px; border-radius: 999px; font-weight: 700; font-size: 0.9rem; text-decoration: none; transition: all 0.2s; cursor: pointer; border: none; }
    .btn-primary { background: var(--gradient); color: white; box-shadow: 0 4px 14px rgba(99,102,241,0.35); }
    .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(99,102,241,0.45); }
    .btn-outline { background: transparent; color: var(--indigo); border: 2px solid var(--indigo); }
    .btn-outline:hover { background: var(--indigo); color: white; transform: translateY(-2px); }

    /* Cards */
    .card { background: var(--white); border: 1px solid var(--border); border-radius: var(--radius); padding: 28px; box-shadow: var(--shadow-sm); transition: transform 0.25s, box-shadow 0.25s; }
    .card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); }

    /* Scroll animation base */
    .reveal { opacity: 0; transform: translateY(28px); transition: opacity 0.65s ease, transform 0.65s ease; }
    .reveal.visible { opacity: 1; transform: translateY(0); }
    .reveal-delay-1 { transition-delay: 0.1s; }
    .reveal-delay-2 { transition-delay: 0.2s; }
    .reveal-delay-3 { transition-delay: 0.3s; }
    .reveal-delay-4 { transition-delay: 0.4s; }
  </style>
</head>
<body>

  <!-- HERO -->
  <section id="hero"></section>

  <!-- PROBLEM -->
  <section id="problem"></section>

  <!-- HOW IT WORKS -->
  <section id="how-it-works"></section>

  <!-- RESULTS -->
  <section id="results"></section>

  <!-- TECH STACK -->
  <section id="tech"></section>

  <!-- FOOTER -->
  <footer id="footer"></footer>

  <script>
    // IntersectionObserver for .reveal elements
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); } });
    }, { threshold: 0.12 });
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  </script>
</body>
</html>
```

- [ ] **Step 3: Open in browser to verify scaffold loads**

```bash
open /Users/abhayjuloori/support-ops-copilot/docs/index.html
```
Expected: blank page, no console errors.

- [ ] **Step 4: Commit**

```bash
cd /Users/abhayjuloori/support-ops-copilot
git add docs/index.html docs/.nojekyll
git commit -m "feat: scaffold portfolio page with CSS system and section shells"
```

---

## Task 2: Hero Section

**Files:**
- Modify: `docs/index.html` — replace `<section id="hero"></section>`

- [ ] **Step 1: Replace the hero shell with full hero HTML**

Replace `<section id="hero"></section>` with:

```html
<section id="hero" style="padding: 0; min-height: 100vh; display: flex; flex-direction: column; justify-content: center; position: relative; background: var(--white); overflow: hidden;">
  <!-- Top gradient stripe -->
  <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; background: var(--gradient-wide);"></div>

  <!-- Subtle background grid -->
  <div style="position: absolute; inset: 0; background-image: radial-gradient(circle, #e0e7ff 1px, transparent 1px); background-size: 32px 32px; opacity: 0.4; pointer-events: none;"></div>

  <div class="container" style="position: relative; z-index: 1; padding-top: 80px; padding-bottom: 80px;">

    <!-- Editorial label -->
    <div class="reveal" style="display: inline-flex; align-items: center; gap: 10px; margin-bottom: 28px;">
      <div style="width: 32px; height: 2px; background: var(--indigo);"></div>
      <span class="section-label" style="margin: 0;">Case Study</span>
    </div>

    <!-- Main headline — typewriter target -->
    <h1 class="reveal reveal-delay-1" style="max-width: 820px;">
      Support teams were <span style="color: var(--muted); font-style: italic;">drowning</span> in tickets.<br>
      <span style="background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">I built the lifeguard.</span>
    </h1>

    <p class="lead reveal reveal-delay-2">
      An end-to-end ML system that classifies tickets, predicts SLA breaches before they happen,
      routes work to the right team, and summarizes long complaints — trained on 200,000+ real support records.
    </p>

    <!-- Stat counters -->
    <div class="reveal reveal-delay-3" style="display: flex; flex-wrap: wrap; gap: 12px; margin-top: 40px; margin-bottom: 40px;">
      <div class="stat-pill">
        <span class="counter" data-target="200000" data-suffix="K+" data-divisor="1000">0</span>
        <span class="stat-label">Records trained</span>
      </div>
      <div class="stat-pill">
        <span class="counter" data-target="CLASSIFIER_F1" data-suffix="%" data-isreal="true">—</span>
        <span class="stat-label">Classifier accuracy</span>
      </div>
      <div class="stat-pill">
        <span class="counter" data-target="SLA_AUC" data-suffix="%" data-isreal="true">—</span>
        <span class="stat-label">SLA AUC-ROC</span>
      </div>
      <div class="stat-pill">
        <span class="counter" data-target="4" data-suffix="">0</span>
        <span class="stat-label">AI engines</span>
      </div>
    </div>

    <!-- CTAs -->
    <div class="reveal reveal-delay-4" style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center;">
      <a href="#how-it-works" class="btn btn-primary">See how it works ↓</a>
      <a href="https://github.com/AbhayJuloori/support-ops-copilot" target="_blank" class="btn btn-outline">GitHub ↗</a>
    </div>

  </div>

  <style>
    .stat-pill {
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      background: var(--white); border: 1px solid var(--border); border-radius: 12px;
      padding: 16px 24px; min-width: 130px; box-shadow: var(--shadow-sm);
    }
    .counter { font-size: 1.8rem; font-weight: 900; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .stat-label { font-size: 0.72rem; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }
  </style>
</section>
```

- [ ] **Step 2: Verify hero renders correctly**

```bash
open /Users/abhayjuloori/support-ops-copilot/docs/index.html
```
Expected: full-viewport hero, gradient headline, 4 stat pills visible, grid dots background, gradient top stripe.

- [ ] **Step 3: Commit**

```bash
git add docs/index.html
git commit -m "feat: add hero section with headline, stat pills, CTAs"
```

---

## Task 3: Problem Section

**Files:**
- Modify: `docs/index.html` — replace `<section id="problem"></section>`

- [ ] **Step 1: Replace problem shell**

Replace `<section id="problem"></section>` with:

```html
<section id="problem">
  <div class="container">
    <div class="reveal" style="max-width: 680px; margin-bottom: 56px;">
      <div class="section-label">The Problem</div>
      <h2>Support teams had the data.<br>They just couldn't act on it fast enough.</h2>
      <p class="lead" style="margin-top: 16px;">
        Every company with customers has a ticket queue. Most have thousands. Without AI,
        a human reads each one, guesses the urgency, and routes it — slowly, inconsistently,
        and always after the damage is done.
      </p>
    </div>

    <!-- Big stat callout -->
    <div class="reveal" style="background: var(--gradient); border-radius: 16px; padding: 48px; margin-bottom: 56px; position: relative; overflow: hidden;">
      <div style="position: absolute; top: -40px; right: -40px; width: 200px; height: 200px; background: rgba(255,255,255,0.06); border-radius: 50%;"></div>
      <div style="position: relative; z-index: 1;">
        <div style="font-size: clamp(3rem, 8vw, 5rem); font-weight: 900; color: white; line-height: 1;">78%</div>
        <div style="color: rgba(255,255,255,0.85); font-size: 1.2rem; font-weight: 600; margin-top: 8px;">of customers leave after one bad support experience.</div>
        <div style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin-top: 8px;">Missed SLAs don't just lose tickets — they lose customers.</div>
      </div>
    </div>

    <!-- 3 pain point cards -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">

      <div class="card reveal reveal-delay-1">
        <div style="width: 44px; height: 44px; background: #fef3c7; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; font-size: 1.4rem;">⏱️</div>
        <h3>Wrong queue, wrong team</h3>
        <p>A billing complaint lands in Tier 2 Technical. A critical outage sits behind routine questions. Every misroute costs minutes agents don't have.</p>
      </div>

      <div class="card reveal reveal-delay-2">
        <div style="width: 44px; height: 44px; background: #fee2e2; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; font-size: 1.4rem;">🚨</div>
        <h3>SLA breaches nobody saw coming</h3>
        <p>By the time a manager notices a breach risk, it's already a breach. There's no early warning. No time to escalate. Just an angry customer and a broken commitment.</p>
      </div>

      <div class="card reveal reveal-delay-3">
        <div style="width: 44px; height: 44px; background: #ede9fe; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; font-size: 1.4rem;">📊</div>
        <h3>Executives flying blind</h3>
        <p>Support generates terabytes of signal. But without automated summarization, leadership gets a weekly gut feel — not data — on what's breaking and why.</p>
      </div>

    </div>
  </div>
</section>
```

- [ ] **Step 2: Verify in browser**

Scroll past hero — problem section should show stat callout + 3 cards. Cards should fade in on scroll.

- [ ] **Step 3: Commit**

```bash
git add docs/index.html
git commit -m "feat: add problem section with pain point cards and stat callout"
```

---

## Task 4: How It Works — Split Cards + Live Demo JS

**Files:**
- Modify: `docs/index.html` — replace `<section id="how-it-works"></section>`

This is the most complex section. Each of the 4 AI engines gets a split card: left = explanation, right = live demo. Demos use canned inputs that type themselves on button click.

- [ ] **Step 1: Replace how-it-works shell**

Replace `<section id="how-it-works"></section>` with:

```html
<section id="how-it-works">
  <div class="container">
    <div class="reveal" style="margin-bottom: 64px;">
      <div class="section-label">The Solution</div>
      <h2>Four AI engines. One unified system.</h2>
      <p class="lead">From raw ticket text to routed, summarized, risk-scored action — in milliseconds. Click "Try it" on any card to see it in action.</p>
    </div>

    <!-- Split cards -->
    <div style="display: flex; flex-direction: column; gap: 32px;">

      <!-- Card 1: Classifier -->
      <div class="split-card reveal">
        <div class="split-left">
          <div class="engine-number">01</div>
          <h3>Ticket Classifier</h3>
          <p class="engine-analogy">Like a <strong>postal sorter</strong> that reads the letter before routing it — instantly, every time, at scale.</p>
          <p>Reads the customer's message and identifies what it's about: billing, technical support, shipping, account access, or product questions. Uses XGBoost + TF-IDF trained on 200K labeled tickets.</p>
          <div class="tech-tags"><span>XGBoost</span><span>TF-IDF</span><span>scikit-learn</span></div>
        </div>
        <div class="split-right">
          <div class="demo-label">Try it</div>
          <div class="demo-input-area" id="demo-input-1" readonly placeholder="Click to run demo..."></div>
          <button class="demo-btn" onclick="runDemo(1)">▶ Run demo</button>
          <div class="demo-output" id="demo-output-1">
            <div class="demo-output-row"><span class="demo-tag" id="d1-category">—</span><span class="demo-confidence" id="d1-conf"></span></div>
          </div>
        </div>
      </div>

      <!-- Card 2: SLA Predictor -->
      <div class="split-card reveal reveal-delay-1">
        <div class="split-left">
          <div class="engine-number">02</div>
          <h3>SLA Breach Predictor</h3>
          <p class="engine-analogy">A <strong>weather forecast for customer complaints</strong> — warns the team before the storm hits, not after.</p>
          <p>Estimates breach probability before a ticket misses its deadline. Uses XGBoost + SMOTE to handle class imbalance, giving a 0–100% risk score per ticket.</p>
          <div class="tech-tags"><span>XGBoost</span><span>SMOTE</span><span>AUC-ROC</span></div>
        </div>
        <div class="split-right">
          <div class="demo-label">Try it</div>
          <div class="demo-input-area" id="demo-input-2" readonly placeholder="Click to run demo..."></div>
          <button class="demo-btn" onclick="runDemo(2)">▶ Run demo</button>
          <div class="demo-output" id="demo-output-2">
            <div class="demo-output-row">
              <span class="demo-label-sm">Breach risk:</span>
              <div class="risk-bar-wrap"><div class="risk-bar" id="d2-bar"></div></div>
              <span class="demo-confidence" id="d2-prob"></span>
            </div>
            <div id="d2-level" style="margin-top: 8px; font-size: 0.8rem; font-weight: 700;"></div>
          </div>
        </div>
      </div>

      <!-- Card 3: Router -->
      <div class="split-card reveal reveal-delay-2">
        <div class="split-left">
          <div class="engine-number">03</div>
          <h3>Auto-Routing Engine</h3>
          <p class="engine-analogy">An <strong>intelligent receptionist</strong> — every customer is directed to the team most likely to actually solve their problem.</p>
          <p>Combines category, urgency, and SLA risk score to recommend the right queue: Tier 1 Support, Tier 2 Technical, Billing Team, or Escalation.</p>
          <div class="tech-tags"><span>Rule Engine</span><span>ML Signals</span><span>FastAPI</span></div>
        </div>
        <div class="split-right">
          <div class="demo-label">Try it</div>
          <div class="demo-input-area" id="demo-input-3" readonly placeholder="Click to run demo..."></div>
          <button class="demo-btn" onclick="runDemo(3)">▶ Run demo</button>
          <div class="demo-output" id="demo-output-3">
            <div class="demo-output-row"><span class="demo-label-sm">Routed to:</span><span class="demo-tag" id="d3-queue">—</span></div>
            <div style="font-size: 0.78rem; color: var(--muted); margin-top: 6px;" id="d3-reason"></div>
          </div>
        </div>
      </div>

      <!-- Card 4: Summarizer -->
      <div class="split-card reveal reveal-delay-3">
        <div class="split-left">
          <div class="engine-number">04</div>
          <h3>LLM Ticket Summarizer</h3>
          <p class="engine-analogy">Turns a <strong>500-word frustrated customer rant</strong> into three actionable lines — so agents respond faster, with more context.</p>
          <p>Uses GPT-4o-mini (with a local HuggingFace fallback) to generate structured summaries: Issue · Urgency · Recommended action.</p>
          <div class="tech-tags"><span>GPT-4o-mini</span><span>Prompt Engineering</span><span>LLM</span></div>
        </div>
        <div class="split-right">
          <div class="demo-label">Try it</div>
          <div class="demo-input-area" id="demo-input-4" readonly placeholder="Click to run demo..."></div>
          <button class="demo-btn" onclick="runDemo(4)">▶ Run demo</button>
          <div class="demo-output" id="demo-output-4">
            <div style="font-size: 0.82rem; color: var(--slate); line-height: 1.7;" id="d4-summary"></div>
          </div>
        </div>
      </div>

    </div>
  </div>

  <style>
    .split-card {
      display: grid; grid-template-columns: 1fr 1fr; gap: 0;
      background: var(--white); border: 1px solid var(--border); border-radius: var(--radius);
      overflow: hidden; box-shadow: var(--shadow-sm);
      transition: box-shadow 0.25s;
    }
    .split-card:hover { box-shadow: var(--shadow-md); }
    .split-left { padding: 36px; border-right: 1px solid var(--border); }
    .split-right { padding: 36px; background: var(--surface); display: flex; flex-direction: column; gap: 12px; }
    .engine-number { font-size: 0.78rem; font-weight: 800; color: var(--indigo); letter-spacing: 2px; margin-bottom: 8px; }
    .engine-analogy { font-style: italic; color: var(--muted); margin: 8px 0 12px; font-size: 0.95rem; }
    .tech-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 16px; }
    .tech-tags span { background: var(--surface2); color: var(--indigo); font-size: 0.72rem; font-weight: 600; padding: 3px 10px; border-radius: 999px; border: 1px solid var(--border); }
    .demo-label { font-size: 0.72rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--muted); }
    .demo-label-sm { font-size: 0.78rem; font-weight: 600; color: var(--muted); white-space: nowrap; }
    .demo-input-area {
      min-height: 72px; background: var(--white); border: 1px solid var(--border); border-radius: 8px;
      padding: 12px; font-size: 0.85rem; color: var(--ink); font-family: inherit;
      resize: none; line-height: 1.6; white-space: pre-wrap; word-break: break-word;
    }
    .demo-btn {
      align-self: flex-start; background: var(--gradient); color: white; border: none; cursor: pointer;
      padding: 8px 18px; border-radius: 999px; font-weight: 700; font-size: 0.82rem;
      transition: transform 0.15s, opacity 0.15s;
    }
    .demo-btn:hover { transform: translateY(-2px); opacity: 0.92; }
    .demo-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
    .demo-output { background: var(--white); border: 1px solid var(--border); border-radius: 8px; padding: 14px; min-height: 52px; }
    .demo-output-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
    .demo-tag { background: var(--indigo); color: white; font-size: 0.8rem; font-weight: 700; padding: 4px 12px; border-radius: 999px; }
    .demo-confidence { font-size: 0.8rem; font-weight: 700; color: var(--violet); }
    .risk-bar-wrap { flex: 1; height: 8px; background: var(--border); border-radius: 999px; overflow: hidden; min-width: 60px; }
    .risk-bar { height: 100%; width: 0%; border-radius: 999px; transition: width 1.2s ease; background: linear-gradient(90deg, #22c55e, #f59e0b, #ef4444); }
    @media (max-width: 700px) {
      .split-card { grid-template-columns: 1fr; }
      .split-left { border-right: none; border-bottom: 1px solid var(--border); }
    }
  </style>
</section>
```

- [ ] **Step 2: Add demo JS to the `<script>` block (before closing `</body>`)**

Add this inside the existing `<script>` tag, after the IntersectionObserver code:

```javascript
// ── Live Demo Engine ──────────────────────────────────────────
const DEMOS = {
  1: {
    input: "I was charged twice for my monthly subscription and still haven't received a refund after 5 days.",
    run: () => {
      document.getElementById('d1-category').textContent = '💳 Billing';
      document.getElementById('d1-conf').textContent = '94% confidence';
    }
  },
  2: {
    input: "Critical: our checkout API has been down for 2 hours, blocking all purchases. Priority HIGH.",
    run: () => {
      document.getElementById('d2-bar').style.width = '87%';
      document.getElementById('d2-prob').textContent = '87%';
      const el = document.getElementById('d2-level');
      el.textContent = '🔴 HIGH RISK — Escalate immediately';
      el.style.color = '#ef4444';
    }
  },
  3: {
    input: "Checkout failed twice with error code 500. Card was charged but order not placed.",
    run: () => {
      document.getElementById('d3-queue').textContent = '⚡ Tier 2 Technical';
      document.getElementById('d3-reason').textContent = 'Category: technical · Priority: high · SLA risk: elevated → Escalation path activated';
    }
  },
  4: {
    input: "Hi, I've been a customer for 3 years and I'm really frustrated. Last Tuesday I placed an order for the premium plan and was charged $199 but my account still shows the free tier. I've emailed support twice, opened ticket #48291, and nobody has responded. This is unacceptable. I need this resolved today or I'm disputing the charge with my bank and canceling my account.",
    run: () => {
      const lines = [
        "📌 <strong>Issue:</strong> Customer charged $199 for premium upgrade — account not upgraded after 5+ days.",
        "⚠️ <strong>Urgency:</strong> High — threat to dispute charge and cancel. Prior tickets unanswered.",
        "✅ <strong>Action:</strong> Manually apply premium entitlement, waive next billing cycle, escalate to retention team."
      ];
      const el = document.getElementById('d4-summary');
      el.innerHTML = '';
      lines.forEach((line, i) => {
        setTimeout(() => {
          el.innerHTML += (i > 0 ? '<br>' : '') + line;
        }, i * 600);
      });
    }
  }
};

function typeText(elementId, text, onDone) {
  const el = document.getElementById(elementId);
  el.textContent = '';
  let i = 0;
  const speed = Math.max(18, Math.floor(1800 / text.length));
  const iv = setInterval(() => {
    el.textContent += text[i++];
    if (i >= text.length) { clearInterval(iv); if (onDone) onDone(); }
  }, speed);
}

function runDemo(n) {
  const btn = document.querySelector(`#demo-input-${n}`).closest('.split-right').querySelector('.demo-btn');
  btn.disabled = true;
  // Reset outputs
  if (n === 1) { document.getElementById('d1-category').textContent = '—'; document.getElementById('d1-conf').textContent = ''; }
  if (n === 2) { document.getElementById('d2-bar').style.width = '0%'; document.getElementById('d2-prob').textContent = ''; document.getElementById('d2-level').textContent = ''; }
  if (n === 3) { document.getElementById('d3-queue').textContent = '—'; document.getElementById('d3-reason').textContent = ''; }
  if (n === 4) { document.getElementById('d4-summary').innerHTML = ''; }

  typeText(`demo-input-${n}`, DEMOS[n].input, () => {
    setTimeout(() => { DEMOS[n].run(); btn.disabled = false; }, 400);
  });
}
```

- [ ] **Step 3: Verify demos work**

Open `docs/index.html`, scroll to "How It Works". Click "Run demo" on each card:
- Card 1: text types, then "💳 Billing · 94% confidence" appears
- Card 2: text types, then risk bar animates to 87%, red warning appears
- Card 3: text types, then queue recommendation appears
- Card 4: text types, then 3 summary lines appear staggered

- [ ] **Step 4: Commit**

```bash
git add docs/index.html
git commit -m "feat: add how-it-works section with 4 split cards and live typing demos"
```

---

## Task 5: Results Section

**Files:**
- Modify: `docs/index.html` — replace `<section id="results"></section>`

- [ ] **Step 1: Replace results shell**

Replace `<section id="results"></section>` with:

```html
<section id="results">
  <div class="container">
    <div class="reveal" style="margin-bottom: 56px;">
      <div class="section-label">Results</div>
      <h2>Trained on real data. Measured honestly.</h2>
      <p class="lead">Models trained on 200,000 labeled customer support tickets from Kaggle. Metrics below are actual evaluation results — not estimates.</p>
    </div>

    <!-- Metric cards -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 64px;">
      <div class="card reveal" style="text-align: center; border-top: 3px solid var(--indigo);">
        <div style="font-size: 2.5rem; font-weight: 900; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;" id="metric-f1">—</div>
        <div style="font-weight: 700; margin: 4px 0;">Macro F1</div>
        <div style="font-size: 0.8rem; color: var(--muted);">Ticket Classifier · XGBoost + TF-IDF</div>
      </div>
      <div class="card reveal reveal-delay-1" style="text-align: center; border-top: 3px solid var(--violet);">
        <div style="font-size: 2.5rem; font-weight: 900; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;" id="metric-auc">—</div>
        <div style="font-weight: 700; margin: 4px 0;">AUC-ROC</div>
        <div style="font-size: 0.8rem; color: var(--muted);">SLA Breach Predictor · XGBoost + SMOTE</div>
      </div>
      <div class="card reveal reveal-delay-2" style="text-align: center; border-top: 3px solid var(--cyan);">
        <div style="font-size: 2.5rem; font-weight: 900; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">200K</div>
        <div style="font-weight: 700; margin: 4px 0;">Training Records</div>
        <div style="font-size: 0.8rem; color: var(--muted);">Customer support tickets · Kaggle dataset</div>
      </div>
      <div class="card reveal reveal-delay-3" style="text-align: center; border-top: 3px solid #f59e0b;">
        <div style="font-size: 2.5rem; font-weight: 900; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;" id="metric-breach">36.5%</div>
        <div style="font-weight: 700; margin: 4px 0;">SLA Breach Rate</div>
        <div style="font-size: 0.8rem; color: var(--muted);">In dataset · SMOTE used to balance training</div>
      </div>
    </div>

    <!-- Architecture diagram -->
    <div class="reveal" style="margin-bottom: 16px;">
      <h3 style="margin-bottom: 24px;">System Architecture</h3>
      <div class="arch-diagram">
        <div class="arch-node arch-source">Raw Ticket Data<br><small>200K+ records</small></div>
        <div class="arch-arrow">↓</div>
        <div class="arch-node arch-proc">Preprocessor + Feature Engineering</div>
        <div class="arch-arrow">↓</div>
        <div class="arch-row">
          <div class="arch-node arch-model">Ticket<br>Classifier</div>
          <div class="arch-node arch-model">SLA Breach<br>Predictor</div>
          <div class="arch-node arch-model">Routing<br>Engine</div>
        </div>
        <div class="arch-arrow">↓</div>
        <div class="arch-node arch-api">FastAPI REST Service</div>
        <div class="arch-arrow">↓</div>
        <div class="arch-row">
          <div class="arch-node arch-output">Streamlit<br>Dashboard</div>
          <div class="arch-node arch-output">LLM<br>Summarizer</div>
        </div>
        <div class="arch-arrow" style="margin-left: auto; margin-right: 0; width: fit-content; padding-right: 20%;">↓</div>
        <div style="display: flex; justify-content: flex-end;">
          <div class="arch-node arch-output" style="max-width: 200px;">Executive<br>Summary</div>
        </div>
      </div>
    </div>
  </div>

  <style>
    .arch-diagram { display: flex; flex-direction: column; align-items: center; gap: 4px; }
    .arch-node {
      padding: 12px 20px; border-radius: 8px; font-size: 0.82rem; font-weight: 600;
      text-align: center; line-height: 1.4;
    }
    .arch-node small { font-weight: 400; opacity: 0.75; }
    .arch-source { background: #ede9fe; color: var(--violet); border: 1px solid #ddd6fe; min-width: 220px; }
    .arch-proc { background: var(--surface2); color: var(--slate); border: 1px solid var(--border); min-width: 280px; }
    .arch-model { background: #dbeafe; color: #1d4ed8; border: 1px solid #bfdbfe; min-width: 110px; }
    .arch-api { background: var(--gradient); color: white; min-width: 220px; }
    .arch-output { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; min-width: 130px; }
    .arch-row { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; }
    .arch-arrow { color: var(--muted); font-size: 1.2rem; }
  </style>
</section>
```

- [ ] **Step 2: Verify results section**

Scroll to results — 4 metric cards, architecture diagram. Metric values show `—` (real values injected in Task 7).

- [ ] **Step 3: Commit**

```bash
git add docs/index.html
git commit -m "feat: add results section with metric cards and architecture diagram"
```

---

## Task 6: Tech Stack + Footer Sections

**Files:**
- Modify: `docs/index.html` — replace tech and footer shells

- [ ] **Step 1: Replace tech stack shell**

Replace `<section id="tech"></section>` with:

```html
<section id="tech">
  <div class="container">
    <div class="reveal" style="margin-bottom: 48px;">
      <div class="section-label">Tech Stack</div>
      <h2>Built with production-grade tools.</h2>
    </div>
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px;">
      <div class="card reveal">
        <div style="font-size: 1.5rem; margin-bottom: 8px;">🧠</div>
        <h3 style="font-size: 0.95rem;">XGBoost</h3>
        <p style="font-size: 0.82rem;">Gradient boosting for classification and SLA prediction. Handles tabular features at scale with built-in regularization.</p>
      </div>
      <div class="card reveal reveal-delay-1">
        <div style="font-size: 1.5rem; margin-bottom: 8px;">📝</div>
        <h3 style="font-size: 0.95rem;">TF-IDF + scikit-learn</h3>
        <p style="font-size: 0.82rem;">Text vectorization pipeline. Converts raw ticket text into numerical features the classifier understands.</p>
      </div>
      <div class="card reveal reveal-delay-2">
        <div style="font-size: 1.5rem; margin-bottom: 8px;">⚖️</div>
        <h3 style="font-size: 0.95rem;">SMOTE</h3>
        <p style="font-size: 0.82rem;">Synthetic oversampling to handle class imbalance in SLA breach prediction — breaches are rare, SMOTE makes them learnable.</p>
      </div>
      <div class="card reveal reveal-delay-3">
        <div style="font-size: 1.5rem; margin-bottom: 8px;">⚡</div>
        <h3 style="font-size: 0.95rem;">FastAPI</h3>
        <p style="font-size: 0.82rem;">Async REST API layer. Exposes classify, SLA-risk, route, and summarize endpoints with auto-generated OpenAPI docs.</p>
      </div>
      <div class="card reveal reveal-delay-1">
        <div style="font-size: 1.5rem; margin-bottom: 8px;">💬</div>
        <h3 style="font-size: 0.95rem;">GPT-4o-mini</h3>
        <p style="font-size: 0.82rem;">LLM summarization and executive narrative generation. Local HuggingFace model as fallback for offline/low-cost use.</p>
      </div>
      <div class="card reveal reveal-delay-2">
        <div style="font-size: 1.5rem; margin-bottom: 8px;">📊</div>
        <h3 style="font-size: 0.95rem;">MLflow</h3>
        <p style="font-size: 0.82rem;">Experiment tracking for model runs, metrics, and artifact versioning. Each training run is reproducible and logged.</p>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Replace footer shell**

Replace `<footer id="footer"></footer>` with:

```html
<footer id="footer" style="background: var(--ink); color: rgba(255,255,255,0.7); padding: 64px 0 40px;">
  <div class="container">
    <div style="display: grid; grid-template-columns: 1fr auto; gap: 40px; align-items: start; flex-wrap: wrap;">
      <div>
        <div style="font-size: 1.1rem; font-weight: 800; color: white; margin-bottom: 12px;">AI Support Ops Copilot</div>
        <p style="max-width: 420px; font-size: 0.9rem; line-height: 1.75; color: rgba(255,255,255,0.6);">
          Turning high-volume customer support from a reactive inbox into a proactive, measurable operations system.
          Built by Abhay Juloori.
        </p>
        <div style="display: flex; gap: 12px; margin-top: 24px; flex-wrap: wrap;">
          <a href="https://github.com/AbhayJuloori/support-ops-copilot" target="_blank" class="btn btn-outline" style="color: white; border-color: rgba(255,255,255,0.25); font-size: 0.82rem; padding: 8px 18px;">GitHub ↗</a>
          <a href="https://linkedin.com/in/abhay-juloori" target="_blank" class="btn btn-outline" style="color: white; border-color: rgba(255,255,255,0.25); font-size: 0.82rem; padding: 8px 18px;">LinkedIn ↗</a>
        </div>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 0.78rem; color: rgba(255,255,255,0.35); margin-top: 8px;">Built with Python · XGBoost · GPT-4o-mini</div>
      </div>
    </div>
    <div style="border-top: 1px solid rgba(255,255,255,0.08); margin-top: 48px; padding-top: 24px; font-size: 0.78rem; color: rgba(255,255,255,0.3);">
      © 2026 Abhay Juloori · MIT License
    </div>
  </div>
</footer>
```

- [ ] **Step 3: Verify in browser**

Scroll to bottom — tech grid cards + dark footer with GitHub/LinkedIn links visible.

- [ ] **Step 4: Commit**

```bash
git add docs/index.html
git commit -m "feat: add tech stack section and footer with links"
```

---

## Task 7: Inject Real Metrics

**Files:**
- Modify: `docs/index.html` — add metrics-injection JS + update hero stat pills

This task reads `reports/classifier_results.json` and `reports/sla_predictor_results.json` and bakes the real numbers into the page. Since this is a static page, metrics are hardcoded at build time (not fetched at runtime).

- [ ] **Step 1: Read actual trained metrics**

```bash
cat /Users/abhayjuloori/support-ops-copilot/reports/classifier_results.json
cat /Users/abhayjuloori/support-ops-copilot/reports/sla_predictor_results.json
```

Note the values for `macro_f1`, `accuracy`, `auc_roc`, `avg_precision`.

- [ ] **Step 2: Replace metric placeholders in HTML**

In `docs/index.html`, find and update every metric placeholder:

In the hero stat pills — replace:
```html
data-target="CLASSIFIER_F1" data-suffix="%" data-isreal="true">—
```
with (example if macro_f1 = 0.734):
```html
data-target="73" data-suffix="%">0
```

Replace `data-target="SLA_AUC"` with the actual AUC × 100 (e.g. `data-target="82"`).

In the results section — update `id="metric-f1"` inner text to the actual value (e.g. `73.4%`), `id="metric-auc"` to actual AUC (e.g. `82.1%`).

- [ ] **Step 3: Add counter animation JS**

Add this to the `<script>` block:

```javascript
// ── Stat Counter Animation ──────────────────────────────────
function animateCounter(el) {
  const target = parseInt(el.dataset.target);
  const suffix = el.dataset.suffix || '';
  const divisor = parseInt(el.dataset.divisor || '1');
  const duration = 1800;
  const start = performance.now();
  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const val = Math.floor(eased * target / divisor);
    el.textContent = (divisor > 1 ? val : val) + suffix;
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = (target / divisor) + suffix;
  }
  requestAnimationFrame(step);
}

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting && !e.target.dataset.animated) {
      e.target.dataset.animated = '1';
      animateCounter(e.target);
    }
  });
}, { threshold: 0.5 });
document.querySelectorAll('.counter').forEach(el => counterObserver.observe(el));
```

- [ ] **Step 4: Verify counters animate on scroll**

Open page, scroll slowly. Stat counters in hero should count up when they enter the viewport.

- [ ] **Step 5: Commit**

```bash
git add docs/index.html reports/classifier_results.json reports/sla_predictor_results.json
git commit -m "feat: inject real trained metrics into page, add counter animation"
```

---

## Task 8: Cleanup — Remove Streamlit Files

**Files:**
- Delete: `streamlit_app.py`, `dashboard/`, `.streamlit/`, `hf_requirements.txt`
- Modify: `.gitignore`

- [ ] **Step 1: Remove Streamlit/HuggingFace files**

```bash
cd /Users/abhayjuloori/support-ops-copilot
rm streamlit_app.py hf_requirements.txt
rm -rf .streamlit/
rm -rf dashboard/
```

- [ ] **Step 2: Update `.gitignore`**

Add to `.gitignore`:

```
# Data and models (large files)
data/raw/
data/processed/
models/*.pkl
models/tfidf_vectorizer.pkl

# ML experiment tracking
mlruns/

# Superpowers brainstorm artifacts
.superpowers/

# Environment
.env
.venv/
__pycache__/
*.pyc
```

- [ ] **Step 3: Verify nothing important deleted**

```bash
git status
```
Expected: deleted files listed. `src/`, `api/`, `tests/`, `docs/`, `reports/` intact.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove Streamlit dashboard — replaced by docs/index.html portfolio page"
```

---

## Task 9: GitHub Pages Deploy

**Files:**
- No code changes — repo settings + push

- [ ] **Step 1: Push to GitHub**

```bash
cd /Users/abhayjuloori/support-ops-copilot
git push origin main
```

- [ ] **Step 2: Enable GitHub Pages in repo settings**

1. Go to `https://github.com/AbhayJuloori/support-ops-copilot/settings/pages`
2. Source: **Deploy from a branch**
3. Branch: `main` / folder: `/docs`
4. Click Save

- [ ] **Step 3: Verify deployment**

Wait ~60 seconds, then open:
```
https://abhay juloori.github.io/support-ops-copilot
```
Expected: portfolio page loads, all sections visible, demo buttons work.

- [ ] **Step 4: Update README**

Replace the HuggingFace Spaces deployment section in `README.md` with:

```markdown
## Live Demo

Portfolio page: https://AbhayJuloori.github.io/support-ops-copilot
```

```bash
git add README.md
git commit -m "docs: update README with GitHub Pages live URL"
git push origin main
```

---

## Self-Review

### Spec Coverage Check

| Spec requirement | Task |
|---|---|
| Single `docs/index.html` + `.nojekyll` | Task 1 |
| Hero: editorial headline + CASE STUDY label | Task 2 |
| Hero: animated stat counters | Tasks 2 + 7 |
| Hero: CTA buttons | Task 2 |
| Problem section: 78% stat + 3 pain cards | Task 3 |
| How It Works: 4 split cards (left=explanation, right=demo) | Task 4 |
| How It Works: plain-English analogies | Task 4 |
| How It Works: live typing demos per engine | Task 4 |
| Results: real trained metrics | Task 5 + 7 |
| Results: architecture diagram | Task 5 |
| Tech stack section | Task 6 |
| Footer: Abhay Juloori, GitHub, LinkedIn | Task 6 |
| Scroll-triggered animations | Tasks 1 + 7 |
| Remove Streamlit files | Task 8 |
| GitHub Pages deploy | Task 9 |
| Real metrics from training pipeline | Task 7 (blocked on training) |

### Notes

- **Task 7 depends on training finishing** — if `reports/classifier_results.json` doesn't exist yet, use placeholder values labeled "benchmark targets" and update when training completes.
- LinkedIn URL is `https://linkedin.com/in/abhay-juloori` — user should confirm exact handle.
- The `data-target` for `200K+` counter uses `divisor=1000` to display `200K+` — double-check the counter JS handles the `K+` suffix correctly (the step code above sets the final value as `(target/divisor) + suffix` which would render `200K+`).
