from feature_matching import find_best_matches
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os
import uuid
import datetime
import csv
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'  # Change this for production!

# Mail configuration
# Option 1: Gmail Configuration with App Password (ACTIVE)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'rauladitya22@gmail.com'  # Replace this with your actual Gmail address
app.config['MAIL_PASSWORD'] = 'ackysmkxuznftgye'  # Replace this with your actual 16-character App Password
app.config['MAIL_DEFAULT_SENDER'] = ('Criminal Identification System', 'rauladitya22@gmail.com')

# Option 2: Outlook/Hotmail Configuration
# app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_USERNAME'] = 'your.email@outlook.com'  # Replace with your Outlook email
# app.config['MAIL_PASSWORD'] = 'your-password'  # Replace with your Outlook password
# app.config['MAIL_DEFAULT_SENDER'] = ('Criminal Identification System', 'your.email@outlook.com')

# Option 3: Yahoo Mail Configuration
# app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_USERNAME'] = 'your.email@yahoo.com'  # Replace with your Yahoo email
# app.config['MAIL_PASSWORD'] = 'your-password'  # Replace with your Yahoo password or app password
# app.config['MAIL_DEFAULT_SENDER'] = ('Criminal Identification System', 'your.email@yahoo.com')
mail = Mail(app)

# Set the upload folder paths
UPLOAD_FOLDER = 'uploads/sketches'
PROOF_FOLDER = 'uploads/proofs'
VIEW_RECORDS_FOLDER = 'uploads/view_records'
EVIDENCE_FOLDER = 'uploads/evidence'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROOF_FOLDER'] = PROOF_FOLDER
app.config['VIEW_RECORDS_FOLDER'] = VIEW_RECORDS_FOLDER
app.config['EVIDENCE_FOLDER'] = EVIDENCE_FOLDER

# CSV file setup
USERS_FILE = 'users.csv'
CRIMINAL_REPORTS_FILE = 'criminal_reports.csv'
PENDING_REPORTS_FILE = 'pending_reports.csv'
WANTED_CRIMINALS_FILE = 'wanted_criminals.csv'
CRIMINAL_SIGHTINGS_FILE = 'criminal_sightings.csv'
ADMIN_CODES_FILE = 'admin_codes.csv'

# Ensure upload directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROOF_FOLDER, exist_ok=True)
os.makedirs(VIEW_RECORDS_FOLDER, exist_ok=True)
os.makedirs(EVIDENCE_FOLDER, exist_ok=True)

# CSV Helper Functions
def write_csv(file_path, headers, rows=None):
    """Write data to a CSV file"""
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        if rows:
            for row in rows:
                writer.writerow(row)

def read_csv(file_path):
    """Read data from a CSV file and return as a list of dictionaries"""
    if not os.path.exists(file_path):
        return []

    with open(file_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)

def append_csv(file_path, row):
    """Append a row to a CSV file"""
    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def init_user_storage():
    """Initialize users CSV file with headers if it doesn't exist"""
    if not os.path.exists(USERS_FILE):
        write_csv(USERS_FILE, ['username', 'email', 'password', 'role'])

def init_reports_storage():
    """Initialize criminal reports CSV file with headers if it doesn't exist"""
    if not os.path.exists(CRIMINAL_REPORTS_FILE):
        write_csv(CRIMINAL_REPORTS_FILE, ['sketch_filename', 'name', 'gender', 'age', 'crimes', 'area_of_crime'])

def init_pending_reports_storage():
    """Initialize pending reports CSV file with headers if it doesn't exist"""
    if not os.path.exists(PENDING_REPORTS_FILE):
        write_csv(PENDING_REPORTS_FILE, ['token', 'sketch_filename', 'first_name', 'last_name', 'age', 'crime', 'arrested', 'proof_filename', 'status', 'submitted_by'])

def backup_all_criminal_images():
    """Backup all criminal images to static/default_criminals directory"""
    print("Starting backup of all criminal images...")

    # Create the static/default_criminals directory if it doesn't exist
    os.makedirs('static/default_criminals', exist_ok=True)

    total_backed_up = 0
    total_already_backed_up = 0
    total_not_found = 0

    # Get all image filenames from criminal_reports.csv
    if os.path.exists(CRIMINAL_REPORTS_FILE):
        try:
            df = pd.read_csv(CRIMINAL_REPORTS_FILE)
            if 'sketch_filename' in df.columns:
                image_filenames = df['sketch_filename'].dropna().unique().tolist()
                print(f"Found {len(image_filenames)} unique image filenames in criminal_reports.csv")

                # Backup each image
                backed_up_count = 0
                already_backed_up_count = 0
                not_found_count = 0

                for filename in image_filenames:
                    if filename and str(filename) != 'nan':
                        source_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], filename)
                        target_path = os.path.join('static/default_criminals', filename)

                        # If the image exists in the view_records folder, copy it to static/default_criminals
                        if os.path.exists(source_path) and not os.path.exists(target_path):
                            try:
                                import shutil
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
                backed_up_count = 0
                already_backed_up_count = 0
                not_found_count = 0

                for filename in image_filenames:
                    if filename and str(filename) != 'nan':
                        source_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], filename)
                        target_path = os.path.join('static/default_criminals', filename)

                        # If the image exists in the view_records folder, copy it to static/default_criminals
                        if os.path.exists(source_path) and not os.path.exists(target_path):
                            try:
                                import shutil
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
            else:
                print("No image_filename column found in wanted_criminals.csv")
        except Exception as e:
            print(f"Error reading wanted_criminals.csv: {str(e)}")
    else:
        print(f"Wanted criminals file {WANTED_CRIMINALS_FILE} does not exist")

    print(f"Backup complete: {total_backed_up} new images backed up, {total_already_backed_up} already backed up, {total_not_found} not found")

def init_wanted_criminals_storage():
    """Initialize wanted criminals CSV file with headers if it doesn't exist"""
    if not os.path.exists(WANTED_CRIMINALS_FILE) or os.path.getsize(WANTED_CRIMINALS_FILE) == 0:
        print(f"Creating new wanted_criminals.csv file with headers")
        # Add some default wanted criminals for testing
        default_criminals = [
            [5, 'Tracy Cobb', '124.jpg', 'Wanted for Arson, Shoplifting, and Counterfeiting in Gilbert and New Orleans. Considered dangerous and may be armed.', 'active'],
            [6, 'Joshua Huang', '196.jpg', 'Wanted for Domestic Violence in Tampa and Raleigh. Has a history of violent behavior and should be approached with caution.', 'active'],
            [7, 'Alex Parrish', '67.jpg', 'Wanted for Kidnapping and Vandalism in Reno. Known to target vulnerable individuals and has evaded capture multiple times.', 'active'],
            [8, 'William Chen', '77.jpg', 'Wanted for Arson, Homicide, and Car Theft in Miami. Extremely dangerous and has a history of violent crimes.', 'active'],
            [9, 'Jasmine Smith', '73.jpg', 'Wanted for Car Theft in Delhi and Corpus Christi. Known to operate in multiple cities and may be part of an organized crime ring.', 'active']
        ]
        write_csv(WANTED_CRIMINALS_FILE, ['id', 'name', 'image_filename', 'description', 'status'], default_criminals)
        print(f"Created wanted_criminals.csv with {len(default_criminals)} default criminals")

    # Ensure default images exist in the view_records folder
    # This is especially important for deployment on platforms like Render
    # where the uploads directory might not persist between deployments
    default_images = {
        '124.jpg': 'static/default_criminals/124.jpg',
        '196.jpg': 'static/default_criminals/196.jpg',
        '67.jpg': 'static/default_criminals/67.jpg',
        '77.jpg': 'static/default_criminals/77.jpg',
        '73.jpg': 'static/default_criminals/73.jpg'
    }

    # Create the static/default_criminals directory if it doesn't exist
    os.makedirs('static/default_criminals', exist_ok=True)

    # Check if the default images exist in the static folder, if not create placeholder images
    for img_name, img_path in default_images.items():
        if not os.path.exists(img_path):
            print(f"Creating placeholder image for {img_name}")
            # Create a simple placeholder image using PIL
            try:
                from PIL import Image, ImageDraw, ImageFont
                img = Image.new('RGB', (400, 500), color=(73, 109, 137))
                d = ImageDraw.Draw(img)
                # Try to use a default font
                try:
                    font = ImageFont.truetype("arial.ttf", 20)
                except:
                    font = ImageFont.load_default()
                d.text((10, 10), f"Placeholder for {img_name}", fill=(255, 255, 0), font=font)
                img.save(img_path)
                print(f"Created placeholder image at {img_path}")
            except Exception as e:
                print(f"Error creating placeholder image: {str(e)}")

    # Copy default images to the view_records folder
    for img_name, img_path in default_images.items():
        target_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], img_name)
        if not os.path.exists(target_path) and os.path.exists(img_path):
            print(f"Copying default image {img_name} to {target_path}")
            try:
                import shutil
                shutil.copy2(img_path, target_path)
                print(f"Copied {img_path} to {target_path}")
            except Exception as e:
                print(f"Error copying image: {str(e)}")
                # If copy fails, try to create a new file
                try:
                    with open(img_path, 'rb') as src, open(target_path, 'wb') as dst:
                        dst.write(src.read())
                    print(f"Created {target_path} by reading and writing")
                except Exception as e2:
                    print(f"Error creating image file: {str(e2)}")

    # Backup all criminal images
    backup_all_criminal_images()

