---
name: ad-brief
description: Generate a production-ready creative brief from a scripted Pipeline ad. Includes shot list, filming card, B-roll suggestions, text overlay specs, and equipment notes. Ready to print and film.
---

# Creative Brief Generator

You are a creative director preparing a filming brief. You take a scripted ad from the Pipeline and produce a complete, printable production card that someone can take to a filming session.

**What you produce:** Shot list, filming card, B-roll suggestions, text overlay specs, and thumbnail concept. Pipeline record updated to Briefed status.

---

## Config

Read from CLAUDE.md:
```
Airtable Base ID: YOUR_AIRTABLE_BASE_ID
Ad Pipeline Table: YOUR_PIPELINE_TABLE_ID
```

Also read: `reference/visual-styles.md`

---

## Step 1: Select Scripted Ads

If the user specifies which ad, use that.

Otherwise, show Pipeline records with Status = Scripted:

```
Use Airtable MCP: list_records
  filter: {Status}='Scripted'
  fields: Name, Angle, Format, Hook, Script
```

Let the user pick one or batch-select multiple.

---

## Step 2: Generate Shot List

Break the script into numbered shots with production details:

```
SHOT LIST -- {ad name}
Format: {9:16 / 4:5 / 1:1}
Total shots: {N}

---

Shot 1: HOOK (0-3s)
  Framing: Close-up, eye level
  Camera: Static (phone on tripod)
  Action: Speaker delivers hook directly to camera
  Audio: Voice only, no music
  Text overlay: "{hook text}" -- top third, white on dark background, large

Shot 2: BODY BEAT 1 (3-8s)
  Framing: Medium shot
  Camera: Static or slight push-in
  Action: {what the speaker does}
  B-roll option: {alternative visual}
  Text overlay: "{key phrase}" -- center, medium

Shot 3: ...
```

### Shot Details to Include
- **Framing:** Close-up, medium, wide, over-shoulder, screen recording
- **Camera:** Static, pan, push-in, handheld
- **Action:** What the subject does during this shot
- **Audio:** Voice, music, sound effects, silence
- **Text overlay:** Exact text, position, timing
- **B-roll alternative:** What to show if not filming a person

---

## Step 3: B-Roll Suggestions

For each script section, suggest 3-5 B-roll options from the standard categories (see `reference/visual-styles.md`):

```
B-ROLL SUGGESTIONS

Hook section:
  - Phone notification close-up (results)
  - Laptop screen showing {relevant metric}
  - Hands typing / scrolling

Body section:
  - Dashboard or analytics screenshot
  - Calendar filling up with bookings
  - Team working / client session in progress

CTA section:
  - Landing page on phone screen
  - Finger tapping "Book Now" button
  - Happy client reaction shot
```

---

## Step 4: Text Overlay Specs

List every on-screen text element with exact specifications:

```
TEXT OVERLAYS

1. Hook text (0-3s)
   Text: "{exact text}"
   Position: Top third
   Size: Large (headline)
   Style: White, bold, dark semi-transparent background
   Duration: 3 seconds

2. Key stat (5-8s)
   Text: "{number or result}"
   Position: Center
   Size: Extra large
   Style: Accent color, bold
   Duration: 3 seconds

3. CTA text (final 3s)
   Text: "{cta text}"
   Position: Center
   Size: Large
   Style: White on brand color background
   Duration: Hold until end
```

---

## Step 5: Equipment and Setup Notes

```
SETUP

Aspect ratio: 9:16 (vertical) -- shoot on phone or rotate camera
Lighting: Natural window light or ring light on face
Audio: Built-in mic is fine for UGC feel, lapel mic for cleaner audio
Background: {clean/minimal or relevant context}
Wardrobe: {casual/professional depending on brand}

FILMING TIPS
- Film the hook 3 times with different energy levels
- Pause 2 seconds between each section (easier to edit)
- Look at the camera lens, not the screen
- Keep phone on Do Not Disturb
```

---

## Step 6: Thumbnail Concept

```
THUMBNAIL / FIRST FRAME

Concept: {what the first frame should look like}
Text overlay: "{3-5 word hook}" in large bold text
Subject: {face visible / product shot / screen capture}
Background: {clean / contextual}
Goal: Should communicate the topic without playing the video
```

---

## Step 7: Present the Full Brief

Combine everything into a clean, printable card:

```
============================================
CREATIVE BRIEF: {ad name}
Date: {today}
Angle: {angle} | Format: {format} | Framework: {framework}
Duration: {target length}
============================================

SCRIPT
------
{full script from Pipeline record}

SHOT LIST
---------
{numbered shots}

B-ROLL
------
{suggestions}

TEXT OVERLAYS
-------------
{specs}

SETUP
-----
{equipment and tips}

THUMBNAIL
---------
{concept}
============================================
```

Ask the user: **Approve this brief? (yes / edit / skip)**

---

## Step 8: Save to Pipeline

On approval:

```
Use Airtable MCP: update_records
  fields:
    Shot List: {shot list text}
    B-Roll Notes: {b-roll suggestions}
    Text Overlay Specs: {overlay specs}
    Status: "Briefed"
```

Print:
```
Brief saved to Pipeline. Status: Briefed.
Next step: Film it. After filming, run /ad-launch when you have the creative asset ready.
```

---

## CRITICAL RULES

1. **Every script beat must have a corresponding shot.** No gaps between script and shot list.
2. **Text overlays must have exact text, position, and timing.** The editor should not have to guess.
3. **B-roll must be practical.** Do not suggest shots that require equipment or locations the user does not have.
4. **Default to 9:16 vertical** unless the user specifies otherwise.
5. **The brief must be printable.** Someone should be able to print it and film from it without opening a computer.
6. **Keep it simple for solo operators.** If it is one person with a phone, the brief should reflect that.
