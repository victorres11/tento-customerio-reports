# Setup Guide

This guide will help you set up the Customer.io weekly reporting workflow.

## Prerequisites

- A GitHub repository (already created: `victorres11/tento-customerio-reports`)
- A Customer.io account with API access
- A Slack workspace where you want to receive reports

## Step 1: Create a Slack Webhook

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Name it "Customer.io Reports" and select your workspace
4. Go to **"Incoming Webhooks"** in the left sidebar
5. Toggle **"Activate Incoming Webhooks"** to ON
6. Click **"Add New Webhook to Workspace"**
7. Select the channel where you want reports sent
8. Copy the Webhook URL (it will be a long URL starting with `https://hooks.slack.com/services/...`)

## Step 2: Configure GitHub Secrets

You need to set up two secrets in your GitHub repository:

### Option A: Using GitHub CLI (Recommended)

```bash
# Set your Customer.io API key
echo "YOUR_CUSTOMER_IO_API_KEY" | gh secret set CUSTOMER_IO_API_KEY --repo victorres11/tento-customerio-reports

# Set your Slack webhook URL
echo "YOUR_SLACK_WEBHOOK_URL" | gh secret set SLACK_WEBHOOK_URL --repo victorres11/tento-customerio-reports
```

### Option B: Using GitHub Web UI

1. Go to: https://github.com/victorres11/tento-customerio-reports/settings/secrets/actions
2. Click **"New repository secret"**
3. Add these secrets:

   **CUSTOMER_IO_API_KEY**
   - Name: `CUSTOMER_IO_API_KEY`
   - Value: Your Customer.io API key

   **SLACK_WEBHOOK_URL**
   - Name: `SLACK_WEBHOOK_URL`
   - Value: Your Slack webhook URL (from Step 1)

## Step 3: Test the Workflow

Once secrets are configured:

1. Go to: https://github.com/victorres11/tento-customerio-reports/actions
2. Click on **"Customer.io Weekly Report"** workflow
3. Click **"Run workflow"** → **"Run workflow"** (manual trigger)
4. Watch it run and check your Slack channel!

## Schedule

The workflow runs automatically every **Wednesday at 9:15 AM UTC**.

To change the schedule, edit `.github/workflows/weekly-report.yml` and modify the cron expression:
- Current: `'15 9 * * 3'` (Wednesday 9:15 AM UTC)
- Format: `minute hour day-of-month month day-of-week`

### Timezone Examples

- **9:15 AM EST** (UTC-5): `'15 14 * * 3'` (2:15 PM UTC)
- **9:15 AM PST** (UTC-8): `'15 17 * * 3'` (5:15 PM UTC)

## Troubleshooting

### Workflow Fails

- Check the workflow logs in GitHub Actions
- Verify both secrets are set correctly
- Ensure the Slack webhook URL is valid

### No Report in Slack

- Check if the workflow completed successfully
- Verify the Slack webhook URL secret is correct
- Check the "Send to Slack" step logs for errors

### Missing Actions in Report

- The script fetches up to 1000 actions per campaign
- If a campaign has more than 1000 actions, only the first 1000 will be included
- Check the workflow logs for any warnings

## Need Help?

If you encounter issues:
1. Check the workflow logs in GitHub Actions
2. Verify all secrets are configured correctly
3. Test the Slack webhook manually using curl

