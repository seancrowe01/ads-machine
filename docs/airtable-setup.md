# Manual Airtable Setup

If `/ads-setup` cannot create tables automatically, follow these steps to set up your Airtable base manually.

## Step 1: Create a New Base

1. Go to [airtable.com](https://airtable.com)
2. Click "Add a base" > "Start from scratch"
3. Name it "Ads Machine" (or whatever you prefer)
4. Note the Base ID from the URL: `https://airtable.com/{BASE_ID}/...`

## Step 2: Create the Competitors Table

Rename the default table to "Competitors" and add these fields:

| Field Name | Field Type | Options |
|-----------|-----------|---------|
| Name | Single line text | |
| Facebook Page ID | Single line text | |
| Website | URL | |
| Niche Tier | Single select | Direct, Adjacent, Aspirational |
| Status | Single select | Active, Paused, Archived |
| Total Ads | Number (integer) | |
| Last Scraped | Date | ISO format |
| Notes | Long text | |

## Step 3: Create the Ad Swipe File Table

Create a new table called "Ad Swipe File" with these fields:

| Field Name | Field Type | Options |
|-----------|-----------|---------|
| Ad Archive ID | Single line text | |
| Competitor | Single line text | |
| Page Name | Single line text | |
| Ad Library URL | URL | |
| Status | Single select | Active, Killed, Winner, Starred |
| Start Date | Date | ISO format |
| End Date | Date | ISO format |
| Days Active | Number (integer) | |
| Longevity Tier | Single select | Test (<30d), Performer (30-90d), Long-Runner (90d+) |
| Display Format | Single select | Video, Image, Carousel, DCO |
| Body Text | Long text | |
| Title | Single line text | |
| CTA Type | Single line text | |
| Link URL | URL | |
| Video URL | URL | |
| Image URL | URL | |
| Video Duration | Number (integer) | |
| Aspect Ratio | Single select | 9:16, 4:5, 1:1, 16:9, Other |
| Transcript | Long text | |
| Hook Video | Long text | |
| Hook Copy | Long text | |
| Word Count | Number (integer) | |
| Angle Category | Single select | Social Proof, Pain-to-Transformation, Tips/Education, Growth Problem, Profit Problem, Authority, Scarcity/Urgency, Behind-the-Scenes, Controversy, Comparison |
| Ad Format Type | Single select | UGC Testimonial, UGC Talking Head, Interview/Case Study, Motion Graphics, Static Image, Screenshot/Demo, Slideshow, Other |
| Visual Style | Long text | |
| Score | Number (integer) | |
| Scrape Date | Date | ISO format |
| Scrape Batch ID | Single line text | |
| Is Analyzed | Checkbox | |
| Winner Source | Single select | Competitor Intelligence, Own Performance |

## Step 4: Create the Ad Pipeline Table

Create a new table called "Ad Pipeline" with these fields:

| Field Name | Field Type | Options |
|-----------|-----------|---------|
| Name | Single line text | |
| Status | Single select | Idea, Scripted, Briefed, Filming, Launched, Active, Kill, Scale, Winner |
| Source Ad | Single line text | |
| Angle | Single select | (same as Swipe File Angle Category) |
| Format | Single select | Video UGC, Video Talking Head, Static, Carousel, Motion Graphics |
| Framework | Single select | PAS, AIDA, Story, Before/After, Controversy, I Tested X |
| Hook | Long text | |
| Script | Long text | |
| Primary Text | Long text | |
| Headline | Single line text | |
| Description | Long text | |
| CTA Type | Single line text | |
| Landing Page | URL | |
| Shot List | Long text | |
| B-Roll Notes | Long text | |
| Text Overlay Specs | Long text | |
| Campaign ID | Single line text | |
| Ad Set ID | Single line text | |
| Ad ID | Single line text | |
| Creative ID | Single line text | |
| Spend | Number (decimal, 2 places) | |
| Leads | Number (integer) | |
| CPL | Number (decimal, 2 places) | |
| CTR | Percent (2 decimal places) | |
| ROAS | Number (decimal, 2 places) | |
| Verdict | Single select | Kill, Watch, Scale, Winner |
| Created Date | Date | ISO format |
| Launch Date | Date | ISO format |
| Kill Date | Date | ISO format |

## Step 5: Note Your Table IDs

For each table, get the table ID:
1. Open the table in Airtable
2. Look at the URL: `https://airtable.com/{BASE_ID}/{TABLE_ID}/...`
3. The table ID starts with `tbl`

Update your `CLAUDE.md` with:
```
Airtable Base ID: {your base ID}
Competitors Table: {competitors table ID}
Ad Swipe File Table: {swipe file table ID}
Ad Pipeline Table: {pipeline table ID}
```

## Step 6: Add Your Competitors

Add at least 3-5 competitors to the Competitors table:
- Set Status to "Active"
- Include their Facebook Page ID (find it: Facebook page > About > Page Transparency > Page ID)
- Set their Niche Tier (Direct, Adjacent, or Aspirational)
