# Meta Pixel & Conversions API (CAPI) Reference

Read this before auditing any ad account. Bad tracking data is the fastest way to waste budget, especially post-Andromeda.

---

## Why the Pixel Alone Is Not Enough

The Facebook pixel fires from the user's browser. It can be blocked or stripped by:
- iOS 14+ privacy settings (user opts out of tracking)
- Ad blockers
- Cookie blockers

If the pixel can't fire, Facebook can't see the conversion. It can't optimise. It spends blind.

**The bigger problem: over-reporting.**

If the same event fires multiple times for one person (e.g. a lead rebooks a call, the pixel fires again), Facebook sees more conversions than actually happened. It then spends more on the "winning" ad -- even though that ad didn't actually win.

Real-world example: one ad reported 8 calls to Facebook. Only 2 actually happened. Facebook allocated more budget to that ad. The campaign wasted $10,000 before the problem was caught.

---

## Conversions API (CAPI)

CAPI sends data directly from the server to Facebook -- not from the browser.

**Benefits:**
- Works even with ad blockers and cookie blockers
- You control exactly which events get sent back
- You can filter -- only send qualified conversions, not all conversions
- Better data = Andromeda optimises for better people

**This is now the standard. If an account is only using the pixel, it is behind.**

---

## The Core Principle: Only Send Back Qualified Events

Facebook optimises for MORE of whatever you send it.

- Optimise for all leads -> Facebook finds the cheapest leads (not the best ones)
- Optimise for qualified leads only -> Facebook finds people like your qualified leads
- Optimise for people who showed up on a call and got pitched -> Facebook finds people like them

**The goal is to filter junk before the pixel fires.**

---

## Three Ways to Filter Before the Event Fires

### 1. Qualifying question on the form
Add a yes/no question on the opt-in form.
- If yes -> pixel fires
- If no -> pixel does not fire

Example: "Are you a business owner who can invest $1,000/month in ads? Yes / No"

Only people who say yes get passed back to Facebook as a lead event.

### 2. Application funnel with disqualification logic
Route leads through an application. After submission:
- Qualified -> show calendar, fire pixel event (submit application)
- Disqualified -> show "we'll be in touch" page, pixel does NOT fire

This means Facebook only sees people who passed qualification. Over time the algorithm learns to find more people like them.

### 3. Custom event via automation -- Qualified Call
Use an automation tool (Zapier, Make, n8n, or your CRM's native automation) to fire a custom event when the sales team marks a lead as qualified.

Workflow:
1. Call happens
2. Closer moves contact to "Qualified" stage or adds a tag
3. CRM workflow triggers -> automation fires a custom "qualified_call" event back to Facebook with name, phone, email

This sends Facebook only people who showed up, got pitched, and were a real prospect. The strongest signal you can give the algorithm.

---

## Preventing Double-Counting (The Reschedule Problem)

A contact can rebook or reschedule multiple times. If the "appointment confirmed" event fires every time, Facebook counts each reschedule as a new conversion.

**Fix in your CRM:**

Workflow: Appointment status = confirmed
-> Check: does contact have tag "schedule pixel fired"?
  - If NO -> fire CAPI schedule event -> add tag "schedule pixel fired"
  - If YES -> skip (do not fire again)

This ensures each contact only counts as one schedule conversion regardless of how many times they reschedule.

---

## Pixel vs CAPI: When to Use Each

| Event type | Timing | Use |
|---|---|---|
| Page view | Immediate | Pixel only |
| Lead / form submission | Same day | Pixel + CAPI (better match quality) |
| Application submitted | Same day | Pixel + CAPI |
| Schedule / call booked | Same day | Pixel + CAPI |
| Call happened / qualified call | 7+ days later | CAPI only |
| Purchase / closed deal | 7+ days later | CAPI only |

**Rule:** If the event happens within 7 days of the ad click, use both pixel and CAPI. If it happens beyond 7 days, use CAPI only -- pixel attribution degrades past 7 days.

Using both for same-day events improves the event match score, which helps Facebook identify the user and serve ads to more people like them.

---

## Event Match Score

In Events Manager you can see the event match quality score for each event. This shows how well Facebook can identify the user behind the conversion.

- High score = Facebook can find more people like this
- Low score = Facebook is guessing

To improve match score:
- Map the Facebook Click ID in your CRM (store it as a custom field on the contact record when they arrive from an ad)
- Use both pixel and CAPI for same-day events
- Pass name, phone, and email with every CAPI event

---

## CRM Setup -- CAPI Workflow

In your CRM, create a separate workflow for each conversion event you want to pass back.

**Workflow structure:**
- Trigger: form submitted / appointment confirmed / pipeline stage changed
- Condition: check qualification (disqualified = false, or tag check for double-count prevention)
- Action: Facebook Conversions API
  - Select standard event (lead, schedule, submit application, purchase) or custom event name
  - Map Facebook Click ID for attribution

**Standard events to consider:**
- Lead
- Schedule
- Submit Application
- Complete Registration
- Purchase
- Page View

**Custom events:** Use an automation tool (Zapier, Make, n8n) with the Facebook Conversions API action. Fire when a sales rep takes a qualifying action (marks as qualified, moves pipeline stage, adds tag).

---

## Audit Checklist -- Tracking

When reviewing an ad account, check:

- [ ] Is CAPI set up or is it pixel only?
- [ ] Are events filtered (qualified only) or sending everything?
- [ ] Is there a double-count prevention tag on the schedule event?
- [ ] Is the event match score high for same-day events?
- [ ] Do Facebook's reported conversions roughly match what the CRM / booking system shows?
- [ ] Is Facebook Click ID being mapped in the CRM?
- [ ] Is there a qualified call / qualified lead custom event set up?

**If Facebook is reporting significantly more conversions than the CRM shows** -> over-reporting problem. Find the duplicate fire and fix it before touching creative or budget.

---

## Red Flags in the Ads Manager

| What you see | What it means |
|---|---|
| High reported conversions, low actual results | Over-reporting -- pixel firing multiple times per person |
| Cost per lead looks great but leads are junk | Optimising for unfiltered event -- no qualifying gate |
| Algorithm keeps spending on one ad that isn't converting | That ad has inflated conversion data -- check for duplicate fires |
| Event match score low on calls/purchases | These are beyond 7-day window -- switch to CAPI only |

---

## Connection to Andromeda

With Andromeda, the algorithm has more control than ever over who sees which ad and how budget is allocated. This makes tracking quality more important, not less.

Bad data + Andromeda = the algorithm confidently optimises in the wrong direction at scale. The better the signal you send, the better Andromeda works for you.

**Summary:** Pixel alone is browser-based and blockable. CAPI is server-based and reliable. Filter what you send back. Only qualified people. One fire per person per event. Map the click ID. The algorithm will do the rest.
