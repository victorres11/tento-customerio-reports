# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Customer.io weekly reporting automation tool that generates reports of campaign activity (email and SMS sends) and delivers them to Slack via GitHub Actions. The report runs every Wednesday at 9:15 AM UTC.

## Key Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the script locally (text output)
export CUSTOMER_IO_API_KEY="your-api-key"
python weekly_report.py

# Generate JSON output (for integration testing)
python weekly_report.py --json
```

### Testing GitHub Actions Workflow
The workflow can be manually triggered from the GitHub Actions UI, which is useful for testing changes before the scheduled run.

## Architecture

### Core Components

1. **weekly_report.py** - Main Python script
   - `get_all_campaigns()`: Fetches all campaigns from Customer.io API
   - `get_campaign_actions(campaign_id)`: Fetches all actions for a campaign using `limit=1000` parameter to avoid pagination
   - `get_action_metrics(campaign_id, action_id, action_type)`: Fetches weekly metrics for email/SMS actions only
   - `generate_weekly_report(output_format)`: Orchestrates the report generation
   - Supports both `text` (human-readable) and `json` (structured) output formats

2. **.github/workflows/weekly-report.yml** - GitHub Actions workflow
   - Runs on schedule (Wednesday 9:15 AM UTC) and manual trigger
   - Executes Python script twice: once for JSON output, once for text
   - Formats report using Slack Block Kit format with rich formatting
   - Implements fallback mechanisms: if Slack formatting fails, uses plain text; if Slack fails entirely, creates a GitHub issue

### Data Flow

1. Script fetches all campaigns from Customer.io
2. For each campaign, fetches all actions (using single API call with `limit=1000`)
3. For each email/SMS action, fetches weekly metrics
4. Deduplicates actions by action ID (important: prevents duplicate reporting)
5. Groups results into "campaigns with activity" and "campaigns without activity"
6. Outputs in requested format (text or JSON)
7. GitHub Actions formats JSON as Slack Block Kit and delivers to Slack

### Key Architectural Decisions

- **Single API call per campaign**: Uses `limit=1000` parameter instead of pagination to minimize API calls and improve performance
- **Action deduplication**: Campaign actions are deduplicated by action ID to prevent duplicate entries in reports
- **Only email/SMS tracking**: Filters for action types "email" and "twilio" (SMS) - other action types are ignored
- **Weekly metrics**: Uses `period=weeks` and `steps=1` to get the most recent week's data
- **Robust error handling**: Multiple fallback mechanisms ensure reports are delivered even if parts fail

## Customer.io API Integration

### Endpoints Used
- `GET /v1/campaigns` - Fetch all campaigns
- `GET /v1/campaigns/{id}/actions?limit=1000` - Fetch all actions for a campaign
- `GET /v1/campaigns/{campaign_id}/actions/{action_id}/metrics` - Get metrics for specific action

### Authentication
Uses Bearer token authentication with API key from `CUSTOMER_IO_API_KEY` environment variable.

### Important Notes
- The script fetches up to 1000 actions per campaign. If a campaign has more, only the first 1000 are processed (rare edge case)
- Metrics endpoint uses type parameter: "email" for email actions, "sms" for twilio actions
- The "created" metric in the series represents sent count

## Environment Variables & Secrets

Required secrets (configured in GitHub repository settings):
- `CUSTOMER_IO_API_KEY`: Customer.io API bearer token
- `SLACK_WEBHOOK_URL`: Slack incoming webhook URL

For local development, set `CUSTOMER_IO_API_KEY` as an environment variable.

## Slack Integration

The workflow creates rich formatted reports using Slack Block Kit with:
- Header with week start date
- Campaigns grouped by activity status
- Individual email and SMS action details with send counts
- Summary footer with campaign statistics
- Fallback to plain text if Block Kit formatting fails

## Schedule Modification

To change the report schedule, edit the cron expression in `.github/workflows/weekly-report.yml`:
- Current: `'15 9 * * 3'` (Wednesday 9:15 AM UTC)
- Format: `minute hour day-of-month month day-of-week` (0=Sunday)

## Common Issues

### Duplicate Actions in Report
The script includes deduplication logic by action ID. If seeing duplicates, check that deduplication in `weekly_report.py` is working correctly.

### Infinite Pagination Loops
Fixed by using `limit=1000` parameter to fetch all actions in a single call instead of paginating. The script warns if a campaign has more than 1000 actions.

### Metrics Not Appearing
Verify the action type is "email" or "twilio" - other action types are intentionally filtered out.
