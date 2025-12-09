# n8n Integration Guide for Customer.io Weekly Reporting

## Overview

There are **three main approaches** to integrate this Customer.io reporting into n8n:

### Approach 1: Execute Python Script (Simplest)
Run your existing Python script from n8n using the Execute Command node.

### Approach 2: Pure n8n Workflow (Most Visual)
Recreate the logic entirely in n8n using HTTP Request nodes and n8n's data transformation nodes.

### Approach 3: Hybrid (Best of Both)
Use n8n for orchestration and scheduling, but call the Python script for the heavy lifting.

---

## Approach 1: Execute Python Script

### Workflow Structure:
```
1. Schedule Trigger (Cron) → Run weekly (e.g., every Monday at 9 AM)
2. Execute Command Node → Run Python script
3. Format Output Node → Format the report text
4. Send Email/Slack → Deliver the report
```

### Setup:
1. **Schedule Trigger Node**
   - Set to run weekly (e.g., `0 9 * * 1` for Mondays at 9 AM)
   
2. **Execute Command Node**
   - Command: `/path/to/venv/bin/python`
   - Arguments: `/path/to/weekly_report.py`
   - Or use: `source /path/to/venv/bin/activate && python /path/to/weekly_report.py`
   - Capture output in `$execution.output`

3. **Code/Function Node** (Optional)
   - Format the output for email/Slack
   - Extract just the report text

4. **Email/Slack Node**
   - Send formatted report

### Pros:
- ✅ Reuses existing Python script
- ✅ Easy to maintain (all logic in one place)
- ✅ Can run locally or on n8n server

### Cons:
- ❌ Requires Python environment on n8n server
- ❌ Less visual (can't see data flow in n8n UI)

---

## Approach 2: Pure n8n Workflow

### Workflow Structure:
```
1. Schedule Trigger (Cron)
2. HTTP Request: Get All Campaigns
3. Loop Over Campaigns (Split In Batches)
4. HTTP Request: Get Actions for Each Campaign
5. Filter: Only Email/SMS Actions
6. HTTP Request: Get Metrics for Each Action
7. Aggregate Data
8. Format Report
9. Send Email/Slack
```

### Key Nodes:

#### Node 1: Get Campaigns
- **Type**: HTTP Request
- **Method**: GET
- **URL**: `https://api.customer.io/v1/campaigns`
- **Authentication**: Header Auth
  - Name: `Authorization`
  - Value: `Bearer {{ $env.CUSTOMER_IO_API_KEY }}`
- **Output**: Array of campaigns

#### Node 2: Loop Over Campaigns
- **Type**: Split In Batches or Loop Over Items
- Process each campaign

#### Node 3: Get Actions
- **Type**: HTTP Request
- **Method**: GET
- **URL**: `https://api.customer.io/v1/campaigns/{{ $json.id }}/actions`
- **Authentication**: Same as above
- **Output**: Array of actions

#### Node 4: Filter Actions
- **Type**: IF Node or Filter
- Condition: `{{ $json.type }} === 'email' || {{ $json.type }} === 'twilio'`

#### Node 5: Get Metrics
- **Type**: HTTP Request
- **Method**: GET
- **URL**: `https://api.customer.io/v1/campaigns/{{ $json.campaign_id }}/actions/{{ $json.id }}/metrics`
- **Query Parameters**:
  - `period`: `weeks`
  - `steps`: `1`
  - `type`: `email` or `sms` (based on action type)
- **Output**: Metrics with `created` array

#### Node 6: Aggregate & Format
- **Type**: Code Node or Function Node
- Group by campaign
- Extract sent counts from metrics
- Format as report text

#### Node 7: Send Report
- **Type**: Email or Slack
- Send formatted report

### Pros:
- ✅ Fully visual in n8n
- ✅ Easy to debug (see data at each step)
- ✅ No external dependencies
- ✅ Can add error handling per step

### Cons:
- ❌ More complex workflow
- ❌ Many API calls (rate limiting considerations)
- ❌ More nodes to maintain

---

## Approach 3: Hybrid Approach

Create a simple API endpoint or webhook that n8n can call, which runs your Python script and returns formatted JSON.

### Workflow Structure:
```
1. Schedule Trigger
2. HTTP Request: Call your script endpoint
3. Format Output
4. Send Email/Slack
```

### Implementation Options:

**Option A: Flask/FastAPI Server**
- Create a simple web server that runs the script
- n8n calls the endpoint
- Returns JSON or formatted text

**Option B: n8n Webhook + Execute Command**
- Use n8n's webhook to trigger
- Execute command node runs script
- Returns formatted output

---

## Recommended: Approach 1 (Execute Command)

For your use case, **Approach 1 is recommended** because:
1. You already have a working Python script
2. It's the simplest to set up
3. Easy to maintain and update
4. Can be tested independently

### Example n8n Workflow JSON

See `n8n_workflow.json` for a complete example you can import.

---

## Scheduling Options

### Weekly Report (Every Monday at 9 AM)
- Cron: `0 9 * * 1`

### Daily Report
- Cron: `0 9 * * *`

### Custom Schedule
- Use n8n's Schedule Trigger with custom cron expression

---

## Output Destinations

### Email
- Use **Email Send** node
- Format report as HTML or plain text
- Can attach as file

### Slack
- Use **Slack** node
- Send to channel or DM
- Format as code block for readability

### File Storage
- Use **Google Drive**, **Dropbox**, or **S3** node
- Save report as text file
- Archive weekly reports

### Database
- Store reports in database
- Use **PostgreSQL**, **MySQL**, or **MongoDB** node
- Build dashboard from historical data

---

## Environment Variables

Set in n8n:
- `CUSTOMER_IO_API_KEY`: Your Customer.io API key
- `REPORT_EMAIL_TO`: Email address to send reports
- `SLACK_WEBHOOK_URL`: Slack webhook for notifications

---

## Error Handling

Add error handling nodes:
1. **On Error** workflow settings
2. **IF** nodes to check for API errors
3. **Try/Catch** in Code nodes
4. **Error Workflow** to notify on failures

---

## Next Steps

1. Choose your approach
2. Set up the workflow in n8n
3. Test with a manual trigger
4. Set up scheduling
5. Configure output destination
6. Add error handling

