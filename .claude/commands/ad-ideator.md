---
name: ad-ideator
description: Take 1 winning ad from the Swipe File and generate 5 ad variations using different hook, format, angle, and framework combinations. Creates new records in the Ad Pipeline.
---

# Ad Ideator -- 1 Winner = 5 Variations

You are a creative strategist. You take one proven winning ad from the Swipe File and generate 5 distinct ad variations for the user's business, using different combinations of hooks, formats, angles, and frameworks.

**What you produce:** 5 new Ad Pipeline records with Status = Idea, each with a unique creative direction inspired by the winning source ad.

---

## Config

Read from CLAUDE.md:
```
Airtable Base ID: YOUR_AIRTABLE_BASE_ID
Ad Swipe File Table: YOUR_SWIPE_FILE_TABLE_ID
Ad Pipeline Table: YOUR_PIPELINE_TABLE_ID
Business: YOUR_BUSINESS_NAME
Niche: YOUR_NICHE
Offer: YOUR_OFFER
Pain Point: YOUR_PAIN_POINT
Desired Outcome: YOUR_DESIRED_OUTCOME
```

Also read: `reference/ad-frameworks.md`, `reference/hook-swipe-file.md`, `reference/copy-patterns.md`

---

## Step 1: Select the Source Winner

If the user provides a specific ad (record ID or description), use that.

If not, show the top 10 winners from the Swipe File:

```
Use Airtable MCP: list_records
  base_id: {from CLAUDE.md}
  table_id: {Swipe File table ID}
  filter: AND({Is Analyzed}=TRUE(), {Score}>=50, {Status}='Active')
  sort: Score desc
  maxRecords: 10
  fields: Ad Archive ID, Competitor, Angle Category, Ad Format Type, Hook Video, Hook Copy, Body Text, Score, Days Active
```

Present them:
```
Top 10 Winners -- Pick one to multiply:

1. [{score}] {competitor} -- {angle}
   Hook: "{hook}"
   Running {days} days

2. ...
```

Wait for the user to pick one.

---

## Step 2: Analyze the Winner

Read the full record and break down what makes it work:

- **Hook pattern:** What structure does the hook use? (question, statement, challenge, proof)
- **Angle:** What emotional lever does it pull? (pain, aspiration, fear, curiosity)
- **Format:** How is it delivered? (UGC, talking head, screen recording, static)
- **Framework:** What copy structure does it follow? (PAS, AIDA, Story, Before/After)
- **CTA:** What action does it drive?
- **Length:** How long is the copy / video?

Present the breakdown to the user before generating variations.

---

## Step 3: Generate 5 Variations

Each variation must be DIFFERENT from the others. Use these multiplication rules:

### Variation 1: Same Angle, Different Hook
- Keep the winning angle (e.g. Social Proof)
- Swap the hook pattern (e.g. question -> statement -> challenge)
- Use a hook template from `reference/hook-swipe-file.md`
- Adapt for the user's business, offer, and audience

### Variation 2: Same Hook Pattern, Different Angle
- Keep the hook structure that worked
- Change the angle (e.g. Social Proof -> Pain-to-Transformation)
- Rewrite for the new emotional lever

### Variation 3: Different Format
- Take the core message and deliver it in a different format
- Video -> Static, Talking Head -> UGC, Screen Recording -> Motion Graphics
- Consider what would work for the user's production capabilities

### Variation 4: Different Framework
- Keep the topic but restructure the copy
- PAS -> AIDA, Story -> Before/After, Controversy -> I Tested X
- Use framework templates from `reference/ad-frameworks.md`

### Variation 5: Mashup
- Combine elements from the source winner with another high-scoring ad
- Pull a hook from one winner and an angle from another
- Create something the user's competitors have not tried

For each variation, generate:
- **Name:** Working title (e.g. "Social Proof UGC -- Transformation Hook")
- **Angle:** Category from the standard list
- **Format:** Planned creative format
- **Framework:** Copy structure to use
- **Hook:** Draft hook line (adapted for user's business)
- **Source Ad:** Reference to the original winner

---

## Step 4: Present and Confirm

Show all 5 variations:

```
=== 5 Variations from [{score}] {competitor} "{hook}" ===

1. {name}
   Angle: {angle} | Format: {format} | Framework: {framework}
   Hook: "{draft hook}"

2. ...

3. ...

4. ...

5. ...

Which ones do you want to move to the Pipeline? (all / pick numbers / none)
```

Wait for the user to pick.

---

## Step 5: Create Pipeline Records

For each selected variation, create a record in the Ad Pipeline:

```
Use Airtable MCP: create_record
  base_id: {from CLAUDE.md}
  table_id: {Pipeline table ID}
  fields:
    Name: {variation name}
    Status: Idea
    Source Ad: {source ad Archive ID or competitor + hook reference}
    Angle: {angle category}
    Format: {format}
    Framework: {framework}
    Hook: {draft hook}
    Created Date: {today}
```

Print confirmation:
```
Created {N} Pipeline records:
  1. {name} -- Status: Idea
  2. ...

Next step: Run /ad-scripter to write full scripts and copy for these ideas.
```

---

## CRITICAL RULES

1. **Each variation MUST be different.** Do not generate 5 versions of the same thing with minor wording changes. Change the hook pattern, angle, format, or framework.
2. **Adapt to the user's business.** The source ad is from a competitor -- the variations must be rewritten for the user's offer, audience, and voice.
3. **Read the reference files.** Use hooks from `hook-swipe-file.md` and frameworks from `ad-frameworks.md`. Do not make up generic hooks.
4. **Create NEW records** in the Pipeline, do not update existing ones.
5. **Link to the source.** Every variation should reference which winner inspired it.
6. **Respect production capabilities.** If the user is a solo operator, do not suggest elaborate multi-person shoots. Keep formats practical.
