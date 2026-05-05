# Portfolio Webpage Design — AI Support Operations Copilot

**Date:** 2026-05-04  
**Status:** Approved  

---

## Overview

Replace the existing Streamlit dashboard with a standalone portfolio webpage that tells the story of the AI Support Operations Copilot to any visitor — from a complete noob to a technical recruiter. Hosted via GitHub Pages (`docs/index.html`). Zero runtime dependencies, no Python needed.

---

## Visual Direction

- **Style:** Clean & Modern with editorial storytelling touches
- **Base palette:** White/light gray (`#f8fafc`, `#f1f5f9`), indigo/violet accents (`#6366f1`, `#8b5cf6`), cyan pop (`#06b6d4`)
- **Typography:** System font stack, heavy weights for headlines, generous whitespace
- **Animations:** Scroll-triggered fade-ins, number counters on viewport entry, typewriter hero text, card hover lifts, live typing demo in How It Works
- **Layout:** Single long scroll page — no nav required. Story unfolds top to bottom.

---

## Page Sections (top to bottom)

### 1. Hero
- **Editorial label:** `CASE STUDY` in small caps, indigo
- **Headline (2 lines):** "Support teams were drowning in tickets." / "I built the lifeguard."
- **Subtext:** "End-to-end ML system — classify, predict SLA, route, summarize. 200,000+ records."
- **Animated stat bar** below headline (scroll-triggered counters): `200K+ Records`, `[real macro F1]% Classifier`, `[real AUC-ROC]% SLA AUC`, `4 AI Engines`
- **CTAs:** "See the story ↓" (smooth scroll) + "GitHub" link
- **Top border stripe:** thin 3px gradient (indigo → violet → cyan)

### 2. The Problem
- **Section label:** `THE PROBLEM` in small caps
- **Hook stat:** Large number callout (e.g. "78% of customers leave after one bad support experience")
- **3 pain point cards:** Tickets misrouted → wrong queue delays. SLA breaches → churn and penalties. No visibility → managers flying blind.
- Tone: visceral, sets up urgency. Written for a noob — no jargon.

### 3. How It Works
- **Section label:** `THE SOLUTION`
- **4 split-cards** (C-style from brainstorm): left = plain-English explanation + analogy, right = live interactive demo
  1. **Ticket Classifier** — "What is this ticket about?" Analogy: *a postal sorter that reads the letter before routing it.* Demo: visitor types ticket text → sees category + confidence score appear in real time
  2. **SLA Breach Predictor** — "Will this ticket miss its deadline?" Analogy: *a weather forecast for customer complaints.* Demo: animated ticket → probability bar fills to risk level
  3. **Auto-Router** — "Which team should handle this?" Analogy: *an intelligent receptionist.* Demo: category + urgency → recommended queue lights up
  4. **LLM Summarizer** — "What does this long complaint actually say?" Demo: long paragraph shrinks to 3-line summary with typewriter effect
- Each card animates in on scroll. Demo interactions use pre-scripted canned inputs that play on click/focus — no live API calls needed.

### 4. The Numbers
- **Section label:** `RESULTS`
- Real trained metrics (populated after pipeline run):
  - Ticket Classifier: Macro F1 = `[actual]`, Accuracy = `[actual]`, N classes = `[actual]`
  - SLA Predictor: AUC-ROC = `[actual]`, Avg Precision = `[actual]`
  - Training data: `[actual row count]` tickets
  - SLA breach rate in dataset: `[actual]%`
- **Architecture flow diagram** (pure CSS/HTML, no image): Raw Data → Preprocessor → Feature Engineering → [Classifier | SLA Predictor | Router] → FastAPI → [Dashboard | LLM Summarizer → Executive Summary]
- Note if metrics are targets vs. actual based on pipeline outcome

### 5. Tech Stack
- **Icon grid** (text-based, no external icon deps): Python · XGBoost · scikit-learn · TF-IDF · SMOTE · FastAPI · GPT-4o-mini · MLflow · Streamlit
- 1-line rationale per tech choice

### 6. CTA / Footer
- "Built by Abhay Juloori"
- GitHub link: `https://github.com/AbhayJuloori/support-ops-copilot`
- LinkedIn link (placeholder — user to fill)
- Tagline: "Turning high-volume support from a reactive inbox into a proactive, measurable system."

---

## Technical Spec

### File structure
```
docs/
  index.html        ← single file, self-contained
  .nojekyll         ← prevents GitHub Pages Jekyll processing
```

### Implementation approach
- **Single HTML file** — all CSS and JS inline. No build step, no bundler, no npm.
- **Animations:** Pure CSS (`@keyframes`, `IntersectionObserver` in vanilla JS for scroll triggers). No animation library.
- **Live demo:** Pre-scripted canned inputs, typewriter JS function simulates typing. All client-side, no API calls.
- **Stat counters:** `IntersectionObserver` fires a JS counter animation when section enters viewport.
- **Metrics placeholders:** Replaced by actual values from training pipeline output (`reports/classifier_results.json`, `reports/sla_predictor_results.json`)

### GitHub Pages setup
- Enable Pages in repo settings → source: `docs/` folder, `main` branch
- Add `docs/.nojekyll`
- Scrap `streamlit_app.py`, `dashboard/`, `.streamlit/` — these become dead weight

### Metrics source of truth
- If `reports/classifier_results.json` exists → use actual values
- If not → label as "Architecture benchmark targets"

---

## What Gets Removed
- `streamlit_app.py` (entry point redirect)
- `dashboard/app.py` and all `dashboard/pages/`
- `dashboard/components/`
- `.streamlit/config.toml`
- `hf_requirements.txt` (HuggingFace Spaces no longer the target)

These are replaced by `docs/index.html`.

---

## Success Criteria
1. A complete stranger reads the page and understands what the project does, why it exists, and what results it achieved — without any prior ML knowledge
2. A recruiter can verify real trained metrics (not made-up targets)
3. Page loads in under 2s, works on mobile, no external dependencies
4. Deployed and live at `https://abhay juloori.github.io/support-ops-copilot` (or custom domain)
