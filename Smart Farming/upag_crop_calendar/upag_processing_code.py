import pandas as pd
import re

# Read the Excel file
df = pd.read_excel('upag_crop_calendar.xlsx')

# Remove rows where season is '-' (empty/invalid season)
df = df[df['season'] != '-'].copy()

# Month columns and their order
month_cols = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
month_names = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

# Function to extract harvesting start month (first #9AC23C occurrence)
def get_harvest_start(row):
    for i, col in enumerate(month_cols):
        val = str(row[col]) if pd.notna(row[col]) else ''
        if '#9AC23C' in val:
            return month_names[i]
    return ''

# Function to extract harvesting end month (last occurrence - could be #9AC23C or #3187B9)
def get_harvest_end(row):
    for i in range(len(month_cols) - 1, -1, -1):
        col = month_cols[i]
        val = str(row[col]) if pd.notna(row[col]) else ''
        if '#9AC23C' in val or '#3187B9' in val:
            return month_names[i]
    return ''

# Function to extract harvesting time (all months with #9AC23C)
def get_harvest_time(row):
    harvest_months = []
    for i, col in enumerate(month_cols):
        val = str(row[col]) if pd.notna(row[col]) else ''
        if '#9AC23C' in val:
            harvest_months.append(month_names[i])
    return ', '.join(harvest_months) if harvest_months else ''

# Function to extract sowing time period (all months with #3187B9)
def get_sowing_time(row):
    sowing_months = []
    for i, col in enumerate(month_cols):
        val = str(row[col]) if pd.notna(row[col]) else ''
        if '#3187B9' in val:
            sowing_months.append(month_names[i])
    return ', '.join(sowing_months) if sowing_months else ''

# Apply the functions to create new columns
df['harvesting_st_month'] = df.apply(get_harvest_start, axis=1)
df['harvesting_end_month'] = df.apply(get_harvest_end, axis=1)
df['harvesting_time'] = df.apply(get_harvest_time, axis=1)
df['sowing_time_period'] = df.apply(get_sowing_time, axis=1)

# Select and rename the required columns
output_df = df[[
    'crops',
    'state',
    'season',
    'harvesting_st_month',
    'harvesting_end_month',
    'harvesting_time',
    'sowing_time_period'
]].copy()

# Rename columns to match requirements
output_df.columns = [
    'crop',
    'state',
    'season',
    'harvesting_st_month',
    'harvesting_end_month',
    'harvesting_time',
    'sowing_time_period'
]

# Remove rows that have no harvesting or sowing data
# Replace empty strings with NaN for proper filtering
output_df = output_df.replace('', pd.NA)
output_df = output_df.dropna(subset=['harvesting_st_month', 'harvesting_end_month', 'harvesting_time', 'sowing_time_period'], how='all')

# Reset index
output_df = output_df.reset_index(drop=True)

# Fill NaN back with empty strings for cleaner output
output_df = output_df.fillna('')

# Save to Excel first
output_df.to_excel('upag_crop_calendar/upag_crop_calendar_processed.xlsx', index=False)

# Convert to CSV
output_df.to_csv('upag_crop_calendar/upag_crop_calendar_processed.csv', index=False)

print(f"Processing complete!")
print(f"Total rows after filtering: {len(output_df)}")
print(f"Files saved:")
print(f"  - upag_crop_calendar/upag_crop_calendar_processed.xlsx")
print(f"  - upag_crop_calendar/upag_crop_calendar_processed.csv")

# Print some stats
print(f"\nRows with harvesting time: {len(output_df[output_df['harvesting_time'] != ''])}")
print(f"Rows with sowing time: {len(output_df[output_df['sowing_time_period'] != ''])}")
print(f"Rows with both: {len(output_df[(output_df['harvesting_time'] != '') & (output_df['sowing_time_period'] != '')])}")
