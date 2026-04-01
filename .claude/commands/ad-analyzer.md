---
name: ad-analyzer
description: Analysis engine for the Ad Swipe File. Downloads video creatives, transcribes with Whisper, extracts hooks and copy patterns with Claude, runs visual analysis with Gemini, scores and ranks everything. Run after /ad-poller.
---

# Ad Analysis Engine

You are a creative analysis system. You process unanalyzed ads from the Swipe File -- downloading videos, transcribing speech, extracting hooks, classifying angles and formats, running visual analysis, and scoring each ad.

**What you produce:** Fully enriched Swipe File records with transcripts, hooks, classifications, visual analysis, and composite scores -- ready for `/ad-ideator` to work from.

---

## Prerequisites

1. **Airtable MCP** connected
2. **Unanalyzed ads** in the Swipe File (run `/ad-poller` first)
3. **ffmpeg installed** -- for audio extraction (check: `ffmpeg -version`)
4. **whisper.cpp installed** -- for transcription (check: `whisper-cli --help`)
   - If not installed, skip transcription and note it in the summary
5. **Gemini API key** in `.env` as `GEMINI_API_KEY` (optional -- for visual analysis)

---

## Config

Read from CLAUDE.md:
```
Airtable Base ID: YOUR_AIRTABLE_BASE_ID
Ad Swipe File Table: YOUR_SWIPE_FILE_TABLE_ID
```

---

## Step 1: Fetch Unanalyzed Ads

```
Use Airtable MCP: list_records
  base_id: {from CLAUDE.md}
  table_id: {Swipe File table ID}
  filter: {Is Analyzed} = FALSE()
  fields: Ad Archive ID, Competitor, Display Format, Body Text, Title, Video URL, Image URL, Hook Copy
```

Print count: `Found {N} unanalyzed ads to process.`

If the user passed a count argument, limit to that many. Otherwise process all.

---

## Step 2: Process Video Ads

For each ad where Display Format = Video AND Video URL exists:

### 2a. Download Video
```bash
mkdir -p /tmp/ads-machine
curl -s -L -o /tmp/ads-machine/{ad_archive_id}.mp4 --max-time 60 "{video_url}"
```

If download fails, log it and continue to the next ad.

### 2b. Get Metadata
```bash
ffprobe -v quiet -print_format json -show_format -show_streams /tmp/ads-machine/{ad_archive_id}.mp4
```

Extract:
- `duration` (seconds, rounded)
- `width` and `height` -> calculate aspect ratio:
```python
ratio = width / height
if abs(ratio - 9/16) < 0.05: aspect = "9:16"
elif abs(ratio - 4/5) < 0.05: aspect = "4:5"
elif abs(ratio - 1) < 0.05: aspect = "1:1"
elif abs(ratio - 16/9) < 0.05: aspect = "16:9"
else: aspect = "Other"
```

### 2c. Extract Audio
```bash
ffmpeg -i /tmp/ads-machine/{ad_archive_id}.mp4 -ar 16000 -ac 1 -f wav /tmp/ads-machine/{ad_archive_id}.wav -y 2>/dev/null
```

### 2d. Transcribe with Whisper
```bash
whisper-cli -m {model_path} -f /tmp/ads-machine/{ad_archive_id}.wav --no-prints
```

Use whichever whisper model is available. `tiny.en` (75MB) is fast and sufficient for ad transcription. `medium.en` (1.5GB) is more accurate.

If whisper is not installed, check for OpenAI API key and use the Whisper API as fallback:
```bash
curl -s https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer {OPENAI_API_KEY}" \
  -F model="whisper-1" \
  -F file="@/tmp/ads-machine/{ad_archive_id}.wav"
```

If neither is available, skip transcription. Log: `Whisper not available -- skipping transcription for {count} video ads.`

### 2e. Extract Hook
Split transcript on sentence boundaries (`. ! ?`). Take the first 1-2 complete sentences.
- If the first sentence is fewer than 8 words, include the second sentence.
- This becomes the `Hook Video` field.

### 2f. Clean Up
```bash
rm /tmp/ads-machine/{ad_archive_id}.mp4 /tmp/ads-machine/{ad_archive_id}.wav
```

---

## Step 3: Classify Angle Category

For every ad (video and non-video), classify based on available text content (body text + title + transcript).

### Signal Table

| Angle | Signals in Copy/Transcript |
|-------|---------------------------|
| Social Proof | Testimonials, revenue numbers, "since we signed up", "my name is", case studies, client results |
| Pain-to-Transformation | Fees, losing money, switching pain, "save you", "fight back", frustration language |
| Tips/Education | How-to, listicles, "reason number", "watch this", educational framing, step-by-step |
| Growth Problem | More orders, scaling, "drive sales", "increase your", growth metrics |
| Profit Problem | Costs, margins, wasted spend, "paying too much", ROI language |
| Authority | Platform features, "only solution", data access, expert positioning, credentials |
| Scarcity/Urgency | Limited time, spots filling, deadline, "last chance", countdown |
| Behind-the-Scenes | Day-in-the-life, process reveal, "how we", "let me show you" |
| Controversy | Contrarian takes, "most people are wrong", "unpopular opinion", industry criticism |
| Comparison | "vs", "compared to", "I tested both", head-to-head |

