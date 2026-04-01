# The Ads Machine -- Blueprint

## The Closed Loop

The Ads Machine is a closed-loop ad intelligence system. It scrapes competitors, analyzes what works, generates your own ads from proven winners, launches them, tracks performance, and feeds winners back into the system.

The longer you run it, the smarter it gets.

## 9 Stages

### 1. Competitors
Define who you are watching. Direct competitors (selling similar things to similar people), adjacent competitors (related niches), and aspirational brands (the big names worth learning from). All stored in Airtable.

### 2. Daily Ad Poller (`/ad-poller`)
Scrapes Meta Ad Library via Apify for every active competitor. Detects new ads, marks killed ads, calculates how long each ad has been running. Ads running 30+ days are flagged as validated winners -- they are spending money on it, so it is working.

### 3. Analysis Engine (`/ad-analyzer`)
Downloads video creatives and runs them through the analysis stack:
- **Whisper** transcribes the audio
- **Claude** extracts hooks, classifies angle and format
- **Gemini** runs visual analysis (text overlays, color palette, production quality)
- Each ad gets a composite score (0-100)

### 4. Ad Swipe File (`/ad-swipe`)
The growing intelligence database. Every ad that has been scraped, transcribed, and classified lives here. Searchable by angle, format, competitor, score, and longevity tier.

This file grows every single day. It is your competitive advantage.

### 5. Ad Ideator (`/ad-ideator`)
Takes 1 winning ad and generates 5 variations:
- Same angle, different hook
- Same hook, different angle
- Different format entirely
- Different copy framework
- Mashup of multiple winners

Each variation is adapted for your business, audience, and offer.

### 6. Ad Scripter (`/ad-scripter`)
Writes timed video scripts with visual directions and platform-ready ad copy (primary text, headline, description, CTA). Uses proven frameworks: PAS, AIDA, Story, Before/After, Controversy.

### 7. Creative Brief (`/ad-brief`)
Turns a script into a printable filming card: shot list, B-roll suggestions, text overlay specs, equipment notes. Take it to a filming session and execute.

### 8. Launch (`/ad-launch`)
Creates the full Meta campaign stack via the Graph API:
- Campaign (objective, budget)
- Ad Set (targeting, optimization)
- Creative (copy + asset)
- Ad (paused until you confirm)

### 9. Performance Monitor (`/ad-monitor`)
Pulls performance data and assigns verdicts:
- **Kill** -- not working, pause it
- **Watch** -- not enough data yet, wait
- **Scale** -- working, increase budget
- **Winner** -- proven performer, feed it back into the swipe file

## The Loop

When an ad reaches Winner status (30+ days at target CPL), the monitor automatically creates a new record in the Swipe File with `Winner Source = Own Performance`.

That winner is now available to the Ideator for multiplication.

Your best ads inform your next ads. The system feeds itself.

## Data Flow

```
Meta Ad Library (Apify)
    |
    v
Ad Swipe File (Airtable)
    |
    v
Ad Pipeline (Airtable)
    |
    v
Meta Ads Manager (Graph API)
    |
    v
Performance Data (Meta Insights)
    |
    v
Winners --> back to Ad Swipe File
```

## Tech Stack

- **Claude Code** -- the brain (runs all skills)
- **Airtable** -- the database (pipeline + swipe file + competitors)
- **Apify** -- the scraper (Meta Ad Library)
- **Meta Graph API** -- the launcher (campaign management)
- **Whisper** -- the ears (video transcription)
- **Gemini** -- the eyes (visual analysis)
- **Slack** -- the alerts (optional)
- **n8n** -- the scheduler (optional)
