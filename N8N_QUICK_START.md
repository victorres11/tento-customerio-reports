# n8n Integration - Quick Start Guide

## TL;DR - Get Started in 5 Minutes

### Option 1: Code (Python) Node (Recommended)

1. **In n8n, create a new workflow**
2. **Add Schedule Trigger node**
   - Set cron: `0 9 * * 1` (Mondays at 9 AM)
3. **Add Code (Python) node** - Run the report logic directly
   - Copy the Python code from the script (see Step 3 below)
4. **Add Code (JavaScript) node** to format the output
5. **Add Email/Slack node** to send report

**OR** use HTTP Request nodes (see Option 2)

### Option 2: Pure n8n with HTTP Request Nodes

Build the entire workflow using HTTP Request nodes (see `n8n_pure_workflow_example.md`)

---

## Detailed Setup: Code (Python) Node

### Step 1: Set Environment Variables in n8n

Go to n8n Settings → Environment Variables:
- `CUSTOMER_IO_API_KEY`: Your API key (get this from Customer.io settings)
- `REPORT_EMAIL_TO`: Email address for reports

### Step 2: Create Workflow

#### Node 1: Schedule Trigger
```
Type: Schedule Trigger
Cron: 0 9 * * 1
Description: Run every Monday at 9 AM
```

#### Node 2: Code (Python) - Generate Report

**Type**: Code  
**Language**: Python

Copy this code into the node:

```python
import requests
import json
import os
from datetime import datetime
from collections import defaultdict

# Get API key from environment
api_key = os.getenv('CUSTOMER_IO_API_KEY')
if not api_key:
    raise ValueError("CUSTOMER_IO_API_KEY environment variable is required")
base_url = "https://api.customer.io/v1"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def get_all_campaigns():
    url = f"{base_url}/campaigns"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("campaigns", [])

def get_campaign_actions(campaign_id):
    url = f"{base_url}/campaigns/{campaign_id}/actions"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("actions", [])

def get_action_metrics(campaign_id, action_id, action_type):
    if action_type not in ["email", "twilio"]:
        return None
    
    metric_type = "email" if action_type == "email" else "sms"
    url = f"{base_url}/campaigns/{campaign_id}/actions/{action_id}/metrics"
    params = {"period": "weeks", "steps": "1", "type": metric_type}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        created = data.get("metric", {}).get("series", {}).get("created", [])
        return created[-1] if created else 0
    except:
        return None

# Main logic
campaigns = get_all_campaigns()
campaigns_with_data = defaultdict(lambda: {"emails": [], "sms": []})
campaigns_without_data = []

today = datetime.now()
week_start = today.strftime("%Y-%m-%d")

for campaign in campaigns:
    campaign_id = campaign.get("id")
    campaign_name = campaign.get("name", "Unnamed Campaign")
    
    try:
        actions = get_campaign_actions(campaign_id)
    except:
        campaigns_without_data.append(campaign_name)
        continue
    
    email_sms_actions = [a for a in actions if a.get("type") in ["email", "twilio"]]
    
    if not email_sms_actions:
        campaigns_without_data.append(campaign_name)
        continue
    
    has_data = False
    
    for action in email_sms_actions:
        action_id = action.get("id")
        action_name = action.get("name", "Unnamed Action")
        action_type = action.get("type")
        sent_count = get_action_metrics(campaign_id, action_id, action_type)
        
        if sent_count is not None and sent_count > 0:
            has_data = True
            if action_type == "email":
                campaigns_with_data[campaign_name]["emails"].append({
                    "name": action_name,
                    "sent": sent_count
                })
            else:
                campaigns_with_data[campaign_name]["sms"].append({
                    "name": action_name,
                    "sent": sent_count
                })
    
    if not has_data:
        campaigns_without_data.append(campaign_name)

# Format as JSON for next node
report_data = {
    "week_start": week_start,
    "generated_at": datetime.now().isoformat(),
    "campaigns_with_data": dict(campaigns_with_data),
    "campaigns_without_data": sorted(campaigns_without_data)
}

return [{"json": report_data}]
```

#### Node 3: Format Report (Code - JavaScript)

**Type**: Code  
**Language**: JavaScript

```javascript
// Get report data from previous Python node
const reportData = $input.item.json;

function formatReport(data) {
  let report = `Week of ${data.week_start} customer.io reporting\n\n`;
  
  // Campaigns with data
  Object.keys(data.campaigns_with_data).sort().forEach(campaign => {
    report += `${campaign}\n`;
    data.campaigns_with_data[campaign].emails.forEach(email => {
      report += `Email ${email.name} - ${email.sent} sent\n`;
    });
    data.campaigns_with_data[campaign].sms.forEach(sms => {
      report += `SMS ${sms.name} - ${sms.sent} sent\n`;
    });
    report += `\n`;
  });
  
  // Campaigns with no data
  if (data.campaigns_without_data.length > 0) {
    report += `Campaigns with no data:\n`;
    data.campaigns_without_data.forEach(campaign => {
      report += `${campaign}\n`;
    });
  }
  
  return report;
}

return {
  json: {
    reportText: formatReport(reportData),
    reportData: reportData,
    subject: `Customer.io Weekly Report - ${reportData.week_start}`
  }
};
```

#### Node 4: Send Email
```
Type: Email Send
To: {{ $env.REPORT_EMAIL_TO }}
Subject: {{ $json.subject }}
Message: {{ $json.reportText }}
```

#### Node 5 (Optional): Send to Slack
```
Type: Slack
Channel: #reports
Message: ```
{{ $json.reportText }}
```
```

### Step 4: Test

1. Click "Execute Workflow" manually
2. Check each node's output
3. Verify email/Slack delivery

### Step 5: Activate

Enable the workflow and it will run automatically on schedule.

---

## Troubleshooting

### Script Not Found
- Use absolute paths in Execute Command node
- Check file permissions

### Python Not Found
- Use full path: `/usr/bin/python3` or `/usr/local/bin/python3`
- Or use virtual env's Python: `{{ $env.VENV_PATH }}/bin/python`

### JSON Parse Error
- Check that `--json` flag is used
- Verify script output in Execute Command node
- Add error handling in Code node

### API Key Issues
- Set `CUSTOMER_IO_API_KEY` environment variable
- Or modify script to use n8n's credential system

---

## Alternative: Import Workflow

1. Copy `n8n_workflow.json`
2. In n8n: Workflows → Import from File
3. Update environment variables
4. Test and activate

---

## Next Steps

- Add error handling nodes
- Store reports in database
- Create dashboard from historical data
- Add alerts for campaigns with zero sends
- Integrate with other tools (Google Sheets, etc.)

