# Meta Ads API Compliance Guide

Read this before connecting any AI tool to Meta Ads. Accounts are being permanently banned for non-compliant API usage.

---

## The Problem

Since late 2025, advertisers have been permanently banned after connecting Claude Code (or other AI agents) to Meta via self-created, unapproved developer apps. Multiple confirmed cases include advertisers with 16+ years and $1.5M+ in lifetime spend losing everything.

This is not speculation. Jon Loomer, Jacob Posel, Cas Smith, and dozens of LinkedIn posts document real bans.

## Why Accounts Get Banned

The bans are NOT caused by using the Meta Marketing API correctly. They are caused by HOW the connection is set up.

### 1. Creating a new developer app on your business account
When you create a developer app on developers.facebook.com using your main business account, Meta flags it as suspicious. The app has no review history, no partner status, no track record.

### 2. Unapproved MCP servers
Most Claude Code + Meta tutorials use open-source MCP servers that make API calls through a self-created app that has never passed Meta App Review. Meta sees unrecognised calls from an unapproved app and flags the account.

### 3. Unusual API call patterns
An AI agent making rapid reads and writes -- pulling data, creating ads, modifying budgets in quick succession -- does not look like normal behaviour. Meta's security system flags this as potentially malicious automation.

### 4. No Meta Business Partner status
If the app is not a recognised Meta Business Partner, Meta treats the activity as potentially malicious. No trust score, no audit trail, no partner agreement.

## What Meta Prohibits

- Accessing or collecting data using automated means without prior permission
- Apps that have not passed Meta App Review using ads_management or ads_read permissions
- Browser automation tools (Selenium, Puppeteer, anti-detect browsers)
- Circumventing rate limits (200 calls per hour per user)

## What Meta Allows

- Using the official Marketing API through an approved, reviewed app
- Reading insights and reporting data (every analytics tool does this)
- Creating and managing ads programmatically -- IF the app is approved
- Third-party tools that have passed Meta App Review and hold Business Partner status

---

## The Two Paths

### SAFE: Read-Only + Approved Partners for Writes

| Action | Method | Risk |
|--------|--------|------|
| Pull performance data | System user token with `ads_read` only | None -- this is what every reporting tool does |
| Generate ad copy and scripts | Claude Code locally (no API needed) | None -- no Meta connection |
| Create campaigns and ads | Route through approved Meta Business Partner (Pipeboard, Madgicx, Revealbot) | None -- partner handles compliance |
| Upload creatives | Through Ads Manager manually or approved tool | None |

### RISKY: Direct Write Access via Self-Created App

| Action | Method | Risk |
|--------|--------|------|
| Create campaigns via API | Self-created app, no App Review | HIGH -- confirmed bans |
| Modify budgets via API | Rapid API calls without rate limiting | HIGH -- triggers security flags |
| Batch-create ads | Multiple write calls in succession | HIGH -- unusual pattern detection |

---

## Best Practices

### For reading data (reporting, dashboards, monitoring)
- Use a system user token with READ-ONLY permissions (`ads_read`)
- This is identical to what Triple Whale, Hyros, and every reporting tool does
- Zero risk of account ban for read-only API access
- Respect rate limits: 200 calls/hour, check `x-fb-ads-insights-throttle` header

### For creating and managing ads
- Route all write operations through an approved Meta Business Partner
- NEVER create a Meta developer app on your main business account
- If you must create your own app, use a SEPARATE developer account with no ad spend history
- Submit your app for Meta App Review with `ads_management` permission BEFORE making write calls
- Complete Meta Business Verification for your Business Manager
- Build in rate limiting and backoff logic for ALL API calls
- Do not batch-create dozens of ads in quick succession

### For account hygiene
- One verified Business Manager per business
- One stable payment method -- do not swap frequently
- Scale budgets gradually (20-30% increases, never sudden jumps)
- Do not log in from random VPNs or constantly switch devices
- Do not create multiple ad accounts for the same offer

### For ad content (fitness, coaching, health niches)
- No specific health claims without medical evidence
- No before/after body transformation images
- No negative self-image messaging
- Disclose AI-generated visuals (mandatory since 2026)

---

## Rate Limiting

Meta enforces a hard limit of 200 API calls per hour per user token. The Ads Machine must:

1. Track call count per session
2. Add 2-3 second delays between write operations
3. Check the `x-fb-ads-insights-throttle` header before insight pulls
4. Back off exponentially if a 429 or throttle response is received
5. Never exceed 10 write operations per minute

---

## If You Get Banned

1. Appeal within 7 days -- early appeals have higher success
2. Tier 1 automated re-review resolves ~35% of false positives within 24 hours
3. Tier 2 human review takes 3-5 business days
4. Tier 3 escalated review takes 10-15 business days
5. After 180 days disabled, the account CANNOT be reinstated
6. Document everything: screenshots, API logs, timeline
7. Disconnect all unapproved MCP servers from other accounts immediately
8. Contact Meta Business Support if you spend over $10,000/month

---

## The Critical Mistake

People follow a tutorial that says "create a Meta app, get a token, paste it into your MCP config" and assume that because the API calls work, they are compliant.

**The API calls working and being compliant are two completely different things.**

Meta will let your unapproved app make calls -- and then ban your account days later.

---

## Recommendation for The Ads Machine

The default workflow should be:

1. **Intelligence layer** (poller, analyzer, swipe file, ideator, scripter, brief) -- NO Meta API needed. This is the core value.
2. **Monitoring** (`/ad-monitor`) -- Read-only `ads_read` token. Safe.
3. **Launching** (`/ad-launch`) -- Two options:
   - **SAFE:** Generate everything in Claude Code, then manually create in Ads Manager or use an approved partner tool
   - **ADVANCED (at your own risk):** Direct API writes with full compliance checklist completed first

---

## Sources

- Jon Loomer -- AI-Related Ad Account Shutdowns (jonloomer.com)
- Jacob Posel -- PSA about Meta app bans (X/Twitter)
- Cas Smith -- Permanent ban after $1.5M lifetime spend (LinkedIn)
- Meta -- Marketing API Rate Limiting (developers.facebook.com)
- Meta -- Platform Terms (developers.facebook.com)
- Meta -- Advertising Standards Enforcement (facebook.com/business)
- Madgicx -- "The Only Safe Way to Connect AI Assistants to Meta Ads"
- Pipeboard -- Meta Business Partner security documentation
