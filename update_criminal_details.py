import pandas as pd
import random
from faker import Faker

# Initialize Faker to generate realistic names
fake = Faker()

# Define paths
CRIMINAL_REPORTS_FILE = 'criminal_reports.csv'

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

# Read the current criminal records
df = pd.read_csv(CRIMINAL_REPORTS_FILE)

# Update each record with random details
for idx, row in df.iterrows():
    # Skip records that already have detailed information
    if pd.notna(row['crimes']) and pd.notna(row['area_of_crime']) and row['crimes'] != 'Unknown' and row['area_of_crime'] != 'Unknown':
        continue

    # Generate a more realistic name if it's in the format "Criminal X"
    if row['name'].startswith('Criminal '):
        df.at[idx, 'name'] = fake.name()

    # Generate 1-3 random crimes
    num_crimes = random.randint(1, 3)
    selected_crimes = random.sample(crimes_list, num_crimes)
    crimes_str = ', '.join(selected_crimes)

    # Generate 1-2 random areas
    num_areas = random.randint(1, 2)
    selected_areas = random.sample(areas_list, num_areas)
    areas_str = ', '.join(selected_areas)

    # Update the record
    df.at[idx, 'crimes'] = crimes_str
    df.at[idx, 'area_of_crime'] = areas_str

# Save the updated DataFrame
df.to_csv(CRIMINAL_REPORTS_FILE, index=False)

print(f"Successfully updated {len(df)} criminal records with detailed information.")
