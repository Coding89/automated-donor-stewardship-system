# Automated Donor Stewardship System
An automated pipeline designed to process CRM donation data, evaluate SLA compliance , calculate UK gift aid (25% extra),
check GDPR consent and dispatch personalised thank you emails to donors. Primarily directed at charities.

## Key Features

* **Automated Processing**: Filters pending thank you emails and updates records with send timestamps.
* **GDPR Compliance Check**: Scans data for missing consent (`Consent_Given == False`) and blocks email dispatch if non-compliant records exist.
* **SLA Tracking**: Calculates days elapsed since the donation date and categorizes requests as `OK`, `WARNING`, `BREACH`, or `UNKNOWN`.
* **Gift Aid Support**: Automatically calculates the additional tax relief value (25%) for eligible donations and includes it in the email copy.
* **Dynamic Email Generation**: Customizes thank-you messages per campaign, including special Easter eggs for specific donation amounts.

## Business Logic & Flow

1. **Date Standardisation**: Converts input strings into standard `datetime` objects and calculates total elapsed days.
2. **GDPR Gatekeeper**: Checks if any row contains `Consent_Given == False`. If detected, the script flags a warning and aborts the dispatch process to protect privacy.
3. **SLA Evaluation**: Evaluates non-sent records against the `SLA_DAYS` target:
   * **`OK`**: Elapsed days are well within target.
   * **`WARNING`**: Exactly 1 day remaining before SLA breach.
   * **`BREACH`**: Exceeded the target SLA period.
   * **`UNKNOWN`**: Date is missing or unparseable.
4. **Email Dispatch**: Builds custom email bodies and logs details while updating the DataFrame status.

## Prerequisites and installation

Ensure that you have Python 3.8+ installed then install the following required dependencies:

```bash
pip install pandas numpy