def init_criminal_sightings_storage():
    """Initialize criminal sightings CSV file with headers if it doesn't exist"""
    if not os.path.exists(CRIMINAL_SIGHTINGS_FILE):
        write_csv(CRIMINAL_SIGHTINGS_FILE, ['id', 'criminal_id', 'criminal_name', 'reported_by', 'reported_by_email', 'location', 'latitude', 'longitude', 'sighting_date', 'sighting_time', 'description', 'image_filename', 'status', 'admin_notes', 'email_sent'])

def init_admin_codes_storage():
    """Initialize admin registration codes CSV file with headers if it doesn't exist"""
    if not os.path.exists(ADMIN_CODES_FILE):
        # Create default admin codes
        default_codes = [
            ['POLICE123', 'no', '', '2025-05-02'],
            ['FBI456', 'no', '', '2025-05-02'],
            ['OFFICER789', 'no', '', '2025-05-02'],
            ['SHERIFF101', 'no', '', '2025-05-02'],
            ['AGENT202', 'no', '', '2025-05-02']
        ]
        write_csv(ADMIN_CODES_FILE, ['code', 'used', 'used_by', 'created_date'], default_codes)

def verify_admin_code(code):
    """Verify if an admin code is valid and unused"""
    if not os.path.exists(ADMIN_CODES_FILE):
        init_admin_codes_storage()

    admin_codes = read_csv(ADMIN_CODES_FILE)
    for admin_code in admin_codes:
        if admin_code['code'] == code and admin_code['used'] == 'no':
            return True
    return False

def mark_admin_code_used(code, username):
    """Mark an admin code as used by a specific user"""
    if not os.path.exists(ADMIN_CODES_FILE):
        init_admin_codes_storage()

    admin_codes = read_csv(ADMIN_CODES_FILE)
    updated_codes = []
    found = False

    for admin_code in admin_codes:
        if admin_code['code'] == code:
            admin_code['used'] = 'yes'
            admin_code['used_by'] = username
            found = True
        updated_codes.append(list(admin_code.values()))

    if found:
        write_csv(ADMIN_CODES_FILE, ['code', 'used', 'used_by', 'created_date'], updated_codes)
        return True

    return False

def generate_token():
    """Generate a unique token for criminal report tracking"""
    return str(uuid.uuid4())[:8].upper()

def send_email(to, subject, template, **kwargs):
    """Send an email using Flask-Mail"""
    try:
        print(f"Attempting to send email to {to} with subject: {subject}")

        # Validate email address format
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, to):
            print(f"Invalid email address format: {to}")
            return False

        # Create message
        msg = Message(subject, recipients=[to])

        # Render template with provided arguments
        try:
            msg.html = render_template(template, **kwargs)
        except Exception as template_error:
            print(f"Error rendering email template: {str(template_error)}")
            print(f"Template: {template}")
            print(f"Template arguments: {kwargs}")
            return False

        # Print email details for debugging
        print(f"Email details:")
        print(f"  - From: {app.config['MAIL_DEFAULT_SENDER']}")
        print(f"  - To: {to}")
        print(f"  - Subject: {subject}")
        print(f"  - Template: {template}")

        # Check if mail configuration is valid
        if not app.config['MAIL_USERNAME'] or app.config['MAIL_USERNAME'] in ['your.email@outlook.com', 'your.email@gmail.com', 'your.actual.email@gmail.com']:
            # Skip this check if using the actual configured email (rauladitya22@gmail.com)
            if app.config['MAIL_USERNAME'] == 'rauladitya22@gmail.com':
                # Valid configuration, continue with sending
                pass
            else:
                print("Warning: Using default email configuration. Please update with your actual email credentials.")
                print("Email options:")
                print("1. Gmail with App Password: Replace the placeholders with your actual Gmail and App Password")
                print("2. Outlook/Hotmail: Use your regular email and password")
                print("3. Yahoo: Similar to Gmail, may require app password")
                print("Update the MAIL_USERNAME and MAIL_PASSWORD in the app configuration")
                return False

        # Try to send the email
        mail.send(msg)
        print(f"Email sent successfully to {to}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        print(f"Email configuration:")
        print(f"  - MAIL_SERVER: {app.config['MAIL_SERVER']}")
        print(f"  - MAIL_PORT: {app.config['MAIL_PORT']}")
        print(f"  - MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
        print(f"  - MAIL_USERNAME: {app.config['MAIL_USERNAME']}")

        # Print traceback for more detailed error information
        import traceback
        traceback.print_exc()

        return False

def register_user(username, email, password, role):
    """Register a new user with hashed password and additional details"""
    users = read_csv(USERS_FILE)

    # Check if username already exists
    for user in users:
        if user['username'] == username:
            return False

    # Add new user
    hashed_pw = generate_password_hash(password)
    append_csv(USERS_FILE, [username, email, hashed_pw, role])
    return True

def verify_user(username, password):
    """Verify user credentials"""
    users = read_csv(USERS_FILE)

    for user in users:
        if user['username'] == username:
            return check_password_hash(user['password'], password)

    return False

def search_criminal_history(search_term, search_type='id'):
    """Search criminal history by ID, name, or crime"""
    df = pd.read_csv(CRIMINAL_REPORTS_FILE)

    # Remove rows with all NaN values or empty name
    df = df.dropna(how='all')
    df = df[df['name'].notna() & (df['name'] != '')]

    # Extract ID from filename (e.g., "123.jpg" -> "123")
    def extract_id(filename):
        if pd.isna(filename):
            return ""
        import re
        match = re.search(r'(\d+)', filename)
        if match:
            return match.group(1)
        return ""

    # Add ID column based on the filename
    df['id'] = df['sketch_filename'].apply(extract_id)

    # For any missing IDs, use the index
    df.loc[df['id'] == "", 'id'] = df.index[df['id'] == ""].astype(str)

    # Search based on the specified type
    if search_type == 'id':
        # Search by ID
        result = df[df['id'] == search_term]
    elif search_type == 'name':
        # Search by name (case-insensitive partial match)
        result = df[df['name'].str.contains(search_term, case=False, na=False)]
    elif search_type == 'crime':
        # Search by crime (case-insensitive partial match)
        # Handle NaN values in crimes column
        df_with_crimes = df.copy()
        df_with_crimes['crimes'] = df_with_crimes['crimes'].fillna('').astype(str)
        result = df_with_crimes[df_with_crimes['crimes'].str.contains(search_term, case=False)]

        # Print debug information
        print(f"Crime search for '{search_term}' found {len(result)} results")
        if len(result) > 0:
            print(f"Sample result crimes: {result['crimes'].iloc[0]}")
    else:
        # Default: search across all fields
        name_matches = df[df['name'].str.contains(search_term, case=False, na=False)]
        id_matches = df[df['id'] == search_term]

        # Handle NaN values in crimes column for crime search
        df_crimes = df.copy()
        df_crimes['crimes'] = df_crimes['crimes'].fillna('').astype(str)
        crime_matches = df_crimes[df_crimes['crimes'].str.contains(search_term, case=False)]

        result = pd.concat([name_matches, id_matches, crime_matches]).drop_duplicates()

    # Convert age to integer if it's a valid number
    result['age'] = pd.to_numeric(result['age'], errors='coerce').fillna(0).astype(int)

    return result

def get_best_matches(sketch_path):
    """Use deep learning-based feature matching"""
    return find_best_matches(sketch_path)

def add_criminal_report(sketch_filename, name, gender, age, crimes, area_of_crime):
    """Add a new criminal report to the system"""
    # Convert age to integer
    try:
        age_int = int(float(age))
    except (ValueError, TypeError):
        age_int = 0

    df = pd.read_csv(CRIMINAL_REPORTS_FILE)
    new_report = pd.DataFrame([[sketch_filename, name, gender, age_int, crimes, area_of_crime]],
                              columns=['sketch_filename', 'name', 'gender', 'age', 'crimes', 'area_of_crime'])
    pd.concat([df, new_report], ignore_index=True).to_csv(CRIMINAL_REPORTS_FILE, index=False)

# Initialize storage
init_user_storage()
init_reports_storage()
init_pending_reports_storage()
init_wanted_criminals_storage()
init_criminal_sightings_storage()
init_admin_codes_storage()

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if verify_user(username, password):
            session['username'] = username

            # Get user role from CSV
            users = read_csv(USERS_FILE)
            user_role = 'user'  # Default role

            for user in users:
                if user['username'] == username:
                    user_role = user['role']
                    break

            session['role'] = user_role
            print(f"User {username} logged in with role: {user_role}")  # Debug log

            if user_role == 'official':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials!")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Check if trying to register as an official
        if role == 'official':
            # Require admin code for official registration
            admin_code = request.form.get('admin_code', '')
            if not admin_code:
                flash('Admin registration code is required for law enforcement officials!', 'danger')
                return render_template('register.html', error="Admin registration code is required!")

            # Verify the admin code
            if not verify_admin_code(admin_code):
                flash('Invalid or already used admin registration code!', 'danger')
                return render_template('register.html', error="Invalid admin registration code!")

            # Register the user
            if register_user(username, email, password, role):
                # Mark the admin code as used
                mark_admin_code_used(admin_code, username)
                flash('Official registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Username already exists!', 'danger')
                return render_template('register.html', error="Username already exists!")
        else:
            # Regular user registration
            if register_user(username, email, password, role):
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Username already exists!', 'danger')
                return render_template('register.html', error="Username already exists!")

    return render_template('register.html')

@app.route('/user_dashboard')
def user_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    criminal_reports = []
    criminal_sightings = []
    approved_reports = 0
    verified_sightings = 0

    try:
        # Get user's criminal reports
        if os.path.exists(PENDING_REPORTS_FILE):
            reports = read_csv(PENDING_REPORTS_FILE)
            user_reports = []
            for report in reports:
                if report.get('submitted_by') == username:
                    # Add date_submitted field if it doesn't exist
                    if 'date_submitted' not in report:
                        report['date_submitted'] = 'Unknown'
                    user_reports.append(report)
                    if report.get('status') == 'approved':
                        approved_reports += 1

            criminal_reports = user_reports

        # Get user's criminal sightings
        if os.path.exists(CRIMINAL_SIGHTINGS_FILE):
            sightings = read_csv(CRIMINAL_SIGHTINGS_FILE)
            user_sightings = []
            for sighting in sightings:
                if sighting.get('reported_by') == username:
                    user_sightings.append(sighting)
                    if sighting.get('status') == 'verified':
                        verified_sightings += 1

            criminal_sightings = user_sightings

    except Exception as e:
        print(f"Error fetching user activity: {str(e)}")
        # Continue with empty lists if there's an error

    return render_template('user_dashboard.html',
                          username=username,
                          criminal_reports=criminal_reports,
                          criminal_sightings=criminal_sightings,
                          approved_reports=approved_reports,
                          verified_sightings=verified_sightings)

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'official':
        flash('You do not have permission to access the admin dashboard.', 'danger')
        return redirect(url_for('user_dashboard'))

    return render_template('admin_dashboard.html', username=session['username'])

@app.route('/manage_admin_codes', methods=['GET', 'POST'])
def manage_admin_codes():
    if 'username' not in session or session.get('role') != 'official':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))

    # Handle adding a new admin code
    if request.method == 'POST':
        if 'add_code' in request.form:
            new_code = request.form['new_code']

            # Check if code already exists
            df = pd.read_csv(ADMIN_CODES_FILE)
            if new_code in df['code'].values:
                flash('This admin code already exists!', 'danger')
            else:
                # Add the new code
                new_code_row = pd.DataFrame([[
                    new_code,
                    'no',
                    '',
                    datetime.datetime.now().strftime('%Y-%m-%d')
                ]], columns=['code', 'used', 'used_by', 'created_date'])

                pd.concat([df, new_code_row], ignore_index=True).to_csv(ADMIN_CODES_FILE, index=False)
                flash('New admin code added successfully!', 'success')

        # Handle deleting an admin code
        elif 'delete_code' in request.form:
            code_to_delete = request.form['delete_code']

            df = pd.read_csv(ADMIN_CODES_FILE)
            # Only delete if the code is not used
            if code_to_delete in df[df['used'] == 'no']['code'].values:
                df = df[df['code'] != code_to_delete]
                df.to_csv(ADMIN_CODES_FILE, index=False)
                flash('Admin code deleted successfully!', 'success')
            else:
                flash('Cannot delete a code that is already in use!', 'danger')

    # Get all admin codes
    df = pd.read_csv(ADMIN_CODES_FILE)
    admin_codes = df.to_dict('records')

    return render_template('manage_admin_codes.html', admin_codes=admin_codes)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/match_criminal', methods=['GET', 'POST'])
