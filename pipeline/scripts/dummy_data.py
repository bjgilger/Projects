import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set a seed for reproducibility
np.random.seed(42)
random.seed(42)

N_ROWS = 15

# Function to generate random dates
def generate_random_date(start_date='2024-01-01', end_date='2024-12-31'):
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    delta = end - start
    random_days = random.randrange(delta.days)
    return (start + timedelta(days=random_days)).strftime('%Y-%m-%d')

dates = [generate_random_date() for _ in range(N_ROWS)]
job_ids = [f'JOB-{i+1:04d}' for i in range(N_ROWS)]
client_names = [f'Client {random.choice(["Alpha", "Beta", "Gamma"])} {i}' for i in range(N_ROWS)]
service_types_list = ['plumbing', 'installation', 'maintenance', 'Consulting', 'class', 'private_session']
service_types = [random.choice(service_types_list) for _ in range(N_ROWS)]
service_types[2] = 'InStAlLaTiOn' # Bad capitalization

# Amounts
labor_amounts = np.round(np.random.uniform(50, 1000, N_ROWS), 2)
labor_amounts[0] = 0.00 # Ensure at least one 0

materials_amounts_raw = np.round(np.random.uniform(0, 500, N_ROWS), 2)
materials_amounts = [m if random.random() > 0.1 else np.nan for m in materials_amounts_raw]
materials_amounts[3] = 0.00 # Ensure at least one 0

tax_rates = np.random.uniform(0.05, 0.12, N_ROWS)
tax_amounts = []
for i in range(N_ROWS):
    base = labor_amounts[i] + (materials_amounts[i] if not pd.isna(materials_amounts[i]) else 0)
    if random.random() < 0.2: # 20% chance of being NaN
        tax_amounts.append(np.nan)
    else:
        tax_amounts.append(np.round(base * tax_rates[i], 2))

# Total amount calculation with allowed rounding difference
total_amounts = []
for i in range(N_ROWS):
    lab = labor_amounts[i]
    mat = materials_amounts[i] if not pd.isna(materials_amounts[i]) else 0
    tax = tax_amounts[i] if not pd.isna(tax_amounts[i]) else 0
    calculated_total = lab + mat + tax
    rounding_diff = np.round(random.uniform(-0.05, 0.05), 2)
    total_amounts.append(np.round(calculated_total + rounding_diff, 2))

# Categorical fields
payment_status_list = ['paid', 'unpaid', 'partial']
payment_statuses = [random.choice(payment_status_list) for _ in range(N_ROWS)]
payment_statuses[5] = 'PaRTiaL' # Non-normalized
payment_statuses[6] = 'PENDING' # Unknown/Error value

payment_method_list = ['cash', 'card', 'bank_transfer', 'check', 'online']
payment_methods = [random.choice(payment_method_list + [np.nan]) for _ in range(N_ROWS)]
payment_methods[7] = 'Crypto' # Unknown value (to map to 'other')

source_list = ['website', 'referral', 'walk-in', 'facebook', 'yelp']
sources = [random.choice(source_list + [np.nan]) for _ in range(N_ROWS)]

notes_list = ['First-time customer.', 'Rush job.', 'Follow-up needed next month.', 'No issues.', np.nan]
notes = [random.choice(notes_list) for _ in range(N_ROWS)]

# Create DataFrame
data = pd.DataFrame({
    'date': dates,
    'job_id': job_ids,
    'client_name': client_names,
    'service_type': service_types,
    'labor_amount': labor_amounts,
    'materials_amount': materials_amounts,
    'tax_amount': tax_amounts,
    'total_amount': total_amounts,
    'payment_status': payment_statuses,
    'payment_method': payment_methods,
    'source': sources,
    'notes': notes
})

output_file = '../data/raw/transactions.csv'
data.to_csv(output_file, index=False)
print(f'Data saved to {output_file}')
