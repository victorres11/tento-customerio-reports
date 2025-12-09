# n8n Simple HTTP Request Workflow

If you prefer not to use Python code in n8n, here's a simpler approach using HTTP Request nodes.

## Workflow Structure

1. **Schedule Trigger** → 2. **HTTP Request: Get Campaigns** → 3. **Loop Over Campaigns** → 4. **HTTP Request: Get Actions** → 5. **HTTP Request: Get Metrics** → 6. **Format & Send**

---

## Step-by-Step Setup

### Node 1: Schedule Trigger
- **Type**: Schedule Trigger
- **Cron**: `0 9 * * 1` (Mondays at 9 AM)

### Node 2: HTTP Request - Get All Campaigns
- **Type**: HTTP Request
- **Method**: GET
- **URL**: `https://api.customer.io/v1/campaigns`
- **Authentication**: Header Auth
  - **Name**: `Authorization`
  - **Value**: `Bearer {{ $env.CUSTOMER_IO_API_KEY }}`
- **Send Headers**: Yes
  - **Name**: `Content-Type`
  - **Value**: `application/json`

**Output**: Array of campaigns

### Node 3: Split In Batches
- **Type**: Split In Batches
- **Batch Size**: 1
- This processes each campaign one at a time

### Node 4: HTTP Request - Get Campaign Actions
- **Type**: HTTP Request
- **Method**: GET
- **URL**: `https://api.customer.io/v1/campaigns/{{ $json.id }}/actions`
- **Authentication**: Same as Node 2

**Output**: Array of actions for the campaign

### Node 5: Filter Actions (IF Node)
- **Type**: IF
- **Condition**: 
  ```
  {{ $json.type }} === 'email' || {{ $json.type }} === 'twilio'
  ```
- This filters to only email and SMS actions

### Node 6: HTTP Request - Get Metrics
- **Type**: HTTP Request
- **Method**: GET
- **URL**: `https://api.customer.io/v1/campaigns/{{ $('Split In Batches').item.json.id }}/actions/{{ $json.id }}/metrics`
- **Query Parameters**:
  - `period`: `weeks`
  - `steps`: `1`
  - `type`: `={{ $json.type === 'email' ? 'email' : 'sms' }}`
- **Authentication**: Same as Node 2

**Output**: Metrics with sent counts

### Node 7: Code - Aggregate Data
- **Type**: Code
- **Language**: JavaScript

This node collects all the data and formats it. Since n8n processes items in batches, you'll need to aggregate at the end.

**Note**: This approach requires more complex aggregation. The Python Code node approach is simpler for this use case.

---

## Recommendation

For this workflow, **using the Code (Python) node** (as shown in N8N_QUICK_START.md) is much simpler because:
- ✅ All logic in one place
- ✅ Easier to aggregate data
- ✅ Less nodes to manage
- ✅ Same result

The HTTP Request approach is better if you want to:
- See data flow visually at each step
- Add custom logic between API calls
- Handle errors per API call

