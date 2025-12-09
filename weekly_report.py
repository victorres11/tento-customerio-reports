#!/usr/bin/env python3
"""
Customer.io Weekly Reporting Script
Generates a weekly report of campaign email and SMS sends.
"""

import requests
import json
import os
import sys
from datetime import datetime
from collections import defaultdict

# Get API key from environment variable (required)
API_KEY = os.getenv("CUSTOMER_IO_API_KEY")
if not API_KEY:
    print("Error: CUSTOMER_IO_API_KEY environment variable is required", file=sys.stderr)
    sys.exit(1)
BASE_URL = "https://api.customer.io/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def get_all_campaigns():
    """Fetch all campaigns from Customer.io"""
    url = f"{BASE_URL}/campaigns"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json().get("campaigns", [])


def get_campaign_actions(campaign_id):
    """Fetch all actions for a specific campaign (handles pagination)"""
    url = f"{BASE_URL}/campaigns/{campaign_id}/actions"
    all_actions = []
    next_cursor = None
    
    while True:
        # Add pagination parameter if we have a cursor
        if next_cursor:
            current_url = f"{url}?next={next_cursor}"
        else:
            current_url = url
        
        response = requests.get(current_url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        # Add actions from this page
        actions = data.get("actions", [])
        all_actions.extend(actions)
        
        # Check if there's a next page
        next_cursor = data.get("next")
        if not next_cursor:
            break
    
    return all_actions


def get_action_metrics(campaign_id, action_id, action_type):
    """Fetch metrics for a specific action (email or SMS only)"""
    # Only fetch metrics for email and SMS actions
    if action_type not in ["email", "twilio"]:
        return None
    
    # Map twilio to sms for the API
    metric_type = "email" if action_type == "email" else "sms"
    
    url = f"{BASE_URL}/campaigns/{campaign_id}/actions/{action_id}/metrics"
    params = {
        "period": "weeks",
        "steps": "1",  # Get last week
        "type": metric_type
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Get the most recent week's "created" count (sent count)
        metric = data.get("metric", {})
        series = metric.get("series", {})
        created = series.get("created", [])
        
        # Return the last value (most recent week)
        if created:
            return created[-1] if len(created) > 0 else 0
        return 0
    except requests.exceptions.RequestException as e:
        # If metrics endpoint fails, return None
        return None


def generate_weekly_report(output_format='text'):
    """Generate the weekly report
    
    Args:
        output_format: 'text' for human-readable, 'json' for structured data
    """
    if output_format == 'text':
        print("Fetching campaigns...")
    campaigns = get_all_campaigns()
    
    # Structure to hold report data
    campaigns_with_data = defaultdict(lambda: {"emails": [], "sms": []})
    campaigns_without_data = []
    
    # Get current week date range for header
    today = datetime.now()
    week_start = today.strftime("%Y-%m-%d")
    
    if output_format == 'text':
        print(f"Processing {len(campaigns)} campaigns...")
    
    for campaign in campaigns:
        campaign_id = campaign.get("id")
        campaign_name = campaign.get("name", "Unnamed Campaign")
        
        if output_format == 'text':
            print(f"  Processing campaign: {campaign_name} (ID: {campaign_id})")
        
        try:
            actions = get_campaign_actions(campaign_id)
        except Exception as e:
            if output_format == 'text':
                print(f"    Error fetching actions: {e}")
            campaigns_without_data.append(campaign_name)
            continue
        
        # Filter for email and SMS actions only
        email_sms_actions = [
            action for action in actions 
            if action.get("type") in ["email", "twilio"]
        ]
        
        if not email_sms_actions:
            campaigns_without_data.append(campaign_name)
            continue
        
        has_data = False
        
        for action in email_sms_actions:
            action_id = action.get("id")
            action_name = action.get("name", "Unnamed Action")
            action_type = action.get("type")
            
            # Get metrics for this action
            sent_count = get_action_metrics(campaign_id, action_id, action_type)
            
            if sent_count is not None and sent_count > 0:
                has_data = True
                action_display_name = action_name
                action_type_label = "Email" if action_type == "email" else "SMS"
                
                if action_type == "email":
                    campaigns_with_data[campaign_name]["emails"].append({
                        "name": action_display_name,
                        "sent": sent_count
                    })
                else:  # twilio
                    campaigns_with_data[campaign_name]["sms"].append({
                        "name": action_display_name,
                        "sent": sent_count
                    })
        
        if not has_data:
            campaigns_without_data.append(campaign_name)
    
    # Generate report output
    if output_format == 'json':
        # Return structured JSON for n8n integration
        report_data = {
            "week_start": week_start,
            "generated_at": datetime.now().isoformat(),
            "campaigns_with_data": {},
            "campaigns_without_data": sorted(campaigns_without_data)
        }
        
        for campaign_name in sorted(campaigns_with_data.keys()):
            data = campaigns_with_data[campaign_name]
            report_data["campaigns_with_data"][campaign_name] = {
                "emails": data["emails"],
                "sms": data["sms"]
            }
        
        return report_data
    else:
        # Print human-readable format
        print("\n" + "="*60)
        print(f"Week of {week_start} customer.io reporting")
        print("="*60 + "\n")
        
        # Print campaigns with data
        for campaign_name in sorted(campaigns_with_data.keys()):
            data = campaigns_with_data[campaign_name]
            print(campaign_name)
            
            # Print emails
            for email in data["emails"]:
                print(f"Email {email['name']} - {email['sent']} sent")
            
            # Print SMS
            for sms in data["sms"]:
                print(f"SMS {sms['name']} - {sms['sent']} sent")
            
            print()
        
        # Print campaigns with no data
        if campaigns_without_data:
            print("Campaigns with no data:")
            for campaign_name in sorted(campaigns_without_data):
                print(campaign_name)
            print()
        
        return None


if __name__ == "__main__":
    try:
        # Check for JSON output flag
        output_format = 'json' if '--json' in sys.argv else 'text'
        result = generate_weekly_report(output_format=output_format)
        
        if output_format == 'json':
            # Output JSON to stdout for n8n to parse
            print(json.dumps(result, indent=2))
    except Exception as e:
        if '--json' in sys.argv:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

