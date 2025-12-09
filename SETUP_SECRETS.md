# Setting Up GitHub Secrets

Your repository is created! Now you need to set up the secrets for email delivery.

## Repository URL
https://github.com/victorres11/tento-customerio-reports

## Secrets Already Set
✅ `CUSTOMER_IO_API_KEY` - Already configured

## Secrets You Need to Set

### Option 1: Using GitHub CLI (Recommended)

```bash
# Set your email address
gh secret set REPORT_EMAIL_TO --repo victorres11/tento-customerio-reports
# When prompted, enter your email address

# Set SendGrid API key (if you have one)
gh secret set SENDGRID_API_KEY --repo victorres11/tento-customerio-reports
# When prompted, enter your SendGrid API key
```

### Option 2: Using GitHub Web UI

1. Go to: https://github.com/victorres11/tento-customerio-reports/settings/secrets/actions
2. Click "New repository secret"
3. Add these secrets:

   **REPORT_EMAIL_TO**
   - Name: `REPORT_EMAIL_TO`
   - Value: Your email address (e.g., `your-email@example.com`)

   **SENDGRID_API_KEY** (if using SendGrid)
   - Name: `SENDGRID_API_KEY`
   - Value: Your SendGrid API key

## Email Service Options

### Option A: SendGrid (Recommended - Free tier available)
1. Sign up at https://sendgrid.com
2. Create an API key in Settings → API Keys
3. Add the API key as `SENDGRID_API_KEY` secret

### Option B: Gmail (Alternative)
If you prefer Gmail, you'll need to:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Update the workflow file to use Gmail settings (see below)

To use Gmail instead, modify `.github/workflows/weekly-report.yml`:
- Replace the SendGrid step with the Gmail configuration
- Add secrets: `GMAIL_USERNAME` and `GMAIL_APP_PASSWORD`

### Option C: No Email (Use GitHub Issues)
If you don't want to set up email, the workflow will create a GitHub Issue if email fails.

## Test the Workflow

Once secrets are set:

1. Go to: https://github.com/victorres11/tento-customerio-reports/actions
2. Click on "Customer.io Weekly Report" workflow
3. Click "Run workflow" → "Run workflow" (manual trigger)
4. Watch it run and check your email!

## Schedule

The workflow runs automatically every Monday at 9:00 AM UTC.

To change the schedule, edit `.github/workflows/weekly-report.yml` and modify the cron expression:
- Current: `'0 9 * * 1'` (Monday 9 AM UTC)
- Example: `'0 14 * * 1'` (Monday 2 PM UTC = 9 AM EST)

