"""
Meta Ads MCP Server
Full-suite MCP server for managing Meta (Facebook) Ads via the Marketing API.
Built with FastMCP. Requires META_ACCESS_TOKEN and META_AD_ACCOUNT_ID env vars.

COMPLIANCE NOTE:
- Read-only tools (insights, list operations) are safe with any valid token
- Write tools (create/update) require your app to have passed Meta App Review
- See reference/compliance.md before using write operations
- Rate limit: 200 calls/hour per user token
"""

import os
import json
import httpx
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from mcp.server.fastmcp import FastMCP, Context

# --- Config -----------------------------------------------------------------

API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
CHARACTER_LIMIT = 25000

ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
AD_ACCOUNT_ID = os.environ.get("META_AD_ACCOUNT_ID", "")


# --- Lifespan: shared httpx client -----------------------------------------

@dataclass
class AppContext:
    client: httpx.AsyncClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        yield AppContext(client=client)


mcp = FastMCP("meta_ads_mcp", lifespan=app_lifespan)


# --- Helpers ----------------------------------------------------------------

def _params(**kwargs) -> dict:
    """Build query params, always including access_token."""
    p = {"access_token": ACCESS_TOKEN}
    p.update({k: v for k, v in kwargs.items() if v is not None})
    return p


def _truncate(text: str) -> str:
    if len(text) <= CHARACTER_LIMIT:
        return text
    return text[:CHARACTER_LIMIT] + "\n\n[Truncated. Use filters/pagination to narrow results.]"


async def _get(ctx: Context, path: str, params: dict | None = None) -> dict:
    client: httpx.AsyncClient = ctx.request_context.lifespan_context.client
    url = f"{BASE_URL}/{path}"
    resp = await client.get(url, params=params or _params())
    resp.raise_for_status()
    return resp.json()


async def _post(ctx: Context, path: str, data: dict) -> dict:
    client: httpx.AsyncClient = ctx.request_context.lifespan_context.client
    url = f"{BASE_URL}/{path}"
    data["access_token"] = ACCESS_TOKEN
    resp = await client.post(url, data=data)
    resp.raise_for_status()
    return resp.json()


def _format_error(e: httpx.HTTPStatusError) -> str:
    try:
        err = e.response.json().get("error", {})
        return f"Meta API Error {err.get('code', '')}: {err.get('message', str(e))}"
    except Exception:
        return f"HTTP {e.response.status_code}: {str(e)}"


# --- TOOL 1: List Campaigns ------------------------------------------------

@mcp.tool(
    name="meta_list_campaigns",
    description="List all campaigns in the ad account. Returns campaign ID, name, status, objective, daily/lifetime budget.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def list_campaigns(
    ctx: Context,
    status_filter: str | None = None,
    limit: int = 25,
    after: str | None = None,
) -> str:
    """
    List campaigns.

    Args:
        status_filter: Filter by status (ACTIVE, PAUSED, ARCHIVED). Leave empty for all.
        limit: Max campaigns to return (1-100).
        after: Pagination cursor from previous response.
    """
    try:
        fields = "id,name,status,objective,daily_budget,lifetime_budget,budget_remaining,created_time,start_time,stop_time"
        params = _params(fields=fields, limit=str(min(limit, 100)))
        if after:
            params["after"] = after
        if status_filter:
            params["filtering"] = json.dumps([{"field": "effective_status", "operator": "IN", "value": [status_filter]}])

        result = await _get(ctx, f"{AD_ACCOUNT_ID}/campaigns", params)
        campaigns = result.get("data", [])
        paging = result.get("paging", {})
        next_cursor = paging.get("cursors", {}).get("after")

        lines = [f"# Campaigns ({len(campaigns)} returned)\n"]
        for c in campaigns:
            budget = c.get("daily_budget") or c.get("lifetime_budget") or "Not set"
            lines.append(f"- **{c['name']}** (`{c['id']}`)")
            lines.append(f"  Status: {c.get('status', 'N/A')} | Objective: {c.get('objective', 'N/A')} | Budget: {budget}")

        if next_cursor:
            lines.append(f"\n*More available. Use after cursor: `{next_cursor}`*")

        return _truncate("\n".join(lines))
    except httpx.HTTPStatusError as e:
        return _format_error(e)


