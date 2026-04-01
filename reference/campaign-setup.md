# Meta Ads Campaign Setup Reference

Use this file when building or auditing campaigns. Covers post-August 2025 campaign structure and setup rules based on the Andromeda algorithm update.

---

## What Is Andromeda

Andromeda is Meta's AI algorithm for ad retrieval. It narrows millions of ads down to the right ad for the right person -- faster and more personally than the old system.

**Announced:** December 2024
**Fully deployed:** July 2025

**Why it matters:** The old system struggled with retrieval, so broad generic hooks worked because they cast a wide net. Andromeda can now find the right person -- which means creative diversity is the new targeting strategy, not audience segmentation.

---

## The Evolution of Campaign Structure

### Old way (2019-2022)
- 1 campaign, multiple ad sets, 1 ad per ad set
- Goal: force a specific ad in front of a specific audience
- You were doing the targeting manually

### Oldish way (2023-mid 2025)
- 1 campaign, multiple ad sets with CBO
- 1 concept per ad set, 3 ads per ad set (same video, 3 different hooks)
- Still working but losing effectiveness

### New way (post-Andromeda)
- 1 campaign, 1 ad set, 10-50 ads
- Broad or Advantage Plus targeting
- The ad set is broad -- the creative does the targeting
- All ads work together inside the ad set

**The old way can still work** but expect a performance decrease because ad sets don't collaborate the way a single consolidated ad set does.

**A/B testing old vs new is valid.** If an account is already running old-style and it's working, do not kill it. Run both in parallel and let the data decide. Compare CPL after 2-3 weeks.

---

## Why the Old Hook Strategy Is Dead

Previously: one video body + 3 different hooks = 3 ads. This worked because Facebook needed help with retrieval -- broad hooks that called out large groups performed better.

Now: Andromeda can find the right person, so it wants the entire ad to be unique -- not just the hook. Near-duplicates (same video, different hook) are not creative diversity. White background vs black background static = near duplicate.

**Creative diversity means:**
- Different concepts and angles (what the ad is about, what pain point it addresses)
- Different formats (short video, long horizontal video, static image, carousel)
- Different personas if needed (put different personas in separate ad sets -- do not mix in one ad set)

---

## The Ad Does the Targeting

Tight audience targeting no longer works the way it used to. Meta will go beyond your audience anyway.

**The words in the ad and body copy put the ad in front of the right people.**

This means: if you want to reach 35-year-old female fitness coaches, say that in the ad -- do not try to engineer it through audience settings. The creative is your targeting tool.

---

## Targeting: Advantage Plus + Value Rules

**Use Advantage Plus targeting for all campaigns.**
- No interest or behaviour audiences
- The algorithm finds the buyers
- Set minimum age at ad set level (recommended: 25 for most service-based offers)

**Value Rules for hard limits:**

When you need to exclude or weight certain groups within Advantage Plus:
- Decrease bid by 90% for ages 55+ if older audiences are wasting budget
- Apply same logic for gender or location
- Alternative: use "limit further reach" at ad set level and set age range with suggestion turned off

This gives you guardrails without locking out Advantage Plus optimisation.

---

## Creative Strategy: What to Put in the Ad Set

All funnel stages live in ONE ad set. No more separate TOFU / MOFU / BOFU campaigns.

The ads work together. Andromeda serves the right ad to the right person at the right stage:

| Funnel Stage | Ad Type | Example |
|---|---|---|
| Top of funnel | Personal story, value content, soft CTA | "I used to struggle with X, here's what changed" |
| Middle of funnel | Pain/problem focused, direct CTA to lead magnet | "If you're struggling with X, click here" |
| Bottom of funnel | Testimonials, results, social proof | "Here's how we helped a client achieve X" |

All ads drive to the same funnel. Mix of formats: short video, long video, static, carousel.

---

## Launch Volume: 10-50 Ads

- Old limit was 6 ads per ad set -- that recommendation is gone
- 10-50 ads per ad set is now the working model
- More ads = more data points for the algorithm = faster learning

**At launch:** Aim for 10-20 ads minimum across 3+ angles and 2+ formats.

---

## Monthly Creative Cadence (Not Weekly)

**Key insight:** Adding new ads to an existing ad set resets the learning phase. Adding a new ad set previously didn't affect other ad sets -- that's no longer true when everything is in one ad set.

**Old cadence (wrong now):** Drop 2-3 new creatives per week.

**New cadence:** Drop 10-50 ads 1-2 times per month.

### Monthly workflow:

1. **Launch day:** Publish 10-50 ads
2. **Daily check:** Identify ads with no spend -- Facebook is not serving them, pause them
3. **Week 1:** ~40 of 50 remain
4. **Week 2:** ~30 remain
5. **Week 3-4:** ~20 survivors
6. **End of month refresh:**
   - Look at the 20 survivors -- what's the common theme?
   - Make 10-20 creative refreshes of proven angles (same angle, different format or location)
   - Make 10 new angles targeting different pain points
   - Relaunch to 50 ads for the next month

**Finding winners and making more:** If a video is winning, repurpose it -- turn it into a carousel, turn it into a static, film the same script in a different location. That counts as creative diversity.

---

## Ads Not Spending = Facebook Doesn't Like Them

With 1 ad set and 10-50 ads, Meta is constantly running an internal auction. Ads that don't get spend are being passed over by the algorithm.

**Rule:** If an ad has been live 3+ days with zero or near-zero spend relative to others in the ad set -- pause it. Don't wait. The algorithm has already decided.

---

## Pixel Health Warning

