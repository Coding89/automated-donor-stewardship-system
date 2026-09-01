import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np  

# Debug logging - might switch to ERROR in prod
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S" 
)

# Configured SLA days to 5 but can be changed to match the deadline requirements of the organisation/charity
SLA_DAYS = 5 
CURRENCY = "£"
GIFT_AID_RATE = 0.25 
GDPR_AUDIT_FIELDS = ["Donor_ID", "Email", "Consent_Given"]  # Fields to check for compliance

def generate_email_body(first_name, amount, campaign_name, gift_aid_eligible=False):
    # Generates a thank you email. NOTE: Gift Aid eligible donors get a slightly different message.
    extra_note = ""
    if amount == 1337:
        extra_note = "\nP.S. Legendary donor! 🎮"
    elif amount == 42:
        extra_note = "\nP.S. The answer to life, the universe, and everything!\n"

    # Add Gift Aid note if applicable
    gift_aid_note = ""
    if gift_aid_eligible:
        gift_aid_note = (
            f"\nThanks to Gift Aid, your donation is worth an extra "
            f"{CURRENCY}{amount * GIFT_AID_RATE:.2f} to us at no extra cost to you!"
        )

    body = (
        f"Dear {first_name},\n\n"
        f"Thank you for your donation of {CURRENCY}{amount:.2f} to {campaign_name}.\n"
        f"Your support makes a real difference.{gift_aid_note}\n"
        f"{extra_note}"
        f"\nWith gratitude,\nThe Fundraising Team"
    )
    return body.strip()

def check_gdpr_compliance(df):
    #Quick GDPR check - flags rows missing consent.
    missing_consent = df[df["Consent_Given"] == False]
    if not missing_consent.empty:
        logging.warning(f"GDPR ISSUE: {len(missing_consent)} donors without consent!")
    return len(missing_consent) == 0

#Main function to process thank-you emails. Also handles Gift Aid tracking and GDPR checks.
def process_thank_queue(df, current_date=None):
    if current_date is None:
        current_date = datetime.now()

    # Convert dates (sometimes this fails with bad CRM data)
    try:
        df["Donation_Date"] = pd.to_datetime(df["Donation_Date"], errors="coerce")
    except Exception as e:
        logging.error(f"Date conversion failed: {e}")

    df["Days_Elapsed"] = (current_date - df["Donation_Date"]).dt.days

    # GDPR check before sending emails
    if not check_gdpr_compliance(df):
        logging.warning("Skipping dispatch due to GDPR non-compliance!")
        return df

    # Find unsent thank-yous (using ~ for fun)
    pending = df[~df["Thank_You_Sent"]]

    def get_sla_status(days):
        if pd.isna(days):  # Handle NaN from bad dates
            return "UNKNOWN"
        if days > SLA_DAYS:
            return "BREACH"
        elif days == SLA_DAYS - 1:
            return "WARNING"
        else:
            return "OK"

    # Apply SLA status
    df.loc[pending.index, "SLA_Status"] = pending["Days_Elapsed"].apply(get_sla_status)

    count = 0
    for idx, row in pending.iterrows():
        try:
            email = generate_email_body(
                row["First_Name"],
                row["Amount"],
                row["Campaign"],
                row.get("Gift_Aid_Eligible", False)  # Default to False if missing
            )
            logging.info(
                f"[{row['SLA_Status']}] Email to {row['First_Name']} "
                f"({row['Email']}) | Gift Aid: {row.get('Gift_Aid_Eligible', 'N/A')}"
            )

    # Mark as sent (sometimes this fails with locked DataFrames)
            df.at[idx, "Thank_You_Sent"] = True
            df.at[idx, "Sent_Timestamp"] = current_date.strftime("%Y-%m-%d %H:%M:%S")
            count += 1
        except KeyError as e:
            logging.error(f"Missing column in row {idx}: {e}")
            continue

    logging.info(f"Dispatch complete. Sent {count}/{len(pending)} emails.")
    return df

if __name__ == "__main__":
    # Test data - real CRM exports are messier than this!
    donations = {
        "Donor_ID": ["D201", "D202", "D203", "D204", "D205"],
        "First_Name": ["Kofi", "Elena", "Marcus", "Ada", "Priya"],
        "Email": [
            "kofi@example.com",
            "elena@example.com",
            "marcus@example.com",
            None,
            "priya@example.com",
        ],
        "Amount": [25, 1337, 42, 50, 100],
        "Campaign": ["General", "Marathon", "In-memory", "Tech", "Appeal"],
        "Donation_Date": ["2026-08-10", "2026-08-12", "2026-08-16", "2026-08-18", "2026-08-01"],
        "Thank_You_Sent": [False, False, False, False, True], 
        "Sent_Timestamp": [None, None, None, None, "2026-08-17 10:00:00"],
        "Gift_Aid_Eligible": [True, False, True, False, True],
        "Consent_Given": [True, True, False, True, True],  
    }

    df = pd.DataFrame(donations)
    updated_df = process_thank_queue(df)

    # Print a quick summary
    print("\n--- Summary ---")
    print(f"Total donors: {len(df)}")
    print(f"Thank-yous sent: {df['Thank_You_Sent'].sum()}")
    print(f"Gift Aid eligible: {df['Gift_Aid_Eligible'].sum()}")