# --- TOOL 2: List Ad Sets --------------------------------------------------

@mcp.tool(
    name="meta_list_adsets",
    description="List ad sets. Optionally filter by campaign ID. Returns targeting, budget, schedule, status.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def list_adsets(
    ctx: Context,
    campaign_id: str | None = None,
    limit: int = 25,
    after: str | None = None,
) -> str:
    """
    List ad sets.

    Args:
        campaign_id: Filter to a specific campaign. Leave empty for all ad sets in account.
        limit: Max results (1-100).
        after: Pagination cursor.
    """
    try:
        fields = "id,name,status,campaign_id,daily_budget,lifetime_budget,bid_strategy,billing_event,optimization_goal,targeting,start_time,end_time"
        params = _params(fields=fields, limit=str(min(limit, 100)))
        if after:
            params["after"] = after

        path = f"{campaign_id}/adsets" if campaign_id else f"{AD_ACCOUNT_ID}/adsets"
        result = await _get(ctx, path, params)
        adsets = result.get("data", [])
        paging = result.get("paging", {})
        next_cursor = paging.get("cursors", {}).get("after")

        lines = [f"# Ad Sets ({len(adsets)} returned)\n"]
        for a in adsets:
            budget = a.get("daily_budget") or a.get("lifetime_budget") or "Not set"
            lines.append(f"- **{a['name']}** (`{a['id']}`)")
            lines.append(f"  Status: {a.get('status')} | Campaign: {a.get('campaign_id')} | Budget: {budget}")
            lines.append(f"  Bid: {a.get('bid_strategy', 'N/A')} | Optimization: {a.get('optimization_goal', 'N/A')}")
            targeting = a.get("targeting", {})
            if targeting:
                geo = targeting.get("geo_locations", {}).get("countries", [])
                age_min = targeting.get("age_min", "")
                age_max = targeting.get("age_max", "")
                lines.append(f"  Targeting: Ages {age_min}-{age_max} | Countries: {', '.join(geo) if geo else 'N/A'}")

        if next_cursor:
            lines.append(f"\n*More available. Use after cursor: `{next_cursor}`*")

        return _truncate("\n".join(lines))
    except httpx.HTTPStatusError as e:
        return _format_error(e)


# --- TOOL 3: List Ads ------------------------------------------------------

@mcp.tool(
    name="meta_list_ads",
    description="List ads. Optionally filter by ad set ID. Returns ad name, status, creative details.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def list_ads(
    ctx: Context,
    adset_id: str | None = None,
    limit: int = 25,
    after: str | None = None,
) -> str:
    """
    List ads.

    Args:
        adset_id: Filter to a specific ad set. Leave empty for all ads in account.
        limit: Max results (1-100).
        after: Pagination cursor.
    """
    try:
        fields = "id,name,status,adset_id,campaign_id,creative{id,name,title,body,image_url,thumbnail_url,call_to_action_type}"
        params = _params(fields=fields, limit=str(min(limit, 100)))
        if after:
            params["after"] = after

        path = f"{adset_id}/ads" if adset_id else f"{AD_ACCOUNT_ID}/ads"
        result = await _get(ctx, path, params)
        ads = result.get("data", [])
        paging = result.get("paging", {})
        next_cursor = paging.get("cursors", {}).get("after")

        lines = [f"# Ads ({len(ads)} returned)\n"]
        for ad in ads:
            lines.append(f"- **{ad['name']}** (`{ad['id']}`)")
            lines.append(f"  Status: {ad.get('status')} | Ad Set: {ad.get('adset_id')} | Campaign: {ad.get('campaign_id')}")
            creative = ad.get("creative", {})
            if creative:
                lines.append(f"  Creative: {creative.get('name', 'N/A')} | CTA: {creative.get('call_to_action_type', 'N/A')}")

        if next_cursor:
            lines.append(f"\n*More available. Use after cursor: `{next_cursor}`*")

        return _truncate("\n".join(lines))
    except httpx.HTTPStatusError as e:
        return _format_error(e)


