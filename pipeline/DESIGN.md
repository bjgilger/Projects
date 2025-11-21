# Design Criteria
## Assumptions
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

| Column | Type | Unique | Required | Notes |
|:---------| :--------|:---:| :---:|:-----------------------------------------------------------------------------|
| job_id | String | Yes | Yes | |
| date | String | No | Yes | Format YYYY-MM-DD. Invalid date: row goes to the error log. |
| client_name | String | No | Yes | |
| service_type | String | No | Yes | Examples: plumbing, installation, maintenance, consulting, class, private_session |
| labor_amount | Numeric | No | Yes | Default is 0. Invalid numeric value: row is sent to the error log. |
| materials_amount | Numeric | No | Yes | Default is 0. Can be empty |
| tax_amount | Numeric | No | No | Default is 0. |
| total_amount | Numeric | No | Yes | Calculation: total_amount ≈ labor_amount + materials_amount + tax_amount. Small rounding differences and log mismatches will be allowed. |
| payment_status | Categorical | No | No | Values: paid, unpaid, partial. Normalized to lower case. Unknown: row is sent to the error log. |
| payment_method | Categorical | No | No | Values: cash, card, bank_transfer, check, online. Unknown values: other with a warning |
| source | String | No | No | Examples: website, referral, walk_in, facebook, yelp. |
| notes | Free text | No | No | Ignored for metrics, retained in cleaned output |
## Row validation rules:
A row is **fatal** (goes to error log, excluded from metrics) if:
- date is missing or cannot be parsed.
- job_id is missing.
- client_name is missing.
- service_type is missing.
- labor_amount or total_amount is not numeric.
- payment_status is missing or not in the allowed set after normalization.
A row is **valid with warnings** (kept, but warning logged) if:
- materials_amount or tax_amount cannot be parsed. We treat them as 0.
- payment_method is not recognized. We map it to *other*.
- total_amount does not match the sum of parts within a tolerance.
- service_type is an unexpected value. We keep it but log it.
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
- Date range
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







