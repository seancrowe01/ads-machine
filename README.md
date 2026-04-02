<div align="center">

<img src="docs/blueprint.png" alt="The Ads Machine Blueprint" width="800" />

# The Ads Machine

*A closed-loop ad intelligence system built in Claude Code.*

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](./LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com)
[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-blueviolet?style=flat-square)](https://claude.ai/claude-code)

Scrape competitors. Analyze winners. Generate ads. Launch campaigns. Track performance.
**The loop feeds itself.**

</div>

---

## Contents

1. [How It Works](#how-it-works)
2. [Quick Start](#quick-start)
3. [Skills](#skills)
4. [The Swipe File](#the-swipe-file)
5. [The Hook Farm](#the-hook-farm)
6. [The Loop](#the-loop)
7. [n8n Automation](#n8n-automation-optional)
8. [MCP Servers](#mcp-servers)
9. [Compliance](#meta-ads-api-compliance)
10. [Reference Files](#reference-files)
11. [Requirements](#requirements)
12. [License](#license)

---

## How It Works

```
POLL       Scrape competitor ads daily from Meta Ad Library
  |
ANALYZE    Whisper transcribe, Claude extract hooks, Gemini visual analysis
  |
SWIPE      Growing database of winning hooks, angles, copy, formats
  |
IDEATE     1 winner = 5 ad variations
  |
SCRIPT     Video scripts + ad copy (primary text, headline, CTA)
  |
BRIEF      Shot list + filming card, ready for production
  |
LAUNCH     Meta API -- Campaign, Ad Set, Creative, Ad (all paused)
  |
MONITOR    Kill / Watch / Scale decisions based on KPI benchmarks
  |
LOOP       Winners feed back into the swipe file. The system learns.
```

---

## Quick Start

```bash
git clone https://github.com/seancrowe01/ads-machine.git
cd ads-machine
cp .env.example .env
# Fill in your API keys in .env
# Open Claude Code and run:
/ads-setup
```

The setup wizard interviews you about your business, creates your Airtable tables, configures your MCP servers, and gets everything wired up.

---

## Skills

| Command | What It Does |
|---------|-------------|
| `/ads-setup` | One-time installation wizard -- creates tables, resolves competitor Page IDs, loads Hormozi as default hook farm |
| `/ad-poller` | Scrape competitors from Meta Ad Library (active + inactive ads) |
| `/ad-analyzer` | Transcribe, classify, grade by Days Active, feed proven hooks to database |
| `/ad-swipe` | Search and browse the swipe file by angle, format, tier, competitor |
| `/ad-ideator` | Generate 5 variations from 1 winner |
| `/ad-scripter` | Write video scripts and ad copy using proven hooks and Long-Runner frameworks |
| `/ad-brief` | Create filming cards and shot lists |
| `/ad-creative` | Generate ad images and visual assets (works with Gemini, DALL-E, or Flux) |
| `/ad-polish` | Strip AI patterns from ad copy -- makes it sound human-written |
| `/ad-launch` | Launch Meta campaigns (Safe Mode default) |
| `/ad-monitor` | Track performance, kill/watch/scale decisions |

---

## The Swipe File

The swipe file is the brain of the system. It starts empty and grows every day:

- **`/ad-poller`** adds new competitor ads (active + inactive)
- **`/ad-analyzer`** enriches them with transcripts, hooks, angles, and longevity grades
- **`/ad-monitor`** feeds your own winners back in

Every ad gets graded by **Days Active** -- the only metric that matters. If someone kept spending on it for 60+ days, it's a proven winner. No subjective scoring.

| Days Active | Grade |
|---|---|
| 60+ | Long-Runner (proven winner) |
| 30-59 | Performer |
| 14-29 | Solid |
| 7-13 | Testing |
| <7 | Killed |

Angle, format, hook, CTA type are **filters** for browsing -- not scoring factors. "Show me all Long-Runners with social proof angle" is how you find patterns.

Long-Runner hooks automatically feed into the **Proven Hooks** database -- a growing collection of battle-tested hooks you can pull from when writing ads.

## The Hook Farm

The repo ships with **Alex Hormozi** as a default aspirational competitor. He tests 150-200 ads at any time with massive budgets. The hooks that survive 60+ days are battle-tested winners.

First scrape pulls ~2000 of his ads. The analyzer finds the ~110 Long-Runners and extracts their hooks into your Proven Hooks database. When you run `/ad-scripter`, it reads those hooks and uses them as framework inspiration for your ads.

The longer you run it, the better your hook library gets. Add more aspirational competitors and you're harvesting millions of dollars of A/B testing for free.

---

## The Loop

This is what makes the system self-improving.

When `/ad-monitor` detects one of your ads has been performing for 30+ days:

1. It marks it as a **Winner**
2. Creates a new record in the Swipe File with `Winner Source = Own Performance`
3. The hook feeds into the Proven Hooks database
4. That winner is now available to `/ad-ideator` for multiplication
5. Your best ads inform your next ads

**The longer you run it, the smarter it gets.**

---

## n8n Automation (Optional)

Want the poller to run daily without you touching it? Import the n8n workflow.

```
n8n/ad-poller-workflow.json
```

5-minute setup:
1. Import the JSON into your n8n instance
2. Add your Airtable + Apify credentials
3. Replace 3 placeholder IDs
4. Activate

Runs daily at 6am. Scrapes all active competitors. Deduplicates. Calculates Days Active. Pushes new ads to Airtable. Your swipe file grows on autopilot.

See [`n8n/README.md`](n8n/README.md) for full setup guide.

---

## MCP Servers

The Ads Machine uses [MCP](https://modelcontextprotocol.io) (Model Context Protocol) to connect Claude Code to external tools:

| MCP Server | Required | What It Does |
|-----------|----------|-------------|
| **Airtable** | Yes | Pipeline database -- swipe file, ad records, status tracking |
| **Apify** | Yes | Meta Ad Library scraping and competitor monitoring |
| **Meta Ads** | For launching | Campaign creation, ad management, performance data |
| **Slack** | Optional | Daily alerts -- new competitor ads, kill/scale decisions |
| **n8n** | Optional | Cron jobs -- daily poller, weekly reports, automation |

All configured during `/ads-setup`. The Meta Ads MCP server ships in the repo at `mcp-servers/meta-ads-mcp/`.

---

## Meta Ads API Compliance

> **Read this before connecting to Meta.** See [`reference/compliance.md`](reference/compliance.md) for the full guide with real cases and sources.

Since late 2025, advertisers have been **permanently banned** after connecting AI tools to Meta via unapproved developer apps. This includes accounts with 16+ years of history and $1.5M+ in lifetime spend.

**What is safe:**
- The intelligence layer (poller, analyzer, swipe file, ideator, scripter, brief) -- **no Meta API needed**
- Reading performance data with `ads_read` permission -- same as every reporting tool
- Creating campaigns manually in Ads Manager using the specs `/ad-launch` generates

**What is risky:**
- Creating a Meta developer app on the same account you run ads from
- Using an app that has not passed Meta App Review for write operations
- Making rapid API calls without rate limiting

**The default `/ad-launch` mode is Safe Mode** -- it generates copy-paste-ready campaign specs for Ads Manager. Direct API access is available but requires a 5-item compliance checklist confirmation first.

For programmatic ad management without risk, use an approved Meta Business Partner like [Pipeboard](https://pipeboard.co), [Madgicx](https://madgicx.com), or [Revealbot](https://revealbot.com).

---

## Reference Files

The `reference/` folder contains universal ad frameworks -- no personal data, no client info:

| File | What It Covers |
|------|---------------|
| `campaign-setup.md` | Post-Andromeda Meta campaign architecture |
| `creative-strategy.md` | Hook rates, script formulas, ad format specs |
| `kpi-benchmarks.md` | Benchmarks and decision rules for kill/watch/scale |
| `ad-frameworks.md` | PAS, AIDA, Story, Before/After, Controversy templates |
| `hook-swipe-file.md` | Starter hooks (grows via the loop) |
| `copy-patterns.md` | Primary text, headline, and CTA patterns |
| `visual-styles.md` | UGC, talking head, motion graphics production specs |
| `troubleshooting.md` | Lead gen diagnostic matrix and CRO checklist |
| `pixel-tracking.md` | Conversions API setup and event filtering |
| `retargeting.md` | Retargeting strategy framework |
| `proof-hierarchy.md` | Proof checklist, testimonial questions, proof-driven ad formats |
| `offer-check.md` | 5-point offer validation before running ads |
| `compliance.md` | Meta API compliance guide, real ban cases, safe vs risky |

---

## Requirements

- [Claude Code](https://claude.ai/claude-code) with a Claude Pro or Team subscription
- [Airtable](https://airtable.com) account (free tier works to start)
- [Apify](https://apify.com) account (free tier gives 100+ scrapes/month)
- [Meta Business](https://business.facebook.com) account (for ad management features)
- Python 3.10+ (for Meta Ads MCP server)
- ffmpeg + whisper.cpp (optional -- for video ad transcription)

---

## License

[MIT](./LICENSE) -- use it however you want.
