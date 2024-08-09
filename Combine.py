import pandas as pd
import os

# Directory containing the CSV files
data_dir = '/Users/aabhasbasnet/Downloads/Nepse AI/data'

# Load all CSV files into a single DataFrame
all_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
data_frames = []
for file in all_files:
    file_path = os.path.join(data_dir, file)
    df = pd.read_csv(file_path)
    
    # Extract date from filename (format: MM_DD_YYYY.csv)
    date_str = file.split('.')[0]
    try:
        date = pd.to_datetime(date_str, format='%m_%d_%Y')
    except ValueError:
        print(f"Date parsing error for file: {file}")
        continue
    
    # Add a new column with the extracted date
    df['Date'] = date
    
    data_frames.append(df)

# Combine all DataFrames into one
data = pd.concat(data_frames, ignore_index=True)

# Convert relevant columns to numeric, coercing errors
data['Turnover'] = pd.to_numeric(data['Turnover'], errors='coerce')
data['Close'] = pd.to_numeric(data['Close'], errors='coerce')

# Ensure 'Date' column is in datetime format and sort by it
data['Date'] = pd.to_datetime(data['Date'])
data.sort_values(by='Date', inplace=True)

# Strip any leading or trailing spaces from column names
data.columns = data.columns.str.strip()

# Remove duplicate columns
data = data.loc[:, ~data.columns.duplicated()]

# Check for missing values
print("\nMissing Values:")
print(data[['Turnover', 'Close']].isna().sum())

# Calculate turnover change percentage
data['Turnover Change %'] = data['Turnover'].pct_change(fill_method=None) * 100

# Calculate price change percentage
data['Price Change %'] = data['Close'].pct_change(fill_method=None) * 100

# Print column names to confirm
print("\nColumn Names (stripped):")
print(data.columns)

# Print a sample of the data to verify column values
print("\nSample Data:")
print(data[['Date', 'Symbol', 'Turnover', 'Turnover Change %', 'Close', 'Price Change %']].head(10))

# Define reasonable thresholds
threshold = 10.0  # Threshold for turnover increase
price_increase_threshold = 1.0  # Threshold for price increase

# Detect sudden increases in turnover
sudden_increases = data[data['Turnover Change %'] > threshold]

# Filter records where price also increased
if 'Price Change %' in data.columns:
    affected_prices = sudden_increases.copy()
    
    # Remove duplicates and handle column names correctly
    affected_prices = affected_prices[['Date', 'Symbol', 'Turnover', 'Turnover Change %']]
    affected_prices = affected_prices.merge(data[['Date', 'Symbol', 'Price Change %']], on=['Date', 'Symbol'], how='left')
    
    print("\nColumns in affected_prices before filtering:")
    print(affected_prices.columns)
    
    affected_prices = affected_prices[affected_prices['Price Change %'] > price_increase_threshold]
else:
    print("\n'Price Change %' column is missing.")

# Output the results
print("\nRecords with sudden turnover increases:")
print(sudden_increases[['Date', 'Symbol', 'Turnover', 'Turnover Change %']].to_string(index=False))

print("\nRecords where turnover increase affected price:")
if 'Price Change %' in affected_prices.columns:
    print(affected_prices[['Date', 'Symbol', 'Turnover', 'Turnover Change %', 'Price Change %']].to_string(index=False))
else:
    print("No records with price change percentage available.")
