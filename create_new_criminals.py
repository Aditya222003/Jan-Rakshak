import pandas as pd
import random
import os
import shutil
from faker import Faker

# Initialize Faker to generate realistic names
fake = Faker()

# Define paths
CRIMINAL_REPORTS_FILE = 'criminal_reports.csv'
PHOTOS_DIR = 'static/dataset/photos'
VIEW_RECORDS_FOLDER = 'uploads/view_records'

# Ensure the view_records folder exists
os.makedirs(VIEW_RECORDS_FOLDER, exist_ok=True)

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

# Get all image files from the photos directory
try:
    photo_files = []
    for i in range(1, 201):
        filename = f"{i}.jpg"
        photo_files.append(filename)
except Exception as e:
    print(f"Error creating filenames: {str(e)}")
    photo_files = [f"{i}.jpg" for i in range(1, 201)]

# Create a new DataFrame with the photo files
data = []
for photo_file in photo_files:
    # Extract numeric ID from filename
    import re
    match = re.search(r'(\d+)', photo_file)
    if match:
        numeric_id = int(match.group(1))
        
        # Generate random data
        name = fake.name()
        gender = 'male' if numeric_id % 2 == 0 else 'female'
        age = (numeric_id % 50) + 18  # Age between 18-67
        
        # Generate 1-3 random crimes
        num_crimes = random.randint(1, 3)
        selected_crimes = random.sample(crimes_list, num_crimes)
        crimes_str = ', '.join(selected_crimes)
        
        # Generate 1-2 random areas
        num_areas = random.randint(1, 2)
        selected_areas = random.sample(areas_list, num_areas)
        areas_str = ', '.join(selected_areas)
        
        data.append({
            'sketch_filename': photo_file,
            'name': name,
            'gender': gender,
            'age': age,
            'crimes': crimes_str,
            'area_of_crime': areas_str
        })

# Create a new DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to CSV
df.to_csv(CRIMINAL_REPORTS_FILE, index=False)

# Copy images from static/dataset/photos to uploads/view_records
for photo_file in photo_files:
    source_path = os.path.join(PHOTOS_DIR, photo_file)
    dest_path = os.path.join(VIEW_RECORDS_FOLDER, photo_file)
    
    # Check if source file exists
    if os.path.exists(source_path):
        try:
            shutil.copy2(source_path, dest_path)
            print(f"Copied {photo_file} to {VIEW_RECORDS_FOLDER}")
        except Exception as e:
            print(f"Error copying {photo_file}: {str(e)}")
    else:
        print(f"Source file not found: {source_path}")

print(f"Successfully created {len(df)} criminal records with detailed information.")
