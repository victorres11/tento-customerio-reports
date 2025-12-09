# Setting Up GitHub Secrets

Your repository is created! Now you need to set up the secret for Slack delivery.

## Repository URL
https://github.com/victorres11/tento-customerio-reports

## Secrets Already Set
✅ `CUSTOMER_IO_API_KEY` - Already configured

## Secrets You Need to Set

### Step 1: Create a Slack Webhook

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name it "Customer.io Reports" and select your workspace
4. Go to "Incoming Webhooks" in the left sidebar
5. Toggle "Activate Incoming Webhooks" to ON
6. Click "Add New Webhook to Workspace"
7. Select the channel where you want reports sent
8. Copy the Webhook URL (it will be a long URL starting with `https://hooks.slack.com/services/...`)

### Step 2: Add Slack Webhook to GitHub Secrets

#### Option A: Using GitHub CLI (Recommended)

```bash
# Set your Slack webhook URL
echo "YOUR_WEBHOOK_URL_HERE" | gh secret set SLACK_WEBHOOK_URL --repo victorres11/tento-customerio-reports
```

Replace `YOUR_WEBHOOK_URL_HERE` with the webhook URL you copied from Slack.

#### Option B: Using GitHub Web UI

1. Go to: https://github.com/victorres11/tento-customerio-reports/settings/secrets/actions
2. Click "New repository secret"
3. Add this secret:
   - **Name**: `SLACK_WEBHOOK_URL`
   - **Value**: Your Slack webhook URL (from Step 1)

## That's It!

Once you've set the `SLACK_WEBHOOK_URL` secret, the workflow will automatically send reports to your Slack channel every Monday at 9 AM UTC.

## Test the Workflow

Once secrets are set:

1. Go to: https://github.com/victorres11/tento-customerio-reports/actions
2. Click on "Customer.io Weekly Report" workflow
3. Click "Run workflow" → "Run workflow" (manual trigger)
4. Watch it run and check your Slack channel!

## Schedule

The workflow runs automatically every Monday at 9:00 AM UTC.

To change the schedule, edit `.github/workflows/weekly-report.yml` and modify the cron expression:
- Current: `'0 9 * * 1'` (Monday 9 AM UTC)
- Example: `'0 14 * * 1'` (Monday 2 PM UTC = 9 AM EST)