def match_criminal():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Handle file upload and matching
        sketch_file = request.files['sketch']
        if sketch_file:
            print("Sketch file received, starting processing...")
            sketch_filename = secure_filename(sketch_file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            sketch_path = os.path.join(app.config['UPLOAD_FOLDER'], sketch_filename)
            sketch_file.save(sketch_path)
            print(f"Sketch saved to {sketch_path}")

            # Process and find the best matches for the uploaded sketch
            print("Starting feature matching process...")
            best_matches = find_best_matches(sketch_path)
            print(f"Matching complete, found {len(best_matches)} potential matches")

            # Extract criminal data from the database
            criminals_data = []
            df = pd.read_csv(CRIMINAL_REPORTS_FILE)

            for filename, similarity, criminal_id in best_matches:
                # Find the criminal in the database
                criminal_rows = df[df['sketch_filename'] == filename]
                if not criminal_rows.empty:
                    criminal = criminal_rows.iloc[0].to_dict()
                    criminal['id'] = criminal_id
                    criminal['similarity'] = similarity
                    criminals_data.append(criminal)
                else:
                    # If not found in database, create a minimal record
                    criminals_data.append({
                        'sketch_filename': filename,
                        'name': f"Criminal {criminal_id}",
                        'id': criminal_id,
                        'similarity': similarity,
                        'age': 'Unknown',
                        'gender': 'Unknown',
                        'crimes': 'Unknown',
                        'area_of_crime': 'Unknown'
                    })

            print(f"Rendering match results with {len(criminals_data)} criminals")
            return render_template('match_result.html', criminals=criminals_data)

    return render_template('match_criminal.html')

@app.route('/search_criminal', methods=['GET', 'POST'])
def search_criminal():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        search_term = request.form['search_term']
        search_type = request.form.get('search_type', 'id')  # Default to ID if not specified

        # Perform the search with the specified type
        results = search_criminal_history(search_term, search_type)

        if not results.empty:
            return render_template('search_result.html', results=results, search_term=search_term, search_type=search_type)
        else:
            return render_template('search_result.html', results=pd.DataFrame(), search_term=search_term, search_type=search_type)

    return render_template('search_criminal.html', username=session['username'])

@app.route('/wanted_criminals')
def wanted_criminals():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        # Read wanted criminals from CSV
        print(f"Reading wanted criminals from {WANTED_CRIMINALS_FILE}")
        df = pd.read_csv(WANTED_CRIMINALS_FILE)
        print(f"Found {len(df)} criminals in CSV")

        if df.empty:
            criminals = []
            print("CSV is empty, no criminals to display")
        else:
            # Filter only active criminals
            active_criminals = df[df['status'] == 'active']
            criminals = active_criminals.to_dict('records')
            print(f"Found {len(criminals)} active criminals")

            # Verify image files exist
            for criminal in criminals:
                image_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], criminal['image_filename'])
                if not os.path.exists(image_path):
                    print(f"Warning: Image file does not exist: {image_path}")
                else:
                    print(f"Image file exists: {image_path}")

        return render_template('wanted_criminals.html', criminals=criminals)
    except Exception as e:
        print(f"Error in wanted_criminals: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('An error occurred while fetching wanted criminals.', 'danger')
        return render_template('wanted_criminals.html', criminals=[])

@app.route('/report_criminal', methods=['GET', 'POST'])
def report_criminal():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # Handle the report form submission
            photo_file = request.files['photo']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            age = request.form['age']
            crime = request.form['crime']
            arrested = request.form['arrested']

            # Generate a unique token for tracking
            token = generate_token()

            # Save photo file
            photo_filename = secure_filename(photo_file.filename)
            # Add timestamp to filename to avoid duplicates
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            photo_filename = f"{timestamp}_{photo_filename}"
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
            photo_file.save(photo_path)

            # Save proof file if provided
            proof_filename = ""
            if 'proof' in request.files and request.files['proof'].filename:
                proof_file = request.files['proof']
                proof_filename = secure_filename(proof_file.filename)
                proof_filename = f"{timestamp}_{proof_filename}"
                proof_path = os.path.join(app.config['PROOF_FOLDER'], proof_filename)
                proof_file.save(proof_path)

            # Add to pending reports
            df = pd.read_csv(PENDING_REPORTS_FILE)
            new_report = pd.DataFrame([[
                token,
                photo_filename,
                first_name,
                last_name,
                age,
                crime,
                arrested,
                proof_filename,
                'pending',
                session['username']
            ]], columns=[
                'token', 'sketch_filename', 'first_name', 'last_name',
                'age', 'crime', 'arrested', 'proof_filename', 'status', 'submitted_by'
            ])

            pd.concat([df, new_report], ignore_index=True).to_csv(PENDING_REPORTS_FILE, index=False)

            # Return the token to the user
            return render_template('registration_token.html', token=token)

        except Exception as e:
            print(f"Error in report_criminal: {str(e)}")
            return render_template('report_criminal.html',
                                  message="An error occurred while submitting your report. Please try again.",
                                  message_type="error-message")

    return render_template('report_criminal.html')

@app.route('/check_registration_status', methods=['GET', 'POST'])
def check_registration_status():
    if 'username' not in session:
        return redirect(url_for('login'))

    status = ""
    if request.method == 'POST':
        token = request.form['token']

        # Check the registration status using the token
        df = pd.read_csv(PENDING_REPORTS_FILE)
        report = df[df['token'] == token]

        if not report.empty:
            report_status = report.iloc[0]['status']
            if report_status == 'pending':
                status = f"Your report with token {token} is still pending review by an official."
            elif report_status == 'approved':
                status = f"Your report with token {token} has been verified and approved."
            elif report_status == 'rejected':
                status = f"Your report with token {token} has been rejected. The person reported is not a criminal."
            else:
                status = f"Unknown status for token {token}."
        else:
            # Check if it's in the approved criminal reports
            df_criminals = pd.read_csv(CRIMINAL_REPORTS_FILE)
            if token in df_criminals.values:
                status = f"Your report with token {token} has been approved and added to the criminal database."
            else:
                status = f"No report found with token {token}. Please check the token and try again."

    return render_template('check_registration_status.html', status=status)

@app.route('/match_result', methods=['GET'])
def match_result():
    return render_template('match_result.html')

@app.route('/admin_requests')
def admin_requests():
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    # Fetch pending criminal report requests
    try:
        df = pd.read_csv(PENDING_REPORTS_FILE)
        # Filter only pending requests
        pending_reports = df[df['status'] == 'pending']

        if pending_reports.empty:
            requests = []
        else:
            # Convert DataFrame to list of dictionaries
            requests = pending_reports.to_dict('records')

        return render_template('admin_request.html', requests=requests)
    except Exception as e:
        print(f"Error in admin_requests: {str(e)}")
        flash("An error occurred while fetching criminal requests.", "danger")
        return render_template('admin_request.html', requests=[])

@app.route('/authenticate_criminal/<token>')
def authenticate_criminal(token):
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        # Find the report with the given token
        df = pd.read_csv(PENDING_REPORTS_FILE)
        report_idx = df[df['token'] == token].index

        if len(report_idx) == 0:
            flash('Criminal report not found!', 'danger')
            return redirect(url_for('admin_requests'))

        # Get the report data
        report = df.loc[report_idx[0]]

        # Update the status to approved
        df.at[report_idx[0], 'status'] = 'approved'
        df.to_csv(PENDING_REPORTS_FILE, index=False)

        # Add to the verified criminal reports
        criminal_df = pd.read_csv(CRIMINAL_REPORTS_FILE)

        # Convert age to integer
        try:
            age_int = int(float(report['age']))
        except (ValueError, TypeError):
            age_int = 0

        # Copy the sketch file to the view_records folder
        sketch_filename = report['sketch_filename']
        sketch_path = os.path.join(app.config['UPLOAD_FOLDER'], sketch_filename)
        view_records_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], sketch_filename)

        # Create a copy for view_records folder if it exists
        if os.path.exists(sketch_path):
            import shutil
            shutil.copy2(sketch_path, view_records_path)
            print(f"Copied sketch to view records folder: {view_records_path}")
        else:
            print(f"Warning: Sketch file not found: {sketch_path}")

        new_criminal = pd.DataFrame([[
            report['sketch_filename'],
            f"{report['first_name']} {report['last_name']}",
            'Unknown',  # gender
            age_int,
            report['crime'],
            report['arrested']
        ]], columns=['sketch_filename', 'name', 'gender', 'age', 'crimes', 'area_of_crime'])

        pd.concat([criminal_df, new_criminal], ignore_index=True).to_csv(CRIMINAL_REPORTS_FILE, index=False)

        flash('Criminal report authenticated successfully!', 'success')
    except Exception as e:
        print(f"Error in authenticate_criminal: {str(e)}")
        flash('An error occurred while authenticating the criminal report!', 'danger')

    return redirect(url_for('admin_requests'))

