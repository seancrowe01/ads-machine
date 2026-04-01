# MCP Server Configs

These are templates for connecting Claude Code to external tools via MCP (Model Context Protocol).

The `/ads-setup` wizard handles this automatically. If you need to configure manually:

## Required
- **airtable.json** — Pipeline database (swipe file, ad records, competitors)
- **apify.json** — Meta Ad Library scraping

## Required for Ad Management
- **meta-ads.json** — Campaign creation, performance data, ad management

## Optional
- **slack.json** — Daily alerts for new competitor ads and kill/scale decisions
- **n8n.json** — Automation and cron jobs (daily poller, weekly reports)

## Manual Setup

1. Copy the relevant JSON file
2. Replace `${VARIABLE}` placeholders with your actual values from `.env`
3. Merge into your Claude Code MCP config (usually `~/.claude/.mcp.json` or project `.mcp.json`)

Or just run `/ads-setup` and it handles everything.
