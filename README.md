# Customer.io Weekly Reporting

Automated weekly reporting for Customer.io campaigns, delivered to Slack via GitHub Actions.

## Overview

This repository contains a Python script that generates weekly reports of Customer.io campaign activity, including email and SMS send counts. The report is automatically generated every Wednesday at 9:15 AM UTC and delivered to a Slack channel via GitHub Actions.

## Features

- 📊 Weekly campaign activity reports
- 📧 Email and SMS send tracking
- 💬 Automated Slack delivery
- ⚡ Fast execution (single API call per campaign)
- 🔒 Secure (API keys stored as GitHub secrets)

## Repository Structure

- `weekly_report.py` - Main Python script that generates the report
- `.github/workflows/weekly-report.yml` - GitHub Actions workflow configuration
- `requirements.txt` - Python dependencies
- `SETUP.md` - Setup instructions for GitHub secrets

## How It Works

1. **GitHub Actions** triggers the workflow every Wednesday at 9:15 AM UTC
2. **Python Script** fetches all campaigns and their actions from Customer.io API
3. **Metrics Collection** retrieves send counts for the most recent week
4. **Formatting** creates a nicely formatted report using Slack Block Kit
5. **Delivery** sends the report to your configured Slack channel

## Setup

See [SETUP.md](SETUP.md) for detailed setup instructions, including:
- Creating a Slack webhook
- Configuring GitHub secrets
- Testing the workflow

## Local Development

To run the script locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export CUSTOMER_IO_API_KEY="your-api-key"

# Run the script
python weekly_report.py

# Or generate JSON output
python weekly_report.py --json
```

## Report Format

The report includes:
- **Campaigns with Activity**: Shows campaigns with email/SMS sends, including:
  - Campaign name
  - Total sent count (emails + SMS)
  - Individual email actions with send counts
  - Individual SMS actions with send counts
- **Campaigns with No Activity**: Lists campaigns with no sends in the reporting period

## Schedule

- **Frequency**: Weekly
- **Day**: Wednesday
- **Time**: 9:15 AM UTC
- **Manual Trigger**: Available via GitHub Actions UI

To change the schedule, edit `.github/workflows/weekly-report.yml` and modify the cron expression.

## API Endpoints Used

- `GET /v1/campaigns` - Fetch all campaigns
- `GET /v1/campaigns/{id}/actions?limit=1000` - Fetch all actions for a campaign
- `GET /v1/campaigns/{campaign_id}/actions/{action_id}/metrics` - Get metrics for an action

## Requirements

- Python 3.11+
- `requests` library
- Customer.io API key
- Slack webhook URL

## License

This project is for internal use.