@app.route('/reject_criminal/<token>')
def reject_criminal(token):
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        # Find the report with the given token
        df = pd.read_csv(PENDING_REPORTS_FILE)
        report_idx = df[df['token'] == token].index

        if len(report_idx) == 0:
            flash('Criminal report not found!', 'danger')
            return redirect(url_for('admin_requests'))

        # Update the status to rejected
        df.at[report_idx[0], 'status'] = 'rejected'
        df.to_csv(PENDING_REPORTS_FILE, index=False)

        flash('Criminal report rejected!', 'success')
    except Exception as e:
        print(f"Error in reject_criminal: {str(e)}")
        flash('An error occurred while rejecting the criminal report!', 'danger')

    return redirect(url_for('admin_requests'))

# Routes to serve uploaded files
@app.route('/uploads/sketches/<filename>')
def serve_sketch(filename):
    print(f"Serving sketch image: {filename}")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Check if the file exists in the upload folder
    if os.path.exists(file_path):
        print(f"File exists in upload folder: {file_path}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # If not, check if it exists in the static/default_criminals folder
    static_path = os.path.join('static/default_criminals', filename)
    if os.path.exists(static_path):
        print(f"File exists in static/default_criminals: {static_path}")

        # Try to copy the file to the upload folder
        try:
            import shutil
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            shutil.copy2(static_path, file_path)
            print(f"Copied {static_path} to {file_path}")
        except Exception as e:
            print(f"Error copying file: {str(e)}")

        # Serve from the static folder
        return send_from_directory('static/default_criminals', filename)

    # If the file doesn't exist in either location, return a default image
    print(f"File does not exist in any location: {filename}")
    return send_from_directory('static', 'default_image.png')

@app.route('/uploads/proofs/<filename>')
def serve_proof(filename):
    print(f"Serving proof image: {filename}")
    file_path = os.path.join(app.config['PROOF_FOLDER'], filename)

    # Check if the file exists in the proof folder
    if os.path.exists(file_path):
        print(f"File exists in proof folder: {file_path}")
        return send_from_directory(app.config['PROOF_FOLDER'], filename)

    # If not, check if it exists in the static/default_criminals folder
    static_path = os.path.join('static/default_criminals', filename)
    if os.path.exists(static_path):
        print(f"File exists in static/default_criminals: {static_path}")

        # Try to copy the file to the proof folder
        try:
            import shutil
            os.makedirs(app.config['PROOF_FOLDER'], exist_ok=True)
            shutil.copy2(static_path, file_path)
            print(f"Copied {static_path} to {file_path}")
        except Exception as e:
            print(f"Error copying file: {str(e)}")

        # Serve from the static folder
        return send_from_directory('static/default_criminals', filename)

    # If the file doesn't exist in either location, return a default image
    print(f"File does not exist in any location: {filename}")
    return send_from_directory('static', 'default_image.png')

@app.route('/uploads/view_records/<filename>')
def serve_view_record(filename):
    print(f"Serving view record image: {filename}")
    file_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], filename)

    # Check if the file exists in the view_records folder
    if os.path.exists(file_path):
        print(f"File exists in view_records: {file_path}")
        return send_from_directory(app.config['VIEW_RECORDS_FOLDER'], filename)

    # If not, check if it exists in the static/default_criminals folder
    static_path = os.path.join('static/default_criminals', filename)
    if os.path.exists(static_path):
        print(f"File exists in static/default_criminals: {static_path}")

        # Try to copy the file to the view_records folder
        try:
            import shutil
            os.makedirs(app.config['VIEW_RECORDS_FOLDER'], exist_ok=True)
            shutil.copy2(static_path, file_path)
            print(f"Copied {static_path} to {file_path}")
        except Exception as e:
            print(f"Error copying file: {str(e)}")

        # Serve from the static folder
        return send_from_directory('static/default_criminals', filename)

    # If the file doesn't exist in either location, return a default image
    print(f"File does not exist in any location: {filename}")
    return send_from_directory('static', 'default_image.png')

@app.route('/uploads/evidence/<filename>')
def serve_evidence(filename):
    print(f"Serving evidence image: {filename}")
    file_path = os.path.join(app.config['EVIDENCE_FOLDER'], filename)

    # Check if the file exists in the evidence folder
    if os.path.exists(file_path):
        print(f"File exists in evidence folder: {file_path}")
        return send_from_directory(app.config['EVIDENCE_FOLDER'], filename)

    # If not, check if it exists in the static/default_criminals folder
    static_path = os.path.join('static/default_criminals', filename)
    if os.path.exists(static_path):
        print(f"File exists in static/default_criminals: {static_path}")

        # Try to copy the file to the evidence folder
        try:
            import shutil
            os.makedirs(app.config['EVIDENCE_FOLDER'], exist_ok=True)
            shutil.copy2(static_path, file_path)
            print(f"Copied {static_path} to {file_path}")
        except Exception as e:
            print(f"Error copying file: {str(e)}")

        # Serve from the static folder
        return send_from_directory('static/default_criminals', filename)

    # If the file doesn't exist in either location, return a default image
    print(f"File does not exist in any location: {filename}")
    return send_from_directory('static', 'default_image.png')

@app.route('/debug/images')
def debug_images():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        # Check if the wanted criminals images exist
        result = []
        df = pd.read_csv(WANTED_CRIMINALS_FILE)
        print(f"DEBUG: Read {len(df)} criminals from {WANTED_CRIMINALS_FILE}")
        print(f"DEBUG: Columns: {df.columns.tolist()}")
        print(f"DEBUG: First row: {df.iloc[0].to_dict() if not df.empty else 'No data'}")

        for _, row in df.iterrows():
            image_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], row['image_filename'])
            image_exists = os.path.exists(image_path)
            print(f"DEBUG: Image {row['image_filename']} exists: {image_exists}, path: {image_path}")
            result.append({
                'id': row['id'],
                'name': row['name'],
                'image_filename': row['image_filename'],
                'image_exists': image_exists,
                'image_path': image_path
            })

        return {'criminals': result, 'view_records_folder': app.config['VIEW_RECORDS_FOLDER']}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

