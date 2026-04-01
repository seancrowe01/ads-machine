# FAQ

## Setup

**Q: Do I need a paid Airtable plan?**
No. The free tier supports up to 1,000 records per base, which is enough to get started. You will eventually need a paid plan as your swipe file grows past 1,000 ads.

**Q: Do I need a paid Apify plan?**
No. The free tier gives you $5/month in platform credits, which is enough for 100+ competitor scrapes per month.

**Q: What Meta permissions do I need?**
Your system user token needs `ads_management` and `ads_read` permissions. The ad account must be assigned to the system user in Business Settings > System Users > Add Assets.

**Q: How do I find a competitor's Facebook Page ID?**
Go to their Facebook page > About > Page Transparency > Page ID. Alternatively, you can use the Ad Library search at facebook.com/ads/library and note the `view_all_page_id` parameter in the URL.

**Q: Can I use this without the Meta Ads API (just for intelligence)?**
Yes. The poller, analyzer, swipe file, ideator, scripter, and brief skills all work without Meta API access. You only need the Meta API for `/ad-launch` and `/ad-monitor`.

## Daily Use

**Q: How often should I run `/ad-poller`?**
Daily is ideal. At minimum, weekly. The more frequently you scrape, the more accurately you track ad longevity (which is the strongest signal for winners).

**Q: How long before the swipe file is useful?**
After 2-3 weeks of daily polling, you will have enough data to see patterns. After a month, you will have validated winners (30d+ ads). The system gets more valuable over time.

**Q: What if Whisper is not installed?**
The system works without it. You will not get video transcripts or video hooks, but you still get copy analysis, format classification, and longevity tracking. Install whisper.cpp later when you want the full analysis.

**Q: What if I do not have a Gemini API key?**
The visual analysis step is skipped. You still get transcription, hook extraction, angle classification, and scoring. Gemini adds visual format analysis but is not required.

## Troubleshooting

**Q: Apify scrape returns 0 ads for a competitor**
- Check that the Facebook Page ID is correct (not the profile ID)
- The competitor may not have active ads right now
- Try visiting the Ad Library URL manually to verify

**Q: Airtable MCP is not connecting**
- Verify your Personal Access Token has the right scopes (data.records:read, data.records:write, schema.bases:read, schema.bases:write)
- Check that the token has access to the specific base

**Q: Meta API returns "Ad creative not valid"**
- Your Meta app must be in Live mode, not Development
- Check that the image/video meets minimum specs (1080x1080 for feed)
- Verify the page ID is correct and accessible to your token

**Q: Ads are not being deduped**
- Dedup is based on the `Ad Archive ID` field. Make sure this is populated for all records.
- If you manually added records, ensure they have unique Ad Archive IDs.

**Q: What if the Apify scraper actor gets removed or stops working?**
The `/ad-poller` depends on a third-party Apify actor (`curious_coder~facebook-ads-library-scraper`). If it is removed or broken:
- Search the Apify Store for alternative "Facebook Ad Library" scrapers
- The input format may differ -- check the new actor's README
- As a manual fallback, browse facebook.com/ads/library directly and add records to the Swipe File in Airtable
- The rest of the pipeline (analyzer, ideator, scripter, brief) still works from whatever data is in the Swipe File

## Architecture

**Q: Can I add more competitors later?**
Yes. Just add rows to the Competitors table in Airtable with Status = Active. The next `/ad-poller` run will pick them up.

**Q: Can I use this for multiple ad accounts?**
Yes, but you will need to switch the `Ad Account ID` in your CLAUDE.md (or pass it as an argument) before running `/ad-launch` or `/ad-monitor`. The intelligence side (poller, analyzer, swipe file) is not tied to any specific ad account.

**Q: How does the scoring work?**
The composite score (0-100) weights: longevity 40%, creative completeness 20%, hook strength 20%, copy quality 20%. Longevity is the strongest signal -- an ad that has been running for 90+ days is spending money, which means it is making money.

**Q: What is "The Loop"?**
When `/ad-monitor` detects one of YOUR ads has been performing for 30+ days at target CPL, it creates a new record in the Swipe File with `Winner Source = Own Performance`. That winner is then available to `/ad-ideator` for multiplication. Your best ads inform your next ads.
