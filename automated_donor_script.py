"""
This script models how a CRM or webhook integrates automatically dispatches personalised thank you emails to donors.
This ensures that no donor goes unacknowledged past the charity's SLA target (which can be adjusted in the script).

This script uses £ symbols but can be change to suit local currency needs.

In other words and in non-technical terms, this script automates thank you emails to donors ensuring that donors are thanked within a charity's turnaround target.
"""
from datetime import datetime, timedelta
import pandas as pd

#Targets and thanks donors within a specific timeframe. The number can be adjusted according to charity turnaround targets.
SLA_DAYS = 5
CURRENT_DATE = datetime.now()

#Generate the email template below after {campaign_name}! and make sure to sign off with your name, position and organisation etc.
def generate_email_body(first_name, amount, campaign_name):
    """ Generates a warm and personalised email body based on donation details."""
    return f"""
Dear {first_name},

Thank you so much for your generous gift of £{amount:.2f} towards our {campaign_name}!

Add your own template

""".strip()

#Scans the donor queue, flags any SLA breaches and dispatches personalised communications.
def process_thank_queue(df: pd.DataFrame):
    df["Donation_Date"] = pd.to_datetime(df["Donation_Date"])
    df["Days_Elapsed"] = (CURRENT_DATE - df["Donation_Date"]).dt.days
    
#Helps to identify any unsent thank yous
pending_mask = df["Thank_You_Sent"] == False
df.loc[pending_mask, "SLA_Status"] = df.loc[pending_mask, "Days_Elapsed"].apply(
    lambda days: (
        "SLA Breach!"
        if days > SLA_DAYS
        else ("SLA WARNING" if days >= 4 else "✔ Within SLA target")
    )
)
