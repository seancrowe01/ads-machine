# Meta Ads Troubleshooting Reference

Use this file when a campaign is underperforming or broken. Run the lead gen matrix first to identify the exact failure point. Then apply the CRO checklist to the landing page before touching the creative or budget.

---

## The Lead Gen Matrix

Systematic decision tree for fixing underperforming lead generation campaigns. Work top to bottom.

```
STEP 1: CHECK CTR
─────────────────
Is CTR above 1%?
│
├── NO (below 1%)
│   └── CREATIVE / AUDIENCE PROBLEM
│       Action 1: Shorten the ad. Change the hook/opening.
│       Action 2: If still no CTR improvement → test broader targeting (Advantage+)
│       Note: Post-Andromeda, creative is the primary lever, not audience.
│
└── YES (above 1%)
    Front-end is working. Problem is downstream. Continue below.

STEP 2: CHECK LEAD VOLUME
─────────────────────────
Sending to landing page (Step 1 of funnel)?
Are they generating booked calls or form completions?
│
├── YES → Funnel is working. Sell the offer.
│
└── NO → FUNNEL PROBLEM
    Action: Change destination URL to send directly to Step 2 (form / opt-in page)

    Are they generating leads on the form/quiz page?
    │
    ├── YES → Redirect to calendar (Step 3) to capture bookings.
    │
    └── NO → LANDING PAGE PROBLEM
        Action: Abandon that landing page/funnel.
        Switch to native Meta Lead Forms.

        Are they generating leads on the Lead Form?
        │
        ├── YES → Set appointments / redirect to calendar.
        │         Lead form final button can redirect to calendar.
        │
        └── NO → OFFER PROBLEM
            The market doesn't want what's being offered at any friction level.
            Action: Switch to Lead Magnet / value resource opt-in to test basic resonance.
            "The market never lies."
```

---

## Key Principles -- Lead Gen Matrix

**CTR benchmark:**
- 1%+ = creative and audience are working. Problem is downstream.
- Below 1% = fix the hook or try broader targeting. Do not touch the funnel yet.

**Volume before quality:**
- Priority at launch: Volume first, Quality second.
- You cannot optimise lead quality with zero leads. Get volume flowing first.
- Only add friction (qualifying questions, longer forms) once volume is established.

**Funnel hierarchy (highest to lowest friction, highest to lowest quality):**
1. Landing page (highest intent, highest quality)
2. Multi-step form / opt-in page
3. Native Meta Lead Form (lowest friction, highest volume, lowest quality)
4. Lead Magnet / value resource opt-in (diagnostic tool -- tests if offer has any resonance)

**Troubleshooting timeline:**
- Allow 2-3 days minimum per change to get meaningful data
- Low-spend accounts (under $35/day): allow 3-5 days before drawing conclusions
- Don't split test everything simultaneously on limited budgets -- test sequentially

**Launch variables (what to start with):**
- 3 ad creatives
- 3 headlines
- 3 body copy variants
- Monitor CTR first before assessing anything else

---

## Offer Diagnosis

If you have 1%+ CTR but Lead Forms are still not converting:
- **Offer problem** -- the market doesn't want what's being offered, even at the lowest friction level
- Switch to a lead magnet or free resource to test whether there's any interest at all
- "The market never lies" -- if nothing converts at lead form level, the offer needs rethinking

---

## Landing Page / CRO Checklist

Run this before blaming the ad for a low conversion rate on the landing page.

| Check | Fix if Failing |
|-------|---------------|
| Site loads in **under 3 seconds** | Compress images, remove unused plugins, upgrade hosting. Test embedded calendars and forms specifically -- they are a common hidden cause of slow loads |
| Headline clearly states offer + benefit | Rewrite to be specific. Generate variations and test |
| CTA visible without scrolling (above the fold) | Reposition button to top of page |
| Contact details easy to find | Add to footer for credibility |
| Trust symbols visible near top | Add reviews, awards, partner logos |
| Payment logos visible (e-com) | Show Visa, Mastercard, PayPal, Klarna on product page -- not just checkout |
| Forms have minimal fields | Remove unnecessary fields -- reduces friction and improves load speed |
| CTA button text is action-oriented | Use specific language: "Get My Free Quote", "Book My Consultation", "Access Finance Now" |
| Multiple CTA buttons across every section | Every section needs a CTA -- no dead ends |
| Thank you page confirms next steps | Explicit: booking confirmed, delivery timeframe, what happens next |
| Benefits before features | Lead with outcomes for the customer, not product specs |
| Headlines clear and simple (6-year-old rule) | Avoid clever but vague wording |
| Images relevant and high quality | Real photos preferred; AI images acceptable but compress carefully |
| Mobile optimised | Test on mobile -- most traffic comes from mobile |

