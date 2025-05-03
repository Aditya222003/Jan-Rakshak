import pandas as pd
import os
import random
from faker import Faker
import glob

# Initialize Faker to generate realistic names
fake = Faker()

# Define paths
CRIMINAL_REPORTS_FILE = 'criminal_reports.csv'
PHOTOS_DIR = 'static/dataset/photos'
VIEW_RECORDS_FOLDER = 'uploads/view_records'

# Ensure the view_records folder exists
os.makedirs(VIEW_RECORDS_FOLDER, exist_ok=True)

# Define lists for random data generation
genders = ['male', 'female']
crimes = [
    'Burglary', 'Fraud', 'Assault', 'Cybercrime', 'Drug Trafficking', 
    'Shoplifting', 'Homicide', 'Armed Robbery', 'Vandalism', 'Car Theft',
    'Arson', 'Kidnapping', 'Illegal Arms Dealing', 'Credit Card Fraud',
    'Domestic Violence', 'Money Laundering', 'Human Trafficking', 'Extortion',
    'Identity Theft', 'Counterfeiting'
]
areas = [
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

# Step 1: Clear the existing criminal_reports.csv file
# Create a new empty CSV with just the headers
df = pd.DataFrame(columns=['sketch_filename', 'name', 'gender', 'age', 'crimes', 'area_of_crime'])
df.to_csv(CRIMINAL_REPORTS_FILE, index=False)

# Step 2: Get list of image files from the photos directory
try:
    photo_files = glob.glob(os.path.join(PHOTOS_DIR, '*.*'))
    
    # If no files found in the specified directory, use a fallback approach
    if not photo_files:
        print(f"No files found in {PHOTOS_DIR}. Using numbered filenames instead.")
        # Generate 200 numbered filenames (101.jpg to 300.jpg)
        photo_files = [f"{i}.jpg" for i in range(101, 301)]
    else:
        # Use just the filenames, not the full paths
        photo_files = [os.path.basename(f) for f in photo_files]
        
    # Limit to 200 files
    photo_files = photo_files[:200]
    
except Exception as e:
    print(f"Error accessing photo directory: {str(e)}")
    # Fallback to numbered filenames
    photo_files = [f"{i}.jpg" for i in range(101, 301)]

# Step 3: Generate 200 new criminal records
criminals = []

for i, photo_file in enumerate(photo_files):
    # Generate random data for each criminal
    name = fake.name()
    gender = random.choice(genders)
    age = random.randint(18, 65)
    crime = random.choice(crimes)
    area = random.choice(areas)
    
    # Add to the list
    criminals.append({
        'sketch_filename': photo_file,
        'name': name,
        'gender': gender,
        'age': age,
        'crimes': crime,
        'area_of_crime': area
    })
    
    # Copy the image file to the view_records folder if it exists in the source directory
    source_path = os.path.join(PHOTOS_DIR, photo_file)
    if os.path.exists(source_path):
        import shutil
        dest_path = os.path.join(VIEW_RECORDS_FOLDER, photo_file)
        try:
            shutil.copy2(source_path, dest_path)
            print(f"Copied {photo_file} to {VIEW_RECORDS_FOLDER}")
        except Exception as e:
            print(f"Error copying {photo_file}: {str(e)}")

# Step 4: Save the new criminal records to the CSV file
criminals_df = pd.DataFrame(criminals)
criminals_df.to_csv(CRIMINAL_REPORTS_FILE, index=False)

print(f"Successfully generated {len(criminals)} criminal records.")
