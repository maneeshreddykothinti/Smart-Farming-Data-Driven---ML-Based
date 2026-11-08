import pandas as pd

# Load the datasets
crop_recommendation_df = pd.read_csv('../crop_recommendation_processed/crop_recommendation_processed.csv')
upag_df = pd.read_csv('../upag_crop_calendar/upag_crop_calendar_processed.csv')

# Get unique crops from crop_recommendation dataset
crop_rec_crops = set(crop_recommendation_df['label'].unique())
print(f"Crops in crop_recommendation dataset: {len(crop_rec_crops)}")
print(crop_rec_crops)

# Get unique crops from UPAG dataset
upag_crops = set(upag_df['crop'].unique())
print(f"\nCrops in UPAG dataset: {len(upag_crops)}")
print(upag_crops)

# Define mapping between crop_recommendation names and UPAG names
crop_name_mapping = {
    'rice': 'Rice',
    'maize': 'Maize',
    'chickpea': 'Gram',
    'pigeonpeas': 'Tur',
    'mothbeans': 'Kulthi',
    'mungbean': 'Moong',
    'blackgram': 'Urad',
    'lentil': 'Lentil',
    'cotton': 'Cotton',
    'jute': 'Jute'
}

# Map crop_recommendation crops to UPAG crop names
mapped_crop_rec_crops = set()
for crop in crop_rec_crops:
    if crop in crop_name_mapping:
        mapped_crop_rec_crops.add(crop_name_mapping[crop])
    else:
        mapped_crop_rec_crops.add(crop)

print(f"\nMapped crop_recommendation crops to UPAG names: {len(mapped_crop_rec_crops)}")
print(mapped_crop_rec_crops)

# Find intersection
intersected_crops = mapped_crop_rec_crops.intersection(upag_crops)
print(f"\nIntersected crops found in UPAG: {len(intersected_crops)}")
print(intersected_crops)

# Crops in crop_recommendation but not in UPAG
missing_crops = mapped_crop_rec_crops - upag_crops
print(f"\nCrops in crop_recommendation but NOT in UPAG: {len(missing_crops)}")
print(missing_crops)

# Create reverse mapping for filtering UPAG data
reverse_mapping = {v: k for k, v in crop_name_mapping.items()}

# Filter UPAG dataset to only include intersected crops
filtered_upag_df = upag_df[upag_df['crop'].isin(intersected_crops)].copy()

# Add a column with the original crop_recommendation name
filtered_upag_df['label'] = filtered_upag_df['crop'].map(reverse_mapping)

# Reorder columns to have label first
cols = ['label'] + [col for col in filtered_upag_df.columns if col != 'label']
filtered_upag_df = filtered_upag_df[cols]

# Save the intersected dataset
filtered_upag_df.to_csv('crop_intersected_dataset.csv', index=False)
print(f"\nSaved crop_intersected_dataset.csv with {len(filtered_upag_df)} rows")
print(f"Columns: {filtered_upag_df.columns.tolist()}")

# Print summary
print(f"\nSummary:")
print(f"- Total crops in crop_recommendation: {len(crop_rec_crops)}")
print(f"- Total crops in UPAG: {len(upag_crops)}")
print(f"- Intersected crops (in both): {len(intersected_crops)}")
print(f"- Missing crops (need synthetic data): {len(missing_crops)}")
