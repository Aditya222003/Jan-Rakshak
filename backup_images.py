import os
import csv
import shutil

# Define paths
CRIMINAL_REPORTS_FILE = 'criminal_reports.csv'
WANTED_CRIMINALS_FILE = 'wanted_criminals.csv'
VIEW_RECORDS_FOLDER = 'uploads/view_records'
STATIC_CRIMINALS_FOLDER = 'static/default_criminals'

def read_csv_column(file_path, column_name):
    """Read a specific column from a CSV file and return unique values"""
    if not os.path.exists(file_path):
        return []

    unique_values = set()
    try:
        with open(file_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            if column_name not in reader.fieldnames:
                print(f"Column '{column_name}' not found in {file_path}")
                return []

            for row in reader:
                value = row.get(column_name, '')
                if value and value.strip() and value.lower() != 'nan':
                    unique_values.add(value)

        return list(unique_values)
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return []

def backup_all_criminal_images():
    """Backup all criminal images to static/default_criminals directory"""
    print("Starting backup of all criminal images...")

    # Create the static/default_criminals directory if it doesn't exist
    os.makedirs(STATIC_CRIMINALS_FOLDER, exist_ok=True)

    total_backed_up = 0
    total_already_backed_up = 0
    total_not_found = 0

    # Get all image filenames from criminal_reports.csv
    image_filenames = read_csv_column(CRIMINAL_REPORTS_FILE, 'sketch_filename')
    print(f"Found {len(image_filenames)} unique image filenames in criminal_reports.csv")

    # Backup each image
    backed_up_count = 0
    already_backed_up_count = 0
    not_found_count = 0

    for filename in image_filenames:
        source_path = os.path.join(VIEW_RECORDS_FOLDER, filename)
        target_path = os.path.join(STATIC_CRIMINALS_FOLDER, filename)

        # If the image exists in the view_records folder, copy it to static/default_criminals
        if os.path.exists(source_path) and not os.path.exists(target_path):
            try:
                shutil.copy2(source_path, target_path)
                backed_up_count += 1
            except Exception as e:
                print(f"Error backing up {filename}: {str(e)}")
        elif os.path.exists(target_path):
            already_backed_up_count += 1
        else:
            not_found_count += 1

    print(f"Criminal reports: Backed up {backed_up_count} new images, {already_backed_up_count} already backed up, {not_found_count} not found")
    total_backed_up += backed_up_count
    total_already_backed_up += already_backed_up_count
    total_not_found += not_found_count

    # Get all image filenames from wanted_criminals.csv
    image_filenames = read_csv_column(WANTED_CRIMINALS_FILE, 'image_filename')
    print(f"Found {len(image_filenames)} unique image filenames in wanted_criminals.csv")

    # Backup each image
    backed_up_count = 0
    already_backed_up_count = 0
    not_found_count = 0

    for filename in image_filenames:
        source_path = os.path.join(VIEW_RECORDS_FOLDER, filename)
        target_path = os.path.join(STATIC_CRIMINALS_FOLDER, filename)

        # If the image exists in the view_records folder, copy it to static/default_criminals
        if os.path.exists(source_path) and not os.path.exists(target_path):
            try:
                shutil.copy2(source_path, target_path)
                backed_up_count += 1
            except Exception as e:
                print(f"Error backing up {filename}: {str(e)}")
        elif os.path.exists(target_path):
            already_backed_up_count += 1
        else:
            not_found_count += 1

    print(f"Wanted criminals: Backed up {backed_up_count} new images, {already_backed_up_count} already backed up, {not_found_count} not found")
    total_backed_up += backed_up_count
    total_already_backed_up += already_backed_up_count
    total_not_found += not_found_count

    print(f"Backup complete: {total_backed_up} new images backed up, {total_already_backed_up} already backed up, {total_not_found} not found")

if __name__ == "__main__":
    backup_all_criminal_images()
