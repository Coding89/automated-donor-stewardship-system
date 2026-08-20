# automated-donor-stewardship-system
An automated pipeline designed to process CRM donation data, evaluate SLA compliance , calculate UK gift aid (25% extra),
check GDPR consent and dispatch personalised thank you emails to donors.

## Key Features

* **Automated Processing**: Filters pending thank you emails and updates records with send timestamps.
* **GDPR Compliance Check**: Scans data for missing consent (`Consent_Given == False`) and blocks email dispatch if non-compliant records exist.
* **SLA Tracking**: Calculates days elapsed since the donation date and categorizes requests as `OK`, `WARNING`, `BREACH`, or `UNKNOWN`.
* **Gift Aid Support**: Automatically calculates the additional tax relief value (25%) for eligible donations and includes it in the email copy.
* **Dynamic Email Generation**: Customizes thank-you messages per campaign, including special Easter eggs for specific donation amounts.