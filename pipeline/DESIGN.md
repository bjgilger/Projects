# Design Criteria
## Assumptions
- Assume standard CSV quoting; Pandas default parser is sufficient.
- The typical user is a small service business
- Jobs are scheduled and completed on specific dates.
- Each row represents one job or one invoice line.
- Revenue may include labor and materials.
- Payment might be cash or credit.
- Owners' concerns are:
  - Revenue
  - Expenses (materials)
  - Profit
  - Breakdown by service type and client
  - Paid vs accounts receivable
## Input Schema 
*CSV file: data/raw/transactions.csv*

| Column | Type | Unique | Required | Notes                                                                                                                                                                  |
|:---------| :--------|:------:|:--------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| job_id | String |   No   |   Yes    |                                                                                                                                                                        |
| date | String |   No   |   Yes    | Format YYYY-MM-DD. Invalid date: row goes to the error log.                                                                                                            |
| client_name | String |   No   |   Yes    |                                                                                                                                                                        |
| service_type | String |   No   |   Yes    | Examples: plumbing, installation, maintenance, consulting, class, private_session                                                                                      |
| labor_amount | Numeric |   No   |   Yes    | Fatal if invalid.                                                                                                                                                      |
| materials_amount | Numeric |   No   |    No    | Treat invalid as 0.                                                                                                                                                    |
| tax_amount | Numeric |   No   |    No    | Treat invalid as 0.                                                                                                                                                    |
| total_amount | Numeric |   No   |   Yes    | Calculation: total_amount ≈ labor_amount + materials_amount + tax_amount. abs(total_amount - (labor_amount + materials_amount + tax_amount)) > 0.05 -> warning logged. |
| payment_status | Categorical |   No   |   Yes    | Values: paid, unpaid, partial. Normalized to lower case. Unknown: row is sent to the error log.                                                                        |
| payment_method | Categorical |   No   |    No    | Values: cash, card, bank_transfer, check, online. Unknown values: other with a warning.                                                                                |
| source | String |   No   |    No    | Examples: website, referral, walk_in, facebook, yelp.                                                                                                                  |
| notes | Free text |   No   |    No    | Ignored for metrics, retained in cleaned output                                                                                                                        |
## String Normalization Rules
- service_type: lowercased
- payment_status: lowercased
- payment_method: After trimming and lowercasing, compare against canonical set.
- client_name: trimmed, original casing preserved
- source: lowercased
- notes: trimmed, case preserved
## Row validation rules:
A row is **fatal** if:
- date missing or invalid
- job_id missing
- client_name missing
- service_type missing
- labor_amount or total_amount not numeric
- payment_status missing or invalid
A row is **valid with warnings** if:
- materials_amount or tax_amount invalid; replace with 0
- payment_method unrecognized; set to *other*
- total_amount mismatch exceeds tolerance of 0.05
- unknown service_type; keep but log, no remapping
- **Completely empty rows** are ignored. 
- **Rows with fewer or more columns than expected (12)** are fatal.
- Whitespace-only fields (" " (spaces only), "\t" (tabs), " \n " (just newline and spaces)) arre treated as missing for required fields.
## Outputs 
### Cleaned transactions output file
*File: data/processed/transactions_cleaned.csv*
Same columns as input, but:
- Dates normalized to YYYY-MM-DD and validated.
- Strings trimmed and normalized (e.g., lowercased where appropriate).
- Numeric fields are numeric and consistent.
- Only valid and “valid with warnings” rows appear.
### Error log
*File: data/processed/transactions_errors.csv*
Columns:
- row_number
- raw_row (optional, or individual fields)
- error_type (e.g., missing_required_field, invalid_date, invalid_numeric)
- details
- ### Console summary
- When running python *scripts/run_pipeline.py data/raw/transactions.csv*, print:
- Date range: 
  - start_date = minimum valid date
  - end_date = maximum valid date
- Total revenue
- Net income
- Top 3 service types by revenue
- Count of unpaid and partial jobs
- Count of error rows
### Metrics summary
File: *data/processed/metrics_summary.json*

Example structure:
```json
{
  "period": {
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "overall": {
    "total_revenue": 18250.50,
    "total_materials_cost": 4150.75,
    "total_tax_collected": 1320.20,
    "net_income": 12779.55,
    "num_jobs": 73,
    "num_clients": 28,
    "num_unpaid_jobs": 5,
    "num_partial_jobs": 3
  },
  "by_service_type": [
    {
      "service_type": "plumbing",
      "total_revenue": 8200.00,
      "num_jobs": 24
    },
    {
      "service_type": "maintenance",
      "total_revenue": 5400.50,
      "num_jobs": 19
    }
  ],
  "by_client": [
    {
      "client_name": "Smith Family",
      "total_revenue": 950.00,
      "num_jobs": 3
    }
  ]
}

```