# --- TOOLS 4-7: Insights ---------------------------------------------------

INSIGHT_FIELDS = (
    "spend,impressions,clicks,cpc,cpm,ctr,reach,frequency,"
    "actions,cost_per_action_type,action_values,purchase_roas,"
    "conversions,cost_per_conversion"
)

VALID_BREAKDOWNS = {"age", "gender", "placement", "device_platform", "country", "region"}
VALID_DATE_PRESETS = {
    "today", "yesterday", "this_month", "last_month",
    "this_quarter", "last_3d", "last_7d", "last_14d",
    "last_28d", "last_30d", "last_90d", "maximum",
}


def _format_insights(data: list, level: str) -> str:
    lines = [f"# {level} Insights\n"]
    for row in data:
        name = row.get("campaign_name") or row.get("adset_name") or row.get("ad_name") or row.get("account_name", "Account")
        lines.append(f"## {name}")
        lines.append(f"- **Spend**: ${row.get('spend', '0')}")
        lines.append(f"- **Impressions**: {row.get('impressions', '0')}")
        lines.append(f"- **Clicks**: {row.get('clicks', '0')}")
        lines.append(f"- **CPC**: ${row.get('cpc', '0')}")
        lines.append(f"- **CPM**: ${row.get('cpm', '0')}")
        lines.append(f"- **CTR**: {row.get('ctr', '0')}%")
        lines.append(f"- **Reach**: {row.get('reach', '0')}")
        lines.append(f"- **Frequency**: {row.get('frequency', '0')}")

        roas = row.get("purchase_roas")
        if roas and isinstance(roas, list):
            for r in roas:
                lines.append(f"- **ROAS ({r.get('action_type', '')})**: {r.get('value', 'N/A')}")

        actions = row.get("actions")
        if actions and isinstance(actions, list):
            lines.append("- **Actions**:")
            for a in actions[:10]:
                lines.append(f"  - {a.get('action_type', '')}: {a.get('value', '')}")

        cpa = row.get("cost_per_action_type")
        if cpa and isinstance(cpa, list):
            lines.append("- **Cost per Action**:")
            for c in cpa[:10]:
                lines.append(f"  - {c.get('action_type', '')}: ${c.get('value', '')}")

        for dim in VALID_BREAKDOWNS:
            if dim in row:
                lines.append(f"- **{dim}**: {row[dim]}")

        lines.append(f"- Date: {row.get('date_start', '')} to {row.get('date_stop', '')}")
        lines.append("")

    return _truncate("\n".join(lines))


async def _get_insights(
    ctx: Context,
    path: str,
    level: str,
    date_preset: str | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
    breakdowns: str | None = None,
    limit: int = 25,
    after: str | None = None,
) -> str:
    try:
        params = _params(fields=INSIGHT_FIELDS, limit=str(min(limit, 100)), level=level)
        if date_preset and date_preset in VALID_DATE_PRESETS:
            params["date_preset"] = date_preset
        elif date_start and date_end:
            params["time_range"] = json.dumps({"since": date_start, "until": date_end})
        else:
            params["date_preset"] = "last_7d"

        if breakdowns:
            valid = [b.strip() for b in breakdowns.split(",") if b.strip() in VALID_BREAKDOWNS]
            if valid:
                params["breakdowns"] = ",".join(valid)

        if after:
            params["after"] = after

        result = await _get(ctx, f"{path}/insights", params)
        data = result.get("data", [])

        if not data:
            return "No insights data found for the selected period."

        output = _format_insights(data, level.title())
        paging = result.get("paging", {})
        next_cursor = paging.get("cursors", {}).get("after")
        if next_cursor:
            output += f"\n*More available. Use after cursor: `{next_cursor}`*"
        return output
    except httpx.HTTPStatusError as e:
        return _format_error(e)


