import pandas as pd
import numpy as np

# Read the crop recommendation dataset
crop_df = pd.read_csv('../Crop_recommendationV2.csv')

# Read the UPAG processed crop calendar
upag_df = pd.read_csv('../upag_crop_calendar/upag_crop_calendar_processed.csv')

print("Crop recommendation dataset shape:", crop_df.shape)
print("UPAG crop calendar shape:", upag_df.shape)

# Get unique crops from both datasets
print("\nUnique crops in recommendation dataset:")
print(crop_df['label'].unique())

print("\nUnique crops in UPAG calendar:")
print(upag_df['crop'].unique())

# Create a mapping dictionary from UPAG data
# We'll aggregate by crop to get the most common season and harvesting info
def get_unique_months(x):
    """Get unique months from comma-separated values, sorted by month order"""
    months_order = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
    
    all_months = []
    for val in x.dropna():
        if val:
            all_months.extend([m.strip() for m in val.split(',')])
    
    # Get unique months
    unique_months = list(set(all_months))
    
    # Sort by month order
    unique_months.sort(key=lambda x: months_order.get(x, 0))
    
    return ', '.join(unique_months) if unique_months else ''

crop_info = upag_df.groupby('crop').agg({
    'season': lambda x: x.mode()[0] if not x.mode().empty else '',
    'harvesting_st_month': lambda x: x.mode()[0] if not x.mode().empty else '',
    'harvesting_end_month': lambda x: x.mode()[0] if not x.mode().empty else '',
    'harvesting_time': get_unique_months,
    'sowing_time_period': get_unique_months
}).reset_index()

print("\nCrop info mapping:")
print(crop_info)

# Create a manual mapping dictionary for crop name variations
crop_name_mapping = {
    'rice': 'Rice',
    'maize': 'Maize',
    'chickpea': 'Gram',
    'kidneybeans': '',  # Not in UPAG
    'pigeonpeas': 'Tur',
    'mothbeans': 'Kulthi',
    'mungbean': 'Moong',
    'blackgram': 'Urad',
    'lentil': 'Lentil',
    'pomegranate': '',  # Not in UPAG
    'banana': '',  # Not in UPAG
    'mango': '',  # Not in UPAG
    'grapes': '',  # Not in UPAG
    'watermelon': '',  # Not in UPAG
    'muskmelon': '',  # Not in UPAG
    'apple': '',  # Not in UPAG
    'orange': '',  # Not in UPAG
    'papaya': '',  # Not in UPAG
    'coconut': '',  # Not in UPAG
    'cotton': 'Cotton',
    'jute': 'Jute',
    'coffee': ''  # Not in UPAG
}

# Function to match crop names using the mapping dictionary
def match_crop_name(crop_label, crop_info_df):
    crop_label_lower = crop_label.lower().strip()
    
    # Use manual mapping first
    if crop_label_lower in crop_name_mapping:
        mapped_name = crop_name_mapping[crop_label_lower]
        if mapped_name:  # If not empty string
            match = crop_info_df[crop_info_df['crop'] == mapped_name]
            if not match.empty:
                return match.iloc[0]
        else:
            return None  # Explicitly marked as not in UPAG
    
    # Direct match (fallback)
    direct_match = crop_info_df[crop_info_df['crop'].str.lower() == crop_label_lower]
    if not direct_match.empty:
        return direct_match.iloc[0]
    
    # Try partial match for variations (fallback)
    for idx, row in crop_info_df.iterrows():
        upag_crop = row['crop'].lower()
        if crop_label_lower in upag_crop or upag_crop in crop_label_lower:
            return row
    
    # If no match found, return None
    return None

# Apply the matching function to add season and harvesting info
crop_info_list = []
for crop_label in crop_df['label']:
    match = match_crop_name(crop_label, crop_info)
    if match is not None:
        crop_info_list.append({
            'season': match['season'],
            'harvesting_st_month': match['harvesting_st_month'],
            'harvesting_end_month': match['harvesting_end_month'],
            'harvesting_time': match['harvesting_time'],
            'sowing_time_period': match['sowing_time_period']
        })
    else:
        crop_info_list.append({
            'season': '',
            'harvesting_st_month': '',
            'harvesting_end_month': '',
            'harvesting_time': '',
            'sowing_time_period': ''
        })

# Create DataFrame from the list
crop_info_df = pd.DataFrame(crop_info_list)

# Concatenate with original crop dataframe
processed_df = pd.concat([crop_df, crop_info_df], axis=1)

# Check which crops were matched
matched_crops = processed_df[processed_df['season'] != '']['label'].unique()
unmatched_crops = processed_df[processed_df['season'] == '']['label'].unique()

print(f"\nMatched crops: {len(matched_crops)}")
print(matched_crops)

print(f"\nUnmatched crops: {len(unmatched_crops)}")
print(unmatched_crops)

# Save the processed dataset
processed_df.to_csv('crop_recommendation_processed.csv', index=False)

print("\nProcessing complete!")
print(f"Processed dataset saved to: crop_recommendation_processed.csv")
print(f"Total rows: {len(processed_df)}")
print(f"Rows with season info: {len(processed_df[processed_df['season'] != ''])}")
