import pandas as pd
import os

def stratified_split(df, label_col, test_size=0.2, random_state=42):
    """
    Perform stratified split by label to ensure each class is represented
    proportionally in both training and testing sets.
    
    Args:
        df: DataFrame to split
        label_col: Column name to stratify by
        test_size: Proportion for test set (default 0.2)
        random_state: Random seed for reproducibility
    
    Returns:
        train_df, test_df: Split DataFrames
    """
    train_list = []
    test_list = []
    
    # Group by label and split each group
    for label, group in df.groupby(label_col):
        # Shuffle the group
        group_shuffled = group.sample(frac=1, random_state=random_state).reset_index(drop=True)
        
        # Calculate split point
        split_idx = int(len(group_shuffled) * (1 - test_size))
        
        # Split into train and test
        train_list.append(group_shuffled.iloc[:split_idx])
        test_list.append(group_shuffled.iloc[split_idx:])
    
    # Concatenate all groups
    train_df = pd.concat(train_list, ignore_index=True)
    test_df = pd.concat(test_list, ignore_index=True)
    
    # Shuffle the final datasets
    train_df = train_df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    test_df = test_df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    return train_df, test_df

# Set the path to the processed dataset
dataset_path = r'C:\D-Drive\Manu\Academics\Final year project\Windsurf\CR_ML\datasets\crop_recommendation_processed.csv'

# Read the dataset
print("Loading dataset...")
df = pd.read_csv(dataset_path)
print(f"Total rows in dataset: {len(df)}")

# Display unique crops and their counts
print("\nUnique crops in dataset:")
print(df['label'].value_counts())
print(f"\nTotal unique crops: {df['label'].nunique()}")

# Create output directories
output_dir = r'C:\D-Drive\Manu\Academics\Final year project\Windsurf\CR_ML\splitting_datasets'
train_dir = os.path.join(output_dir, 'training_datasets')
test_dir = os.path.join(output_dir, 'testing_datasets')

os.makedirs(train_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

print(f"\nCreated directories:")
print(f"Training: {train_dir}")
print(f"Testing: {test_dir}")

# Perform stratified split by crop (label column)
# This ensures each crop is represented in both training and testing sets proportionally
print("\nPerforming stratified 80-20 split by crop...")
train_df, test_df = stratified_split(df, 'label', test_size=0.2, random_state=42)

print(f"Training set size: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
print(f"Testing set size: {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")

# Verify that all crops are present in both sets
print("\nVerifying crop distribution:")
print("\nTraining set crop counts:")
print(train_df['label'].value_counts())
print(f"\nUnique crops in training: {train_df['label'].nunique()}")

print("\nTesting set crop counts:")
print(test_df['label'].value_counts())
print(f"\nUnique crops in testing: {test_df['label'].nunique()}")

# Check if any crop is missing from either set
train_crops = set(train_df['label'].unique())
test_crops = set(test_df['label'].unique())
all_crops = set(df['label'].unique())

missing_in_train = all_crops - train_crops
missing_in_test = all_crops - test_crops

if missing_in_train:
    print(f"\nWARNING: Crops missing from training set: {missing_in_train}")
else:
    print("\n[OK] All crops present in training set")

if missing_in_test:
    print(f"\nWARNING: Crops missing from testing set: {missing_in_test}")
else:
    print("[OK] All crops present in testing set")

# Save the split datasets
train_output_path = os.path.join(train_dir, 'crop_recommendation_train.csv')
test_output_path = os.path.join(test_dir, 'crop_recommendation_test.csv')

train_df.to_csv(train_output_path, index=False)
test_df.to_csv(test_output_path, index=False)

print(f"\nDatasets saved successfully:")
print(f"Training: {train_output_path}")
print(f"Testing: {test_output_path}")

print("\nSplitting complete!")