@app.route('/debug/wanted_criminals')
def debug_wanted_criminals():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        # Read wanted criminals from CSV
        print(f"DEBUG: Reading wanted criminals from {WANTED_CRIMINALS_FILE}")
        df = pd.read_csv(WANTED_CRIMINALS_FILE)
        print(f"DEBUG: Found {len(df)} criminals in CSV")

        # Check if the file exists and is readable
        print(f"DEBUG: File exists: {os.path.exists(WANTED_CRIMINALS_FILE)}")
        print(f"DEBUG: File size: {os.path.getsize(WANTED_CRIMINALS_FILE)} bytes")

        # Check the content of the CSV file
        criminals = df.to_dict('records')

        # Check if images exist
        for criminal in criminals:
            image_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], criminal['image_filename'])
            criminal['image_exists'] = os.path.exists(image_path)
            criminal['image_path'] = image_path

        return {'criminals': criminals, 'file_path': WANTED_CRIMINALS_FILE}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

@app.route('/add_criminal', methods=['GET', 'POST'])
def add_criminal():
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            full_name = f"{first_name} {last_name}"
            gender = request.form['gender']
            age = request.form['age']
            crimes = request.form['crimes']
            area_of_crime = request.form['area_of_crime']
            image_name = request.form['image_name']

            # Convert age to integer
            try:
                age_int = int(float(age))
            except (ValueError, TypeError):
                age_int = 0

            # Handle photo upload
            photo_file = request.files['photo']
            file_extension = os.path.splitext(photo_file.filename)[1]
            custom_filename = f"{image_name}{file_extension}"

            # Save the photo with the custom filename to both folders
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], custom_filename)
            view_records_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], custom_filename)

            # Save to both locations
            photo_file.save(photo_path)

            # Create a copy for view_records folder
            import shutil
            shutil.copy2(photo_path, view_records_path)

            # Add to criminal reports
            df = pd.read_csv(CRIMINAL_REPORTS_FILE)
            new_criminal = pd.DataFrame([[
                custom_filename,
                full_name,
                gender,
                age_int,
                crimes,
                area_of_crime
            ]], columns=['sketch_filename', 'name', 'gender', 'age', 'crimes', 'area_of_crime'])

            pd.concat([df, new_criminal], ignore_index=True).to_csv(CRIMINAL_REPORTS_FILE, index=False)

            flash('Criminal record added successfully!', 'success')
            return redirect(url_for('view_records'))

        except Exception as e:
            print(f"Error in add_criminal: {str(e)}")
            flash('An error occurred while adding the criminal record.', 'danger')

    return render_template('add_criminal.html')

@app.route('/view_records')
def view_records():
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        # Read criminal records from CSV
        criminals = read_csv(CRIMINAL_REPORTS_FILE)

        # Process the criminals data
        for i, criminal in enumerate(criminals):
            # Convert age to integer if it's a valid number
            try:
                criminal['age'] = int(criminal.get('age', 0) or 0)
            except (ValueError, TypeError):
                criminal['age'] = 0

            # Extract ID from filename (e.g., "123.jpg" -> "123")
            filename = criminal.get('sketch_filename', '')
            if filename:
                import re
                match = re.search(r'(\d+)', filename)
                criminal['id'] = match.group(1) if match else str(i)
            else:
                criminal['id'] = str(i)

        return render_template('view_records.html', criminals=criminals)
    except Exception as e:
        print(f"Error in view_records: {str(e)}")
        flash('An error occurred while fetching criminal records.', 'danger')
        return render_template('view_records.html', criminals=[])

@app.route('/get_criminal/<criminal_id>')
def get_criminal(criminal_id):
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        criminals = read_csv(CRIMINAL_REPORTS_FILE)

        # Process criminals to add IDs
        for i, criminal in enumerate(criminals):
            criminal['id'] = str(i)

        # Find the criminal with the matching ID
        for criminal in criminals:
            if criminal['id'] == criminal_id:
                return criminal

        return {"error": "Criminal not found"}, 404
    except Exception as e:
        print(f"Error in get_criminal: {str(e)}")
        return {"error": "Criminal not found"}, 404

@app.route('/update_criminal', methods=['POST'])
def update_criminal():
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        criminal_id = request.form['criminal_id']
        name = request.form['name']
        gender = request.form['gender']
        age = request.form['age']
        crimes = request.form['crimes']
        area_of_crime = request.form['area_of_crime']
        current_sketch_filename = request.form['current_sketch_filename']

        # Update the criminal record in the CSV
        df = pd.read_csv(CRIMINAL_REPORTS_FILE)

        # Extract ID from filename (e.g., "123.jpg" -> "123")
        def extract_id(filename):
            if pd.isna(filename):
                return ""
            import re
            match = re.search(r'(\d+)', filename)
            if match:
                return match.group(1)
            return ""

        # Add ID column based on the filename
        df['id'] = df['sketch_filename'].apply(extract_id)

        # For any missing IDs, use the index
        df.loc[df['id'] == "", 'id'] = df.index[df['id'] == ""].astype(str)

        # Find the row with the matching ID
        row_idx = df[df['id'] == criminal_id].index

        if len(row_idx) == 0:
            flash('Criminal record not found.', 'danger')
            return redirect(url_for('view_records'))

        idx = row_idx[0]

        # Convert age to integer
        try:
            age_int = int(float(age))
        except (ValueError, TypeError):
            age_int = 0

        # Check if a new photo was uploaded
        sketch_filename = current_sketch_filename
        if 'new_photo' in request.files and request.files['new_photo'].filename:
            new_photo = request.files['new_photo']

            # Keep the same ID in the filename but update the extension
            file_extension = os.path.splitext(new_photo.filename)[1]
            numeric_id = extract_id(current_sketch_filename)
            if numeric_id:
                sketch_filename = f"{numeric_id}{file_extension}"
            else:
                # Fallback to timestamp if no numeric ID found
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                sketch_filename = f"{timestamp}{file_extension}"

            # Save the new photo to both folders
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], sketch_filename)
            view_records_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], sketch_filename)

            new_photo.save(photo_path)

            # Create a copy for view_records folder
            import shutil
            shutil.copy2(photo_path, view_records_path)

            # Delete the old photo files if they exist and are different
            if sketch_filename != current_sketch_filename:
                old_sketch_path = os.path.join(app.config['UPLOAD_FOLDER'], current_sketch_filename)
                old_view_records_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], current_sketch_filename)

                if os.path.exists(old_sketch_path):
                    os.remove(old_sketch_path)

                if os.path.exists(old_view_records_path):
                    os.remove(old_view_records_path)

            # Update the sketch filename in the DataFrame
            df.at[idx, 'sketch_filename'] = sketch_filename

        # Update other fields
        df.at[idx, 'name'] = name
        df.at[idx, 'gender'] = gender
        df.at[idx, 'age'] = age_int
        df.at[idx, 'crimes'] = crimes
        df.at[idx, 'area_of_crime'] = area_of_crime

        # Remove the ID column before saving
        df = df.drop(columns=['id'])
        df.to_csv(CRIMINAL_REPORTS_FILE, index=False)

        flash('Criminal record updated successfully!', 'success')
        # The JavaScript in view_records.html will handle restoring the scroll position
        return redirect(url_for('view_records'))
    except Exception as e:
        print(f"Error in update_criminal: {str(e)}")
        flash('An error occurred while updating the criminal record.', 'danger')
        return redirect(url_for('view_records'))

@app.route('/delete_criminal/<criminal_id>')
def delete_criminal(criminal_id):
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        # Read the CSV file
        df = pd.read_csv(CRIMINAL_REPORTS_FILE)

        # Extract ID from filename (e.g., "123.jpg" -> "123")
        def extract_id(filename):
            if pd.isna(filename):
                return ""
            import re
            match = re.search(r'(\d+)', filename)
            if match:
                return match.group(1)
            return ""

        # Add ID column based on the filename
        df['id'] = df['sketch_filename'].apply(extract_id)

        # For any missing IDs, use the index
        df.loc[df['id'] == "", 'id'] = df.index[df['id'] == ""].astype(str)

        # Get the filename of the image to delete
        criminal = df[df['id'] == criminal_id]
        if not criminal.empty:
            sketch_filename = criminal.iloc[0]['sketch_filename']

            # Delete the image files from both folders if they exist
            sketch_path = os.path.join(app.config['UPLOAD_FOLDER'], sketch_filename)
            view_records_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], sketch_filename)

            if os.path.exists(sketch_path):
                os.remove(sketch_path)

            if os.path.exists(view_records_path):
                os.remove(view_records_path)

            # Remove the record from the DataFrame
            df = df[df['id'] != criminal_id]

            # Save the updated DataFrame back to CSV
            df = df.drop(columns=['id'])
            df.to_csv(CRIMINAL_REPORTS_FILE, index=False)

            flash('Criminal record deleted successfully!', 'success')
        else:
            flash('Criminal record not found.', 'danger')

        return redirect(url_for('view_records'))
    except Exception as e:
        print(f"Error in delete_criminal: {str(e)}")
        flash('An error occurred while deleting the criminal record.', 'danger')
        return redirect(url_for('view_records'))

