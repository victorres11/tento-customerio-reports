# Customer.io Weekly Reporting Script

This script generates a weekly report of Customer.io campaigns, showing email and SMS send counts for the most recent week.

## Setup

1. Create a virtual environment (if not already created):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Set your Customer.io API key as an environment variable:
   ```bash
   export CUSTOMER_IO_API_KEY="your-api-key-here"
   ```
   If not set, the script will use the default API key from the instructions.

## Usage

Run the script:
```bash
source venv/bin/activate
python weekly_report.py
```

## Output Format

The script generates a report in the following format:

```
Week of {date} customer.io reporting
Campaign 1 Name
Email 1 Name - 25 sent
Email 2 Name - 15 sent
SMS 1 Name - 15 sent

Campaign 2 Name
Email 1 Name - 10 sent
SMS 1 Name - 4 sent

Campaigns with no data:
Campaign 1 name
campaign 2 name
```

## How It Works

1. Fetches all campaigns from Customer.io
2. For each campaign, fetches all actions (emails and SMS)
3. For each email/SMS action, fetches metrics for the most recent week
4. Groups campaigns by whether they have send data
5. Formats and displays the report

## Notes

- Only campaigns with email or SMS actions that have sent data in the most recent week are shown in the main section
- Campaigns with no email/SMS actions or no send data are grouped separately
- The script uses the Customer.io API endpoints:
  - `/v1/campaigns` - Get all campaigns
  - `/v1/campaigns/{id}/actions` - Get actions for a campaign
  - `/v1/campaigns/{campaign_id}/actions/{action_id}/metrics` - Get metrics for an action

