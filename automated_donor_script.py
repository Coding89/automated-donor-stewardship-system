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

#dispatches messages
dispatched_count = 0
for idx, row in df[pending_mask].iterrows():
    email_content = generate_email_body(
        row["First_Name"], row["Amount"], row["Campaign"]
    )
    
    #In production, this connnects to SendGrid/SMTP/CRM Email API
    print(
        f"[{row['SLA_Status']}] Dispatching email to {row['First_Name']} ({row['Email']}...)"
    )
    df.at[idx, "Thank_You_Sent"] = True
    df.at[idx, "Sent_Timestamp"] = CURRENT_DATE.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    dispatched_count += 1
    
    print(f"\nSuccessfully dispatched {dispatched_count} thank you messages.")
    return df

# Mock CRM execution
def main():
    mock_donations = {
        "Donor_ID": ["D201", "D202", "D203"],
        "First_Name": ["Kofi", "Elena", "Marcus"],
        "Email": ["kofi@example", "elena@example.com", "marcus@example.com"],
        "Amount": [25.00, 100.00, 50.00],
        "Campaign": [
            "General Giving",
            "London Marathon 2026",
            "Community raising BBQ",
            "In-memory appeal",
            "NHS Foundation trust drive",
        ],
        "Donation_Date": [
            "2026-02-12",
            "2026-02-08",
            "2026-02-14",
        ],
        "Thank_You_Sent":[False, False, False],
    }
    
    df_crm = pd.DataFrame(mock_donations)
    
    df_updated = process_thankyou_queue(df_crm)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