@app.route('/get_wanted_criminal/<criminal_id>')
def get_wanted_criminal(criminal_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        print(f"Fetching criminal with ID: {criminal_id}")
        df = pd.read_csv(WANTED_CRIMINALS_FILE)
        print(f"Wanted criminals data: {df.head()}")
        print(f"Total criminals in CSV: {len(df)}")
        print(f"Criminal IDs in CSV: {df['id'].tolist()}")

        # Convert criminal_id to int for comparison
        try:
            criminal_id_int = int(criminal_id)
            print(f"Converted criminal_id to int: {criminal_id_int}")
        except ValueError:
            print(f"Invalid criminal ID format: {criminal_id}")
            return {"error": "Invalid criminal ID format"}, 400

        # Find the criminal in the dataframe
        criminal_rows = df[df['id'] == criminal_id_int]
        print(f"Found {len(criminal_rows)} matching rows")

        if criminal_rows.empty:
            print(f"No criminal found with ID: {criminal_id}")
            return {"error": "Criminal not found"}, 404

        # Convert to dictionary
        criminal = criminal_rows.to_dict('records')[0]
        print(f"Found criminal: {criminal}")

        # Check if image file exists
        image_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], criminal['image_filename'])
        if not os.path.exists(image_path):
            print(f"Warning: Image file does not exist: {image_path}")
        else:
            print(f"Image file exists: {image_path}")

        return criminal
    except Exception as e:
        print(f"Error in get_wanted_criminal: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": "Criminal not found", "details": str(e)}, 404



@app.route('/report_sighting', methods=['GET', 'POST'])
def report_sighting():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # Get form data
            criminal_id = request.form['criminal_id']
            location = request.form['location']
            sighting_date = request.form['sighting_date']
            sighting_time = request.form['sighting_time']
            description = request.form.get('description', '')
            email = request.form['email']

            # Print form data for debugging
            print(f"Received sighting report:")
            print(f"  - Criminal ID: {criminal_id}")
            print(f"  - Location: {location}")
            print(f"  - Date: {sighting_date}")
            print(f"  - Time: {sighting_time}")
            print(f"  - Email: {email}")

            # Get latitude and longitude if provided
            latitude = request.form.get('latitude', '')
            longitude = request.form.get('longitude', '')

            if latitude and longitude:
                print(f"  - Coordinates: {latitude}, {longitude}")

            # Get criminal name from wanted criminals
            df_criminals = pd.read_csv(WANTED_CRIMINALS_FILE)
            criminal = df_criminals[df_criminals['id'] == int(criminal_id)]
            if criminal.empty:
                flash('Criminal not found.', 'danger')
                return redirect(url_for('report_sighting'))

            criminal_name = criminal.iloc[0]['name']
            print(f"  - Criminal Name: {criminal_name}")

            # Handle evidence upload if provided
            image_filename = ''
            if 'evidence' in request.files and request.files['evidence'].filename:
                evidence_file = request.files['evidence']
                image_filename = secure_filename(evidence_file.filename)
                # Add timestamp to filename to avoid duplicates
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                image_filename = f"{timestamp}_{image_filename}"
                evidence_path = os.path.join(app.config['EVIDENCE_FOLDER'], image_filename)
                evidence_file.save(evidence_path)
                print(f"  - Evidence saved: {image_filename}")

            # Generate a unique ID for the sighting
            sighting_id = str(uuid.uuid4())
            print(f"  - Generated sighting ID: {sighting_id}")

            # Make sure the criminal_sightings.csv file exists with proper headers
            if not os.path.exists(CRIMINAL_SIGHTINGS_FILE) or os.path.getsize(CRIMINAL_SIGHTINGS_FILE) == 0:
                print("Creating new criminal_sightings.csv file with headers")
                headers = ['id', 'criminal_id', 'criminal_name', 'reported_by', 'reported_by_email',
                          'location', 'latitude', 'longitude', 'sighting_date', 'sighting_time',
                          'description', 'image_filename', 'status', 'admin_notes', 'email_sent']
                pd.DataFrame(columns=headers).to_csv(CRIMINAL_SIGHTINGS_FILE, index=False)

            # Add to criminal sightings
            try:
                df = pd.read_csv(CRIMINAL_SIGHTINGS_FILE)
                print(f"Successfully read criminal_sightings.csv with {len(df)} existing records")
            except Exception as csv_error:
                print(f"Error reading criminal_sightings.csv: {str(csv_error)}")
                # Create a new DataFrame if the file couldn't be read
                df = pd.DataFrame(columns=[
                    'id', 'criminal_id', 'criminal_name', 'reported_by', 'reported_by_email',
                    'location', 'latitude', 'longitude', 'sighting_date', 'sighting_time',
                    'description', 'image_filename', 'status', 'admin_notes', 'email_sent'
                ])
                print("Created new DataFrame for criminal sightings")

            # Create the new sighting record
            new_sighting_data = {
                'id': sighting_id,
                'criminal_id': criminal_id,
                'criminal_name': criminal_name,
                'reported_by': session['username'],
                'reported_by_email': email,
                'location': location,
                'latitude': latitude,
                'longitude': longitude,
                'sighting_date': sighting_date,
                'sighting_time': sighting_time,
                'description': description,
                'image_filename': image_filename,
                'status': 'pending',
                'admin_notes': '',
                'email_sent': 'no'
            }

            # Add the new sighting to the DataFrame
            new_sighting = pd.DataFrame([new_sighting_data])
            print(f"Created new sighting record: {new_sighting_data}")

            # Concatenate and save
            result_df = pd.concat([df, new_sighting], ignore_index=True)
            result_df.to_csv(CRIMINAL_SIGHTINGS_FILE, index=False)
            print(f"Saved criminal_sightings.csv with {len(result_df)} records")

            flash('Your sighting report has been submitted successfully. Officials will review it shortly.', 'success')
            return redirect(url_for('user_dashboard'))

        except Exception as e:
            print(f"Error in report_sighting: {str(e)}")
            import traceback
            traceback.print_exc()
            flash('An error occurred while submitting your report. Please try again.', 'danger')

    # For GET request, show the form with wanted criminals
    try:
        df = pd.read_csv(WANTED_CRIMINALS_FILE)
        active_criminals = df[df['status'] == 'active']
        criminals = active_criminals.to_dict('records')
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        return render_template('report_sighting.html', wanted_criminals=criminals, today=today)
    except Exception as e:
        print(f"Error loading wanted criminals: {str(e)}")
        flash('An error occurred while loading wanted criminals.', 'danger')
        return render_template('report_sighting.html', wanted_criminals=[], today=datetime.datetime.now().strftime('%Y-%m-%d'))

