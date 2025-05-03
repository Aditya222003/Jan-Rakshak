import pandas as pd
import os
import shutil
import re
import glob

# Define paths
CRIMINAL_REPORTS_FILE = 'criminal_reports.csv'
PHOTOS_DIR = 'static/dataset/photos'
VIEW_RECORDS_FOLDER = 'uploads/view_records'

# Ensure the view_records folder exists
os.makedirs(VIEW_RECORDS_FOLDER, exist_ok=True)

# Step 1: Get all image files from the photos directory
try:
    photo_files = glob.glob(os.path.join(PHOTOS_DIR, '*.*'))

    # If no files found in the specified directory, use a fallback approach
    if not photo_files:
        print(f"No files found in {PHOTOS_DIR}. Using numbered filenames instead.")
        # Generate 200 numbered filenames (1.jpg to 200.jpg)
        photo_files = [f"{i}.jpg" for i in range(1, 201)]
    else:
        # Use just the filenames, not the full paths
        photo_files = [os.path.basename(f) for f in photo_files]

except Exception as e:
    print(f"Error accessing photo directory: {str(e)}")
    # Fallback to numbered filenames
    photo_files = [f"{i}.jpg" for i in range(1, 201)]

# Step 2: Create a new DataFrame with the photo files
data = []
for photo_file in photo_files:
    # Extract numeric ID from filename
    match = re.search(r'(\d+)', photo_file)
    if match:
        numeric_id = int(match.group(1))

        # Get existing data for this file if it exists in the current CSV
        try:
            df = pd.read_csv(CRIMINAL_REPORTS_FILE)
            existing_row = df[df['sketch_filename'] == photo_file]

            if not existing_row.empty:
                # Use existing data
                row = existing_row.iloc[0].to_dict()
                row['numeric_id'] = numeric_id
                data.append(row)
            else:
                # Create new random data with detailed crimes and areas
                import random

                # Define lists for random data generation
                crimes_list = [
                    'Burglary', 'Fraud', 'Assault', 'Cybercrime', 'Drug Trafficking',
                    'Shoplifting', 'Homicide', 'Armed Robbery', 'Vandalism', 'Car Theft',
                    'Arson', 'Kidnapping', 'Illegal Arms Dealing', 'Credit Card Fraud',
                    'Domestic Violence', 'Money Laundering', 'Human Trafficking', 'Extortion',
                    'Identity Theft', 'Counterfeiting'
                ]

                areas_list = [
                    'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
                    'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville',
                    'Fort Worth', 'Columbus', 'Charlotte', 'San Francisco', 'Indianapolis',
                    'Seattle', 'Denver', 'Washington DC', 'Boston', 'Las Vegas', 'Portland',
                    'Oklahoma City', 'Detroit', 'Memphis', 'Louisville', 'Baltimore', 'Milwaukee',
                    'Albuquerque', 'Tucson', 'Fresno', 'Sacramento', 'Long Beach', 'Kansas City',
                    'Mesa', 'Atlanta', 'Colorado Springs', 'Raleigh', 'Omaha', 'Miami', 'Oakland',
                    'Minneapolis', 'Tulsa', 'Cleveland', 'Wichita', 'Arlington', 'New Orleans',
                    'Bakersfield', 'Tampa', 'Honolulu', 'Aurora', 'Anaheim', 'Santa Ana',
                    'St. Louis', 'Riverside', 'Corpus Christi', 'Lexington', 'Pittsburgh',
                    'Anchorage', 'Stockton', 'Cincinnati', 'St. Paul', 'Toledo', 'Newark',
                    'Greensboro', 'Plano', 'Henderson', 'Lincoln', 'Buffalo', 'Fort Wayne',
                    'Jersey City', 'Chula Vista', 'Orlando', 'St. Petersburg', 'Norfolk',
                    'Chandler', 'Laredo', 'Madison', 'Durham', 'Lubbock', 'Winston-Salem',
                    'Garland', 'Glendale', 'Hialeah', 'Reno', 'Baton Rouge', 'Irvine', 'Chesapeake',
                    'Irving', 'Scottsdale', 'North Las Vegas', 'Fremont', 'Gilbert', 'San Bernardino',
                    'Boise', 'Birmingham', 'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai',
                    'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'
                ]

                # Generate 1-3 random crimes
                num_crimes = random.randint(1, 3)
                selected_crimes = random.sample(crimes_list, num_crimes)
                crimes_str = ', '.join(selected_crimes)

                # Generate 1-2 random areas
                num_areas = random.randint(1, 2)
                selected_areas = random.sample(areas_list, num_areas)
                areas_str = ', '.join(selected_areas)

                # Generate a more realistic name
                from faker import Faker
                fake = Faker()

                data.append({
                    'sketch_filename': photo_file,
                    'name': fake.name(),
                    'gender': 'male' if numeric_id % 2 == 0 else 'female',
                    'age': (numeric_id % 50) + 18,  # Age between 18-67
                    'crimes': crimes_str,
                    'area_of_crime': areas_str,
                    'numeric_id': numeric_id
                })
        except Exception as e:
            print(f"Error processing file {photo_file}: {str(e)}")
            # Create minimal data with some random details
            import random

            # Define simple lists for random data generation
            crimes_list = ['Theft', 'Fraud', 'Assault', 'Robbery', 'Vandalism']
            areas_list = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']

            # Generate random crime and area
            crime = random.choice(crimes_list)
            area = random.choice(areas_list)

            data.append({
                'sketch_filename': photo_file,
                'name': f"Criminal {numeric_id}",
                'gender': 'unknown',
                'age': 30,
                'crimes': crime,
                'area_of_crime': area,
                'numeric_id': numeric_id
            })

# Create a new DataFrame and sort by numeric_id
new_df = pd.DataFrame(data)
new_df = new_df.sort_values(by='numeric_id').reset_index(drop=True)

# Step 3: Copy images from static/dataset/photos to uploads/view_records
for _, row in new_df.iterrows():
    filename = row['sketch_filename']
    source_path = os.path.join(PHOTOS_DIR, filename)
    dest_path = os.path.join(VIEW_RECORDS_FOLDER, filename)

    # Check if source file exists
    if os.path.exists(source_path):
        try:
            shutil.copy2(source_path, dest_path)
            print(f"Copied {filename} to {VIEW_RECORDS_FOLDER}")
        except Exception as e:
            print(f"Error copying {filename}: {str(e)}")
    else:
        print(f"Source file not found: {source_path}")

# Step 4: Save the updated DataFrame (without the numeric_id column)
new_df = new_df.drop(columns=['numeric_id'])
new_df.to_csv(CRIMINAL_REPORTS_FILE, index=False)

print(f"Successfully processed {len(new_df)} criminal records.")
