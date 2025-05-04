import os
import pandas as pd
import shutil

# Define paths
CRIMINAL_REPORTS_FILE = 'criminal_reports.csv'
WANTED_CRIMINALS_FILE = 'wanted_criminals.csv'
VIEW_RECORDS_FOLDER = 'uploads/view_records'
STATIC_CRIMINALS_FOLDER = 'static/default_criminals'

def backup_all_criminal_images():
    """Backup all criminal images to static/default_criminals directory"""
    print("Starting backup of all criminal images...")
    
    # Create the static/default_criminals directory if it doesn't exist
    os.makedirs(STATIC_CRIMINALS_FOLDER, exist_ok=True)
    
    # Get all image filenames from criminal_reports.csv
    if os.path.exists(CRIMINAL_REPORTS_FILE):
        try:
            df = pd.read_csv(CRIMINAL_REPORTS_FILE)
            if 'sketch_filename' in df.columns:
                image_filenames = df['sketch_filename'].dropna().unique().tolist()
                print(f"Found {len(image_filenames)} unique image filenames in criminal_reports.csv")
                
                # Backup each image
                for filename in image_filenames:
                    if filename and str(filename) != 'nan':
                        source_path = os.path.join(VIEW_RECORDS_FOLDER, filename)
                        target_path = os.path.join(STATIC_CRIMINALS_FOLDER, filename)
                        
                        # If the image exists in the view_records folder, copy it to static/default_criminals
                        if os.path.exists(source_path) and not os.path.exists(target_path):
                            try:
                                shutil.copy2(source_path, target_path)
                                print(f"Backed up {filename} to static/default_criminals")
                            except Exception as e:
                                print(f"Error backing up {filename}: {str(e)}")
                        elif os.path.exists(target_path):
                            print(f"Image {filename} already backed up")
                        else:
                            print(f"Image {filename} not found in view_records folder")
            else:
                print("No sketch_filename column found in criminal_reports.csv")
        except Exception as e:
            print(f"Error reading criminal_reports.csv: {str(e)}")
    else:
        print(f"Criminal reports file {CRIMINAL_REPORTS_FILE} does not exist")
    
    # Get all image filenames from wanted_criminals.csv
    if os.path.exists(WANTED_CRIMINALS_FILE):
        try:
            df = pd.read_csv(WANTED_CRIMINALS_FILE)
            if 'image_filename' in df.columns:
                image_filenames = df['image_filename'].dropna().unique().tolist()
                print(f"Found {len(image_filenames)} unique image filenames in wanted_criminals.csv")
                
                # Backup each image
                for filename in image_filenames:
                    if filename and str(filename) != 'nan':
                        source_path = os.path.join(VIEW_RECORDS_FOLDER, filename)
                        target_path = os.path.join(STATIC_CRIMINALS_FOLDER, filename)
                        
                        # If the image exists in the view_records folder, copy it to static/default_criminals
                        if os.path.exists(source_path) and not os.path.exists(target_path):
                            try:
                                shutil.copy2(source_path, target_path)
                                print(f"Backed up {filename} to static/default_criminals")
                            except Exception as e:
                                print(f"Error backing up {filename}: {str(e)}")
                        elif os.path.exists(target_path):
                            print(f"Image {filename} already backed up")
                        else:
                            print(f"Image {filename} not found in view_records folder")
            else:
                print("No image_filename column found in wanted_criminals.csv")
        except Exception as e:
            print(f"Error reading wanted_criminals.csv: {str(e)}")
    else:
        print(f"Wanted criminals file {WANTED_CRIMINALS_FILE} does not exist")
    
    print("Finished backup of all criminal images")

if __name__ == "__main__":
    backup_all_criminal_images()