If using Advantage Plus and optimising for leads or messages -- you will get volume, but quality can suffer.

**The algorithm optimises for whatever you tell it to.** If you say leads, it sends leads. If those leads are junk, the pixel learns to find more junk.

Before running Advantage Plus at scale:
- Pixel must be sending back only qualified lead events
- Add friction in the funnel (application step, qualifying question) to filter junk before the pixel fires
- A healthy pixel conditioning on quality leads = Advantage Plus working for you

---

## Messenger / Engagement Campaign Setup

**Campaign objective:** Engagement (for Messenger/DM funnels)

**Naming convention:** `O_message_[offer description]`
- Example: `O_message_discovery-call`
- O = Outbound, message = Messenger objective

**Budget:** $50-100/day at the ad set level

**Schedule:** Start time at midnight the following day so all ads launch simultaneously -- prevents one ad getting a head start and skewing data

**Optimisation event:** Messenger conversations (not link clicks)

---

## Key Rules for Campaign Build

1. **1 campaign, 1 ad set, 10-50 ads** -- do not split audiences across ad sets
2. **Advantage Plus + Value Rules** -- no manual interest targeting
3. **Creative diversity = concepts + formats** -- not just hooks on the same video
4. **TOFU + MOFU + BOFU all in one ad set** -- they work together now
5. **Drop creatives 1-2x per month** -- not weekly, to protect the learning phase
6. **Pause ads not spending within 3 days** -- algorithm has rejected them
7. **The ad is the targeting** -- write creative that calls out the right person

---

## Audit Checklist -- Is This Account Running Old or New Structure?

| Check | Old Style (Flag) | New Style (Good) |
|---|---|---|
| Campaign structure | Multiple ad sets, 1-3 ads each | 1 ad set, 10+ ads |
| Targeting | Manual interests, tight audiences | Advantage Plus or broad |
| Creative count | Under 6 ads total | 10-50 ads |
| Creative diversity | Same video, different hooks only | Different concepts, angles, formats |
| Funnel stage split | Separate TOFU/MOFU/BOFU campaigns | All stages in one ad set |
| Add frequency | New creatives weekly | New creatives 1-2x per month |

**Decision rules:**
- Old style performing (CPL on benchmark, ROAS positive) -- do not touch it, let it run
- Old style underperforming -- consolidate to Andromeda structure before changing creative
- New account -- start with Andromeda structure
- Want to test -- run both in parallel, compare CPL at 2-3 weeks, then cut the loser

---

## Campaign Objectives -- Only Two Matter

**Always use Leads or Sales. Never use Traffic, Engagement, or Awareness for performance campaigns.**

The objective signals to the algorithm who to find. Wrong objective = wrong people:
- **Traffic** -- finds clickers, not buyers
- **Engagement** -- finds likers, not leads
- **Awareness** -- finds viewers, not prospects

**Leads objective sub-types:**
- **Website/Funnel** -- lower volume, higher intent and quality (preferred)
- **Instant Forms** -- higher volume, lower quality ("panning for gold")
- **Messenger/WhatsApp/Instagram DM** -- conversation-starter lead; effective for service businesses

Despite Meta recommending Instant Forms for "more conversions," stick with website/funnel if lead quality matters. Only fall back to Instant Forms as a troubleshooting step.

**Performance goal:** Maximise number of conversions. Conversion event: Lead (or Schedule if tracking booked calls).

---

## Special Ad Categories -- Declare or Risk Account Ban

If a campaign involves any of the following, declare it in the Special Ad Categories field before publishing:
- Financial products or anything regulated by financial authorities
- Employment / job ads
- Housing / property / mortgages
- Social issues, elections, or politics

**Not declaring = risk of ad rejection or permanent account ban.** These categories also restrict granular targeting by design (fair access principle). Build this check into every new campaign setup.

---

## Budget Per Ad Set Rules

| Daily Budget | Max Ad Sets |
|-------------|------------|
| Under $50/day | 2 ad sets maximum |
| $50/day | 3 ad sets |
| $100/day | 3 cold audience ad sets |

**Rationale:** Budget must be sufficient to get actionable data from each ad set within a week. Too many ad sets on a small budget = underfunded tests with no valid conclusions.

**Do not toggle between CBO and ABO** once a campaign is running -- toggling resets ad set settings.

---

## Launch Approach -- Volume First, Quality Second

At launch: prioritise getting lead volume before optimising lead quality.

You cannot optimise quality with zero data. Once volume is established and the funnel is working, then add qualification friction (longer forms, qualifying questions) to improve quality.

**No shortened or redirected links:** Use the full destination URL in the link field. Bitly links and URL shorteners get ads disapproved or accounts flagged. The display URL can be simplified, but the actual destination must be the real URL so Meta's bots can verify compliance.

---

## When to Use CBO vs ABO

- **ABO (Ad Set Budget):** Use when specific locations or segments each need guaranteed spend. Example: 3 locations each need leads -- ABO ensures each gets its share, not just the strongest market.
- **CBO (Campaign Budget):** Use for cold traffic campaigns when you want Meta to allocate automatically to the best-performing ad set.

**Do not toggle between CBO and ABO** after campaign launch -- toggling resets ad set settings.

Do not switch to CBO until you have a proven structure and a winning angle.

---

## Notes on the July 2025 Rollout

Some accounts saw CPC spike in July 2025. Others saw it drop. Some accounts switched strategies entirely (DM ads to book-a-call funnels and back) because results were unstable.

This was the Andromeda rollout destabilising old campaign structures. If an account had unusual performance in July-August 2025, that is the likely cause -- not the creative or the offer.
