#!/usr/bin/env python3
"""
Customer.io Weekly Reporting Script
Generates a weekly report of campaign email and SMS sends.
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

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
    """Fetch all actions for a specific campaign"""
    url = f"{BASE_URL}/campaigns/{campaign_id}/actions"
    # Use limit parameter to get all actions at once (up to 1000, which should be more than enough)
    params = {"limit": 1000}
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()
    
    actions = data.get("actions", [])
    
    # If there's still a next cursor, it means there are more than 1000 actions (unlikely but handle it)
    if data.get("next") and len(actions) >= 1000:
        print(f"      Warning: Campaign has more than 1000 actions, only fetching first 1000")
    
    return actions


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


# Historical data file path
HISTORY_FILE = Path(__file__).parent / "report_history.json"


def load_historical_data():
    """Load historical report data from JSON file"""
    if not HISTORY_FILE.exists():
        return {}

    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load historical data: {e}", file=sys.stderr)
        return {}


def save_historical_data(week_start, campaigns_data):
    """Save current week's data to history file

    Args:
        week_start: Date string for the week (YYYY-MM-DD)
        campaigns_data: Dictionary of campaign data to save
    """
    history = load_historical_data()

    # Store data by week
    history[week_start] = campaigns_data

    # Keep only last 8 weeks to prevent file from growing too large
    sorted_weeks = sorted(history.keys(), reverse=True)
    if len(sorted_weeks) > 8:
        for old_week in sorted_weeks[8:]:
            del history[old_week]

    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save historical data: {e}", file=sys.stderr)


def get_previous_week_data(current_week_start):
    """Get data from previous week for comparison

    Args:
        current_week_start: Current week start date string (YYYY-MM-DD)

    Returns:
        Dictionary of previous week's campaign data, or empty dict if not found
    """
    history = load_historical_data()

    # Calculate previous week's date
    current_date = datetime.strptime(current_week_start, "%Y-%m-%d")
    previous_date = current_date - timedelta(days=7)
    previous_week_str = previous_date.strftime("%Y-%m-%d")

    return history.get(previous_week_str, {})


def calculate_trend(current, previous):
    """Calculate percentage change and trend indicator

    Args:
        current: Current value
        previous: Previous value

    Returns:
        Tuple of (percentage_change, trend_indicator)
    """
    if previous == 0:
        if current == 0:
            return 0, "→"
        return 100, "↑"

    pct_change = ((current - previous) / previous) * 100

    if pct_change > 5:
        indicator = "↑"
    elif pct_change < -5:
        indicator = "↓"
    else:
        indicator = "→"

    return pct_change, indicator


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

    # Load previous week's data for comparison
    previous_week_data = get_previous_week_data(week_start)

    if output_format == 'text':
        if previous_week_data:
            print(f"Processing {len(campaigns)} campaigns (comparing to previous week)...")
        else:
            print(f"Processing {len(campaigns)} campaigns...")
    
    for campaign in campaigns:
        campaign_id = campaign.get("id")
        campaign_name = campaign.get("name", "Unnamed Campaign")
        # Check both 'state' and 'status' fields (API might use either)
        campaign_state = campaign.get("state") or campaign.get("status") or "unknown"

        # Skip non-running campaigns (draft, archived, stopped, etc.)
        # Accept both "running" and "active" as valid running states
        if campaign_state.lower() not in ["running", "active"]:
            if output_format == 'text':
                print(f"  Skipping {campaign_state} campaign: {campaign_name}")
            continue

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

                # Calculate trend if we have previous week's data
                trend_pct = None
                trend_indicator = None
                if previous_week_data and campaign_name in previous_week_data:
                    prev_campaign = previous_week_data[campaign_name]
                    action_list = prev_campaign.get("emails" if action_type == "email" else "sms", [])

                    # Find matching action in previous week
                    for prev_action in action_list:
                        if prev_action["name"] == action_display_name:
                            prev_sent = prev_action["sent"]
                            trend_pct, trend_indicator = calculate_trend(sent_count, prev_sent)
                            break

                action_data = {
                    "name": action_display_name,
                    "sent": sent_count
                }

                # Add trend data if available
                if trend_pct is not None:
                    action_data["trend_pct"] = trend_pct
                    action_data["trend_indicator"] = trend_indicator

                if action_type == "email":
                    campaigns_with_data[campaign_name]["emails"].append(action_data)
                else:  # twilio
                    campaigns_with_data[campaign_name]["sms"].append(action_data)
        
        if not has_data:
            campaigns_without_data.append(campaign_name)
    
    # Save current week's data for next week's comparison
    save_historical_data(week_start, dict(campaigns_with_data))

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
                trend_str = ""
                if "trend_indicator" in email:
                    trend_str = f" {email['trend_indicator']}"
                    if email['trend_pct'] != 0:
                        trend_str += f" {email['trend_pct']:+.1f}%"
                print(f"Email {email['name']} - {email['sent']} sent{trend_str}")

            # Print SMS
            for sms in data["sms"]:
                trend_str = ""
                if "trend_indicator" in sms:
                    trend_str = f" {sms['trend_indicator']}"
                    if sms['trend_pct'] != 0:
                        trend_str += f" {sms['trend_pct']:+.1f}%"
                print(f"SMS {sms['name']} - {sms['sent']} sent{trend_str}")
            
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