@mcp.tool(
    name="meta_account_insights",
    description="Get account-level performance insights. Supports date ranges, breakdowns (age, gender, placement, device_platform).",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def account_insights(
    ctx: Context,
    date_preset: str | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
    breakdowns: str | None = None,
    limit: int = 25,
    after: str | None = None,
) -> str:
    """
    Get account-level insights.

    Args:
        date_preset: Shortcut like last_7d, last_30d, this_month, yesterday, maximum.
        date_start: Start date YYYY-MM-DD (use with date_end instead of date_preset).
        date_end: End date YYYY-MM-DD.
        breakdowns: Comma-separated: age, gender, placement, device_platform, country.
        limit: Max rows.
        after: Pagination cursor.
    """
    return await _get_insights(ctx, AD_ACCOUNT_ID, "account", date_preset, date_start, date_end, breakdowns, limit, after)


@mcp.tool(
    name="meta_campaign_insights",
    description="Get performance insights for campaigns. Filter by campaign ID or get all. Supports date ranges and breakdowns.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def campaign_insights(
    ctx: Context,
    campaign_id: str | None = None,
    date_preset: str | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
    breakdowns: str | None = None,
    limit: int = 25,
    after: str | None = None,
) -> str:
    """
    Get campaign-level insights.

    Args:
        campaign_id: Specific campaign ID. Leave empty for all campaigns.
        date_preset: Shortcut like last_7d, last_30d, this_month, yesterday.
        date_start: Start date YYYY-MM-DD.
        date_end: End date YYYY-MM-DD.
        breakdowns: Comma-separated: age, gender, placement, device_platform.
        limit: Max rows.
        after: Pagination cursor.
    """
    path = campaign_id if campaign_id else AD_ACCOUNT_ID
    return await _get_insights(ctx, path, "campaign", date_preset, date_start, date_end, breakdowns, limit, after)


@mcp.tool(
    name="meta_adset_insights",
    description="Get performance insights for ad sets. Filter by ad set ID or get all. Supports date ranges and breakdowns.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def adset_insights(
    ctx: Context,
    adset_id: str | None = None,
    date_preset: str | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
    breakdowns: str | None = None,
    limit: int = 25,
    after: str | None = None,
) -> str:
    """
    Get ad set-level insights.

    Args:
        adset_id: Specific ad set ID. Leave empty for all ad sets.
        date_preset: Shortcut like last_7d, last_30d, this_month, yesterday.
        date_start: Start date YYYY-MM-DD.
        date_end: End date YYYY-MM-DD.
        breakdowns: Comma-separated: age, gender, placement, device_platform.
        limit: Max rows.
        after: Pagination cursor.
    """
    path = adset_id if adset_id else AD_ACCOUNT_ID
    return await _get_insights(ctx, path, "adset", date_preset, date_start, date_end, breakdowns, limit, after)


@mcp.tool(
    name="meta_ad_insights",
    description="Get performance insights for individual ads. Filter by ad ID or get all. Supports date ranges and breakdowns.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def ad_insights(
    ctx: Context,
    ad_id: str | None = None,
    date_preset: str | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
    breakdowns: str | None = None,
    limit: int = 25,
    after: str | None = None,
) -> str:
    """
    Get ad-level insights.

    Args:
        ad_id: Specific ad ID. Leave empty for all ads.
        date_preset: Shortcut like last_7d, last_30d, this_month, yesterday.
        date_start: Start date YYYY-MM-DD.
        date_end: End date YYYY-MM-DD.
        breakdowns: Comma-separated: age, gender, placement, device_platform.
        limit: Max rows.
        after: Pagination cursor.
    """
    path = ad_id if ad_id else AD_ACCOUNT_ID
    return await _get_insights(ctx, path, "ad", date_preset, date_start, date_end, breakdowns, limit, after)


# --- TOOL 8: Create Campaign -----------------------------------------------
# WARNING: Write operation. Requires Meta App Review with ads_management permission.

@mcp.tool(
    name="meta_create_campaign",
    description="Create a new campaign. WARNING: Write operation -- requires approved Meta app. See reference/compliance.md.",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
)
async def create_campaign(
    ctx: Context,
    name: str,
    objective: str,
    status: str = "PAUSED",
    daily_budget: str | None = None,
    lifetime_budget: str | None = None,
    special_ad_categories: str = "NONE",
) -> str:
    """
    Create a campaign.

    Args:
        name: Campaign name.
        objective: OUTCOME_AWARENESS, OUTCOME_ENGAGEMENT, OUTCOME_LEADS, OUTCOME_SALES, OUTCOME_TRAFFIC.
        status: ACTIVE or PAUSED (default PAUSED for safety).
        daily_budget: Daily budget in cents (e.g. "5000" = $50.00).
        lifetime_budget: Lifetime budget in cents.
        special_ad_categories: Use "NONE" for no special category. Or "HOUSING", "EMPLOYMENT", "CREDIT".
    """
    try:
        data = {
            "name": name,
            "objective": objective,
            "status": status,
            "special_ad_categories": special_ad_categories,
        }
        if daily_budget:
            data["daily_budget"] = daily_budget
        if lifetime_budget:
            data["lifetime_budget"] = lifetime_budget

        result = await _post(ctx, f"{AD_ACCOUNT_ID}/campaigns", data)
        return f"Campaign created successfully.\n- **ID**: `{result.get('id')}`\n- **Name**: {name}\n- **Status**: {status}"
    except httpx.HTTPStatusError as e:
        return _format_error(e)


# --- TOOL 9: Update Campaign -----------------------------------------------

@mcp.tool(
    name="meta_update_campaign",
    description="Update an existing campaign. Change name, status (ACTIVE/PAUSED), or budget.",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def update_campaign(
    ctx: Context,
    campaign_id: str,
    name: str | None = None,
    status: str | None = None,
    daily_budget: str | None = None,
    lifetime_budget: str | None = None,
) -> str:
    """
    Update a campaign.

    Args:
        campaign_id: The campaign ID to update.
        name: New campaign name.
        status: ACTIVE or PAUSED.
        daily_budget: New daily budget in cents.
        lifetime_budget: New lifetime budget in cents.
    """
    try:
        data = {}
        if name:
            data["name"] = name
        if status:
            data["status"] = status
        if daily_budget:
            data["daily_budget"] = daily_budget
        if lifetime_budget:
            data["lifetime_budget"] = lifetime_budget

        if not data:
            return "No fields provided to update."

        result = await _post(ctx, campaign_id, data)
        return f"Campaign `{campaign_id}` updated successfully.\nUpdated fields: {', '.join(data.keys())}"
    except httpx.HTTPStatusError as e:
        return _format_error(e)


# --- TOOL 10: Create Ad Set ------------------------------------------------

@mcp.tool(
    name="meta_create_adset",
    description="Create a new ad set. WARNING: Write operation -- requires approved Meta app.",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
)
async def create_adset(
    ctx: Context,
    campaign_id: str,
    name: str,
    daily_budget: str,
    optimization_goal: str,
    billing_event: str = "IMPRESSIONS",
    bid_strategy: str = "LOWEST_COST_WITHOUT_CAP",
    targeting_countries: str = "US",
    targeting_age_min: int = 18,
    targeting_age_max: int = 65,
    targeting_genders: str | None = None,
    targeting_interests: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    status: str = "PAUSED",
    bid_amount: str | None = None,
) -> str:
    """
    Create an ad set.

    Args:
        campaign_id: Parent campaign ID.
        name: Ad set name.
        daily_budget: Daily budget in cents (e.g. "5000" = $50.00).
        optimization_goal: IMPRESSIONS, LINK_CLICKS, REACH, LANDING_PAGE_VIEWS, OFFSITE_CONVERSIONS, LEAD_GENERATION.
        billing_event: IMPRESSIONS (most common) or LINK_CLICKS.
        bid_strategy: LOWEST_COST_WITHOUT_CAP, LOWEST_COST_WITH_BID_CAP, COST_CAP.
        targeting_countries: Comma-separated country codes (e.g. "US,CA,GB").
        targeting_age_min: Minimum age (18-65).
        targeting_age_max: Maximum age (18-65).
        targeting_genders: "1" for male, "2" for female. Comma-separated for both. Leave empty for all.
        targeting_interests: JSON array of interest objects.
        start_time: ISO 8601 datetime.
        end_time: ISO 8601 datetime.
        status: ACTIVE or PAUSED (default PAUSED).
        bid_amount: Bid amount in cents (required for BID_CAP strategy).
    """
    try:
        countries = [c.strip() for c in targeting_countries.split(",")]
        targeting = {
            "geo_locations": {"countries": countries},
            "age_min": targeting_age_min,
            "age_max": targeting_age_max,
        }
        if targeting_genders:
            targeting["genders"] = [int(g.strip()) for g in targeting_genders.split(",")]
        if targeting_interests:
            targeting["flexible_spec"] = [{"interests": json.loads(targeting_interests)}]

        data = {
            "campaign_id": campaign_id,
            "name": name,
            "daily_budget": daily_budget,
            "optimization_goal": optimization_goal,
            "billing_event": billing_event,
            "bid_strategy": bid_strategy,
            "targeting": json.dumps(targeting),
            "status": status,
        }
        if start_time:
            data["start_time"] = start_time
        if end_time:
            data["end_time"] = end_time
        if bid_amount:
            data["bid_amount"] = bid_amount

        result = await _post(ctx, f"{AD_ACCOUNT_ID}/adsets", data)
        return f"Ad Set created successfully.\n- **ID**: `{result.get('id')}`\n- **Name**: {name}\n- **Campaign**: {campaign_id}\n- **Status**: {status}"
    except httpx.HTTPStatusError as e:
        return _format_error(e)


# --- TOOL 11: Update Ad Set ------------------------------------------------

@mcp.tool(
    name="meta_update_adset",
    description="Update an existing ad set. Change name, status, budget, targeting, or schedule.",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def update_adset(
    ctx: Context,
    adset_id: str,
    name: str | None = None,
    status: str | None = None,
    daily_budget: str | None = None,
    targeting_json: str | None = None,
    end_time: str | None = None,
    bid_amount: str | None = None,
) -> str:
    """
    Update an ad set.

    Args:
        adset_id: The ad set ID to update.
        name: New name.
        status: ACTIVE or PAUSED.
        daily_budget: New daily budget in cents.
        targeting_json: Full targeting JSON object to replace current targeting.
        end_time: New end time in ISO 8601.
        bid_amount: New bid amount in cents.
    """
    try:
        data = {}
        if name:
            data["name"] = name
        if status:
            data["status"] = status
        if daily_budget:
            data["daily_budget"] = daily_budget
        if targeting_json:
            data["targeting"] = targeting_json
        if end_time:
            data["end_time"] = end_time
        if bid_amount:
            data["bid_amount"] = bid_amount

        if not data:
            return "No fields provided to update."

        result = await _post(ctx, adset_id, data)
        return f"Ad Set `{adset_id}` updated successfully.\nUpdated fields: {', '.join(data.keys())}"
    except httpx.HTTPStatusError as e:
        return _format_error(e)


# --- TOOL 12: Create Ad ----------------------------------------------------

@mcp.tool(
    name="meta_create_ad",
    description="Create a new ad by linking an existing creative to an ad set. WARNING: Write operation.",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
)
async def create_ad(
    ctx: Context,
    adset_id: str,
    name: str,
    creative_id: str,
    status: str = "PAUSED",
) -> str:
    """
    Create an ad.

    Args:
        adset_id: Parent ad set ID.
        name: Ad name.
        creative_id: The creative ID to use.
        status: ACTIVE or PAUSED (default PAUSED).
    """
    try:
        data = {
            "adset_id": adset_id,
            "name": name,
            "creative": json.dumps({"creative_id": creative_id}),
            "status": status,
        }
        result = await _post(ctx, f"{AD_ACCOUNT_ID}/ads", data)
        return f"Ad created successfully.\n- **ID**: `{result.get('id')}`\n- **Name**: {name}\n- **Ad Set**: {adset_id}\n- **Status**: {status}"
    except httpx.HTTPStatusError as e:
        return _format_error(e)


# --- TOOL 13: Update Ad ----------------------------------------------------

@mcp.tool(
    name="meta_update_ad",
    description="Update an existing ad. Change name, status, or creative.",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def update_ad(
    ctx: Context,
    ad_id: str,
    name: str | None = None,
    status: str | None = None,
    creative_id: str | None = None,
) -> str:
    """
    Update an ad.

    Args:
        ad_id: The ad ID to update.
        name: New ad name.
        status: ACTIVE or PAUSED.
        creative_id: New creative ID to swap in.
    """
    try:
        data = {}
        if name:
            data["name"] = name
        if status:
            data["status"] = status
        if creative_id:
            data["creative"] = json.dumps({"creative_id": creative_id})

        if not data:
            return "No fields provided to update."

        result = await _post(ctx, ad_id, data)
        return f"Ad `{ad_id}` updated successfully.\nUpdated fields: {', '.join(data.keys())}"
    except httpx.HTTPStatusError as e:
        return _format_error(e)


# --- TOOL 14: List Custom Audiences ----------------------------------------

@mcp.tool(
    name="meta_list_audiences",
    description="List custom audiences in the ad account. Shows audience name, size, type, and status.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def list_audiences(
    ctx: Context,
    limit: int = 25,
    after: str | None = None,
) -> str:
    """
    List custom audiences.

    Args:
        limit: Max results (1-100).
        after: Pagination cursor.
    """
    try:
        fields = "id,name,subtype,approximate_count,delivery_status,description,time_created,time_updated"
        params = _params(fields=fields, limit=str(min(limit, 100)))
        if after:
            params["after"] = after

        result = await _get(ctx, f"{AD_ACCOUNT_ID}/customaudiences", params)
        audiences = result.get("data", [])
        paging = result.get("paging", {})
        next_cursor = paging.get("cursors", {}).get("after")

        lines = [f"# Custom Audiences ({len(audiences)} returned)\n"]
        for a in audiences:
            size = a.get("approximate_count", "Unknown")
            lines.append(f"- **{a['name']}** (`{a['id']}`)")
            lines.append(f"  Type: {a.get('subtype', 'N/A')} | Size: ~{size} | Status: {a.get('delivery_status', {}).get('status', 'N/A')}")

        if next_cursor:
            lines.append(f"\n*More available. Use after cursor: `{next_cursor}`*")

        return _truncate("\n".join(lines))
    except httpx.HTTPStatusError as e:
        return _format_error(e)


# --- TOOL 15: Create Custom Audience ---------------------------------------

@mcp.tool(
    name="meta_create_audience",
    description="Create a custom audience. Supports WEBSITE, CUSTOM (customer list), and ENGAGEMENT subtypes. WARNING: Write operation.",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
)
async def create_audience(
    ctx: Context,
    name: str,
    subtype: str,
    description: str = "",
    customer_file_source: str | None = None,
    rule: str | None = None,
    retention_days: int = 30,
    pixel_id: str | None = None,
) -> str:
    """
    Create a custom audience.

    Args:
        name: Audience name.
        subtype: WEBSITE, CUSTOM, ENGAGEMENT, LOOKALIKE, VIDEO.
        description: Audience description.
        customer_file_source: For CUSTOM subtype: USER_PROVIDED_ONLY, PARTNER_PROVIDED_ONLY, BOTH_USER_AND_PARTNER_PROVIDED.
        rule: JSON rule for WEBSITE audiences.
        retention_days: Days to retain audience members (WEBSITE). Default 30.
        pixel_id: Your Meta Pixel ID (for WEBSITE audiences).
    """
    try:
        data = {
            "name": name,
            "subtype": subtype,
            "description": description,
        }
        if subtype == "CUSTOM" and customer_file_source:
            data["customer_file_source"] = customer_file_source
        if subtype == "WEBSITE":
            if rule:
                data["rule"] = rule
            elif pixel_id:
                rule_obj = {
                    "inclusions": {
                        "operator": "or",
                        "rules": [{
                            "event_sources": [{"id": pixel_id, "type": "pixel"}],
                            "retention_seconds": retention_days * 86400,
                        }]
                    }
                }
                data["rule"] = json.dumps(rule_obj)

        result = await _post(ctx, f"{AD_ACCOUNT_ID}/customaudiences", data)
        return f"Custom Audience created successfully.\n- **ID**: `{result.get('id')}`\n- **Name**: {name}\n- **Subtype**: {subtype}"
    except httpx.HTTPStatusError as e:
        return _format_error(e)


# --- Run --------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