**CTA button rule:** Every section of the page should have a CTA button. 12 CTA buttons on a single-page funnel is not excessive -- it is intentional.

**Page speed tools:** Use Google's free page speed tools -- they provide a specific checklist of what's slowing load time.

---

## Standard Lead Gen Funnel Architecture

The 4-step funnel used for lead generation campaigns:

```
1. Landing Page
   ↓
2. Multi-step Form (with 2-3 qualifying questions)
   ↓
3. Calendar / Booking Page
   ↓
4. Thank You Page (confirms next steps explicitly)
```

**Landing page must include:**
- Clear outcome-focused headline
- Social proof above the fold (review count + star rating)
- Video and/or imagery showing real people and real environment
- Before/after visuals (where applicable)
- Step-by-step process section (reduces post-click anxiety)
- Founder/team bio (humanises the brand)
- Partner/accreditation logos (third-party credibility)
- Objection-handling section and FAQ
- Contact details and address (local trust signal)
- 12+ CTA buttons across the full page

**The funnel is a dedicated page, not the main website.** Purpose-built for the specific offer/campaign.

---

## Campaign Optimisation Checklist

Use this on every account review (weekly for smaller accounts; twice weekly for high-spend accounts).

### Campaign Level
- [ ] Correct objective being used (Leads -> Leads; Sales -> Sales -- never Traffic/Engagement/Awareness)
- [ ] Campaigns clearly named by funnel stage (TOF / MOF / BOF)
- [ ] Inactive/redundant campaigns paused
- [ ] Budget optimisation setting is intentional (CBO vs ABO)
- [ ] Special ad categories declared if applicable (financial, housing, employment, political)

### Ad Set Level
- [ ] Budget not spread too thin ($50/day = max 3 ad sets; below $50 = max 2 ad sets)
- [ ] No overlapping audiences across ad sets (same interests in multiple ad sets = bidding against yourself)
- [ ] Frequency monitored: above 2.5 on TOF/cold audiences = pause and replace
- [ ] Placements: Feeds + Stories + Reels only. Remove: Right Column, Inbox, Audience Network

### Ad Level
- [ ] Hook Rate reviewed in Ads Manager
- [ ] Hold Rate reviewed in Ads Manager
- [ ] Ads with zero spend after 3 days: pause them (algorithm has rejected them)
- [ ] CTR monitored: below 1% = creative problem
- [ ] Creative naming follows a consistent convention
- [ ] Challenger creative running alongside control

### Tracking
- [ ] Pixel / CAPI firing correctly (check Events Manager)
- [ ] Correct conversion event selected (Lead or Schedule)
- [ ] Meta reported conversions cross-referenced against CRM records
- [ ] No double-firing pixel on destination pages

---

## Common Failure Patterns

| Symptom | Most Likely Cause | First Action |
|---------|------------------|-------------|
| No spend after 24 hours | Ad in review or rejected | Check delivery status in Ads Manager |
| Low spend vs other ads | Algorithm has deprioritised it | Pause after 3 days of minimal spend |
| CTR below 1% | Weak hook or wrong audience | Shorten the ad, change the opening 3 seconds |
| Leads coming in but no calls booked | Follow-up system broken | Check CRM sequences -- not an ads problem |
| Calls booked but no clients signed | Sales problem | Do not kill the campaign -- review close rate |
| High CPL in first week | Learning phase | Do not kill in first 7 days -- algorithm still learning |
| CPL 3x benchmark after 500+ impressions | Creative or funnel problem | Run lead gen matrix to diagnose |
| High frequency (2.5+) on TOF | Ad fatigue | Pause and replace cold audience campaign |
| Low landing page conversion despite good CTR | CRO problem | Run CRO checklist on landing page |
| Meta reports more conversions than CRM shows | Pixel over-reporting | Check for duplicate pixel firing; CAPI setup |