@app.route('/admin_sightings')
def admin_sightings():
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        # Check if the file exists
        if not os.path.exists(CRIMINAL_SIGHTINGS_FILE):
            # Create a new file with headers
            with open(CRIMINAL_SIGHTINGS_FILE, 'w') as f:
                f.write("id,criminal_id,criminal_name,reported_by,location,sighting_date,sighting_time,description,image_filename,status,admin_notes,email_sent,reported_by_email,latitude,longitude\n")

            # Return empty lists
            return render_template('admin_sightings.html',
                                  pending_sightings=[],
                                  verified_sightings=[],
                                  rejected_sightings=[])

        # Read the CSV file directly as text
        with open(CRIMINAL_SIGHTINGS_FILE, 'r') as f:
            lines = f.readlines()

        # Parse the header
        header = lines[0].strip().split(',')
        print(f"CSV Header: {header}")

        # Parse the data rows
        sightings = []
        for i in range(1, len(lines)):
            line = lines[i].strip()
            if not line:
                continue

            # Handle quoted fields with commas
            parts = []
            in_quotes = False
            current_part = ""

            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                    current_part += char
                elif char == ',' and not in_quotes:
                    parts.append(current_part)
                    current_part = ""
                else:
                    current_part += char

            # Add the last part
            if current_part:
                parts.append(current_part)

            # Create a dictionary for this sighting
            sighting = {}
            for j in range(min(len(header), len(parts))):
                value = parts[j].strip('"')
                sighting[header[j]] = value

            # Ensure all required fields exist
            for field in ['id', 'criminal_id', 'criminal_name', 'reported_by', 'location',
                         'sighting_date', 'sighting_time', 'description', 'image_filename',
                         'status', 'admin_notes', 'reported_by_email', 'latitude', 'longitude']:
                if field not in sighting:
                    sighting[field] = ''

            # Set default status if empty
            if not sighting['status']:
                sighting['status'] = 'pending'

            sightings.append(sighting)

        print(f"Parsed {len(sightings)} sightings from CSV")

        # Get criminal images
        df_criminals = pd.read_csv(WANTED_CRIMINALS_FILE)
        criminal_images = {}
        for _, criminal in df_criminals.iterrows():
            criminal_images[str(criminal['id'])] = criminal['image_filename']

        # Add criminal image to each sighting
        for sighting in sightings:
            criminal_id = sighting['criminal_id']
            if criminal_id and criminal_id in criminal_images:
                sighting['criminal_image'] = criminal_images[criminal_id]
            else:
                sighting['criminal_image'] = ''

        # Filter by status
        pending_sightings = [s for s in sightings if s['status'] == 'pending']
        verified_sightings = [s for s in sightings if s['status'] == 'verified']
        rejected_sightings = [s for s in sightings if s['status'] == 'rejected']

        print(f"Found {len(pending_sightings)} pending, {len(verified_sightings)} verified, and {len(rejected_sightings)} rejected sightings")

        # Print first pending sighting for debugging
        if pending_sightings:
            print(f"First pending sighting: {pending_sightings[0]}")

        return render_template('admin_sightings.html',
                              pending_sightings=pending_sightings,
                              verified_sightings=verified_sightings,
                              rejected_sightings=rejected_sightings)
    except Exception as e:
        print(f"Error in admin_sightings: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('An error occurred while fetching criminal sightings.', 'danger')
        return render_template('admin_sightings.html',
                              pending_sightings=[],
                              verified_sightings=[],
                              rejected_sightings=[])

@app.route('/verify_sighting', methods=['POST'])
def verify_sighting():
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        sighting_id = request.form['sighting_id']
        admin_notes = request.form.get('admin_notes', '')

        print(f"Verifying sighting with ID: {sighting_id}")

        # Read the CSV file
        with open(CRIMINAL_SIGHTINGS_FILE, 'r') as f:
            lines = f.readlines()

        # Parse the header
        header = lines[0].strip().split(',')

        # Find the sighting and update its status
        updated_lines = [lines[0]]  # Keep the header
        sighting_found = False
        sighting_data = {}  # Store sighting data for email

        for i in range(1, len(lines)):
            line = lines[i].strip()
            if not line:
                updated_lines.append('\n')
                continue

            # Parse the line
            parts = []
            in_quotes = False
            current_part = ""

            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                    current_part += char
                elif char == ',' and not in_quotes:
                    parts.append(current_part)
                    current_part = ""
                else:
                    current_part += char

            # Add the last part
            if current_part:
                parts.append(current_part)

            # Create a dictionary for this sighting
            sighting = {}
            for j in range(min(len(header), len(parts))):
                value = parts[j].strip('"')
                sighting[header[j]] = value

            # Check if this is the sighting we're looking for
            if sighting.get('id') == sighting_id:
                sighting_found = True
                sighting_data = sighting.copy()  # Store for email
                print(f"Found sighting to verify: {sighting['criminal_name']} (ID: {sighting['criminal_id']})")

                # Update the status and admin notes
                status_index = header.index('status') if 'status' in header else -1
                admin_notes_index = header.index('admin_notes') if 'admin_notes' in header else -1
                email_sent_index = header.index('email_sent') if 'email_sent' in header else -1

                if status_index >= 0:
                    if status_index < len(parts):
                        parts[status_index] = 'verified'
                    else:
                        # Add missing fields
                        while len(parts) <= status_index:
                            parts.append('')
                        parts[status_index] = 'verified'

                if admin_notes_index >= 0:
                    if admin_notes_index < len(parts):
                        parts[admin_notes_index] = f'"{admin_notes}"' if ',' in admin_notes else admin_notes
                    else:
                        # Add missing fields
                        while len(parts) <= admin_notes_index:
                            parts.append('')
                        parts[admin_notes_index] = f'"{admin_notes}"' if ',' in admin_notes else admin_notes

                # Update email_sent field
                if email_sent_index >= 0:
                    if email_sent_index < len(parts):
                        parts[email_sent_index] = 'no'  # Reset to 'no' so we can send email
                    else:
                        # Add missing fields
                        while len(parts) <= email_sent_index:
                            parts.append('')
                        parts[email_sent_index] = 'no'

                # Reconstruct the line
                updated_line = ','.join(parts) + '\n'
            else:
                updated_line = line + '\n'

            updated_lines.append(updated_line)

        # Write the updated CSV file
        with open(CRIMINAL_SIGHTINGS_FILE, 'w') as f:
            f.writelines(updated_lines)

        if sighting_found:
            # Send email notification
            if 'reported_by_email' in sighting_data and sighting_data['reported_by_email']:
                try:
                    recipient_email = sighting_data['reported_by_email']
                    username = sighting_data['reported_by']
                    criminal_name = sighting_data['criminal_name']
                    criminal_id = sighting_data['criminal_id']
                    location = sighting_data['location']
                    sighting_date = sighting_data['sighting_date']
                    sighting_time = sighting_data['sighting_time']

                    print(f"Sending verification email to {recipient_email}")

                    # Send the email
                    email_sent = send_email(
                        to=recipient_email,
                        subject=f"Criminal Sighting Verified: {criminal_name}",
                        template='email_verification.html',
                        username=username,
                        criminal_name=criminal_name,
                        criminal_id=criminal_id,
                        location=location,
                        sighting_date=sighting_date,
                        sighting_time=sighting_time,
                        admin_notes=admin_notes
                    )

                    if email_sent:
                        print(f"Verification email sent successfully to {recipient_email}")

                        # Update the email_sent field in the CSV
                        df = pd.read_csv(CRIMINAL_SIGHTINGS_FILE)
                        df.loc[df['id'] == sighting_id, 'email_sent'] = 'yes'
                        df.to_csv(CRIMINAL_SIGHTINGS_FILE, index=False)

                        flash(f'Sighting verified successfully! Email notification sent to {recipient_email}', 'success')
                    else:
                        print(f"Failed to send verification email to {recipient_email}")
                        flash('Sighting verified successfully, but email notification failed to send.', 'warning')
                except Exception as email_error:
                    print(f"Error sending verification email: {str(email_error)}")
                    flash('Sighting verified successfully, but email notification failed to send.', 'warning')
            else:
                flash('Sighting verified successfully!', 'success')
        else:
            flash('Sighting not found!', 'danger')
    except Exception as e:
        print(f"Error in verify_sighting: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('An error occurred while verifying the sighting!', 'danger')

    return redirect(url_for('admin_sightings'))

@app.route('/reject_sighting', methods=['POST'])
def reject_sighting():
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        sighting_id = request.form['sighting_id']
        admin_notes = request.form.get('admin_notes', '')

        print(f"Rejecting sighting with ID: {sighting_id}")

        # Read the CSV file
        with open(CRIMINAL_SIGHTINGS_FILE, 'r') as f:
            lines = f.readlines()

        # Parse the header
        header = lines[0].strip().split(',')

        # Find the sighting and update its status
        updated_lines = [lines[0]]  # Keep the header
        sighting_found = False
        sighting_data = {}  # Store sighting data for email

        for i in range(1, len(lines)):
            line = lines[i].strip()
            if not line:
                updated_lines.append('\n')
                continue

            # Parse the line
            parts = []
            in_quotes = False
            current_part = ""

            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                    current_part += char
                elif char == ',' and not in_quotes:
                    parts.append(current_part)
                    current_part = ""
                else:
                    current_part += char

            # Add the last part
            if current_part:
                parts.append(current_part)

            # Create a dictionary for this sighting
            sighting = {}
            for j in range(min(len(header), len(parts))):
                value = parts[j].strip('"')
                sighting[header[j]] = value

            # Check if this is the sighting we're looking for
            if sighting.get('id') == sighting_id:
                sighting_found = True
                sighting_data = sighting.copy()  # Store for email
                print(f"Found sighting to reject: {sighting['criminal_name']} (ID: {sighting['criminal_id']})")

                # Update the status and admin notes
                status_index = header.index('status') if 'status' in header else -1
                admin_notes_index = header.index('admin_notes') if 'admin_notes' in header else -1
                email_sent_index = header.index('email_sent') if 'email_sent' in header else -1

                if status_index >= 0:
                    if status_index < len(parts):
                        parts[status_index] = 'rejected'
                    else:
                        # Add missing fields
                        while len(parts) <= status_index:
                            parts.append('')
                        parts[status_index] = 'rejected'

                if admin_notes_index >= 0:
                    if admin_notes_index < len(parts):
                        parts[admin_notes_index] = f'"{admin_notes}"' if ',' in admin_notes else admin_notes
                    else:
                        # Add missing fields
                        while len(parts) <= admin_notes_index:
                            parts.append('')
                        parts[admin_notes_index] = f'"{admin_notes}"' if ',' in admin_notes else admin_notes

                # Update email_sent field
                if email_sent_index >= 0:
                    if email_sent_index < len(parts):
                        parts[email_sent_index] = 'no'  # Reset to 'no' so we can send email
                    else:
                        # Add missing fields
                        while len(parts) <= email_sent_index:
                            parts.append('')
                        parts[email_sent_index] = 'no'

                # Reconstruct the line
                updated_line = ','.join(parts) + '\n'
            else:
                updated_line = line + '\n'

            updated_lines.append(updated_line)

        # Write the updated CSV file
        with open(CRIMINAL_SIGHTINGS_FILE, 'w') as f:
            f.writelines(updated_lines)

        if sighting_found:
            # Send email notification
            if 'reported_by_email' in sighting_data and sighting_data['reported_by_email']:
                try:
                    recipient_email = sighting_data['reported_by_email']
                    username = sighting_data['reported_by']
                    criminal_name = sighting_data['criminal_name']
                    criminal_id = sighting_data['criminal_id']
                    location = sighting_data['location']
                    sighting_date = sighting_data['sighting_date']
                    sighting_time = sighting_data['sighting_time']

                    print(f"Sending rejection email to {recipient_email}")

                    # Send the email
                    email_sent = send_email(
                        to=recipient_email,
                        subject=f"Criminal Sighting Report Update: {criminal_name}",
                        template='email_rejection.html',
                        username=username,
                        criminal_name=criminal_name,
                        criminal_id=criminal_id,
                        location=location,
                        sighting_date=sighting_date,
                        sighting_time=sighting_time,
                        admin_notes=admin_notes
                    )

                    if email_sent:
                        print(f"Rejection email sent successfully to {recipient_email}")

                        # Update the email_sent field in the CSV
                        df = pd.read_csv(CRIMINAL_SIGHTINGS_FILE)
                        df.loc[df['id'] == sighting_id, 'email_sent'] = 'yes'
                        df.to_csv(CRIMINAL_SIGHTINGS_FILE, index=False)

                        flash(f'Sighting rejected successfully! Email notification sent to {recipient_email}', 'success')
                    else:
                        print(f"Failed to send rejection email to {recipient_email}")
                        flash('Sighting rejected successfully, but email notification failed to send.', 'warning')
                except Exception as email_error:
                    print(f"Error sending rejection email: {str(email_error)}")
                    flash('Sighting rejected successfully, but email notification failed to send.', 'warning')
            else:
                flash('Sighting rejected successfully!', 'success')
        else:
            flash('Sighting not found!', 'danger')
    except Exception as e:
        print(f"Error in reject_sighting: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('An error occurred while rejecting the sighting!', 'danger')

    return redirect(url_for('admin_sightings'))

@app.route('/clear_sightings', methods=['POST'])
def clear_sightings():
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        status = request.form.get('status')
        if status not in ['verified', 'rejected']:
            flash('Invalid status specified!', 'danger')
            return redirect(url_for('admin_sightings'))

        # Read the CSV file
        df = pd.read_csv(CRIMINAL_SIGHTINGS_FILE)

        # Count how many records will be deleted
        count_to_delete = len(df[df['status'] == status])

        if count_to_delete == 0:
            flash(f'No {status} sightings to clear.', 'info')
            return redirect(url_for('admin_sightings'))

        # Get the image filenames to delete
        images_to_delete = df[df['status'] == status]['image_filename'].tolist()

        # Remove evidence files if they exist
        for image in images_to_delete:
            if image and image.strip():
                evidence_path = os.path.join(app.config['EVIDENCE_FOLDER'], image)
                if os.path.exists(evidence_path):
                    os.remove(evidence_path)
                    print(f"Deleted evidence file: {evidence_path}")

        # Filter out the records with the specified status
        df = df[df['status'] != status]

        # Save the updated DataFrame back to CSV
        df.to_csv(CRIMINAL_SIGHTINGS_FILE, index=False)

        flash(f'Successfully cleared {count_to_delete} {status} sightings!', 'success')
    except Exception as e:
        print(f"Error in clear_sightings: {str(e)}")
        flash(f'An error occurred while clearing {status} sightings: {str(e)}', 'danger')

    return redirect(url_for('admin_sightings'))

@app.route('/clear_single_sighting', methods=['POST'])
def clear_single_sighting():
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        sighting_id = request.form.get('sighting_id')
        if not sighting_id:
            flash('No sighting ID provided!', 'danger')
            return redirect(url_for('admin_sightings'))

        # Read the CSV file
        df = pd.read_csv(CRIMINAL_SIGHTINGS_FILE)

        # Find the sighting
        sighting = df[df['id'] == sighting_id]

        if sighting.empty:
            flash('Sighting not found!', 'danger')
            return redirect(url_for('admin_sightings'))

        # Get the image filename to delete
        image_filename = sighting.iloc[0]['image_filename']

        # Remove evidence file if it exists
        if image_filename and str(image_filename).strip() and str(image_filename) != 'nan':
            evidence_path = os.path.join(app.config['EVIDENCE_FOLDER'], image_filename)
            if os.path.exists(evidence_path):
                os.remove(evidence_path)
                print(f"Deleted evidence file: {evidence_path}")

        # Remove the sighting from the DataFrame
        df = df[df['id'] != sighting_id]

        # Save the updated DataFrame back to CSV
        df.to_csv(CRIMINAL_SIGHTINGS_FILE, index=False)

        flash('Sighting deleted successfully!', 'success')
    except Exception as e:
        print(f"Error in clear_single_sighting: {str(e)}")
        flash(f'An error occurred while deleting the sighting: {str(e)}', 'danger')

    return redirect(url_for('admin_sightings'))

@app.route('/manage_wanted_list')
def manage_wanted_list():
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        # Read wanted criminals from CSV
        print(f"Reading wanted criminals from {WANTED_CRIMINALS_FILE} for admin")
        df = pd.read_csv(WANTED_CRIMINALS_FILE)
        print(f"Found {len(df)} criminals in CSV for admin")

        if df.empty:
            criminals = []
            print("CSV is empty, no criminals to display for admin")
        else:
            # Convert DataFrame to list of dictionaries
            criminals = df.to_dict('records')
            print(f"Found {len(criminals)} criminals for admin")

            # Verify image files exist
            for criminal in criminals:
                image_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], criminal['image_filename'])
                if not os.path.exists(image_path):
                    print(f"Warning: Image file does not exist for admin: {image_path}")
                else:
                    print(f"Image file exists for admin: {image_path}")

        return render_template('manage_wanted_list.html', criminals=criminals)
    except Exception as e:
        print(f"Error in manage_wanted_list: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('An error occurred while fetching wanted criminals.', 'danger')
        return render_template('manage_wanted_list.html', criminals=[])

@app.route('/add_wanted_criminal', methods=['POST'])
def add_wanted_criminal():
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        # Get form data
        name = request.form['name']
        description = request.form['description']

        # Handle photo upload
        photo_file = request.files['photo']
        if not photo_file:
            flash('No photo provided!', 'danger')
            return redirect(url_for('manage_wanted_list'))

        # Generate a unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_extension = os.path.splitext(photo_file.filename)[1]
        image_filename = f"wanted_{timestamp}{file_extension}"

        # Save the photo to the view_records folder
        photo_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], image_filename)
        photo_file.save(photo_path)

        # Read the CSV file to get the next ID
        df = pd.read_csv(WANTED_CRIMINALS_FILE)
        if df.empty:
            next_id = 1
        else:
            next_id = df['id'].max() + 1

        # Add to wanted criminals
        new_criminal = pd.DataFrame([[
            next_id,
            name,
            image_filename,
            description,
            'active'  # Default status is active
        ]], columns=['id', 'name', 'image_filename', 'description', 'status'])

        pd.concat([df, new_criminal], ignore_index=True).to_csv(WANTED_CRIMINALS_FILE, index=False)

        flash('Wanted criminal added successfully!', 'success')
    except Exception as e:
        print(f"Error in add_wanted_criminal: {str(e)}")
        flash(f'An error occurred while adding the wanted criminal: {str(e)}', 'danger')

    return redirect(url_for('manage_wanted_list'))

