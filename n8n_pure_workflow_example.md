# Pure n8n Workflow Example (No Python)

This shows how to build the Customer.io report entirely in n8n using HTTP Request nodes.

## Workflow Steps

### 1. Schedule Trigger
- **Cron**: `0 9 * * 1` (Every Monday at 9 AM)
- **Mode**: Every Week

### 2. HTTP Request: Get All Campaigns
```json
{
  "method": "GET",
  "url": "https://api.customer.io/v1/campaigns",
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "Bearer {{ $env.CUSTOMER_IO_API_KEY }}"
      },
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  }
}
```

**Output**: Array of campaign objects

### 3. Split In Batches (Process Each Campaign)
- **Batch Size**: 1
- This loops through each campaign

### 4. HTTP Request: Get Campaign Actions
```json
{
  "method": "GET",
  "url": "https://api.customer.io/v1/campaigns/{{ $json.id }}/actions",
  "authentication": "same as above"
}
```

**Output**: Array of actions for the campaign

### 5. Filter: Only Email/SMS Actions
- **Type**: IF Node
- **Condition**: 
  ```
  {{ $json.type }} === 'email' || {{ $json.type }} === 'twilio'
  ```

### 6. HTTP Request: Get Action Metrics
```json
{
  "method": "GET",
  "url": "https://api.customer.io/v1/campaigns/{{ $('Get Campaign Actions').item.json.campaign_id }}/actions/{{ $json.id }}/metrics",
  "queryParameters": {
    "parameters": [
      {
        "name": "period",
        "value": "weeks"
      },
      {
        "name": "steps",
        "value": "1"
      },
      {
        "name": "type",
        "value": "={{ $json.type === 'email' ? 'email' : 'sms' }}"
      }
    ]
  }
}
```

**Output**: Metrics object with `metric.series.created` array

### 7. Code Node: Extract Sent Count
```javascript
// Get the last value from the created array (most recent week)
const metrics = $input.item.json;
const sentCount = metrics.metric?.series?.created?.slice(-1)[0] || 0;

// Get campaign and action info from previous nodes
const campaignName = $('Get All Campaigns').item.json.name;
const actionName = $('Get Campaign Actions').item.json.name;
const actionType = $('Get Campaign Actions').item.json.type;

return {
  json: {
    campaignName: campaignName,
    actionName: actionName,
    actionType: actionType === 'email' ? 'Email' : 'SMS',
    sentCount: sentCount,
    campaignId: $('Get All Campaigns').item.json.id
  }
};
```

### 8. Aggregate: Group by Campaign
- **Type**: Aggregate Node
- **Group By**: `campaignName`
- **Operations**: 
  - Collect all actions into an array
  - Sum sent counts (optional)

### 9. Code Node: Format Report
```javascript
// Group data by campaign
const items = $input.all();
const campaignsWithData = {};
const campaignsWithoutData = [];

items.forEach(item => {
  const campaign = item.json.campaignName;
  const actionType = item.json.actionType;
  const actionName = item.json.actionName;
  const sent = item.json.sentCount;
  
  if (sent > 0) {
    if (!campaignsWithData[campaign]) {
      campaignsWithData[campaign] = { emails: [], sms: [] };
    }
    
    if (actionType === 'Email') {
      campaignsWithData[campaign].emails.push({ name: actionName, sent: sent });
    } else {
      campaignsWithData[campaign].sms.push({ name: actionName, sent: sent });
    }
  }
});

// Format report
const today = new Date().toISOString().split('T')[0];
let report = `Week of ${today} customer.io reporting\n\n`;

// Campaigns with data
Object.keys(campaignsWithData).sort().forEach(campaign => {
  report += `${campaign}\n`;
  campaignsWithData[campaign].emails.forEach(email => {
    report += `Email ${email.name} - ${email.sent} sent\n`;
  });
  campaignsWithData[campaign].sms.forEach(sms => {
    report += `SMS ${sms.name} - ${sms.sent} sent\n`;
  });
  report += `\n`;
});

// Campaigns with no data
if (campaignsWithoutData.length > 0) {
  report += `Campaigns with no data:\n`;
  campaignsWithoutData.sort().forEach(campaign => {
    report += `${campaign}\n`;
  });
}

return {
  json: {
    report: report,
    timestamp: new Date().toISOString()
  }
};
```

### 10. Send Email/Slack
- Use Email Send or Slack node
- Send the formatted report

## Notes

- This approach makes many API calls (one per campaign, one per action)
- Consider rate limiting and add delays if needed
- Use n8n's error handling to catch API failures
- The workflow will be longer but fully visual in n8n