If multiple signals match, choose the dominant one. If unclear, default to the first match.

---

## Step 4: Classify Ad Format Type

| Format | Detection Rules |
|--------|----------------|
| UGC Testimonial | Video + first-person experience ("my name is", "our sales", "since we", customer story) |
| UGC Talking Head | Video + presenter explaining features/benefits (second-person "you", instructional) |
| Interview/Case Study | Video + Q&A pattern, multiple speakers, interviewer framing |
| Motion Graphics | Video + no meaningful transcript (music only, silence, or very short text) |
| Static Image | Image display format with real copy |
| Screenshot/Demo | Image showing product interface, dashboard, or screen capture |
| Slideshow | Carousel or multi-image format |
| Other | DCO with template variables `{{product.name}}` or unclassifiable |

---

## Step 5: Visual Analysis with Gemini (Optional)

If `GEMINI_API_KEY` is in `.env`, run visual analysis on ads with images or video thumbnails.

For each ad with an Image URL or video thumbnail:

```
Analyze this ad creative and describe:
1. Visual format (photo, graphic, screenshot, text-heavy, minimal)
2. Color palette (dominant colors)
3. Text overlay presence and style (bold, subtle, none)
4. Production quality (professional, semi-pro, casual/UGC)
5. Human presence (face visible, hands only, no people)
6. Key visual elements that grab attention
```

Store the response in the `Visual Style` field.

If Gemini is not configured, skip this step silently. The rest of the analysis still works.

---

## Step 6: Score Each Ad

Calculate a composite score (0-100) based on available data:

```python
score = 0

# Longevity weight (40 points max)
days = ad.days_active or 0
if days >= 90:
    score += 40  # Long-runner = proven winner
elif days >= 60:
    score += 30
elif days >= 30:
    score += 20  # Performer
elif days >= 14:
    score += 10
else:
    score += 0   # Too early to judge

# Creative completeness (20 points max)
if ad.transcript:
    score += 5
if ad.hook_video:
    score += 5
if ad.body_text and len(ad.body_text) > 20:
    score += 5
if ad.visual_style:
    score += 5

# Hook strength (20 points max)
hook = ad.hook_video or ad.hook_copy or ""
if len(hook) > 0:
    score += 5  # Has a hook at all
if any(word in hook.lower() for word in ["you", "your", "how", "why", "what if"]):
    score += 5  # Addresses the reader
if any(char in hook for char in "0123456789$%"):
    score += 5  # Contains specifics (numbers, money)
if len(hook.split()) <= 15:
    score += 5  # Concise hook

# Copy quality (20 points max)
body = ad.body_text or ""
word_count = len(body.split())
if 20 <= word_count <= 100:
    score += 10  # Good length range
elif word_count > 0:
    score += 5   # Has copy but suboptimal length
if ad.cta_type:
    score += 5   # Has a CTA
if ad.link_url:
    score += 5   # Has a destination
```

---

## Step 7: Update Airtable Records

Batch update all processed ads (10 per request):

Fields to update:
- `Video Duration` (if video)
- `Aspect Ratio` (if video)
- `Transcript` (if video + whisper available)
- `Hook Video` (if video + transcript)
- `Word Count`
- `Angle Category`
- `Ad Format Type`
- `Visual Style` (if Gemini available)
- `Score`
- `Is Analyzed` = true

---

## Step 8: Print Summary

```
=== Analysis Complete ===

Ads processed: {total}
  Videos transcribed: {transcribed}
  Visuals analyzed: {visual_count}
  Skipped (no media): {skipped}

By angle:
  Social Proof: {count}
  Pain-to-Transformation: {count}
  Tips/Education: {count}
  ...

By format:
  UGC Talking Head: {count}
  UGC Testimonial: {count}
  Static Image: {count}
  ...

Score distribution:
  80-100 (Strong): {count}
  60-79 (Good): {count}
  40-59 (Average): {count}
  0-39 (Weak): {count}

Top 5 highest-scoring ads:
  1. [{score}] {competitor} -- "{hook}" ({angle}, {format})
  2. ...

Next step: Run /ad-swipe to browse your swipe file, or /ad-ideator to generate variations from winners.
```

---

## CRITICAL RULES

1. **Process ads one at a time** for video download/transcription. Clean up files after each.
2. **Never fail the whole batch** because one ad fails. Log the error and continue.
3. **Whisper tiny.en** is the default model. Use whatever is installed.
4. **Hook extraction:** Split on sentence boundaries, not word count. Take first 1-2 complete sentences.
5. **Airtable batch limit is 10.** Always batch updates.
6. **DCO ads have no media.** Still classify them from body text and title.
7. **Score is a heuristic, not gospel.** Longevity is the strongest signal -- an ad running 90+ days is a proven winner regardless of other scores.
8. **Gemini visual analysis is optional.** The system works without it. Do not error if the key is missing.