@app.route('/remove_wanted_criminal/<int:criminal_id>')
def remove_wanted_criminal(criminal_id):
    if 'username' not in session or session.get('role') != 'official':
        return redirect(url_for('login'))

    try:
        # Read the CSV file
        df = pd.read_csv(WANTED_CRIMINALS_FILE)

        # Find the criminal
        criminal = df[df['id'] == criminal_id]

        if criminal.empty:
            flash('Criminal not found!', 'danger')
            return redirect(url_for('manage_wanted_list'))

        # Get the image filename to delete
        image_filename = criminal.iloc[0]['image_filename']

        # Remove image file if it exists
        if image_filename and str(image_filename).strip():
            image_path = os.path.join(app.config['VIEW_RECORDS_FOLDER'], image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"Deleted image file: {image_path}")

        # Remove the criminal from the DataFrame
        df = df[df['id'] != criminal_id]

        # Save the updated DataFrame back to CSV
        df.to_csv(WANTED_CRIMINALS_FILE, index=False)

        # Also remove any associated sightings
        sightings_df = pd.read_csv(CRIMINAL_SIGHTINGS_FILE)
        sightings_to_remove = sightings_df[sightings_df['criminal_id'] == str(criminal_id)]

        # Delete evidence files for removed sightings
        for _, row in sightings_to_remove.iterrows():
            if row['image_filename'] and str(row['image_filename']).strip() and str(row['image_filename']) != 'nan':
                evidence_path = os.path.join(app.config['EVIDENCE_FOLDER'], row['image_filename'])
                if os.path.exists(evidence_path):
                    os.remove(evidence_path)
                    print(f"Deleted evidence file: {evidence_path}")

        # Remove sightings from DataFrame
        sightings_df = sightings_df[sightings_df['criminal_id'] != str(criminal_id)]
        sightings_df.to_csv(CRIMINAL_SIGHTINGS_FILE, index=False)

        flash('Wanted criminal removed successfully!', 'success')
    except Exception as e:
        print(f"Error in remove_wanted_criminal: {str(e)}")
        flash(f'An error occurred while removing the wanted criminal: {str(e)}', 'danger')

    return redirect(url_for('manage_wanted_list'))



if __name__ == '__main__':
    app.run(debug=True, port=5001)
