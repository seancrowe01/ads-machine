# Meta Ads Retargeting Reference

---

## The Core Problem Retargeting Solves

Direct response ads (DM me, book a call, opt in) are getting harder to convert. Trust is lower. People have their guard up. Making big claims no longer cuts through.

Retargeting is not about asking for the action again. It is about making someone decide they want to work with you before they ever get to the sales conversation.

---

## The "Hammer Them" Campaign

Strategy credit: Jeremy Haynes. The concept is to force content in front of warm leads at high frequency -- cheaply -- so they consume enough to overcome every objection on their own.

**What it is:** An awareness campaign that serves organic content (reels, carousels, posts) to people who have recently opted in. No CTA. No link. Just content.

**Goal:** By the time they book a call or reply to a DM, they already know, like, and trust you. Show rate goes up. Close rate goes up.

---

## Campaign Structure

| Setting | Value |
|---|---|
| Objective | Awareness (not engagement) |
| Budget type | CBO -- Advantage Campaign Budget |
| Budget | ~5% of total daily ad spend |
| Ad sets | 1 ad per ad set (e.g. 22 ad sets = 22 ads) |
| Frequency cap | 1 impression per 5 days per ad set |
| Placements | Manual -- choose the platform where your audience is most active |

**Why awareness over engagement:**
- Engagement optimises for video views or watch time
- Awareness optimises for lowest cost per impression -- more reach, more frequency
- Goal is impressions, not clicks or actions

**Why 1 ad per ad set:**
- Allows individual frequency caps per piece of content
- CBO distributes spend to the ads getting the best response
- Easy to add new content -- just add a new ad set

**Why CBO:**
- Meta moves budget to the best-performing content automatically
- No need to manually manage individual ad set budgets

---

## Creative: Objection-Crushing Content

Use existing organic posts -- reels, carousels, short videos. Do not create new ad-specific creative for this campaign.

**All content should overcome objections.** Examples:
- "How long does it take to see results?"
- "How much should I spend to start seeing results?"
- "What's the worst case scenario?"
- "What if it doesn't work for my situation?"
- "I've tried this before and it didn't work -- what's different?"

No CTA. No link. No ask. Just value and social proof. People consume it and decide on their own.

Aim for 20-40 pieces of content in this campaign over time. Keep adding to it.

---

## Frequency and Reach

- Frequency cap of 1/5 days per ad set = a person can see any single ad up to 6 times in 30 days
- More ads in the campaign = lower frequency per ad = content stays fresh
- Target: each warm lead sees 4-6 pieces of your content over the 30-day window

**Expectation:** Facebook can only track and serve ads to roughly 60-75% of your audience. If you have 600 leads, expect ~400 to actually see the ads. CAPI helps push this number higher.

---

## The Audience: 30-Day Leads

Build a custom audience of anyone who opted in within the last 30 days.

**Pixel-based sources:**
- Visited thank you page URL (post opt-in or post-registration)
- Lead event fired
- Complete registration event fired
- Any specific thank you page URL for each lead magnet

**Instagram-based alternative:**
- People who sent a DM in the last 30 days
- Lower quality than pixel leads -- includes spam accounts -- only use if you don't have enough pixel data

**Preferred:** Pixel + CAPI combined audience. CAPI pushes leads into the audience even when the pixel can't track them (ad blockers, iOS).

---

## CRM Setup: Auto-Adding Leads to the Retargeting Audience

In your CRM, create a workflow that fires when someone opts in:

1. Trigger: lead submits form / completes workflow
2. Action: CAPI event -> adds contact to Facebook custom audience (30-day leads)
3. Wait: 30 days
4. Action: remove from audience

This ensures every new lead is pushed into the retargeting audience via server-side data, not just browser pixel.

---

## Retroactively Building the Audience (Past Leads)

To push existing leads into the audience on day one:

1. In your CRM contacts, filter by: workflow completed (any lead magnet) + created within last 45 days
2. Select all contacts
3. Add to automation: retargeting manual push workflow
4. The workflow adds them to the Facebook custom audience via CAPI

Repeat for each lead magnet / funnel. This fills the audience immediately rather than waiting for new leads to accumulate.

---

## Retroactive Pixel Training (Qualified Calls)

If CAPI was not previously set up, you can retroactively train the pixel with past qualified leads:

1. In your CRM, find all contacts who were ever tagged as a qualified call or moved to a qualified pipeline stage
2. Push them through a workflow that fires a CAPI "schedule" or "qualified call" event
3. Facebook receives this historical data and starts to find more people like them

This is a one-time catch-up that improves algorithm targeting quality for future campaigns.

---

## Where to Use This in the Funnel

The original strategy (Jeremy Haynes) places this after a call is booked -- to improve show rate and close rate. The lead has booked but not yet shown up. Hammering them with content in that window builds confidence and reduces no-shows.

**Modified application:** Move it earlier -- after opt-in, before booking. Use it to convert warm leads who opted in but haven't booked a call yet.

**Choose based on the bottleneck:**

| Bottleneck | Where to run it |
|---|---|
| Leads opting in but not booking | After opt-in, 30-day window |
| Leads booking but not showing | After booking, before call |
| Leads showing but not closing | After call, 30-day nurture |

---

## Budget Guide

| Daily ad spend | Retargeting budget |
|---|---|
| $50/day | $2-3/day |
| $100/day | $5/day |
| $500/day | $25/day |
| $1,000/day | $50/day |

5% of total daily spend is the rule. This is a supporting campaign, not a primary spend channel.

---

## Audit Checklist -- Retargeting

When reviewing an ad account:

- [ ] Is there any retargeting campaign running?
- [ ] If yes -- is it direct response (asking for action) or awareness (building trust)?
- [ ] Is the audience 30-day leads, 30-day website visitors, or social engagers?
- [ ] Is CAPI being used to push leads into the retargeting audience?
- [ ] What is the frequency? Are people seeing enough content or just 1-2 impressions?
- [ ] Is the creative objection-focused or just a recycled cold ad?
- [ ] Is the budget ~5% of total spend or being over-allocated?

**If no retargeting:** Flag it. Especially if CPL is fine but show rate or close rate is low -- retargeting is the fix before blaming the sales process.
