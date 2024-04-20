import os
import pyodbc
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash,check_password_hash
import matplotlib.pyplot as plt
import mpld3
import seaborn as sns
import pandas as pd
import numpy as np
from io import BytesIO
import base64

############### database connection ###############
# Get the current script's directory
current_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the database path
db_path = os.path.join(current_dir, 'edutech_db.accdb')

# Construct the connection string
conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            rf'DBQ={db_path};')

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


############### database connection ###############

app = Flask(__name__)
app.secret_key = 'keygen'

###########################################
# Routes for navigation bar

@app.route('/')
def home():  # put application's code here
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():  # put application's code here
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if role == 'admin':
            table = 'admin_auth'
        elif role == 'institute':
            table = 'institute_auth'
        elif role == 'student':
            table = 'student_auth'
        else:
            return render_template('login.html',error="Invalid role.")

        # SQL Injection Vulnerability - Use parameterized queries
        cursor.execute(f"SELECT * FROM {table} WHERE aadhaar_no = ?",(username,))
        result = cursor.fetchone()

        if result and check_password_hash(result.password,password):
            session['aadhaar_no'] = username
            return redirect(url_for(f'{role}_dashboard'))
        else:
            return render_template('login.html',error="Invalid username or password.")

    return render_template('login.html')

@app.route('/password_reset')
def password_reset():
    return render_template('password_reset.html')

@app.route('/register')
def register():
    return render_template('register_tnc.html')

@app.route('/registration_success')
def registration_success():
    return render_template('registration_success.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Routes for navigation bar
############################################


###########################################
# Routes for admin

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        return admin_register_post()
    else:
        return render_template('Admin/admin_register.html')

def admin_register_post():
    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        dob = request.form['dob']
        email = request.form['email']
        phone_no = request.form['phone_no']
        aadhaar_no = request.form['aadhaar_no']
        confirm_aadhaar_no = request.form['confirm_aadhaar_no']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Perform your validation checks here
        if aadhaar_no != confirm_aadhaar_no:
            return "Aadhaar numbers do not match", 400
        if password != confirm_password:
            return "Passwords do not match", 400

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert data into database
        cursor.execute("""
            INSERT INTO admin_auth (aadhaar_no, password)
            VALUES (?, ?)
        """, (aadhaar_no, hashed_password))

        cursor.execute("""
            INSERT INTO admin_info (first_name, last_name, gender, date_of_birth, email, phone_no, aadhaar_no)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, gender, dob, email, phone_no, aadhaar_no))

        # Commit changes and close connection
        conn.commit()

        # Redirect to success page
        return redirect(url_for('registration_success'))

    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e),500

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('Admin/admin_dashboard.html')


@app.route('/admin_manage')
def admin_manage():
    return render_template('Admin/admin_manage.html')



@app.route('/admin_profile')
def admin_profile():
    # Execute SQL query to fetch admin details
    cursor.execute("SELECT * FROM admin_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
    admin_details = cursor.fetchone()

    # Pass the admin details to the template
    return render_template('admin/admin_profile.html', admin=admin_details)

@app.route('/form_admin_info', methods=['GET', 'POST'])
def form_admin_info():
    if request.method == 'POST':
        return form_admin_info_post()
    else:
        # Fetch admin info from the database
        cursor.execute("SELECT * FROM admin_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        admin_info = cursor.fetchone()

        # assuming admin_info.date_of_birth is a datetime object
        if admin_info.date_of_birth:
            admin_info.date_of_birth = admin_info.date_of_birth.date()

        # If admin_info is None, create a default admin_info object
        if admin_info is None:
            admin_info = {
                'aadhaar_no': '',
                'pan_no': '',
                'first_name': '',
                'middle_name': '',
                'last_name': '',
                'date_of_birth': '',
                'gender': '',
                'phone_no': '',
                'email': ''
            }

        # Pass the admin info to the template
        return render_template('admin/form_admin_info.html', admin_info=admin_info)

def form_admin_info_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = request.form['aadhaar_no']
            pan_no = request.form['pan_no']
            first_name = request.form['first_name']
            middle_name = request.form['middle_name']
            last_name = request.form['last_name']
            date_of_birth = request.form['date_of_birth']
            gender = request.form['gender']
            phone_no = request.form['phone_no']
            email = request.form['email']

            # Update admin info in the database
            cursor.execute("""
                UPDATE admin_info
                SET pan_no = ?, first_name = ?, middle_name = ?, last_name = ?, date_of_birth = ?, gender = ?, phone_no = ?, email = ?
                WHERE aadhaar_no = ?
            """, (pan_no, first_name, middle_name, last_name, date_of_birth, gender, phone_no, email, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_admin_address'))

        else:
            # Fetch admin info from the database
            cursor.execute("SELECT * FROM admin_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            admin_info = cursor.fetchone()

            # Pass the admin info to the template
            return render_template('admin/form_admin_info.html', admin_info=admin_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e),500

@app.route('/form_admin_address', methods=['GET', 'POST'])
def form_admin_address():
    if request.method == 'POST':
        return form_admin_address_post()
    else:
        # Fetch address info from the database
        cursor.execute("SELECT * FROM admin_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        address_info = cursor.fetchone()

        # If address_info is None, create a default address_info object
        if address_info is None:
            address_info = {
                'ca_line_1': '',
                'ca_line_2': '',
                'ca_line_3': '',
                'ca_city': '',
                'ca_district': '',
                'ca_state': '',
                'ca_pincode': '',
                'pa_line_1': '',
                'pa_line_2': '',
                'pa_line_3': '',
                'pa_city': '',
                'pa_district': '',
                'pa_state': '',
                'pa_pincode': ''
            }

        # Pass the address info to the template
        return render_template('Admin/form_admin_address.html',admin_info=address_info)

def form_admin_address_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            ca_line_1 = request.form['ca_line_1']
            ca_line_2 = request.form['ca_line_2']
            ca_line_3 = request.form['ca_line_3']
            ca_city = request.form['ca_city']
            ca_district = request.form['ca_district']
            ca_state = request.form['ca_state']
            ca_pincode = request.form['ca_pincode']
            pa_line_1 = request.form['pa_line_1']
            pa_line_2 = request.form['pa_line_2']
            pa_line_3 = request.form['pa_line_3']
            pa_city = request.form['pa_city']
            pa_district = request.form['pa_district']
            pa_state = request.form['pa_state']
            pa_pincode = request.form['pa_pincode']

            # Update address info in the database
            cursor.execute("""
                UPDATE admin_info
                SET ca_line_1 = ?, ca_line_2 = ?, ca_line_3 = ?, ca_city = ?, ca_district = ?, ca_state = ?, ca_pincode = ?, pa_line_1 = ?, pa_line_2 = ?, pa_line_3 = ?, pa_city = ?, pa_district = ?, pa_state = ?, pa_pincode = ?
                WHERE aadhaar_no = ?
            """, (ca_line_1, ca_line_2, ca_line_3, ca_city, ca_district, ca_state, ca_pincode, pa_line_1, pa_line_2, pa_line_3, pa_city, pa_district, pa_state, pa_pincode, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_admin_address'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch address info from the database
            cursor.execute("SELECT * FROM admin_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            address_info = cursor.fetchone()

            # Pass the address info to the template
            return render_template('Admin/form_admin_address.html',admin_info=address_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


# Routes for admin
############################################


###########################################
# Routes for institute

@app.route('/institute_register', methods=['GET', 'POST'])
def institute_register():
    if request.method == 'POST':
        return institute_register_post()
    else:
        return render_template('Institute/institute_register.html')

def institute_register_post():
    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        dob = request.form['dob']
        email = request.form['email']
        phone_no = request.form['phone_no']
        institute_name = request.form['institute_name']
        institute_code = request.form['institute_code']
        institute_type = request.form['institute_type']
        institute_email = request.form['institute_email']
        institute_phone_no = request.form['institute_phone_no']
        aadhaar_no = request.form['aadhaar_no']
        confirm_aadhaar_no = request.form['confirm_aadhaar_no']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if aadhaar_no != confirm_aadhaar_no:
            return "Aadhaar numbers do not match",400
        # Check if passwords match
        if password != confirm_password:
            return "Passwords do not match",400

        if len(aadhaar_no) > 12:  # Assuming aadhaar_no should not be more than 12 digits
            return "Aadhaar number is too long",400
        if len(phone_no) > 10:  # Assuming phone_number should not be more than 10 digits
            return "Phone number is too long",400

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert data into database
        cursor.execute("""
            INSERT INTO institute_auth (aadhaar_no, password)
            VALUES (?, ?)
        """,(aadhaar_no,hashed_password))

        # Insert data into database
        cursor.execute("""
            INSERT INTO institute_info (first_name, last_name, gender, date_of_birth, email, phone_no, aadhaar_no, institute_name, institute_code, institute_type, institute_email, institute_phone_no)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,(first_name,last_name,gender,dob,email,phone_no,aadhaar_no,institute_name,institute_code,institute_type,institute_email,institute_phone_no))

        # Commit changes and close connection
        conn.commit()

        # Redirect to success page
        return redirect(url_for('registration_success'))
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e),500

@app.route('/institute_dashboard')
def institute_dashboard():
    return render_template('Institute/institute_dashboard.html')

@app.route('/institute_manage')
def institute_manage():
    return render_template('Institute/institute_manage.html')

@app.route('/institute_profile')
def institute_profile():
    # Execute SQL query to fetch institute details
    cursor.execute("SELECT * FROM institute_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
    institute_details = cursor.fetchone()

    # Pass the institute details to the template
    return render_template('Institute/institute_profile.html', institute=institute_details)

@app.route('/form_institute_info', methods=['GET', 'POST'])
def form_institute_info():
    if request.method == 'POST':
        return form_institute_info_post()
    else:
        # Fetch institute info from the database
        cursor.execute("SELECT * FROM institute_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        institute_info = cursor.fetchone()

        # assuming institute_info.date_of_birth is a datetime object
        if institute_info.date_of_birth:
            institute_info.date_of_birth = institute_info.date_of_birth.date()

        # If institute_info is None, create a default institute_info object
        if institute_info is None:
            institute_info = {
                'aadhaar_no': '',
                'pan_no': '',
                'first_name': '',
                'middle_name': '',
                'last_name': '',
                'date_of_birth': '',
                'gender': '',
                'phone_no': '',
                'email': ''
            }

        # Pass the institute info to the template
        return render_template('Institute/form_institute_info.html', institute_info=institute_info)

def form_institute_info_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = request.form['aadhaar_no']
            pan_no = request.form['pan_no']
            first_name = request.form['first_name']
            middle_name = request.form['middle_name']
            last_name = request.form['last_name']
            date_of_birth = request.form['date_of_birth']
            gender = request.form['gender']
            phone_no = request.form['phone_no']
            email = request.form['email']

            # Update institute info in the database
            cursor.execute("""
                UPDATE institute_info
                SET pan_no = ?, first_name = ?, middle_name = ?, last_name = ?, date_of_birth = ?, gender = ?, phone_no = ?, email = ?
                WHERE aadhaar_no = ?
            """, (pan_no, first_name, middle_name, last_name, date_of_birth, gender, phone_no, email, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_institute_address'))

        else:
            # Fetch institute info from the database
            cursor.execute("SELECT * FROM institute_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            institute_info = cursor.fetchone()

            # Pass the institute info to the template
            return render_template('Institute/form_institute_info.html', institute_info=institute_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e),500


@app.route('/form_institute_address', methods=['GET', 'POST'])
def form_institute_address():
    if request.method == 'POST':
        return form_institute_address_post()
    else:
        # Fetch address info from the database
        cursor.execute("SELECT * FROM institute_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        address_info = cursor.fetchone()

        # If address_info is None, create a default address_info object
        if address_info is None:
            address_info = {
                'ca_line_1': '',
                'ca_line_2': '',
                'ca_line_3': '',
                'ca_city': '',
                'ca_district': '',
                'ca_state': '',
                'ca_pincode': '',
                'pa_line_1': '',
                'pa_line_2': '',
                'pa_line_3': '',
                'pa_city': '',
                'pa_district': '',
                'pa_state': '',
                'pa_pincode': ''
            }

        # Pass the address info to the template
        return render_template('Institute/form_institute_address.html',institute_info=address_info)

def form_institute_address_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            ca_line_1 = request.form['ca_line_1']
            ca_line_2 = request.form['ca_line_2']
            ca_line_3 = request.form['ca_line_3']
            ca_city = request.form['ca_city']
            ca_district = request.form['ca_district']
            ca_state = request.form['ca_state']
            ca_pincode = request.form['ca_pincode']
            pa_line_1 = request.form['pa_line_1']
            pa_line_2 = request.form['pa_line_2']
            pa_line_3 = request.form['pa_line_3']
            pa_city = request.form['pa_city']
            pa_district = request.form['pa_district']
            pa_state = request.form['pa_state']
            pa_pincode = request.form['pa_pincode']

            # Update address info in the database
            cursor.execute("""
                UPDATE institute_info
                SET ca_line_1 = ?, ca_line_2 = ?, ca_line_3 = ?, ca_city = ?, ca_district = ?, ca_state = ?, ca_pincode = ?, pa_line_1 = ?, pa_line_2 = ?, pa_line_3 = ?, pa_city = ?, pa_district = ?, pa_state = ?, pa_pincode = ?
                WHERE aadhaar_no = ?
            """, (ca_line_1, ca_line_2, ca_line_3, ca_city, ca_district, ca_state, ca_pincode, pa_line_1, pa_line_2, pa_line_3, pa_city, pa_district, pa_state, pa_pincode, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_institute_address'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch address info from the database
            cursor.execute("SELECT * FROM institute_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            address_info = cursor.fetchone()

            # Pass the address info to the template
            return render_template('Institute/form_institute_address.html',institute_info=address_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


# Routes for institute
############################################

###########################################
# Routes for student

@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        return student_register_post()
    else:
        return render_template('Student/student_register.html')

def student_register_post():
    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        dob = request.form['dob']
        email = request.form['email']
        phone_no = request.form['phone_no']
        aadhaar_no = request.form['aadhaar_no']
        confirm_aadhaar_no = request.form['confirm_aadhaar_no']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if aadhaar_no != confirm_aadhaar_no:
            return "Aadhaar numbers do not match",400
        # Check if passwords match
        if password != confirm_password:
            return "Passwords do not match",400

        if len(aadhaar_no) > 12:  # Assuming aadhaar_no should not be more than 12 digits
            return "Aadhaar number is too long", 400
        if len(phone_no) > 10:  # Assuming phone_number should not be more than 10 digits
            return "Phone number is too long", 400

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert data into database
        cursor.execute("""
            INSERT INTO student_auth (aadhaar_no, password)
            VALUES (?, ?)
        """,(aadhaar_no, hashed_password))

        # Insert data into database
        cursor.execute("""
            INSERT INTO student_info (first_name, last_name, gender, date_of_birth, email, phone_no, aadhaar_no)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,(first_name,last_name,gender,dob,email,phone_no,aadhaar_no))

        # Commit changes and close connection
        conn.commit()

        # Redirect to success page
        return redirect(url_for('registration_success'))
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e),500

# @app.route('/student_dashboard1')
# def student_dashboard1():
#
#     marks_obtained = []
#     total_marks = []
#     percentage = []
#     grade = []
#     cgpa = []
#
#     for i in range(1,13):
#         # Execute the SQL query
#         cursor.execute(
#             f"SELECT c_{i}_marks_obtained, c_{i}_total_marks, c_{i}_percentage, c_{i}_grade, c_{i}_cgpa FROM class_{i} WHERE aadhaar_no = ?",
#             (session['aadhaar_no'],))
#
#         # Fetch all the rows
#         data = cursor.fetchall()
#
#         marks_obtained_class = []
#         total_marks_class = []
#         percentage_class = []
#         grade_class = []
#         cgpa_class = []
#
#         if data:
#             for row in data:
#                 marks_obtained_class.append(row[0])
#                 total_marks_class.append(row[1])
#                 percentage_class.append(row[2])
#                 grade_class.append(row[3])
#                 cgpa_class.append(row[4])
#
#         marks_obtained.append(marks_obtained_class)
#         total_marks.append(total_marks_class)
#         percentage.append(percentage_class)
#         grade.append(grade_class)
#         cgpa.append(cgpa_class)
#
#     print(marks_obtained)
#     print(total_marks)
#     print(percentage)
#     print(grade)
#     print(cgpa)
#
#     # Convert nested lists to flat lists
#     marks_obtained = [int(x[0]) for x in marks_obtained]
#     total_marks = [int(x[0]) for x in total_marks]
#     percentage = [float(x[0]) for x in percentage]
#     grade = [x[0] for x in grade]
#     cgpa = [float(x[0]) for x in cgpa]
#
#     class_labels = ["Class 1","Class 2","Class 3","Class 4","Class 5","Class 6","Class 7","Class 8","Class 9",
#                     "Class 10","Class 11","Class 12"]
#
#     # Create bar graphs
#     # Set the color palette
#     colors = sns.color_palette("icefire", 5)
#     # Marks Obtained vs Total Marks
#     fig,ax = plt.subplots(figsize=(5,5))
#
#     # Width of each bar
#     bar_width = 0.35
#
#     # Position of each bar on x-axis
#     x = np.arange(len(class_labels))
#
#     # Plot the bars
#     ax.bar(x - bar_width / 2,marks_obtained,bar_width,label='Marks Obtained', color=colors[0])
#     ax.bar(x + bar_width / 2,total_marks,bar_width,label='Total Marks', color=colors[1])
#
#     # Add labels, title, and legend
#     ax.set_xlabel('Classes')
#     ax.set_ylabel('Marks')
#     ax.set_title('Marks Obtained vs Total Marks')
#     ax.set_xticks(x)
#     ax.set_xticklabels(class_labels,rotation=45)
#     ax.legend()
#     marks_total_img = BytesIO()
#     plt.savefig(marks_total_img,format='png')
#     marks_total_img.seek(0)
#     marks_total_img_encoded = base64.b64encode(marks_total_img.getvalue()).decode('utf-8')
#     marks_total_img_html = f'<img src="data:image/png;base64,{marks_total_img_encoded}" alt="Marks Obtained vs Total Marks">'
#
#     # Percentage vs Classes
#     plt.figure(figsize=(5, 5))
#     plt.bar(class_labels, percentage, label="Percentage", color=colors[2])
#     plt.xlabel('Classes')
#     plt.ylabel('Percentage')
#     plt.title('Percentage vs Classes')
#     plt.xticks(rotation=45)
#     plt.yticks([i for i in range(0,101,5)])
#     plt.legend()
#     percentage_img = BytesIO()
#     plt.savefig(percentage_img, format='png')
#     percentage_img.seek(0)
#     percentage_img_encoded = base64.b64encode(percentage_img.getvalue()).decode('utf-8')
#     percentage_img_html = f'<img src="data:image/png;base64,{percentage_img_encoded}" alt="Percentage vs Classes">'
#
#     # Grade vs Classes
#     grade_mapping = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}
#     numerical_grades = [grade_mapping[grade] for grade in grade]
#     plt.figure(figsize=(5, 5))
#     plt.bar(class_labels, numerical_grades, label="Grade", color=colors[3])
#     plt.xlabel('Classes')
#     plt.ylabel('Grade')
#     plt.title('Grade vs Classes')
#     plt.xticks(rotation=45)
#     plt.yticks(range(6), ['F', 'E', 'D', 'C', 'B', 'A'])
#     plt.legend()
#     grade_img = BytesIO()
#     plt.savefig(grade_img, format='png')
#     grade_img.seek(0)
#     grade_img_encoded = base64.b64encode(grade_img.getvalue()).decode('utf-8')
#     grade_img_html = f'<img src="data:image/png;base64,{grade_img_encoded}" alt="Grade vs Classes">'
#
#     # CGPA vs Classes
#     plt.figure(figsize=(5, 5))
#     plt.bar(class_labels, cgpa, label="CGPA", color=colors[4])
#     plt.xlabel('Classes')
#     plt.ylabel('CGPA')
#     plt.title('CGPA vs Classes')
#     plt.xticks(rotation=45)
#     plt.yticks([i for i in range(0,10,1)])
#     plt.legend()
#     cgpa_img = BytesIO()
#     plt.savefig(cgpa_img, format='png')
#     cgpa_img.seek(0)
#     cgpa_img_encoded = base64.b64encode(cgpa_img.getvalue()).decode('utf-8')
#     cgpa_img_html = f'<img src="data:image/png;base64,{cgpa_img_encoded}" alt="CGPA vs Classes">'
#
#     # Render the student_dashboard.html template and pass the bar graph images as HTML
#     return render_template('Student/student_dashboard.html', marks_total_img=marks_total_img_html,percentage_img=percentage_img_html, grade_img=grade_img_html, cgpa_img=cgpa_img_html)

@app.route('/student_dashboard')
def student_dashboard():

    marks_obtained = []
    total_marks = []
    percentage = []
    grade = []
    cgpa = []

    for i in range(1, 13):
        # Execute the SQL query
        cursor.execute(
            f"SELECT c_{i}_marks_obtained, c_{i}_total_marks, c_{i}_percentage, c_{i}_grade, c_{i}_cgpa FROM class_{i} WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))

        # Fetch all the rows
        data = cursor.fetchall()

        marks_obtained_class = []
        total_marks_class = []
        percentage_class = []
        grade_class = []
        cgpa_class = []

        if data:
            for row in data:
                marks_obtained_class.append(row[0])
                total_marks_class.append(row[1])
                percentage_class.append(row[2])
                grade_class.append(row[3])
                cgpa_class.append(row[4])

        marks_obtained.append(marks_obtained_class)
        total_marks.append(total_marks_class)
        percentage.append(percentage_class)
        grade.append(grade_class)
        cgpa.append(cgpa_class)

    # Convert nested lists to flat lists
    marks_obtained = [int(x[0]) if x else 0 for x in marks_obtained]
    total_marks = [int(x[0]) if x else 0 for x in total_marks]

    class_labels = ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Class 7", "Class 8", "Class 9",
                    "Class 10", "Class 11", "Class 12"]

    # Create bar graphs
    # Set the color palette
    colors = sns.color_palette("icefire", 5)

    # Marks Obtained vs Total Marks
    if marks_obtained and total_marks:
        fig,ax = plt.subplots(figsize=(5,5))
        bar_width = 0.35
        x = np.arange(len(class_labels))
        ax.bar(x - bar_width / 2,marks_obtained,bar_width,label='Marks Obtained',color=colors[0])
        ax.bar(x + bar_width / 2,total_marks,bar_width,label='Total Marks',color=colors[1])
        ax.set_xlabel('Classes')
        ax.set_ylabel('Marks')
        ax.set_title('Marks Obtained vs Total Marks')
        ax.set_xticks(x)
        ax.set_xticklabels(class_labels,rotation=45)
        ax.legend()
        marks_total_img = BytesIO()
        plt.savefig(marks_total_img,format='png')
        marks_total_img.seek(0)
        marks_total_img_encoded = base64.b64encode(marks_total_img.getvalue()).decode('utf-8')
        marks_total_img_html = f'<img src="data:image/png;base64,{marks_total_img_encoded}" alt="Marks Obtained vs Total Marks">'

    # Check if the lists are not empty before converting them for other graphs
    if percentage:
        percentage = [float(x[0]) if x else 0.0 for x in percentage]

        # Percentage vs Classes
        plt.figure(figsize=(5, 5))
        plt.bar(class_labels, percentage, label="Percentage", color=colors[2])
        plt.xlabel('Classes')
        plt.ylabel('Percentage')
        plt.title('Percentage vs Classes')
        plt.xticks(rotation=45)
        plt.yticks([i for i in range(0, 101, 5)])
        plt.legend()
        percentage_img = BytesIO()
        plt.savefig(percentage_img, format='png')
        percentage_img.seek(0)
        percentage_img_encoded = base64.b64encode(percentage_img.getvalue()).decode('utf-8')
        percentage_img_html = f'<img src="data:image/png;base64,{percentage_img_encoded}" alt="Percentage vs Classes">'
    else:
        percentage_img_html = "<p>No data available for Percentage vs Classes</p>"

    # Check if the lists are not empty before converting them for Grade vs Classes
    if grade:
        grade_mapping = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}
        numerical_grades = [grade_mapping[g[0]] if g else 0 for g in grade]

        # Grade vs Classes
        plt.figure(figsize=(5, 5))
        plt.bar(class_labels, numerical_grades, label="Grade", color=colors[3])
        plt.xlabel('Classes')
        plt.ylabel('Grade')
        plt.title('Grade vs Classes')
        plt.xticks(rotation=45)
        plt.yticks(range(6), ['F', 'E', 'D', 'C', 'B', 'A'])
        plt.legend()
        grade_img = BytesIO()
        plt.savefig(grade_img, format='png')
        grade_img.seek(0)
        grade_img_encoded = base64.b64encode(grade_img.getvalue()).decode('utf-8')
        grade_img_html = f'<img src="data:image/png;base64,{grade_img_encoded}" alt="Grade vs Classes">'
    else:
        grade_img_html = "<p>No data available for Grade vs Classes</p>"

    # Check if the lists are not empty before converting them for CGPA vs Classes
    if cgpa:
        cgpa = [float(x[0]) if x else 0.0 for x in cgpa]

        # CGPA vs Classes
        plt.figure(figsize=(5, 5))
        plt.bar(class_labels, cgpa, label="CGPA", color=colors[4])
        plt.xlabel('Classes')
        plt.ylabel('CGPA')
        plt.title('CGPA vs Classes')
        plt.xticks(rotation=45)
        plt.yticks([i for i in range(0, 10, 1)])
        plt.legend()
        cgpa_img = BytesIO()
        plt.savefig(cgpa_img, format='png')
        cgpa_img.seek(0)
        cgpa_img_encoded = base64.b64encode(cgpa_img.getvalue()).decode('utf-8')
        cgpa_img_html = f'<img src="data:image/png;base64,{cgpa_img_encoded}" alt="CGPA vs Classes">'
    else:
        cgpa_img_html = "<p>No data available for CGPA vs Classes</p>"

    # Render the student_dashboard.html template and pass the graph images as HTML
    return render_template('Student/student_dashboard.html', marks_total_img=marks_total_img_html,
                           percentage_img=percentage_img_html, grade_img=grade_img_html, cgpa_img=cgpa_img_html)

@app.route('/student_manage')
def student_manage():
    return render_template('Student/student_manage.html')

@app.route('/student_profile')
def student_profile():
    # Execute SQL query to fetch student details
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
    student_details = cursor.fetchone()



    # Pass the student details to the template
    return render_template('Student/student_profile.html', student=student_details)

# Routes for student
############################################

###########################################
# Routes for student form

@app.route('/form_student_info', methods=['GET', 'POST'])
def form_student_info():
    if request.method == 'POST':
        return form_student_info_post()
    else:
        # Fetch student info from the database
        cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        student_info = cursor.fetchone()

        # assuming student_info.date_of_birth is a datetime object
        if student_info.date_of_birth:
            student_info.date_of_birth = student_info.date_of_birth.date()

        # If student_info is None, create a default student_info object
        if student_info is None:
            student_info = {
                'aadhaar_no': '',
                'pan_no': '',
                'first_name': '',
                'middle_name': '',
                'last_name': '',
                'date_of_birth': '',
                'gender': '',
                'phone_no': '',
                'email': ''
            }

        # Pass the student info to the template
        return render_template('Student/student_info_forms/form_student_info.html', student_info=student_info)

def form_student_info_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = request.form['aadhaar_no']
            pan_no = request.form['pan_no']
            first_name = request.form['first_name']
            middle_name = request.form['middle_name']
            last_name = request.form['last_name']
            date_of_birth = request.form['date_of_birth']
            gender = request.form['gender']
            phone_no = request.form['phone_no']
            email = request.form['email']

            # Update student info in the database
            cursor.execute("""
                UPDATE student_info
                SET pan_no = ?, first_name = ?, middle_name = ?, last_name = ?, date_of_birth = ?, gender = ?, phone_no = ?, email = ?
                WHERE aadhaar_no = ?
            """, (pan_no, first_name, middle_name, last_name, date_of_birth, gender, phone_no, email, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_parents_info'))

        else:
            # Fetch student info from the database
            cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            student_info = cursor.fetchone()

            # Pass the student info to the template
            return render_template('Student/student_info_forms/form_student_info.html', student_info=student_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e),500

@app.route('/form_parents_info', methods=['GET', 'POST'])
def form_parents_info():
    if request.method == 'POST':
        return form_parents_info_post()
    else:
        # Fetch parents info from the database
        cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        parents_info = cursor.fetchone()

        # If parents_info is None, create a default parents_info object
        if parents_info is None:
            parents_info = {
                'f_first_name': '',
                'f_middle_name': '',
                'f_last_name': '',
                'f_phone_no': '',
                'f_email': '',
                'f_occupation': '',
                'm_first_name': '',
                'm_middle_name': '',
                'm_last_name': '',
                'm_phone_no': '',
                'm_email': '',
                'm_occupation': ''
            }

        # Pass the parents info to the template
        return render_template('Student/student_info_forms/form_parents_info.html', student_info=parents_info)

def form_parents_info_post():
    try:
        if request.method == 'POST':
            # Get form data
            f_first_name = request.form['f_first_name']
            f_middle_name = request.form['f_middle_name']
            f_last_name = request.form['f_last_name']
            f_phone_no = request.form['f_phone_no']
            f_email = request.form['f_email']
            f_occupation = request.form['f_occupation']
            m_first_name = request.form['m_first_name']
            m_middle_name = request.form['m_middle_name']
            m_last_name = request.form['m_last_name']
            m_phone_no = request.form['m_phone_no']
            m_email = request.form['m_email']
            m_occupation = request.form['m_occupation']

            # Update parents info in the database
            cursor.execute("""
                UPDATE student_info
                SET f_first_name = ?, f_middle_name = ?, f_last_name = ?, f_phone_no = ?, f_email = ?,f_occupation = ?, m_first_name = ?, m_middle_name = ?, m_last_name = ?, m_phone_no = ?, m_email = ?, m_occupation = ?
                WHERE aadhaar_no = ?
            """, (f_first_name, f_middle_name, f_last_name, f_phone_no, f_email, f_occupation, m_first_name, m_middle_name, m_last_name, m_phone_no, m_email, m_occupation, session['aadhaar_no']))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect('/form_student_address')

        else:
            # Fetch parents info from the database
            cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            parents_info = cursor.fetchone()

            # Pass the parents info to the template
            return render_template('Student/student_info_forms/form_parents_info.html', student_info=parents_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_student_address', methods=['GET', 'POST'])
def form_student_address():
    if request.method == 'POST':
        return form_student_address_post()
    else:
        # Fetch address info from the database
        cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        address_info = cursor.fetchone()

        # If address_info is None, create a default address_info object
        if address_info is None:
            address_info = {
                'ca_line_1': '',
                'ca_line_2': '',
                'ca_line_3': '',
                'ca_city': '',
                'ca_district': '',
                'ca_state': '',
                'ca_pincode': '',
                'pa_line_1': '',
                'pa_line_2': '',
                'pa_line_3': '',
                'pa_city': '',
                'pa_district': '',
                'pa_state': '',
                'pa_pincode': ''
            }

        # Pass the address info to the template
        return render_template('Student/student_info_forms/form_student_address.html',student_info=address_info)

def form_student_address_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            ca_line_1 = request.form['ca_line_1']
            ca_line_2 = request.form['ca_line_2']
            ca_line_3 = request.form['ca_line_3']
            ca_city = request.form['ca_city']
            ca_district = request.form['ca_district']
            ca_state = request.form['ca_state']
            ca_pincode = request.form['ca_pincode']
            pa_line_1 = request.form['pa_line_1']
            pa_line_2 = request.form['pa_line_2']
            pa_line_3 = request.form['pa_line_3']
            pa_city = request.form['pa_city']
            pa_district = request.form['pa_district']
            pa_state = request.form['pa_state']
            pa_pincode = request.form['pa_pincode']

            # Update address info in the database
            cursor.execute("""
                UPDATE student_info
                SET ca_line_1 = ?, ca_line_2 = ?, ca_line_3 = ?, ca_city = ?, ca_district = ?, ca_state = ?, ca_pincode = ?, pa_line_1 = ?, pa_line_2 = ?, pa_line_3 = ?, pa_city = ?, pa_district = ?, pa_state = ?, pa_pincode = ?
                WHERE aadhaar_no = ?
            """, (ca_line_1, ca_line_2, ca_line_3, ca_city, ca_district, ca_state, ca_pincode, pa_line_1, pa_line_2, pa_line_3, pa_city, pa_district, pa_state, pa_pincode, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_c_1'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch address info from the database
            cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            address_info = cursor.fetchone()

            # Pass the address info to the template
            return render_template('Student/student_info_forms/form_student_address.html',student_info=address_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_c_1', methods=['GET', 'POST'])
def form_c_1():
    if request.method == 'POST':
        return form_c_1_post()
    else:
        # Fetch c_1_info from the database
        cursor.execute("SELECT * FROM class_1 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        c_1_info = cursor.fetchone()

        # If c_1_info is None, create a default c_1_info object
        if c_1_info is None:
            c_1_info = {
				' c_1_year': '',
				' c_1_board': '',
				' c_1_roll_no': '',
				' c_1_result': '',
                ' c_1_sub_1_name': '',
                ' c_1_sub_1_marks_obtained': '',
                ' c_1_sub_1_total_marks': '',
                ' c_1_sub_2_name': '',
                ' c_1_sub_2_marks_obtained': '',
                ' c_1_sub_2_total_marks': '',
                ' c_1_sub_3_name': '',
                ' c_1_sub_3_marks_obtained': '',
                ' c_1_sub_3_total_marks': '',
                ' c_1_sub_4_name': '',
                ' c_1_sub_4_marks_obtained': '',
                ' c_1_sub_4_total_marks': '',
                ' c_1_sub_5_name': '',
                ' c_1_sub_5_marks_obtained': '',
                ' c_1_sub_5_total_marks': '',
                ' c_1_sub_6_name': '',
                ' c_1_sub_6_marks_obtained': '',
                ' c_1_sub_6_total_marks': '',
                ' c_1_sub_7_name': '',
                ' c_1_sub_7_marks_obtained': '',
                ' c_1_sub_7_total_marks': '',
                ' c_1_sub_8_name': '',
                ' c_1_sub_8_marks_obtained': '',
                ' c_1_sub_8_total_marks': '',
                ' c_1_sub_9_name': '',
                ' c_1_sub_9_marks_obtained': '',
                ' c_1_sub_9_total_marks': '',
                ' c_1_sub_10_name': '',
                ' c_1_sub_10_marks_obtained': '',
                ' c_1_sub_10_total_marks': '',
                ' c_1_sub_11_name': '',
                ' c_1_sub_11_marks_obtained': '',
                ' c_1_sub_11_total_marks': '',
                ' c_1_sub_12_name': '',
                ' c_1_sub_12_marks_obtained': '',
                ' c_1_sub_12_total_marks': '',
                ' c_1_sub_13_name': '',
                ' c_1_sub_13_marks_obtained': '',
                ' c_1_sub_13_total_marks': '',
                ' c_1_sub_14_name': '',
                ' c_1_sub_14_marks_obtained': '',
                ' c_1_sub_14_total_marks': '',
                ' c_1_sub_15_name': '',
                ' c_1_sub_15_marks_obtained': '',
                ' c_1_sub_15_total_marks': ''
            }

        # Pass the c_1_info to the template
        return render_template('Student/student_info_forms/form_c_1.html', class_1=c_1_info)

def form_c_1_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            c_1_year = request.form['c_1_year']
            c_1_board = request.form['c_1_board']
            c_1_roll_no = request.form['c_1_roll_no']
            c_1_result = request.form['c_1_result']
            c_1_sub_1_name = request.form['c_1_sub_1_name']
            c_1_sub_1_marks_obtained = request.form['c_1_sub_1_marks_obtained']
            c_1_sub_1_total_marks = request.form['c_1_sub_1_total_marks']
            c_1_sub_2_name = request.form['c_1_sub_2_name']
            c_1_sub_2_marks_obtained = request.form['c_1_sub_2_marks_obtained']
            c_1_sub_2_total_marks = request.form['c_1_sub_2_total_marks']
            c_1_sub_3_name = request.form['c_1_sub_3_name']
            c_1_sub_3_marks_obtained = request.form['c_1_sub_3_marks_obtained']
            c_1_sub_3_total_marks = request.form['c_1_sub_3_total_marks']
            c_1_sub_4_name = request.form['c_1_sub_4_name']
            c_1_sub_4_marks_obtained = request.form['c_1_sub_4_marks_obtained']
            c_1_sub_4_total_marks = request.form['c_1_sub_4_total_marks']
            c_1_sub_5_name = request.form['c_1_sub_5_name']
            c_1_sub_5_marks_obtained = request.form['c_1_sub_5_marks_obtained']
            c_1_sub_5_total_marks = request.form['c_1_sub_5_total_marks']
            c_1_sub_6_name = request.form['c_1_sub_6_name']
            c_1_sub_6_marks_obtained = request.form['c_1_sub_6_marks_obtained']
            c_1_sub_6_total_marks = request.form['c_1_sub_6_total_marks']
            c_1_sub_7_name = request.form['c_1_sub_7_name']
            c_1_sub_7_marks_obtained = request.form['c_1_sub_7_marks_obtained']
            c_1_sub_7_total_marks = request.form['c_1_sub_7_total_marks']
            c_1_sub_8_name = request.form['c_1_sub_8_name']
            c_1_sub_8_marks_obtained = request.form['c_1_sub_8_marks_obtained']
            c_1_sub_8_total_marks = request.form['c_1_sub_8_total_marks']
            c_1_sub_9_name = request.form['c_1_sub_9_name']
            c_1_sub_9_marks_obtained = request.form['c_1_sub_9_marks_obtained']
            c_1_sub_9_total_marks = request.form['c_1_sub_9_total_marks']
            c_1_sub_10_name = request.form['c_1_sub_10_name']
            c_1_sub_10_marks_obtained = request.form['c_1_sub_10_marks_obtained']
            c_1_sub_10_total_marks = request.form['c_1_sub_10_total_marks']
            c_1_sub_11_name = request.form['c_1_sub_11_name']
            c_1_sub_11_marks_obtained = request.form['c_1_sub_11_marks_obtained']
            c_1_sub_11_total_marks = request.form['c_1_sub_11_total_marks']
            c_1_sub_12_name = request.form['c_1_sub_12_name']
            c_1_sub_12_marks_obtained = request.form['c_1_sub_12_marks_obtained']
            c_1_sub_12_total_marks = request.form['c_1_sub_12_total_marks']
            c_1_sub_13_name = request.form['c_1_sub_13_name']
            c_1_sub_13_marks_obtained = request.form['c_1_sub_13_marks_obtained']
            c_1_sub_13_total_marks = request.form['c_1_sub_13_total_marks']
            c_1_sub_14_name = request.form['c_1_sub_14_name']
            c_1_sub_14_marks_obtained = request.form['c_1_sub_14_marks_obtained']
            c_1_sub_14_total_marks = request.form['c_1_sub_14_total_marks']
            c_1_sub_15_name = request.form['c_1_sub_15_name']
            c_1_sub_15_marks_obtained = request.form['c_1_sub_15_marks_obtained']
            c_1_sub_15_total_marks = request.form['c_1_sub_15_total_marks']

            # Check if c_1_info already exists
            cursor.execute("SELECT * FROM class_1 WHERE aadhaar_no = ?",(aadhaar_no,))
            existing_c_1_info = cursor.fetchone()

            if existing_c_1_info:
                # Update c_1_info in the database
                cursor.execute("""
                    UPDATE class_1 
                    SET 
						c_1_year = ?, c_1_board = ?, c_1_roll_no = ?, c_1_result = ?,
                        c_1_sub_1_name = ?, c_1_sub_1_marks_obtained = ?, c_1_sub_1_total_marks = ?, 
                        c_1_sub_2_name = ?, c_1_sub_2_marks_obtained = ?, c_1_sub_2_total_marks = ?, 
                        c_1_sub_3_name = ?, c_1_sub_3_marks_obtained = ?, c_1_sub_3_total_marks = ?, 
                        c_1_sub_4_name = ?, c_1_sub_4_marks_obtained = ?, c_1_sub_4_total_marks = ?, 
                        c_1_sub_5_name = ?, c_1_sub_5_marks_obtained = ?, c_1_sub_5_total_marks = ?, 
                        c_1_sub_6_name = ?, c_1_sub_6_marks_obtained = ?, c_1_sub_6_total_marks = ?, 
                        c_1_sub_7_name = ?, c_1_sub_7_marks_obtained = ?, c_1_sub_7_total_marks = ?, 
                        c_1_sub_8_name = ?, c_1_sub_8_marks_obtained = ?, c_1_sub_8_total_marks = ?, 
                        c_1_sub_9_name = ?, c_1_sub_9_marks_obtained = ?, c_1_sub_9_total_marks = ?, 
                        c_1_sub_10_name = ?, c_1_sub_10_marks_obtained = ?, c_1_sub_10_total_marks = ?, 
                        c_1_sub_11_name = ?, c_1_sub_11_marks_obtained = ?, c_1_sub_11_total_marks = ?, 
                        c_1_sub_12_name = ?, c_1_sub_12_marks_obtained = ?, c_1_sub_12_total_marks = ?, 
                        c_1_sub_13_name = ?, c_1_sub_13_marks_obtained = ?, c_1_sub_13_total_marks = ?, 
                        c_1_sub_14_name = ?, c_1_sub_14_marks_obtained = ?, c_1_sub_14_total_marks = ?, 
                        c_1_sub_15_name = ?, c_1_sub_15_marks_obtained = ?, c_1_sub_15_total_marks = ? 
                    WHERE aadhaar_no = ?
                """,(
					c_1_year, c_1_board, c_1_roll_no, c_1_result,
                    c_1_sub_1_name,c_1_sub_1_marks_obtained,c_1_sub_1_total_marks,
                    c_1_sub_2_name,c_1_sub_2_marks_obtained,c_1_sub_2_total_marks,
                    c_1_sub_3_name,c_1_sub_3_marks_obtained,c_1_sub_3_total_marks,
                    c_1_sub_4_name,c_1_sub_4_marks_obtained,c_1_sub_4_total_marks,
                    c_1_sub_5_name,c_1_sub_5_marks_obtained,c_1_sub_5_total_marks,
                    c_1_sub_6_name,c_1_sub_6_marks_obtained,c_1_sub_6_total_marks,
                    c_1_sub_7_name,c_1_sub_7_marks_obtained,c_1_sub_7_total_marks,
                    c_1_sub_8_name,c_1_sub_8_marks_obtained,c_1_sub_8_total_marks,
                    c_1_sub_9_name,c_1_sub_9_marks_obtained,c_1_sub_9_total_marks,
                    c_1_sub_10_name,c_1_sub_10_marks_obtained,c_1_sub_10_total_marks,
                    c_1_sub_11_name,c_1_sub_11_marks_obtained,c_1_sub_11_total_marks,
                    c_1_sub_12_name,c_1_sub_12_marks_obtained,c_1_sub_12_total_marks,
                    c_1_sub_13_name,c_1_sub_13_marks_obtained,c_1_sub_13_total_marks,
                    c_1_sub_14_name,c_1_sub_14_marks_obtained,c_1_sub_14_total_marks,
                    c_1_sub_15_name,c_1_sub_15_marks_obtained,c_1_sub_15_total_marks,
                    aadhaar_no
                ))
            else:
                # Insert new c_1_info into the database
                cursor.execute("""
                    INSERT INTO class_1 (
                        aadhaar_no, 
						c_1_year, c_1_board, c_1_roll_no, c_1_result,
                        c_1_sub_1_name, c_1_sub_1_marks_obtained, c_1_sub_1_total_marks, 
                        c_1_sub_2_name, c_1_sub_2_marks_obtained, c_1_sub_2_total_marks, 
                        c_1_sub_3_name, c_1_sub_3_marks_obtained, c_1_sub_3_total_marks, 
                        c_1_sub_4_name, c_1_sub_4_marks_obtained, c_1_sub_4_total_marks, 
                        c_1_sub_5_name, c_1_sub_5_marks_obtained, c_1_sub_5_total_marks, 
                        c_1_sub_6_name, c_1_sub_6_marks_obtained, c_1_sub_6_total_marks, 
                        c_1_sub_7_name, c_1_sub_7_marks_obtained, c_1_sub_7_total_marks, 
                        c_1_sub_8_name, c_1_sub_8_marks_obtained, c_1_sub_8_total_marks, 
                        c_1_sub_9_name, c_1_sub_9_marks_obtained, c_1_sub_9_total_marks, 
                        c_1_sub_10_name, c_1_sub_10_marks_obtained, c_1_sub_10_total_marks, 
                        c_1_sub_11_name, c_1_sub_11_marks_obtained, c_1_sub_11_total_marks, 
                        c_1_sub_12_name, c_1_sub_12_marks_obtained, c_1_sub_12_total_marks, 
                        c_1_sub_13_name, c_1_sub_13_marks_obtained, c_1_sub_13_total_marks, 
                        c_1_sub_14_name, c_1_sub_14_marks_obtained, c_1_sub_14_total_marks, 
                        c_1_sub_15_name, c_1_sub_15_marks_obtained, c_1_sub_15_total_marks 
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,(
                    aadhaar_no,
					c_1_year, c_1_board, c_1_roll_no, c_1_result,
                    c_1_sub_1_name,c_1_sub_1_marks_obtained,c_1_sub_1_total_marks,
                    c_1_sub_2_name,c_1_sub_2_marks_obtained,c_1_sub_2_total_marks,
                    c_1_sub_3_name,c_1_sub_3_marks_obtained,c_1_sub_3_total_marks,
                    c_1_sub_4_name,c_1_sub_4_marks_obtained,c_1_sub_4_total_marks,
                    c_1_sub_5_name,c_1_sub_5_marks_obtained,c_1_sub_5_total_marks,
                    c_1_sub_6_name,c_1_sub_6_marks_obtained,c_1_sub_6_total_marks,
                    c_1_sub_7_name,c_1_sub_7_marks_obtained,c_1_sub_7_total_marks,
                    c_1_sub_8_name,c_1_sub_8_marks_obtained,c_1_sub_8_total_marks,
                    c_1_sub_9_name,c_1_sub_9_marks_obtained,c_1_sub_9_total_marks,
                    c_1_sub_10_name,c_1_sub_10_marks_obtained,c_1_sub_10_total_marks,
                    c_1_sub_11_name,c_1_sub_11_marks_obtained,c_1_sub_11_total_marks,
                    c_1_sub_12_name,c_1_sub_12_marks_obtained,c_1_sub_12_total_marks,
                    c_1_sub_13_name,c_1_sub_13_marks_obtained,c_1_sub_13_total_marks,
                    c_1_sub_14_name,c_1_sub_14_marks_obtained,c_1_sub_14_total_marks,
                    c_1_sub_15_name,c_1_sub_15_marks_obtained,c_1_sub_15_total_marks
                ))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_c_2'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_1_info from the database
            cursor.execute("SELECT * FROM class_1 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            c_1_info = cursor.fetchone()

            # Pass the c_1_info to the template
            return render_template('Student/student_info_forms/form_c_1.html', class_1=c_1_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_c_2', methods=['GET', 'POST'])
def form_c_2():
    if request.method == 'POST':
        return form_c_2_post()
    else:
        # Fetch c_2_info from the database
        cursor.execute("SELECT * FROM class_2 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        c_2_info = cursor.fetchone()

        # If c_2_info is None, create a default c_2_info object
        if c_2_info is None:
            c_2_info = {
                ' c_2_year': '',
                ' c_2_board': '',
                ' c_2_roll_no': '',
                ' c_2_result': '',
                ' c_2_sub_1_name': '',
                ' c_2_sub_1_marks_obtained': '',
                ' c_2_sub_1_total_marks': '',
                ' c_2_sub_2_name': '',
                ' c_2_sub_2_marks_obtained': '',
                ' c_2_sub_2_total_marks': '',
                ' c_2_sub_3_name': '',
                ' c_2_sub_3_marks_obtained': '',
                ' c_2_sub_3_total_marks': '',
                ' c_2_sub_4_name': '',
                ' c_2_sub_4_marks_obtained': '',
                ' c_2_sub_4_total_marks': '',
                ' c_2_sub_5_name': '',
                ' c_2_sub_5_marks_obtained': '',
                ' c_2_sub_5_total_marks': '',
                ' c_2_sub_6_name': '',
                ' c_2_sub_6_marks_obtained': '',
                ' c_2_sub_6_total_marks': '',
                ' c_2_sub_7_name': '',
                ' c_2_sub_7_marks_obtained': '',
                ' c_2_sub_7_total_marks': '',
                ' c_2_sub_8_name': '',
                ' c_2_sub_8_marks_obtained': '',
                ' c_2_sub_8_total_marks': '',
                ' c_2_sub_9_name': '',
                ' c_2_sub_9_marks_obtained': '',
                ' c_2_sub_9_total_marks': '',
                ' c_2_sub_10_name': '',
                ' c_2_sub_10_marks_obtained': '',
                ' c_2_sub_10_total_marks': '',
                ' c_2_sub_11_name': '',
                ' c_2_sub_11_marks_obtained': '',
                ' c_2_sub_11_total_marks': '',
                ' c_2_sub_12_name': '',
                ' c_2_sub_12_marks_obtained': '',
                ' c_2_sub_12_total_marks': '',
                ' c_2_sub_13_name': '',
                ' c_2_sub_13_marks_obtained': '',
                ' c_2_sub_13_total_marks': '',
                ' c_2_sub_14_name': '',
                ' c_2_sub_14_marks_obtained': '',
                ' c_2_sub_14_total_marks': '',
                ' c_2_sub_15_name': '',
                ' c_2_sub_15_marks_obtained': '',
                ' c_2_sub_15_total_marks': ''
            }

        # Pass the c_2_info to the template
        return render_template('Student/student_info_forms/form_c_2.html', class_2=c_2_info)

def form_c_2_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            c_2_year = request.form['c_2_year']
            c_2_board = request.form['c_2_board']
            c_2_roll_no = request.form['c_2_roll_no']
            c_2_result = request.form['c_2_result']
            c_2_sub_1_name = request.form['c_2_sub_1_name']
            c_2_sub_1_marks_obtained = request.form['c_2_sub_1_marks_obtained']
            c_2_sub_1_total_marks = request.form['c_2_sub_1_total_marks']
            c_2_sub_2_name = request.form['c_2_sub_2_name']
            c_2_sub_2_marks_obtained = request.form['c_2_sub_2_marks_obtained']
            c_2_sub_2_total_marks = request.form['c_2_sub_2_total_marks']
            c_2_sub_3_name = request.form['c_2_sub_3_name']
            c_2_sub_3_marks_obtained = request.form['c_2_sub_3_marks_obtained']
            c_2_sub_3_total_marks = request.form['c_2_sub_3_total_marks']
            c_2_sub_4_name = request.form['c_2_sub_4_name']
            c_2_sub_4_marks_obtained = request.form['c_2_sub_4_marks_obtained']
            c_2_sub_4_total_marks = request.form['c_2_sub_4_total_marks']
            c_2_sub_5_name = request.form['c_2_sub_5_name']
            c_2_sub_5_marks_obtained = request.form['c_2_sub_5_marks_obtained']
            c_2_sub_5_total_marks = request.form['c_2_sub_5_total_marks']
            c_2_sub_6_name = request.form['c_2_sub_6_name']
            c_2_sub_6_marks_obtained = request.form['c_2_sub_6_marks_obtained']
            c_2_sub_6_total_marks = request.form['c_2_sub_6_total_marks']
            c_2_sub_7_name = request.form['c_2_sub_7_name']
            c_2_sub_7_marks_obtained = request.form['c_2_sub_7_marks_obtained']
            c_2_sub_7_total_marks = request.form['c_2_sub_7_total_marks']
            c_2_sub_8_name = request.form['c_2_sub_8_name']
            c_2_sub_8_marks_obtained = request.form['c_2_sub_8_marks_obtained']
            c_2_sub_8_total_marks = request.form['c_2_sub_8_total_marks']
            c_2_sub_9_name = request.form['c_2_sub_9_name']
            c_2_sub_9_marks_obtained = request.form['c_2_sub_9_marks_obtained']
            c_2_sub_9_total_marks = request.form['c_2_sub_9_total_marks']
            c_2_sub_10_name = request.form['c_2_sub_10_name']
            c_2_sub_10_marks_obtained = request.form['c_2_sub_10_marks_obtained']
            c_2_sub_10_total_marks = request.form['c_2_sub_10_total_marks']
            c_2_sub_11_name = request.form['c_2_sub_11_name']
            c_2_sub_11_marks_obtained = request.form['c_2_sub_11_marks_obtained']
            c_2_sub_11_total_marks = request.form['c_2_sub_11_total_marks']
            c_2_sub_12_name = request.form['c_2_sub_12_name']
            c_2_sub_12_marks_obtained = request.form['c_2_sub_12_marks_obtained']
            c_2_sub_12_total_marks = request.form['c_2_sub_12_total_marks']
            c_2_sub_13_name = request.form['c_2_sub_13_name']
            c_2_sub_13_marks_obtained = request.form['c_2_sub_13_marks_obtained']
            c_2_sub_13_total_marks = request.form['c_2_sub_13_total_marks']
            c_2_sub_14_name = request.form['c_2_sub_14_name']
            c_2_sub_14_marks_obtained = request.form['c_2_sub_14_marks_obtained']
            c_2_sub_14_total_marks = request.form['c_2_sub_14_total_marks']
            c_2_sub_15_name = request.form['c_2_sub_15_name']
            c_2_sub_15_marks_obtained = request.form['c_2_sub_15_marks_obtained']
            c_2_sub_15_total_marks = request.form['c_2_sub_15_total_marks']

            # Check if c_2_info already exists
            cursor.execute("SELECT * FROM class_2 WHERE aadhaar_no = ?",(aadhaar_no,))
            existing_c_2_info = cursor.fetchone()

            if existing_c_2_info:
                # Update c_2_info in the database
                cursor.execute("""
                    UPDATE class_2 
                    SET 
						c_2_year = ?, c_2_board = ?, c_2_roll_no = ?, c_2_result = ?,                    
                        c_2_sub_1_name = ?, c_2_sub_1_marks_obtained = ?, c_2_sub_1_total_marks = ?, 
                        c_2_sub_2_name = ?, c_2_sub_2_marks_obtained = ?, c_2_sub_2_total_marks = ?, 
                        c_2_sub_3_name = ?, c_2_sub_3_marks_obtained = ?, c_2_sub_3_total_marks = ?, 
                        c_2_sub_4_name = ?, c_2_sub_4_marks_obtained = ?, c_2_sub_4_total_marks = ?, 
                        c_2_sub_5_name = ?, c_2_sub_5_marks_obtained = ?, c_2_sub_5_total_marks = ?, 
                        c_2_sub_6_name = ?, c_2_sub_6_marks_obtained = ?, c_2_sub_6_total_marks = ?, 
                        c_2_sub_7_name = ?, c_2_sub_7_marks_obtained = ?, c_2_sub_7_total_marks = ?, 
                        c_2_sub_8_name = ?, c_2_sub_8_marks_obtained = ?, c_2_sub_8_total_marks = ?, 
                        c_2_sub_9_name = ?, c_2_sub_9_marks_obtained = ?, c_2_sub_9_total_marks = ?, 
                        c_2_sub_10_name = ?, c_2_sub_10_marks_obtained = ?, c_2_sub_10_total_marks = ?, 
                        c_2_sub_11_name = ?, c_2_sub_11_marks_obtained = ?, c_2_sub_11_total_marks = ?, 
                        c_2_sub_12_name = ?, c_2_sub_12_marks_obtained = ?, c_2_sub_12_total_marks = ?, 
                        c_2_sub_13_name = ?, c_2_sub_13_marks_obtained = ?, c_2_sub_13_total_marks = ?, 
                        c_2_sub_14_name = ?, c_2_sub_14_marks_obtained = ?, c_2_sub_14_total_marks = ?, 
                        c_2_sub_15_name = ?, c_2_sub_15_marks_obtained = ?, c_2_sub_15_total_marks = ? 
                    WHERE aadhaar_no = ?
                """,(
                    c_2_year,c_2_board,c_2_roll_no,c_2_result,
                    c_2_sub_1_name,c_2_sub_1_marks_obtained,c_2_sub_1_total_marks,
                    c_2_sub_2_name,c_2_sub_2_marks_obtained,c_2_sub_2_total_marks,
                    c_2_sub_3_name,c_2_sub_3_marks_obtained,c_2_sub_3_total_marks,
                    c_2_sub_4_name,c_2_sub_4_marks_obtained,c_2_sub_4_total_marks,
                    c_2_sub_5_name,c_2_sub_5_marks_obtained,c_2_sub_5_total_marks,
                    c_2_sub_6_name,c_2_sub_6_marks_obtained,c_2_sub_6_total_marks,
                    c_2_sub_7_name,c_2_sub_7_marks_obtained,c_2_sub_7_total_marks,
                    c_2_sub_8_name,c_2_sub_8_marks_obtained,c_2_sub_8_total_marks,
                    c_2_sub_9_name,c_2_sub_9_marks_obtained,c_2_sub_9_total_marks,
                    c_2_sub_10_name,c_2_sub_10_marks_obtained,c_2_sub_10_total_marks,
                    c_2_sub_11_name,c_2_sub_11_marks_obtained,c_2_sub_11_total_marks,
                    c_2_sub_12_name,c_2_sub_12_marks_obtained,c_2_sub_12_total_marks,
                    c_2_sub_13_name,c_2_sub_13_marks_obtained,c_2_sub_13_total_marks,
                    c_2_sub_14_name,c_2_sub_14_marks_obtained,c_2_sub_14_total_marks,
                    c_2_sub_15_name,c_2_sub_15_marks_obtained,c_2_sub_15_total_marks,
                    aadhaar_no
                ))
            else:
                # Insert new c_2_info into the database
                cursor.execute("""
                    INSERT INTO class_2 (
                        aadhaar_no,
						c_2_year, c_2_board, c_2_roll_no, c_2_result,                         
                        c_2_sub_1_name, c_2_sub_1_marks_obtained, c_2_sub_1_total_marks, 
                        c_2_sub_2_name, c_2_sub_2_marks_obtained, c_2_sub_2_total_marks, 
                        c_2_sub_3_name, c_2_sub_3_marks_obtained, c_2_sub_3_total_marks, 
                        c_2_sub_4_name, c_2_sub_4_marks_obtained, c_2_sub_4_total_marks, 
                        c_2_sub_5_name, c_2_sub_5_marks_obtained, c_2_sub_5_total_marks, 
                        c_2_sub_6_name, c_2_sub_6_marks_obtained, c_2_sub_6_total_marks, 
                        c_2_sub_7_name, c_2_sub_7_marks_obtained, c_2_sub_7_total_marks, 
                        c_2_sub_8_name, c_2_sub_8_marks_obtained, c_2_sub_8_total_marks, 
                        c_2_sub_9_name, c_2_sub_9_marks_obtained, c_2_sub_9_total_marks, 
                        c_2_sub_10_name, c_2_sub_10_marks_obtained, c_2_sub_10_total_marks, 
                        c_2_sub_11_name, c_2_sub_11_marks_obtained, c_2_sub_11_total_marks, 
                        c_2_sub_12_name, c_2_sub_12_marks_obtained, c_2_sub_12_total_marks, 
                        c_2_sub_13_name, c_2_sub_13_marks_obtained, c_2_sub_13_total_marks, 
                        c_2_sub_14_name, c_2_sub_14_marks_obtained, c_2_sub_14_total_marks, 
                        c_2_sub_15_name, c_2_sub_15_marks_obtained, c_2_sub_15_total_marks 
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,(
                    aadhaar_no,
                    c_2_year,c_2_board,c_2_roll_no,c_2_result,
                    c_2_sub_1_name,c_2_sub_1_marks_obtained,c_2_sub_1_total_marks,
                    c_2_sub_2_name,c_2_sub_2_marks_obtained,c_2_sub_2_total_marks,
                    c_2_sub_3_name,c_2_sub_3_marks_obtained,c_2_sub_3_total_marks,
                    c_2_sub_4_name,c_2_sub_4_marks_obtained,c_2_sub_4_total_marks,
                    c_2_sub_5_name,c_2_sub_5_marks_obtained,c_2_sub_5_total_marks,
                    c_2_sub_6_name,c_2_sub_6_marks_obtained,c_2_sub_6_total_marks,
                    c_2_sub_7_name,c_2_sub_7_marks_obtained,c_2_sub_7_total_marks,
                    c_2_sub_8_name,c_2_sub_8_marks_obtained,c_2_sub_8_total_marks,
                    c_2_sub_9_name,c_2_sub_9_marks_obtained,c_2_sub_9_total_marks,
                    c_2_sub_10_name,c_2_sub_10_marks_obtained,c_2_sub_10_total_marks,
                    c_2_sub_11_name,c_2_sub_11_marks_obtained,c_2_sub_11_total_marks,
                    c_2_sub_12_name,c_2_sub_12_marks_obtained,c_2_sub_12_total_marks,
                    c_2_sub_13_name,c_2_sub_13_marks_obtained,c_2_sub_13_total_marks,
                    c_2_sub_14_name,c_2_sub_14_marks_obtained,c_2_sub_14_total_marks,
                    c_2_sub_15_name,c_2_sub_15_marks_obtained,c_2_sub_15_total_marks
                ))


            # Redirect to the next form
            return redirect(url_for('form_c_3'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_2_info from the database
            cursor.execute("SELECT * FROM class_2 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            c_2_info = cursor.fetchone()

            # Pass the c_2_info to the template
            return render_template('Student/student_info_forms/form_c_2.html', class_2=c_2_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_c_3', methods=['GET', 'POST'])
def form_c_3():
    if request.method == 'POST':
        return form_c_3_post()
    else:
        # Fetch c_3_info from the database
        cursor.execute("SELECT * FROM class_3 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        c_3_info = cursor.fetchone()

        # If c_3_info is None, create a default c_3_info object
        if c_3_info is None:
            c_3_info = {
                ' c_3_year': '',
                ' c_3_board': '',
                ' c_3_roll_no': '',
                ' c_3_result': '',
                ' c_3_sub_1_name': '',
                ' c_3_sub_1_marks_obtained': '',
                ' c_3_sub_1_total_marks': '',
                ' c_3_sub_2_name': '',
                ' c_3_sub_2_marks_obtained': '',
                ' c_3_sub_2_total_marks': '',
                ' c_3_sub_3_name': '',
                ' c_3_sub_3_marks_obtained': '',
                ' c_3_sub_3_total_marks': '',
                ' c_3_sub_4_name': '',
                ' c_3_sub_4_marks_obtained': '',
                ' c_3_sub_4_total_marks': '',
                ' c_3_sub_5_name': '',
                ' c_3_sub_5_marks_obtained': '',
                ' c_3_sub_5_total_marks': '',
                ' c_3_sub_6_name': '',
                ' c_3_sub_6_marks_obtained': '',
                ' c_3_sub_6_total_marks': '',
                ' c_3_sub_7_name': '',
                ' c_3_sub_7_marks_obtained': '',
                ' c_3_sub_7_total_marks': '',
                ' c_3_sub_8_name': '',
                ' c_3_sub_8_marks_obtained': '',
                ' c_3_sub_8_total_marks': '',
                ' c_3_sub_9_name': '',
                ' c_3_sub_9_marks_obtained': '',
                ' c_3_sub_9_total_marks': '',
                ' c_3_sub_10_name': '',
                ' c_3_sub_10_marks_obtained': '',
                ' c_3_sub_10_total_marks': '',
                ' c_3_sub_11_name': '',
                ' c_3_sub_11_marks_obtained': '',
                ' c_3_sub_11_total_marks': '',
                ' c_3_sub_12_name': '',
                ' c_3_sub_12_marks_obtained': '',
                ' c_3_sub_12_total_marks': '',
                ' c_3_sub_13_name': '',
                ' c_3_sub_13_marks_obtained': '',
                ' c_3_sub_13_total_marks': '',
                ' c_3_sub_14_name': '',
                ' c_3_sub_14_marks_obtained': '',
                ' c_3_sub_14_total_marks': '',
                ' c_3_sub_15_name': '',
                ' c_3_sub_15_marks_obtained': '',
                ' c_3_sub_15_total_marks': ''
            }

        # Pass the c_3_info to the template
        return render_template('Student/student_info_forms/form_c_3.html', class_3=c_3_info)

def form_c_3_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            c_3_year = request.form['c_3_year']
            c_3_board = request.form['c_3_board']
            c_3_roll_no = request.form['c_3_roll_no']
            c_3_result = request.form['c_3_result']
            c_3_sub_1_name = request.form['c_3_sub_1_name']
            c_3_sub_1_marks_obtained = request.form['c_3_sub_1_marks_obtained']
            c_3_sub_1_total_marks = request.form['c_3_sub_1_total_marks']
            c_3_sub_2_name = request.form['c_3_sub_2_name']
            c_3_sub_2_marks_obtained = request.form['c_3_sub_2_marks_obtained']
            c_3_sub_2_total_marks = request.form['c_3_sub_2_total_marks']
            c_3_sub_3_name = request.form['c_3_sub_3_name']
            c_3_sub_3_marks_obtained = request.form['c_3_sub_3_marks_obtained']
            c_3_sub_3_total_marks = request.form['c_3_sub_3_total_marks']
            c_3_sub_4_name = request.form['c_3_sub_4_name']
            c_3_sub_4_marks_obtained = request.form['c_3_sub_4_marks_obtained']
            c_3_sub_4_total_marks = request.form['c_3_sub_4_total_marks']
            c_3_sub_5_name = request.form['c_3_sub_5_name']
            c_3_sub_5_marks_obtained = request.form['c_3_sub_5_marks_obtained']
            c_3_sub_5_total_marks = request.form['c_3_sub_5_total_marks']
            c_3_sub_6_name = request.form['c_3_sub_6_name']
            c_3_sub_6_marks_obtained = request.form['c_3_sub_6_marks_obtained']
            c_3_sub_6_total_marks = request.form['c_3_sub_6_total_marks']
            c_3_sub_7_name = request.form['c_3_sub_7_name']
            c_3_sub_7_marks_obtained = request.form['c_3_sub_7_marks_obtained']
            c_3_sub_7_total_marks = request.form['c_3_sub_7_total_marks']
            c_3_sub_8_name = request.form['c_3_sub_8_name']
            c_3_sub_8_marks_obtained = request.form['c_3_sub_8_marks_obtained']
            c_3_sub_8_total_marks = request.form['c_3_sub_8_total_marks']
            c_3_sub_9_name = request.form['c_3_sub_9_name']
            c_3_sub_9_marks_obtained = request.form['c_3_sub_9_marks_obtained']
            c_3_sub_9_total_marks = request.form['c_3_sub_9_total_marks']
            c_3_sub_10_name = request.form['c_3_sub_10_name']
            c_3_sub_10_marks_obtained = request.form['c_3_sub_10_marks_obtained']
            c_3_sub_10_total_marks = request.form['c_3_sub_10_total_marks']
            c_3_sub_11_name = request.form['c_3_sub_11_name']
            c_3_sub_11_marks_obtained = request.form['c_3_sub_11_marks_obtained']
            c_3_sub_11_total_marks = request.form['c_3_sub_11_total_marks']
            c_3_sub_12_name = request.form['c_3_sub_12_name']
            c_3_sub_12_marks_obtained = request.form['c_3_sub_12_marks_obtained']
            c_3_sub_12_total_marks = request.form['c_3_sub_12_total_marks']
            c_3_sub_13_name = request.form['c_3_sub_13_name']
            c_3_sub_13_marks_obtained = request.form['c_3_sub_13_marks_obtained']
            c_3_sub_13_total_marks = request.form['c_3_sub_13_total_marks']
            c_3_sub_14_name = request.form['c_3_sub_14_name']
            c_3_sub_14_marks_obtained = request.form['c_3_sub_14_marks_obtained']
            c_3_sub_14_total_marks = request.form['c_3_sub_14_total_marks']
            c_3_sub_15_name = request.form['c_3_sub_15_name']
            c_3_sub_15_marks_obtained = request.form['c_3_sub_15_marks_obtained']
            c_3_sub_15_total_marks = request.form['c_3_sub_15_total_marks']

            # Update c_3_info in the database
            cursor.execute("""
                UPDATE class_3
                SET c_3_year = ?, c_3_board = ?, c_3_roll_no = ?, c_3_result = ?, c_3_sub_1_name = ?, c_3_sub_1_marks_obtained = ?, c_3_sub_1_total_marks = ?, c_3_sub_2_name = ?, c_3_sub_2_marks_obtained = ?, c_3_sub_2_total_marks = ?, c_3_sub_3_name = ?, c_3_sub_3_marks_obtained = ?, c_3_sub_3_total_marks = ?, c_3_sub_4_name = ?, c_3_sub_4_marks_obtained = ?, c_3_sub_4_total_marks = ?, c_3_sub_5_name = ?, c_3_sub_5_marks_obtained = ?, c_3_sub_5_total_marks = ?, c_3_sub_6_name = ?, c_3_sub_6_marks_obtained = ?, c_3_sub_6_total_marks = ?, c_3_sub_7_name = ?, c_3_sub_7_marks_obtained = ?, c_3_sub_7_total_marks = ?, c_3_sub_8_name = ?, c_3_sub_8_marks_obtained = ?, c_3_sub_8_total_marks = ?, c_3_sub_9_name = ?, c_3_sub_9_marks_obtained = ?, c_3_sub_9_total_marks = ?, c_3_sub_10_name = ?, c_3_sub_10_marks_obtained = ?, c_3_sub_10_total_marks = ?, c_3_sub_11_name = ?, c_3_sub_11_marks_obtained = ?, c_3_sub_11_total_marks = ?, c_3_sub_12_name = ?, c_3_sub_12_marks_obtained = ?, c_3_sub_12_total_marks = ?, c_3_sub_13_name = ?, c_3_sub_13_marks_obtained = ?, c_3_sub_13_total_marks = ?, c_3_sub_14_name = ?, c_3_sub_14_marks_obtained = ?, c_3_sub_14_total_marks = ?, c_3_sub_15_name = ?, c_3_sub_15_marks_obtained = ?, c_3_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_3_year, c_3_board, c_3_roll_no, c_3_result, c_3_sub_1_name, c_3_sub_1_marks_obtained, c_3_sub_1_total_marks, c_3_sub_2_name, c_3_sub_2_marks_obtained, c_3_sub_2_total_marks, c_3_sub_3_name, c_3_sub_3_marks_obtained, c_3_sub_3_total_marks, c_3_sub_4_name, c_3_sub_4_marks_obtained, c_3_sub_4_total_marks, c_3_sub_5_name, c_3_sub_5_marks_obtained, c_3_sub_5_total_marks, c_3_sub_6_name, c_3_sub_6_marks_obtained, c_3_sub_6_total_marks, c_3_sub_7_name, c_3_sub_7_marks_obtained, c_3_sub_7_total_marks, c_3_sub_8_name, c_3_sub_8_marks_obtained, c_3_sub_8_total_marks, c_3_sub_9_name, c_3_sub_9_marks_obtained, c_3_sub_9_total_marks, c_3_sub_10_name, c_3_sub_10_marks_obtained, c_3_sub_10_total_marks, c_3_sub_11_name, c_3_sub_11_marks_obtained, c_3_sub_11_total_marks, c_3_sub_12_name, c_3_sub_12_marks_obtained, c_3_sub_12_total_marks, c_3_sub_13_name, c_3_sub_13_marks_obtained, c_3_sub_13_total_marks, c_3_sub_14_name, c_3_sub_14_marks_obtained, c_3_sub_14_total_marks, c_3_sub_15_name, c_3_sub_15_marks_obtained, c_3_sub_15_total_marks, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_c_4'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_3_info from the database
            cursor.execute("SELECT * FROM class_3 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            c_3_info = cursor.fetchone()

            # Pass the c_3_info to the template
            return render_template('Student/student_info_forms/form_c_3.html', class_3=c_3_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_c_4', methods=['GET', 'POST'])
def form_c_4():
    if request.method == 'POST':
        return form_c_4_post()
    else:
        # Fetch c_4_info from the database
        cursor.execute("SELECT * FROM class_4 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        c_4_info = cursor.fetchone()

        # If c_4_info is None, create a default c_4_info object
        if c_4_info is None:
            c_4_info = {
                ' c_4_year': '',
                ' c_4_board': '',
                ' c_4_roll_no': '',
                ' c_4_result': '',
                ' c_4_sub_1_name': '',
                ' c_4_sub_1_marks_obtained': '',
                ' c_4_sub_1_total_marks': '',
                ' c_4_sub_2_name': '',
                ' c_4_sub_2_marks_obtained': '',
                ' c_4_sub_2_total_marks': '',
                ' c_4_sub_3_name': '',
                ' c_4_sub_3_marks_obtained': '',
                ' c_4_sub_3_total_marks': '',
                ' c_4_sub_4_name': '',
                ' c_4_sub_4_marks_obtained': '',
                ' c_4_sub_4_total_marks': '',
                ' c_4_sub_5_name': '',
                ' c_4_sub_5_marks_obtained': '',
                ' c_4_sub_5_total_marks': '',
                ' c_4_sub_6_name': '',
                ' c_4_sub_6_marks_obtained': '',
                ' c_4_sub_6_total_marks': '',
                ' c_4_sub_7_name': '',
                ' c_4_sub_7_marks_obtained': '',
                ' c_4_sub_7_total_marks': '',
                ' c_4_sub_8_name': '',
                ' c_4_sub_8_marks_obtained': '',
                ' c_4_sub_8_total_marks': '',
                ' c_4_sub_9_name': '',
                ' c_4_sub_9_marks_obtained': '',
                ' c_4_sub_9_total_marks': '',
                ' c_4_sub_10_name': '',
                ' c_4_sub_10_marks_obtained': '',
                ' c_4_sub_10_total_marks': '',
                ' c_4_sub_11_name': '',
                ' c_4_sub_11_marks_obtained': '',
                ' c_4_sub_11_total_marks': '',
                ' c_4_sub_12_name': '',
                ' c_4_sub_12_marks_obtained': '',
                ' c_4_sub_12_total_marks': '',
                ' c_4_sub_13_name': '',
                ' c_4_sub_13_marks_obtained': '',
                ' c_4_sub_13_total_marks': '',
                ' c_4_sub_14_name': '',
                ' c_4_sub_14_marks_obtained': '',
                ' c_4_sub_14_total_marks': '',
                ' c_4_sub_15_name': '',
                ' c_4_sub_15_marks_obtained': '',
                ' c_4_sub_15_total_marks': ''
            }

        # Pass the c_4_info to the template
        return render_template('Student/student_info_forms/form_c_4.html', class_4=c_4_info)

def form_c_4_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            c_4_year = request.form['c_4_year']
            c_4_board = request.form['c_4_board']
            c_4_roll_no = request.form['c_4_roll_no']
            c_4_result = request.form['c_4_result']
            c_4_sub_1_name = request.form['c_4_sub_1_name']
            c_4_sub_1_marks_obtained = request.form['c_4_sub_1_marks_obtained']
            c_4_sub_1_total_marks = request.form['c_4_sub_1_total_marks']
            c_4_sub_2_name = request.form['c_4_sub_2_name']
            c_4_sub_2_marks_obtained = request.form['c_4_sub_2_marks_obtained']
            c_4_sub_2_total_marks = request.form['c_4_sub_2_total_marks']
            c_4_sub_3_name = request.form['c_4_sub_3_name']
            c_4_sub_3_marks_obtained = request.form['c_4_sub_3_marks_obtained']
            c_4_sub_3_total_marks = request.form['c_4_sub_3_total_marks']
            c_4_sub_4_name = request.form['c_4_sub_4_name']
            c_4_sub_4_marks_obtained = request.form['c_4_sub_4_marks_obtained']
            c_4_sub_4_total_marks = request.form['c_4_sub_4_total_marks']
            c_4_sub_5_name = request.form['c_4_sub_5_name']
            c_4_sub_5_marks_obtained = request.form['c_4_sub_5_marks_obtained']
            c_4_sub_5_total_marks = request.form['c_4_sub_5_total_marks']
            c_4_sub_6_name = request.form['c_4_sub_6_name']
            c_4_sub_6_marks_obtained = request.form['c_4_sub_6_marks_obtained']
            c_4_sub_6_total_marks = request.form['c_4_sub_6_total_marks']
            c_4_sub_7_name = request.form['c_4_sub_7_name']
            c_4_sub_7_marks_obtained = request.form['c_4_sub_7_marks_obtained']
            c_4_sub_7_total_marks = request.form['c_4_sub_7_total_marks']
            c_4_sub_8_name = request.form['c_4_sub_8_name']
            c_4_sub_8_marks_obtained = request.form['c_4_sub_8_marks_obtained']
            c_4_sub_8_total_marks = request.form['c_4_sub_8_total_marks']
            c_4_sub_9_name = request.form['c_4_sub_9_name']
            c_4_sub_9_marks_obtained = request.form['c_4_sub_9_marks_obtained']
            c_4_sub_9_total_marks = request.form['c_4_sub_9_total_marks']
            c_4_sub_10_name = request.form['c_4_sub_10_name']
            c_4_sub_10_marks_obtained = request.form['c_4_sub_10_marks_obtained']
            c_4_sub_10_total_marks = request.form['c_4_sub_10_total_marks']
            c_4_sub_11_name = request.form['c_4_sub_11_name']
            c_4_sub_11_marks_obtained = request.form['c_4_sub_11_marks_obtained']
            c_4_sub_11_total_marks = request.form['c_4_sub_11_total_marks']
            c_4_sub_12_name = request.form['c_4_sub_12_name']
            c_4_sub_12_marks_obtained = request.form['c_4_sub_12_marks_obtained']
            c_4_sub_12_total_marks = request.form['c_4_sub_12_total_marks']
            c_4_sub_13_name = request.form['c_4_sub_13_name']
            c_4_sub_13_marks_obtained = request.form['c_4_sub_13_marks_obtained']
            c_4_sub_13_total_marks = request.form['c_4_sub_13_total_marks']
            c_4_sub_14_name = request.form['c_4_sub_14_name']
            c_4_sub_14_marks_obtained = request.form['c_4_sub_14_marks_obtained']
            c_4_sub_14_total_marks = request.form['c_4_sub_14_total_marks']
            c_4_sub_15_name = request.form['c_4_sub_15_name']
            c_4_sub_15_marks_obtained = request.form['c_4_sub_15_marks_obtained']
            c_4_sub_15_total_marks = request.form['c_4_sub_15_total_marks']

            # Update c_4_info in the database
            cursor.execute("""
                UPDATE class_4
                SET c_4_year = ?, c_4_board = ?, c_4_roll_no = ?, c_4_result = ?, c_4_sub_1_name = ?, c_4_sub_1_marks_obtained = ?, c_4_sub_1_total_marks = ?, c_4_sub_2_name = ?, c_4_sub_2_marks_obtained = ?, c_4_sub_2_total_marks = ?, c_4_sub_3_name = ?, c_4_sub_3_marks_obtained = ?, c_4_sub_3_total_marks = ?, c_4_sub_4_name = ?, c_4_sub_4_marks_obtained = ?, c_4_sub_4_total_marks = ?, c_4_sub_5_name = ?, c_4_sub_5_marks_obtained = ?, c_4_sub_5_total_marks = ?, c_4_sub_6_name = ?, c_4_sub_6_marks_obtained = ?, c_4_sub_6_total_marks = ?, c_4_sub_7_name = ?, c_4_sub_7_marks_obtained = ?, c_4_sub_7_total_marks = ?, c_4_sub_8_name = ?, c_4_sub_8_marks_obtained = ?, c_4_sub_8_total_marks = ?, c_4_sub_9_name = ?, c_4_sub_9_marks_obtained = ?, c_4_sub_9_total_marks = ?, c_4_sub_10_name = ?, c_4_sub_10_marks_obtained = ?, c_4_sub_10_total_marks = ?, c_4_sub_11_name = ?, c_4_sub_11_marks_obtained = ?, c_4_sub_11_total_marks = ?, c_4_sub_12_name = ?, c_4_sub_12_marks_obtained = ?, c_4_sub_12_total_marks = ?, c_4_sub_13_name = ?, c_4_sub_13_marks_obtained = ?, c_4_sub_13_total_marks = ?, c_4_sub_14_name = ?, c_4_sub_14_marks_obtained = ?, c_4_sub_14_total_marks = ?, c_4_sub_15_name = ?, c_4_sub_15_marks_obtained = ?, c_4_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_4_year, c_4_board, c_4_roll_no, c_4_result,c_4_sub_1_name, c_4_sub_1_marks_obtained, c_4_sub_1_total_marks, c_4_sub_2_name, c_4_sub_2_marks_obtained, c_4_sub_2_total_marks, c_4_sub_3_name, c_4_sub_3_marks_obtained, c_4_sub_3_total_marks, c_4_sub_4_name, c_4_sub_4_marks_obtained, c_4_sub_4_total_marks, c_4_sub_5_name, c_4_sub_5_marks_obtained, c_4_sub_5_total_marks, c_4_sub_6_name, c_4_sub_6_marks_obtained, c_4_sub_6_total_marks, c_4_sub_7_name, c_4_sub_7_marks_obtained, c_4_sub_7_total_marks, c_4_sub_8_name, c_4_sub_8_marks_obtained, c_4_sub_8_total_marks, c_4_sub_9_name, c_4_sub_9_marks_obtained, c_4_sub_9_total_marks, c_4_sub_10_name, c_4_sub_10_marks_obtained, c_4_sub_10_total_marks, c_4_sub_11_name, c_4_sub_11_marks_obtained, c_4_sub_11_total_marks, c_4_sub_12_name, c_4_sub_12_marks_obtained, c_4_sub_12_total_marks, c_4_sub_13_name, c_4_sub_13_marks_obtained, c_4_sub_13_total_marks, c_4_sub_14_name, c_4_sub_14_marks_obtained, c_4_sub_14_total_marks, c_4_sub_15_name, c_4_sub_15_marks_obtained, c_4_sub_15_total_marks, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_c_5'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_4_info from the database
            cursor.execute("SELECT * FROM class_4 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            c_4_info = cursor.fetchone()

            # Pass the c_4_info to the template
            return render_template('Student/student_info_forms/form_c_4.html', class_4=c_4_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_c_5', methods=['GET', 'POST'])
def form_c_5():
    if request.method == 'POST':
        return form_c_5_post()
    else:
        # Fetch c_5_info from the database
        cursor.execute("SELECT * FROM class_5 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        c_5_info = cursor.fetchone()

        # If c_5_info is None, create a default c_5_info object
        if c_5_info is None:
            c_5_info = {
                ' c_5_year': '',
                ' c_5_board': '',
                ' c_5_roll_no': '',
                ' c_5_result': '',
                ' c_5_sub_1_name': '',
                ' c_5_sub_1_marks_obtained': '',
                ' c_5_sub_1_total_marks': '',
                ' c_5_sub_2_name': '',
                ' c_5_sub_2_marks_obtained': '',
                ' c_5_sub_2_total_marks': '',
                ' c_5_sub_3_name': '',
                ' c_5_sub_3_marks_obtained': '',
                ' c_5_sub_3_total_marks': '',
                ' c_5_sub_4_name': '',
                ' c_5_sub_4_marks_obtained': '',
                ' c_5_sub_4_total_marks': '',
                ' c_5_sub_5_name': '',
                ' c_5_sub_5_marks_obtained': '',
                ' c_5_sub_5_total_marks': '',
                ' c_5_sub_6_name': '',
                ' c_5_sub_6_marks_obtained': '',
                ' c_5_sub_6_total_marks': '',
                ' c_5_sub_7_name': '',
                ' c_5_sub_7_marks_obtained': '',
                ' c_5_sub_7_total_marks': '',
                ' c_5_sub_8_name': '',
                ' c_5_sub_8_marks_obtained': '',
                ' c_5_sub_8_total_marks': '',
                ' c_5_sub_9_name': '',
                ' c_5_sub_9_marks_obtained': '',
                ' c_5_sub_9_total_marks': '',
                ' c_5_sub_10_name': '',
                ' c_5_sub_10_marks_obtained': '',
                ' c_5_sub_10_total_marks': '',
                ' c_5_sub_11_name': '',
                ' c_5_sub_11_marks_obtained': '',
                ' c_5_sub_11_total_marks': '',
                ' c_5_sub_12_name': '',
                ' c_5_sub_12_marks_obtained': '',
                ' c_5_sub_12_total_marks': '',
                ' c_5_sub_13_name': '',
                ' c_5_sub_13_marks_obtained': '',
                ' c_5_sub_13_total_marks': '',
                ' c_5_sub_14_name': '',
                ' c_5_sub_14_marks_obtained': '',
                ' c_5_sub_14_total_marks': '',
                ' c_5_sub_15_name': '',
                ' c_5_sub_15_marks_obtained': '',
                ' c_5_sub_15_total_marks': ''
            }

        # Pass the c_5_info to the template
        return render_template('Student/student_info_forms/form_c_5.html', class_5=c_5_info)

def form_c_5_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            c_5_year = request.form['c_5_year']
            c_5_board = request.form['c_5_board']
            c_5_roll_no = request.form['c_5_roll_no']
            c_5_result = request.form['c_5_result']
            c_5_sub_1_name = request.form['c_5_sub_1_name']
            c_5_sub_1_marks_obtained = request.form['c_5_sub_1_marks_obtained']
            c_5_sub_1_total_marks = request.form['c_5_sub_1_total_marks']
            c_5_sub_2_name = request.form['c_5_sub_2_name']
            c_5_sub_2_marks_obtained = request.form['c_5_sub_2_marks_obtained']
            c_5_sub_2_total_marks = request.form['c_5_sub_2_total_marks']
            c_5_sub_3_name = request.form['c_5_sub_3_name']
            c_5_sub_3_marks_obtained = request.form['c_5_sub_3_marks_obtained']
            c_5_sub_3_total_marks = request.form['c_5_sub_3_total_marks']
            c_5_sub_4_name = request.form['c_5_sub_4_name']
            c_5_sub_4_marks_obtained = request.form['c_5_sub_4_marks_obtained']
            c_5_sub_4_total_marks = request.form['c_5_sub_4_total_marks']
            c_5_sub_5_name = request.form['c_5_sub_5_name']
            c_5_sub_5_marks_obtained = request.form['c_5_sub_5_marks_obtained']
            c_5_sub_5_total_marks = request.form['c_5_sub_5_total_marks']
            c_5_sub_6_name = request.form['c_5_sub_6_name']
            c_5_sub_6_marks_obtained = request.form['c_5_sub_6_marks_obtained']
            c_5_sub_6_total_marks = request.form['c_5_sub_6_total_marks']
            c_5_sub_7_name = request.form['c_5_sub_7_name']
            c_5_sub_7_marks_obtained = request.form['c_5_sub_7_marks_obtained']
            c_5_sub_7_total_marks = request.form['c_5_sub_7_total_marks']
            c_5_sub_8_name = request.form['c_5_sub_8_name']
            c_5_sub_8_marks_obtained = request.form['c_5_sub_8_marks_obtained']
            c_5_sub_8_total_marks = request.form['c_5_sub_8_total_marks']
            c_5_sub_9_name = request.form['c_5_sub_9_name']
            c_5_sub_9_marks_obtained = request.form['c_5_sub_9_marks_obtained']
            c_5_sub_9_total_marks = request.form['c_5_sub_9_total_marks']
            c_5_sub_10_name = request.form['c_5_sub_10_name']
            c_5_sub_10_marks_obtained = request.form['c_5_sub_10_marks_obtained']
            c_5_sub_10_total_marks = request.form['c_5_sub_10_total_marks']
            c_5_sub_11_name = request.form['c_5_sub_11_name']
            c_5_sub_11_marks_obtained = request.form['c_5_sub_11_marks_obtained']
            c_5_sub_11_total_marks = request.form['c_5_sub_11_total_marks']
            c_5_sub_12_name = request.form['c_5_sub_12_name']
            c_5_sub_12_marks_obtained = request.form['c_5_sub_12_marks_obtained']
            c_5_sub_12_total_marks = request.form['c_5_sub_12_total_marks']
            c_5_sub_13_name = request.form['c_5_sub_13_name']
            c_5_sub_13_marks_obtained = request.form['c_5_sub_13_marks_obtained']
            c_5_sub_13_total_marks = request.form['c_5_sub_13_total_marks']
            c_5_sub_14_name = request.form['c_5_sub_14_name']
            c_5_sub_14_marks_obtained = request.form['c_5_sub_14_marks_obtained']
            c_5_sub_14_total_marks = request.form['c_5_sub_14_total_marks']
            c_5_sub_15_name = request.form['c_5_sub_15_name']
            c_5_sub_15_marks_obtained = request.form['c_5_sub_15_marks_obtained']
            c_5_sub_15_total_marks = request.form['c_5_sub_15_total_marks']

            # Update c_5_info in the database
            cursor.execute("""
                UPDATE class_5
                SET c_5_year = ?, c_5_board = ?, c_5_roll_no = ?, c_5_result = ?, c_5_sub_1_name = ?, c_5_sub_1_marks_obtained = ?, c_5_sub_1_total_marks = ?, c_5_sub_2_name = ?, c_5_sub_2_marks_obtained = ?, c_5_sub_2_total_marks = ?, c_5_sub_3_name = ?, c_5_sub_3_marks_obtained = ?, c_5_sub_3_total_marks = ?, c_5_sub_4_name = ?, c_5_sub_4_marks_obtained = ?, c_5_sub_4_total_marks = ?, c_5_sub_5_name = ?, c_5_sub_5_marks_obtained = ?, c_5_sub_5_total_marks = ?, c_5_sub_6_name = ?, c_5_sub_6_marks_obtained = ?, c_5_sub_6_total_marks = ?, c_5_sub_7_name = ?, c_5_sub_7_marks_obtained = ?, c_5_sub_7_total_marks = ?, c_5_sub_8_name = ?, c_5_sub_8_marks_obtained = ?, c_5_sub_8_total_marks = ?, c_5_sub_9_name = ?, c_5_sub_9_marks_obtained = ?, c_5_sub_9_total_marks = ?, c_5_sub_10_name = ?, c_5_sub_10_marks_obtained = ?, c_5_sub_10_total_marks = ?, c_5_sub_11_name = ?, c_5_sub_11_marks_obtained = ?, c_5_sub_11_total_marks = ?, c_5_sub_12_name = ?, c_5_sub_12_marks_obtained = ?, c_5_sub_12_total_marks = ?, c_5_sub_13_name = ?, c_5_sub_13_marks_obtained = ?, c_5_sub_13_total_marks = ?, c_5_sub_14_name = ?, c_5_sub_14_marks_obtained = ?, c_5_sub_14_total_marks = ?, c_5_sub_15_name = ?, c_5_sub_15_marks_obtained = ?, c_5_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_5_year, c_5_board, c_5_roll_no, c_5_result, c_5_sub_1_name, c_5_sub_1_marks_obtained, c_5_sub_1_total_marks, c_5_sub_2_name, c_5_sub_2_marks_obtained, c_5_sub_2_total_marks, c_5_sub_3_name, c_5_sub_3_marks_obtained, c_5_sub_3_total_marks, c_5_sub_4_name, c_5_sub_4_marks_obtained, c_5_sub_4_total_marks, c_5_sub_5_name, c_5_sub_5_marks_obtained, c_5_sub_5_total_marks, c_5_sub_6_name, c_5_sub_6_marks_obtained, c_5_sub_6_total_marks, c_5_sub_7_name, c_5_sub_7_marks_obtained, c_5_sub_7_total_marks, c_5_sub_8_name, c_5_sub_8_marks_obtained, c_5_sub_8_total_marks, c_5_sub_9_name, c_5_sub_9_marks_obtained, c_5_sub_9_total_marks, c_5_sub_10_name, c_5_sub_10_marks_obtained, c_5_sub_10_total_marks, c_5_sub_11_name, c_5_sub_11_marks_obtained, c_5_sub_11_total_marks, c_5_sub_12_name, c_5_sub_12_marks_obtained, c_5_sub_12_total_marks, c_5_sub_13_name, c_5_sub_13_marks_obtained, c_5_sub_13_total_marks, c_5_sub_14_name, c_5_sub_14_marks_obtained, c_5_sub_14_total_marks, c_5_sub_15_name, c_5_sub_15_marks_obtained, c_5_sub_15_total_marks, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_c_6'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_5_info from the database
            cursor.execute("SELECT * FROM class_5 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            c_5_info = cursor.fetchone()

            # Pass the c_5_info to the template
            return render_template('Student/student_info_forms/form_c_5.html', class_5=c_5_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_c_6', methods=['GET', 'POST'])
def form_c_6():
    if request.method == 'POST':
        return form_c_6_post()
    else:
        # Fetch c_6_info from the database
        cursor.execute("SELECT * FROM class_6 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        c_6_info = cursor.fetchone()

        # If c_6_info is None, create a default c_6_info object
        if c_6_info is None:
            c_6_info = {
                ' c_6_year': '',
                ' c_6_board': '',
                ' c_6_roll_no': '',
                ' c_6_result': '',
                ' c_6_sub_1_name': '',
                ' c_6_sub_1_marks_obtained': '',
                ' c_6_sub_1_total_marks': '',
                ' c_6_sub_2_name': '',
                ' c_6_sub_2_marks_obtained': '',
                ' c_6_sub_2_total_marks': '',
                ' c_6_sub_3_name': '',
                ' c_6_sub_3_marks_obtained': '',
                ' c_6_sub_3_total_marks': '',
                ' c_6_sub_4_name': '',
                ' c_6_sub_4_marks_obtained': '',
                ' c_6_sub_4_total_marks': '',
                ' c_6_sub_5_name': '',
                ' c_6_sub_5_marks_obtained': '',
                ' c_6_sub_5_total_marks': '',
                ' c_6_sub_6_name': '',
                ' c_6_sub_6_marks_obtained': '',
                ' c_6_sub_6_total_marks': '',
                ' c_6_sub_7_name': '',
                ' c_6_sub_7_marks_obtained': '',
                ' c_6_sub_7_total_marks': '',
                ' c_6_sub_8_name': '',
                ' c_6_sub_8_marks_obtained': '',
                ' c_6_sub_8_total_marks': '',
                ' c_6_sub_9_name': '',
                ' c_6_sub_9_marks_obtained': '',
                ' c_6_sub_9_total_marks': '',
                ' c_6_sub_10_name': '',
                ' c_6_sub_10_marks_obtained': '',
                ' c_6_sub_10_total_marks': '',
                ' c_6_sub_11_name': '',
                ' c_6_sub_11_marks_obtained': '',
                ' c_6_sub_11_total_marks': '',
                ' c_6_sub_12_name': '',
                ' c_6_sub_12_marks_obtained': '',
                ' c_6_sub_12_total_marks': '',
                ' c_6_sub_13_name': '',
                ' c_6_sub_13_marks_obtained': '',
                ' c_6_sub_13_total_marks': '',
                ' c_6_sub_14_name': '',
                ' c_6_sub_14_marks_obtained': '',
                ' c_6_sub_14_total_marks': '',
                ' c_6_sub_15_name': '',
                ' c_6_sub_15_marks_obtained': '',
                ' c_6_sub_15_total_marks': ''
            }

        # Pass the c_6_info to the template
        return render_template('Student/student_info_forms/form_c_6.html', class_6=c_6_info)

def form_c_6_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            c_6_year = request.form['c_6_year']
            c_6_board = request.form['c_6_board']
            c_6_roll_no = request.form['c_6_roll_no']
            c_6_result = request.form['c_6_result']
            c_6_sub_1_name = request.form['c_6_sub_1_name']
            c_6_sub_1_marks_obtained = request.form['c_6_sub_1_marks_obtained']
            c_6_sub_1_total_marks = request.form['c_6_sub_1_total_marks']
            c_6_sub_2_name = request.form['c_6_sub_2_name']
            c_6_sub_2_marks_obtained = request.form['c_6_sub_2_marks_obtained']
            c_6_sub_2_total_marks = request.form['c_6_sub_2_total_marks']
            c_6_sub_3_name = request.form['c_6_sub_3_name']
            c_6_sub_3_marks_obtained = request.form['c_6_sub_3_marks_obtained']
            c_6_sub_3_total_marks = request.form['c_6_sub_3_total_marks']
            c_6_sub_4_name = request.form['c_6_sub_4_name']
            c_6_sub_4_marks_obtained = request.form['c_6_sub_4_marks_obtained']
            c_6_sub_4_total_marks = request.form['c_6_sub_4_total_marks']
            c_6_sub_5_name = request.form['c_6_sub_5_name']
            c_6_sub_5_marks_obtained = request.form['c_6_sub_5_marks_obtained']
            c_6_sub_5_total_marks = request.form['c_6_sub_5_total_marks']
            c_6_sub_6_name = request.form['c_6_sub_6_name']
            c_6_sub_6_marks_obtained = request.form['c_6_sub_6_marks_obtained']
            c_6_sub_6_total_marks = request.form['c_6_sub_6_total_marks']
            c_6_sub_7_name = request.form['c_6_sub_7_name']
            c_6_sub_7_marks_obtained = request.form['c_6_sub_7_marks_obtained']
            c_6_sub_7_total_marks = request.form['c_6_sub_7_total_marks']
            c_6_sub_8_name = request.form['c_6_sub_8_name']
            c_6_sub_8_marks_obtained = request.form['c_6_sub_8_marks_obtained']
            c_6_sub_8_total_marks = request.form['c_6_sub_8_total_marks']
            c_6_sub_9_name = request.form['c_6_sub_9_name']
            c_6_sub_9_marks_obtained = request.form['c_6_sub_9_marks_obtained']
            c_6_sub_9_total_marks = request.form['c_6_sub_9_total_marks']
            c_6_sub_10_name = request.form['c_6_sub_10_name']
            c_6_sub_10_marks_obtained = request.form['c_6_sub_10_marks_obtained']
            c_6_sub_10_total_marks = request.form['c_6_sub_10_total_marks']
            c_6_sub_11_name = request.form['c_6_sub_11_name']
            c_6_sub_11_marks_obtained = request.form['c_6_sub_11_marks_obtained']
            c_6_sub_11_total_marks = request.form['c_6_sub_11_total_marks']
            c_6_sub_12_name = request.form['c_6_sub_12_name']
            c_6_sub_12_marks_obtained = request.form['c_6_sub_12_marks_obtained']
            c_6_sub_12_total_marks = request.form['c_6_sub_12_total_marks']
            c_6_sub_13_name = request.form['c_6_sub_13_name']
            c_6_sub_13_marks_obtained = request.form['c_6_sub_13_marks_obtained']
            c_6_sub_13_total_marks = request.form['c_6_sub_13_total_marks']
            c_6_sub_14_name = request.form['c_6_sub_14_name']
            c_6_sub_14_marks_obtained = request.form['c_6_sub_14_marks_obtained']
            c_6_sub_14_total_marks = request.form['c_6_sub_14_total_marks']
            c_6_sub_15_name = request.form['c_6_sub_15_name']
            c_6_sub_15_marks_obtained = request.form['c_6_sub_15_marks_obtained']
            c_6_sub_15_total_marks = request.form['c_6_sub_15_total_marks']

            # Update c_6_info in the database
            cursor.execute("""
                UPDATE class_6
                SET c_6_year = ?, c_6_board = ?, c_6_roll_no = ?, c_6_result = ?, c_6_sub_1_name = ?, c_6_sub_1_marks_obtained = ?, c_6_sub_1_total_marks = ?, c_6_sub_2_name = ?, c_6_sub_2_marks_obtained = ?, c_6_sub_2_total_marks = ?, c_6_sub_3_name = ?, c_6_sub_3_marks_obtained = ?, c_6_sub_3_total_marks = ?, c_6_sub_4_name = ?, c_6_sub_4_marks_obtained = ?, c_6_sub_4_total_marks = ?, c_6_sub_5_name = ?, c_6_sub_5_marks_obtained = ?, c_6_sub_5_total_marks = ?, c_6_sub_6_name = ?, c_6_sub_6_marks_obtained = ?, c_6_sub_6_total_marks = ?, c_6_sub_7_name = ?, c_6_sub_7_marks_obtained = ?, c_6_sub_7_total_marks = ?, c_6_sub_8_name = ?, c_6_sub_8_marks_obtained = ?, c_6_sub_8_total_marks = ?, c_6_sub_9_name = ?, c_6_sub_9_marks_obtained = ?, c_6_sub_9_total_marks = ?, c_6_sub_10_name = ?, c_6_sub_10_marks_obtained = ?, c_6_sub_10_total_marks = ?, c_6_sub_11_name = ?, c_6_sub_11_marks_obtained = ?, c_6_sub_11_total_marks = ?, c_6_sub_12_name = ?, c_6_sub_12_marks_obtained = ?, c_6_sub_12_total_marks = ?, c_6_sub_13_name = ?, c_6_sub_13_marks_obtained = ?, c_6_sub_13_total_marks = ?, c_6_sub_14_name = ?, c_6_sub_14_marks_obtained = ?, c_6_sub_14_total_marks = ?, c_6_sub_15_name = ?, c_6_sub_15_marks_obtained = ?, c_6_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_6_year, c_6_board, c_6_roll_no, c_6_result, c_6_sub_1_name, c_6_sub_1_marks_obtained, c_6_sub_1_total_marks, c_6_sub_2_name, c_6_sub_2_marks_obtained, c_6_sub_2_total_marks, c_6_sub_3_name, c_6_sub_3_marks_obtained, c_6_sub_3_total_marks, c_6_sub_4_name, c_6_sub_4_marks_obtained, c_6_sub_4_total_marks, c_6_sub_5_name, c_6_sub_5_marks_obtained, c_6_sub_5_total_marks, c_6_sub_6_name, c_6_sub_6_marks_obtained, c_6_sub_6_total_marks, c_6_sub_7_name, c_6_sub_7_marks_obtained, c_6_sub_7_total_marks, c_6_sub_8_name, c_6_sub_8_marks_obtained, c_6_sub_8_total_marks, c_6_sub_9_name, c_6_sub_9_marks_obtained, c_6_sub_9_total_marks, c_6_sub_10_name, c_6_sub_10_marks_obtained, c_6_sub_10_total_marks, c_6_sub_11_name, c_6_sub_11_marks_obtained, c_6_sub_11_total_marks, c_6_sub_12_name, c_6_sub_12_marks_obtained, c_6_sub_12_total_marks, c_6_sub_13_name, c_6_sub_13_marks_obtained, c_6_sub_13_total_marks, c_6_sub_14_name, c_6_sub_14_marks_obtained, c_6_sub_14_total_marks, c_6_sub_15_name, c_6_sub_15_marks_obtained, c_6_sub_15_total_marks, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_c_7'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_6_info from the database
            cursor.execute("SELECT * FROM class_6 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            c_6_info = cursor.fetchone()

            # Pass the c_6_info to the template
            return render_template('Student/student_info_forms/form_c_6.html', class_6=c_6_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_c_7', methods=['GET', 'POST'])
def form_c_7():
    if request.method == 'POST':
        return form_c_7_post()
    else:
        # Fetch c_7_info from the database
        cursor.execute("SELECT * FROM class_7 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        c_7_info = cursor.fetchone()

        # If c_7_info is None, create a default c_7_info object
        if c_7_info is None:
            c_7_info = {
                ' c_7_year': '',
                ' c_7_board': '',
                ' c_7_roll_no': '',
                ' c_7_result': '',
                ' c_7_sub_1_name': '',
                ' c_7_sub_1_marks_obtained': '',
                ' c_7_sub_1_total_marks': '',
                ' c_7_sub_2_name': '',
                ' c_7_sub_2_marks_obtained': '',
                ' c_7_sub_2_total_marks': '',
                ' c_7_sub_3_name': '',
                ' c_7_sub_3_marks_obtained': '',
                ' c_7_sub_3_total_marks': '',
                ' c_7_sub_4_name': '',
                ' c_7_sub_4_marks_obtained': '',
                ' c_7_sub_4_total_marks': '',
                ' c_7_sub_5_name': '',
                ' c_7_sub_5_marks_obtained': '',
                ' c_7_sub_5_total_marks': '',
                ' c_7_sub_6_name': '',
                ' c_7_sub_6_marks_obtained': '',
                ' c_7_sub_6_total_marks': '',
                ' c_7_sub_7_name': '',
                ' c_7_sub_7_marks_obtained': '',
                ' c_7_sub_7_total_marks': '',
                ' c_7_sub_8_name': '',
                ' c_7_sub_8_marks_obtained': '',
                ' c_7_sub_8_total_marks': '',
                ' c_7_sub_9_name': '',
                ' c_7_sub_9_marks_obtained': '',
                ' c_7_sub_9_total_marks': '',
                ' c_7_sub_10_name': '',
                ' c_7_sub_10_marks_obtained': '',
                ' c_7_sub_10_total_marks': '',
                ' c_7_sub_11_name': '',
                ' c_7_sub_11_marks_obtained': '',
                ' c_7_sub_11_total_marks': '',
                ' c_7_sub_12_name': '',
                ' c_7_sub_12_marks_obtained': '',
                ' c_7_sub_12_total_marks': '',
                ' c_7_sub_13_name': '',
                ' c_7_sub_13_marks_obtained': '',
                ' c_7_sub_13_total_marks': '',
                ' c_7_sub_14_name': '',
                ' c_7_sub_14_marks_obtained': '',
                ' c_7_sub_14_total_marks': '',
                ' c_7_sub_15_name': '',
                ' c_7_sub_15_marks_obtained': '',
                ' c_7_sub_15_total_marks': ''
            }

        # Pass the c_7_info to the template
        return render_template('Student/student_info_forms/form_c_7.html', class_7=c_7_info)

def form_c_7_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            c_7_year = request.form['c_7_year']
            c_7_board = request.form['c_7_board']
            c_7_roll_no = request.form['c_7_roll_no']
            c_7_result = request.form['c_7_result']
            c_7_sub_1_name = request.form['c_7_sub_1_name']
            c_7_sub_1_marks_obtained = request.form['c_7_sub_1_marks_obtained']
            c_7_sub_1_total_marks = request.form['c_7_sub_1_total_marks']
            c_7_sub_2_name = request.form['c_7_sub_2_name']
            c_7_sub_2_marks_obtained = request.form['c_7_sub_2_marks_obtained']
            c_7_sub_2_total_marks = request.form['c_7_sub_2_total_marks']
            c_7_sub_3_name = request.form['c_7_sub_3_name']
            c_7_sub_3_marks_obtained = request.form['c_7_sub_3_marks_obtained']
            c_7_sub_3_total_marks = request.form['c_7_sub_3_total_marks']
            c_7_sub_4_name = request.form['c_7_sub_4_name']
            c_7_sub_4_marks_obtained = request.form['c_7_sub_4_marks_obtained']
            c_7_sub_4_total_marks = request.form['c_7_sub_4_total_marks']
            c_7_sub_5_name = request.form['c_7_sub_5_name']
            c_7_sub_5_marks_obtained = request.form['c_7_sub_5_marks_obtained']
            c_7_sub_5_total_marks = request.form['c_7_sub_5_total_marks']
            c_7_sub_6_name = request.form['c_7_sub_6_name']
            c_7_sub_6_marks_obtained = request.form['c_7_sub_6_marks_obtained']
            c_7_sub_6_total_marks = request.form['c_7_sub_6_total_marks']
            c_7_sub_7_name = request.form['c_7_sub_7_name']
            c_7_sub_7_marks_obtained = request.form['c_7_sub_7_marks_obtained']
            c_7_sub_7_total_marks = request.form['c_7_sub_7_total_marks']
            c_7_sub_8_name = request.form['c_7_sub_8_name']
            c_7_sub_8_marks_obtained = request.form['c_7_sub_8_marks_obtained']
            c_7_sub_8_total_marks = request.form['c_7_sub_8_total_marks']
            c_7_sub_9_name = request.form['c_7_sub_9_name']
            c_7_sub_9_marks_obtained = request.form['c_7_sub_9_marks_obtained']
            c_7_sub_9_total_marks = request.form['c_7_sub_9_total_marks']
            c_7_sub_10_name = request.form['c_7_sub_10_name']
            c_7_sub_10_marks_obtained = request.form['c_7_sub_10_marks_obtained']
            c_7_sub_10_total_marks = request.form['c_7_sub_10_total_marks']
            c_7_sub_11_name = request.form['c_7_sub_11_name']
            c_7_sub_11_marks_obtained = request.form['c_7_sub_11_marks_obtained']
            c_7_sub_11_total_marks = request.form['c_7_sub_11_total_marks']
            c_7_sub_12_name = request.form['c_7_sub_12_name']
            c_7_sub_12_marks_obtained = request.form['c_7_sub_12_marks_obtained']
            c_7_sub_12_total_marks = request.form['c_7_sub_12_total_marks']
            c_7_sub_13_name = request.form['c_7_sub_13_name']
            c_7_sub_13_marks_obtained = request.form['c_7_sub_13_marks_obtained']
            c_7_sub_13_total_marks = request.form['c_7_sub_13_total_marks']
            c_7_sub_14_name = request.form['c_7_sub_14_name']
            c_7_sub_14_marks_obtained = request.form['c_7_sub_14_marks_obtained']
            c_7_sub_14_total_marks = request.form['c_7_sub_14_total_marks']
            c_7_sub_15_name = request.form['c_7_sub_15_name']
            c_7_sub_15_marks_obtained = request.form['c_7_sub_15_marks_obtained']
            c_7_sub_15_total_marks = request.form['c_7_sub_15_total_marks']

            # Update c_7_info in the database
            cursor.execute("""
                UPDATE class_7
                SET c_7_year = ?, c_7_board = ?, c_7_roll_no = ?, c_7_result = ?, c_7_sub_1_name = ?, c_7_sub_1_marks_obtained = ?, c_7_sub_1_total_marks = ?, c_7_sub_2_name = ?, c_7_sub_2_marks_obtained = ?, c_7_sub_2_total_marks = ?, c_7_sub_3_name = ?, c_7_sub_3_marks_obtained = ?, c_7_sub_3_total_marks = ?, c_7_sub_4_name = ?, c_7_sub_4_marks_obtained = ?, c_7_sub_4_total_marks = ?, c_7_sub_5_name = ?, c_7_sub_5_marks_obtained = ?, c_7_sub_5_total_marks = ?, c_7_sub_6_name = ?, c_7_sub_6_marks_obtained = ?, c_7_sub_6_total_marks = ?, c_7_sub_7_name = ?, c_7_sub_7_marks_obtained = ?, c_7_sub_7_total_marks = ?, c_7_sub_8_name = ?, c_7_sub_8_marks_obtained = ?, c_7_sub_8_total_marks = ?, c_7_sub_9_name = ?, c_7_sub_9_marks_obtained = ?, c_7_sub_9_total_marks = ?, c_7_sub_10_name = ?, c_7_sub_10_marks_obtained = ?, c_7_sub_10_total_marks = ?, c_7_sub_11_name = ?, c_7_sub_11_marks_obtained = ?, c_7_sub_11_total_marks = ?, c_7_sub_12_name = ?, c_7_sub_12_marks_obtained = ?, c_7_sub_12_total_marks = ?, c_7_sub_13_name = ?, c_7_sub_13_marks_obtained = ?, c_7_sub_13_total_marks = ?, c_7_sub_14_name = ?, c_7_sub_14_marks_obtained = ?, c_7_sub_14_total_marks = ?, c_7_sub_15_name = ?, c_7_sub_15_marks_obtained = ?, c_7_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_7_year, c_7_board, c_7_roll_no, c_7_result, c_7_sub_1_name, c_7_sub_1_marks_obtained, c_7_sub_1_total_marks, c_7_sub_2_name, c_7_sub_2_marks_obtained, c_7_sub_2_total_marks, c_7_sub_3_name, c_7_sub_3_marks_obtained, c_7_sub_3_total_marks, c_7_sub_4_name, c_7_sub_4_marks_obtained, c_7_sub_4_total_marks, c_7_sub_5_name, c_7_sub_5_marks_obtained, c_7_sub_5_total_marks, c_7_sub_6_name, c_7_sub_6_marks_obtained, c_7_sub_6_total_marks, c_7_sub_7_name, c_7_sub_7_marks_obtained, c_7_sub_7_total_marks, c_7_sub_8_name, c_7_sub_8_marks_obtained, c_7_sub_8_total_marks, c_7_sub_9_name, c_7_sub_9_marks_obtained, c_7_sub_9_total_marks, c_7_sub_10_name, c_7_sub_10_marks_obtained, c_7_sub_10_total_marks, c_7_sub_11_name, c_7_sub_11_marks_obtained, c_7_sub_11_total_marks, c_7_sub_12_name, c_7_sub_12_marks_obtained, c_7_sub_12_total_marks, c_7_sub_13_name, c_7_sub_13_marks_obtained, c_7_sub_13_total_marks, c_7_sub_14_name, c_7_sub_14_marks_obtained, c_7_sub_14_total_marks, c_7_sub_15_name, c_7_sub_15_marks_obtained, c_7_sub_15_total_marks, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_c_8'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_7_info from the database
            cursor.execute("SELECT * FROM class_7 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            c_7_info = cursor.fetchone()

            # Pass the c_7_info to the template
            return render_template('Student/student_info_forms/form_c_7.html', class_7=c_7_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_c_8', methods=['GET', 'POST'])
def form_c_8():
    if request.method == 'POST':
        return form_c_8_post()
    else:
        # Fetch c_8_info from the database
        cursor.execute("SELECT * FROM class_8 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        c_8_info = cursor.fetchone()

        # If c_8_info is None, create a default c_8_info object
        if c_8_info is None:
            c_8_info = {
                ' c_8_year': '',
                ' c_8_board': '',
                ' c_8_roll_no': '',
                ' c_8_result': '',
                ' c_8_sub_1_name': '',
                ' c_8_sub_1_marks_obtained': '',
                ' c_8_sub_1_total_marks': '',
                ' c_8_sub_2_name': '',
                ' c_8_sub_2_marks_obtained': '',
                ' c_8_sub_2_total_marks': '',
                ' c_8_sub_3_name': '',
                ' c_8_sub_3_marks_obtained': '',
                ' c_8_sub_3_total_marks': '',
                ' c_8_sub_4_name': '',
                ' c_8_sub_4_marks_obtained': '',
                ' c_8_sub_4_total_marks': '',
                ' c_8_sub_5_name': '',
                ' c_8_sub_5_marks_obtained': '',
                ' c_8_sub_5_total_marks': '',
                ' c_8_sub_6_name': '',
                ' c_8_sub_6_marks_obtained': '',
                ' c_8_sub_6_total_marks': '',
                ' c_8_sub_7_name': '',
                ' c_8_sub_7_marks_obtained': '',
                ' c_8_sub_7_total_marks': '',
                ' c_8_sub_8_name': '',
                ' c_8_sub_8_marks_obtained': '',
                ' c_8_sub_8_total_marks': '',
                ' c_8_sub_9_name': '',
                ' c_8_sub_9_marks_obtained': '',
                ' c_8_sub_9_total_marks': '',
                ' c_8_sub_10_name': '',
                ' c_8_sub_10_marks_obtained': '',
                ' c_8_sub_10_total_marks': '',
                ' c_8_sub_11_name': '',
                ' c_8_sub_11_marks_obtained': '',
                ' c_8_sub_11_total_marks': '',
                ' c_8_sub_12_name': '',
                ' c_8_sub_12_marks_obtained': '',
                ' c_8_sub_12_total_marks': '',
                ' c_8_sub_13_name': '',
                ' c_8_sub_13_marks_obtained': '',
                ' c_8_sub_13_total_marks': '',
                ' c_8_sub_14_name': '',
                ' c_8_sub_14_marks_obtained': '',
                ' c_8_sub_14_total_marks': '',
                ' c_8_sub_15_name': '',
                ' c_8_sub_15_marks_obtained': '',
                ' c_8_sub_15_total_marks': ''
            }

        # Pass the c_8_info to the template
        return render_template('Student/student_info_forms/form_c_8.html', class_8=c_8_info)

def form_c_8_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            c_8_year = request.form['c_8_year']
            c_8_board = request.form['c_8_board']
            c_8_roll_no = request.form['c_8_roll_no']
            c_8_result = request.form['c_8_result']
            c_8_sub_1_name = request.form['c_8_sub_1_name']
            c_8_sub_1_marks_obtained = request.form['c_8_sub_1_marks_obtained']
            c_8_sub_1_total_marks = request.form['c_8_sub_1_total_marks']
            c_8_sub_2_name = request.form['c_8_sub_2_name']
            c_8_sub_2_marks_obtained = request.form['c_8_sub_2_marks_obtained']
            c_8_sub_2_total_marks = request.form['c_8_sub_2_total_marks']
            c_8_sub_3_name = request.form['c_8_sub_3_name']
            c_8_sub_3_marks_obtained = request.form['c_8_sub_3_marks_obtained']
            c_8_sub_3_total_marks = request.form['c_8_sub_3_total_marks']
            c_8_sub_4_name = request.form['c_8_sub_4_name']
            c_8_sub_4_marks_obtained = request.form['c_8_sub_4_marks_obtained']
            c_8_sub_4_total_marks = request.form['c_8_sub_4_total_marks']
            c_8_sub_5_name = request.form['c_8_sub_5_name']
            c_8_sub_5_marks_obtained = request.form['c_8_sub_5_marks_obtained']
            c_8_sub_5_total_marks = request.form['c_8_sub_5_total_marks']
            c_8_sub_6_name = request.form['c_8_sub_6_name']
            c_8_sub_6_marks_obtained = request.form['c_8_sub_6_marks_obtained']
            c_8_sub_6_total_marks = request.form['c_8_sub_6_total_marks']
            c_8_sub_7_name = request.form['c_8_sub_7_name']
            c_8_sub_7_marks_obtained = request.form['c_8_sub_7_marks_obtained']
            c_8_sub_7_total_marks = request.form['c_8_sub_7_total_marks']
            c_8_sub_8_name = request.form['c_8_sub_8_name']
            c_8_sub_8_marks_obtained = request.form['c_8_sub_8_marks_obtained']
            c_8_sub_8_total_marks = request.form['c_8_sub_8_total_marks']
            c_8_sub_9_name = request.form['c_8_sub_9_name']
            c_8_sub_9_marks_obtained = request.form['c_8_sub_9_marks_obtained']
            c_8_sub_9_total_marks = request.form['c_8_sub_9_total_marks']
            c_8_sub_10_name = request.form['c_8_sub_10_name']
            c_8_sub_10_marks_obtained = request.form['c_8_sub_10_marks_obtained']
            c_8_sub_10_total_marks = request.form['c_8_sub_10_total_marks']
            c_8_sub_11_name = request.form['c_8_sub_11_name']
            c_8_sub_11_marks_obtained = request.form['c_8_sub_11_marks_obtained']
            c_8_sub_11_total_marks = request.form['c_8_sub_11_total_marks']
            c_8_sub_12_name = request.form['c_8_sub_12_name']
            c_8_sub_12_marks_obtained = request.form['c_8_sub_12_marks_obtained']
            c_8_sub_12_total_marks = request.form['c_8_sub_12_total_marks']
            c_8_sub_13_name = request.form['c_8_sub_13_name']
            c_8_sub_13_marks_obtained = request.form['c_8_sub_13_marks_obtained']
            c_8_sub_13_total_marks = request.form['c_8_sub_13_total_marks']
            c_8_sub_14_name = request.form['c_8_sub_14_name']
            c_8_sub_14_marks_obtained = request.form['c_8_sub_14_marks_obtained']
            c_8_sub_14_total_marks = request.form['c_8_sub_14_total_marks']
            c_8_sub_15_name = request.form['c_8_sub_15_name']
            c_8_sub_15_marks_obtained = request.form['c_8_sub_15_marks_obtained']
            c_8_sub_15_total_marks = request.form['c_8_sub_15_total_marks']

            # Update c_8_info in the database
            cursor.execute("""
                UPDATE class_8
                SET c_8_year = ?, c_8_board = ?, c_8_roll_no = ?, c_8_result = ?, c_8_sub_1_name = ?, c_8_sub_1_marks_obtained = ?, c_8_sub_1_total_marks = ?, c_8_sub_2_name = ?, c_8_sub_2_marks_obtained = ?, c_8_sub_2_total_marks = ?, c_8_sub_3_name = ?, c_8_sub_3_marks_obtained = ?, c_8_sub_3_total_marks = ?, c_8_sub_4_name = ?, c_8_sub_4_marks_obtained = ?, c_8_sub_4_total_marks = ?, c_8_sub_5_name = ?, c_8_sub_5_marks_obtained = ?, c_8_sub_5_total_marks = ?, c_8_sub_6_name = ?, c_8_sub_6_marks_obtained = ?, c_8_sub_6_total_marks = ?, c_8_sub_7_name = ?, c_8_sub_7_marks_obtained = ?, c_8_sub_7_total_marks = ?, c_8_sub_8_name = ?, c_8_sub_8_marks_obtained = ?, c_8_sub_8_total_marks = ?, c_8_sub_9_name = ?, c_8_sub_9_marks_obtained = ?, c_8_sub_9_total_marks = ?, c_8_sub_10_name = ?, c_8_sub_10_marks_obtained = ?, c_8_sub_10_total_marks = ?, c_8_sub_11_name = ?, c_8_sub_11_marks_obtained = ?, c_8_sub_11_total_marks = ?, c_8_sub_12_name = ?, c_8_sub_12_marks_obtained = ?, c_8_sub_12_total_marks = ?, c_8_sub_13_name = ?, c_8_sub_13_marks_obtained = ?, c_8_sub_13_total_marks = ?, c_8_sub_14_name = ?, c_8_sub_14_marks_obtained = ?, c_8_sub_14_total_marks = ?, c_8_sub_15_name = ?, c_8_sub_15_marks_obtained = ?, c_8_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_8_year, c_8_board, c_8_roll_no, c_8_result, c_8_sub_1_name, c_8_sub_1_marks_obtained, c_8_sub_1_total_marks, c_8_sub_2_name, c_8_sub_2_marks_obtained, c_8_sub_2_total_marks, c_8_sub_3_name, c_8_sub_3_marks_obtained, c_8_sub_3_total_marks, c_8_sub_4_name, c_8_sub_4_marks_obtained, c_8_sub_4_total_marks, c_8_sub_5_name, c_8_sub_5_marks_obtained, c_8_sub_5_total_marks, c_8_sub_6_name, c_8_sub_6_marks_obtained, c_8_sub_6_total_marks, c_8_sub_7_name, c_8_sub_7_marks_obtained, c_8_sub_7_total_marks, c_8_sub_8_name, c_8_sub_8_marks_obtained, c_8_sub_8_total_marks, c_8_sub_9_name, c_8_sub_9_marks_obtained, c_8_sub_9_total_marks, c_8_sub_10_name, c_8_sub_10_marks_obtained, c_8_sub_10_total_marks, c_8_sub_11_name, c_8_sub_11_marks_obtained, c_8_sub_11_total_marks, c_8_sub_12_name, c_8_sub_12_marks_obtained, c_8_sub_12_total_marks, c_8_sub_13_name, c_8_sub_13_marks_obtained, c_8_sub_13_total_marks, c_8_sub_14_name, c_8_sub_14_marks_obtained, c_8_sub_14_total_marks, c_8_sub_15_name, c_8_sub_15_marks_obtained, c_8_sub_15_total_marks, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_c_9'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_8_info from the database
            cursor.execute("SELECT * FROM class_8 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            c_8_info = cursor.fetchone()

            # Pass the c_8_info to the template
            return render_template('Student/student_info_forms/form_c_8.html', class_8=c_8_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_c_9', methods=['GET', 'POST'])
def form_c_9():
    if request.method == 'POST':
        return form_c_9_post()
    else:
        # Fetch c_9_info from the database
        cursor.execute("SELECT * FROM class_9 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        c_9_info = cursor.fetchone()

        # If c_9_info is None, create a default c_9_info object
        if c_9_info is None:
            c_9_info = {
                ' c_9_year': '',
                ' c_9_board': '',
                ' c_9_roll_no': '',
                ' c_9_result': '',
                ' c_9_sub_1_name': '',
                ' c_9_sub_1_marks_obtained': '',
                ' c_9_sub_1_total_marks': '',
                ' c_9_sub_2_name': '',
                ' c_9_sub_2_marks_obtained': '',
                ' c_9_sub_2_total_marks': '',
                ' c_9_sub_3_name': '',
                ' c_9_sub_3_marks_obtained': '',
                ' c_9_sub_3_total_marks': '',
                ' c_9_sub_4_name': '',
                ' c_9_sub_4_marks_obtained': '',
                ' c_9_sub_4_total_marks': '',
                ' c_9_sub_5_name': '',
                ' c_9_sub_5_marks_obtained': '',
                ' c_9_sub_5_total_marks': '',
                ' c_9_sub_6_name': '',
                ' c_9_sub_6_marks_obtained': '',
                ' c_9_sub_6_total_marks': '',
                ' c_9_sub_7_name': '',
                ' c_9_sub_7_marks_obtained': '',
                ' c_9_sub_7_total_marks': '',
                ' c_9_sub_8_name': '',
                ' c_9_sub_8_marks_obtained': '',
                ' c_9_sub_8_total_marks': '',
                ' c_9_sub_9_name': '',
                ' c_9_sub_9_marks_obtained': '',
                ' c_9_sub_9_total_marks': '',
                ' c_9_sub_10_name': '',
                ' c_9_sub_10_marks_obtained': '',
                ' c_9_sub_10_total_marks': '',
                ' c_9_sub_11_name': '',
                ' c_9_sub_11_marks_obtained': '',
                ' c_9_sub_11_total_marks': '',
                ' c_9_sub_12_name': '',
                ' c_9_sub_12_marks_obtained': '',
                ' c_9_sub_12_total_marks': '',
                ' c_9_sub_13_name': '',
                ' c_9_sub_13_marks_obtained': '',
                ' c_9_sub_13_total_marks': '',
                ' c_9_sub_14_name': '',
                ' c_9_sub_14_marks_obtained': '',
                ' c_9_sub_14_total_marks': '',
                ' c_9_sub_15_name': '',
                ' c_9_sub_15_marks_obtained': '',
                ' c_9_sub_15_total_marks': ''
            }

        # Pass the c_9_info to the template
        return render_template('Student/student_info_forms/form_c_9.html', class_9=c_9_info)

def form_c_9_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            c_9_year = request.form['c_9_year']
            c_9_board = request.form['c_9_board']
            c_9_roll_no = request.form['c_9_roll_no']
            c_9_result = request.form['c_9_result']
            c_9_sub_1_name = request.form['c_9_sub_1_name']
            c_9_sub_1_marks_obtained = request.form['c_9_sub_1_marks_obtained']
            c_9_sub_1_total_marks = request.form['c_9_sub_1_total_marks']
            c_9_sub_2_name = request.form['c_9_sub_2_name']
            c_9_sub_2_marks_obtained = request.form['c_9_sub_2_marks_obtained']
            c_9_sub_2_total_marks = request.form['c_9_sub_2_total_marks']
            c_9_sub_3_name = request.form['c_9_sub_3_name']
            c_9_sub_3_marks_obtained = request.form['c_9_sub_3_marks_obtained']
            c_9_sub_3_total_marks = request.form['c_9_sub_3_total_marks']
            c_9_sub_4_name = request.form['c_9_sub_4_name']
            c_9_sub_4_marks_obtained = request.form['c_9_sub_4_marks_obtained']
            c_9_sub_4_total_marks = request.form['c_9_sub_4_total_marks']
            c_9_sub_5_name = request.form['c_9_sub_5_name']
            c_9_sub_5_marks_obtained = request.form['c_9_sub_5_marks_obtained']
            c_9_sub_5_total_marks = request.form['c_9_sub_5_total_marks']
            c_9_sub_6_name = request.form['c_9_sub_6_name']
            c_9_sub_6_marks_obtained = request.form['c_9_sub_6_marks_obtained']
            c_9_sub_6_total_marks = request.form['c_9_sub_6_total_marks']
            c_9_sub_7_name = request.form['c_9_sub_7_name']
            c_9_sub_7_marks_obtained = request.form['c_9_sub_7_marks_obtained']
            c_9_sub_7_total_marks = request.form['c_9_sub_7_total_marks']
            c_9_sub_8_name = request.form['c_9_sub_8_name']
            c_9_sub_8_marks_obtained = request.form['c_9_sub_8_marks_obtained']
            c_9_sub_8_total_marks = request.form['c_9_sub_8_total_marks']
            c_9_sub_9_name = request.form['c_9_sub_9_name']
            c_9_sub_9_marks_obtained = request.form['c_9_sub_9_marks_obtained']
            c_9_sub_9_total_marks = request.form['c_9_sub_9_total_marks']
            c_9_sub_10_name = request.form['c_9_sub_10_name']
            c_9_sub_10_marks_obtained = request.form['c_9_sub_10_marks_obtained']
            c_9_sub_10_total_marks = request.form['c_9_sub_10_total_marks']
            c_9_sub_11_name = request.form['c_9_sub_11_name']
            c_9_sub_11_marks_obtained = request.form['c_9_sub_11_marks_obtained']
            c_9_sub_11_total_marks = request.form['c_9_sub_11_total_marks']
            c_9_sub_12_name = request.form['c_9_sub_12_name']
            c_9_sub_12_marks_obtained = request.form['c_9_sub_12_marks_obtained']
            c_9_sub_12_total_marks = request.form['c_9_sub_12_total_marks']
            c_9_sub_13_name = request.form['c_9_sub_13_name']
            c_9_sub_13_marks_obtained = request.form['c_9_sub_13_marks_obtained']
            c_9_sub_13_total_marks = request.form['c_9_sub_13_total_marks']
            c_9_sub_14_name = request.form['c_9_sub_14_name']
            c_9_sub_14_marks_obtained = request.form['c_9_sub_14_marks_obtained']
            c_9_sub_14_total_marks = request.form['c_9_sub_14_total_marks']
            c_9_sub_15_name = request.form['c_9_sub_15_name']
            c_9_sub_15_marks_obtained = request.form['c_9_sub_15_marks_obtained']
            c_9_sub_15_total_marks = request.form['c_9_sub_15_total_marks']

            # Update c_9_info in the database
            cursor.execute("""
                UPDATE class_9
                SET c_9_year = ?, c_9_board = ?, c_9_roll_no = ?, c_9_result = ?, c_9_sub_1_name = ?, c_9_sub_1_marks_obtained = ?, c_9_sub_1_total_marks = ?, c_9_sub_2_name = ?, c_9_sub_2_marks_obtained = ?, c_9_sub_2_total_marks = ?, c_9_sub_3_name = ?, c_9_sub_3_marks_obtained = ?, c_9_sub_3_total_marks = ?, c_9_sub_4_name = ?, c_9_sub_4_marks_obtained = ?, c_9_sub_4_total_marks = ?, c_9_sub_5_name = ?, c_9_sub_5_marks_obtained = ?, c_9_sub_5_total_marks = ?, c_9_sub_6_name = ?, c_9_sub_6_marks_obtained = ?, c_9_sub_6_total_marks = ?, c_9_sub_7_name = ?, c_9_sub_7_marks_obtained = ?, c_9_sub_7_total_marks = ?, c_9_sub_8_name = ?, c_9_sub_8_marks_obtained = ?, c_9_sub_8_total_marks = ?, c_9_sub_9_name = ?, c_9_sub_9_marks_obtained = ?, c_9_sub_9_total_marks = ?, c_9_sub_10_name = ?, c_9_sub_10_marks_obtained = ?, c_9_sub_10_total_marks = ?, c_9_sub_11_name = ?, c_9_sub_11_marks_obtained = ?, c_9_sub_11_total_marks = ?, c_9_sub_12_name = ?, c_9_sub_12_marks_obtained = ?, c_9_sub_12_total_marks = ?, c_9_sub_13_name = ?, c_9_sub_13_marks_obtained = ?, c_9_sub_13_total_marks = ?, c_9_sub_14_name = ?, c_9_sub_14_marks_obtained = ?, c_9_sub_14_total_marks = ?, c_9_sub_15_name = ?, c_9_sub_15_marks_obtained = ?, c_9_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_9_year, c_9_board, c_9_roll_no, c_9_result, c_9_sub_1_name, c_9_sub_1_marks_obtained, c_9_sub_1_total_marks, c_9_sub_2_name, c_9_sub_2_marks_obtained, c_9_sub_2_total_marks, c_9_sub_3_name, c_9_sub_3_marks_obtained, c_9_sub_3_total_marks, c_9_sub_4_name, c_9_sub_4_marks_obtained, c_9_sub_4_total_marks, c_9_sub_5_name, c_9_sub_5_marks_obtained, c_9_sub_5_total_marks, c_9_sub_6_name, c_9_sub_6_marks_obtained, c_9_sub_6_total_marks, c_9_sub_7_name, c_9_sub_7_marks_obtained, c_9_sub_7_total_marks, c_9_sub_8_name, c_9_sub_8_marks_obtained, c_9_sub_8_total_marks, c_9_sub_9_name, c_9_sub_9_marks_obtained, c_9_sub_9_total_marks, c_9_sub_10_name, c_9_sub_10_marks_obtained, c_9_sub_10_total_marks, c_9_sub_11_name, c_9_sub_11_marks_obtained, c_9_sub_11_total_marks, c_9_sub_12_name, c_9_sub_12_marks_obtained, c_9_sub_12_total_marks, c_9_sub_13_name, c_9_sub_13_marks_obtained, c_9_sub_13_total_marks, c_9_sub_14_name, c_9_sub_14_marks_obtained, c_9_sub_14_total_marks, c_9_sub_15_name, c_9_sub_15_marks_obtained, c_9_sub_15_total_marks, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_c_10'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_9_info from the database
            cursor.execute("SELECT * FROM class_9 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            c_9_info = cursor.fetchone()

            # Pass the c_9_info to the template
            return render_template('Student/student_info_forms/form_c_9.html', class_9=c_9_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_c_10', methods=['GET', 'POST'])
def form_c_10():
    if request.method == 'POST':
        return form_c_10_post()
    else:
        # Fetch c_10_info from the database
        cursor.execute("SELECT * FROM class_10 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        c_10_info = cursor.fetchone()

        # If c_10_info is None, create a default c_10_info object
        if c_10_info is None:
            c_10_info = {
                ' c_10_year': '',
                ' c_10_board': '',
                ' c_10_roll_no': '',
                ' c_10_result': '',
                ' c_10_sub_1_name': '',
                ' c_10_sub_1_marks_obtained': '',
                ' c_10_sub_1_total_marks': '',
                ' c_10_sub_2_name': '',
                ' c_10_sub_2_marks_obtained': '',
                ' c_10_sub_2_total_marks': '',
                ' c_10_sub_3_name': '',
                ' c_10_sub_3_marks_obtained': '',
                ' c_10_sub_3_total_marks': '',
                ' c_10_sub_4_name': '',
                ' c_10_sub_4_marks_obtained': '',
                ' c_10_sub_4_total_marks': '',
                ' c_10_sub_5_name': '',
                ' c_10_sub_5_marks_obtained': '',
                ' c_10_sub_5_total_marks': '',
                ' c_10_sub_6_name': '',
                ' c_10_sub_6_marks_obtained': '',
                ' c_10_sub_6_total_marks': '',
                ' c_10_sub_7_name': '',
                ' c_10_sub_7_marks_obtained': '',
                ' c_10_sub_7_total_marks': '',
                ' c_10_sub_8_name': '',
                ' c_10_sub_8_marks_obtained': '',
                ' c_10_sub_8_total_marks': '',
                ' c_10_sub_9_name': '',
                ' c_10_sub_9_marks_obtained': '',
                ' c_10_sub_9_total_marks': '',
                ' c_10_sub_10_name': '',
                ' c_10_sub_10_marks_obtained': '',
                ' c_10_sub_10_total_marks': '',
                ' c_10_sub_11_name': '',
                ' c_10_sub_11_marks_obtained': '',
                ' c_10_sub_11_total_marks': '',
                ' c_10_sub_12_name': '',
                ' c_10_sub_12_marks_obtained': '',
                ' c_10_sub_12_total_marks': '',
                ' c_10_sub_13_name': '',
                ' c_10_sub_13_marks_obtained': '',
                ' c_10_sub_13_total_marks': '',
                ' c_10_sub_14_name': '',
                ' c_10_sub_14_marks_obtained': '',
                ' c_10_sub_14_total_marks': '',
                ' c_10_sub_15_name': '',
                ' c_10_sub_15_marks_obtained': '',
                ' c_10_sub_15_total_marks': ''
            }

        # Pass the c_10_info to the template
        return render_template('Student/student_info_forms/form_c_10.html', class_10=c_10_info)

def form_c_10_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            c_10_year = request.form['c_10_year']
            c_10_board = request.form['c_10_board']
            c_10_roll_no = request.form['c_10_roll_no']
            c_10_result = request.form['c_10_result']
            c_10_sub_1_name = request.form['c_10_sub_1_name']
            c_10_sub_1_marks_obtained = request.form['c_10_sub_1_marks_obtained']
            c_10_sub_1_total_marks = request.form['c_10_sub_1_total_marks']
            c_10_sub_2_name = request.form['c_10_sub_2_name']
            c_10_sub_2_marks_obtained = request.form['c_10_sub_2_marks_obtained']
            c_10_sub_2_total_marks = request.form['c_10_sub_2_total_marks']
            c_10_sub_3_name = request.form['c_10_sub_3_name']
            c_10_sub_3_marks_obtained = request.form['c_10_sub_3_marks_obtained']
            c_10_sub_3_total_marks = request.form['c_10_sub_3_total_marks']
            c_10_sub_4_name = request.form['c_10_sub_4_name']
            c_10_sub_4_marks_obtained = request.form['c_10_sub_4_marks_obtained']
            c_10_sub_4_total_marks = request.form['c_10_sub_4_total_marks']
            c_10_sub_5_name = request.form['c_10_sub_5_name']
            c_10_sub_5_marks_obtained = request.form['c_10_sub_5_marks_obtained']
            c_10_sub_5_total_marks = request.form['c_10_sub_5_total_marks']
            c_10_sub_6_name = request.form['c_10_sub_6_name']
            c_10_sub_6_marks_obtained = request.form['c_10_sub_6_marks_obtained']
            c_10_sub_6_total_marks = request.form['c_10_sub_6_total_marks']
            c_10_sub_7_name = request.form['c_10_sub_7_name']
            c_10_sub_7_marks_obtained = request.form['c_10_sub_7_marks_obtained']
            c_10_sub_7_total_marks = request.form['c_10_sub_7_total_marks']
            c_10_sub_8_name = request.form['c_10_sub_8_name']
            c_10_sub_8_marks_obtained = request.form['c_10_sub_8_marks_obtained']
            c_10_sub_8_total_marks = request.form['c_10_sub_8_total_marks']
            c_10_sub_9_name = request.form['c_10_sub_9_name']
            c_10_sub_9_marks_obtained = request.form['c_10_sub_9_marks_obtained']
            c_10_sub_9_total_marks = request.form['c_10_sub_9_total_marks']
            c_10_sub_10_name = request.form['c_10_sub_10_name']
            c_10_sub_10_marks_obtained = request.form['c_10_sub_10_marks_obtained']
            c_10_sub_10_total_marks = request.form['c_10_sub_10_total_marks']
            c_10_sub_11_name = request.form['c_10_sub_11_name']
            c_10_sub_11_marks_obtained = request.form['c_10_sub_11_marks_obtained']
            c_10_sub_11_total_marks = request.form['c_10_sub_11_total_marks']
            c_10_sub_12_name = request.form['c_10_sub_12_name']
            c_10_sub_12_marks_obtained = request.form['c_10_sub_12_marks_obtained']
            c_10_sub_12_total_marks = request.form['c_10_sub_12_total_marks']
            c_10_sub_13_name = request.form['c_10_sub_13_name']
            c_10_sub_13_marks_obtained = request.form['c_10_sub_13_marks_obtained']
            c_10_sub_13_total_marks = request.form['c_10_sub_13_total_marks']
            c_10_sub_14_name = request.form['c_10_sub_14_name']
            c_10_sub_14_marks_obtained = request.form['c_10_sub_14_marks_obtained']
            c_10_sub_14_total_marks = request.form['c_10_sub_14_total_marks']
            c_10_sub_15_name = request.form['c_10_sub_15_name']
            c_10_sub_15_marks_obtained = request.form['c_10_sub_15_marks_obtained']
            c_10_sub_15_total_marks = request.form['c_10_sub_15_total_marks']

            # Update c_10_info in the database
            cursor.execute("""
                UPDATE class_10
                SET c_10_year = ?, c_10_board = ?, c_10_roll_no = ?, c_10_result = ?, c_10_sub_1_name = ?, c_10_sub_1_marks_obtained = ?, c_10_sub_1_total_marks = ?, c_10_sub_2_name = ?, c_10_sub_2_marks_obtained = ?, c_10_sub_2_total_marks = ?, c_10_sub_3_name = ?, c_10_sub_3_marks_obtained = ?, c_10_sub_3_total_marks = ?, c_10_sub_4_name = ?, c_10_sub_4_marks_obtained = ?, c_10_sub_4_total_marks = ?, c_10_sub_5_name = ?, c_10_sub_5_marks_obtained = ?, c_10_sub_5_total_marks = ?, c_10_sub_6_name = ?, c_10_sub_6_marks_obtained = ?, c_10_sub_6_total_marks = ?, c_10_sub_7_name = ?, c_10_sub_7_marks_obtained = ?, c_10_sub_7_total_marks = ?, c_10_sub_8_name = ?, c_10_sub_8_marks_obtained = ?, c_10_sub_8_total_marks = ?, c_10_sub_9_name = ?, c_10_sub_9_marks_obtained = ?, c_10_sub_9_total_marks = ?, c_10_sub_10_name = ?, c_10_sub_10_marks_obtained = ?, c_10_sub_10_total_marks = ?, c_10_sub_11_name = ?, c_10_sub_11_marks_obtained = ?, c_10_sub_11_total_marks = ?, c_10_sub_12_name = ?, c_10_sub_12_marks_obtained = ?, c_10_sub_12_total_marks = ?, c_10_sub_13_name = ?, c_10_sub_13_marks_obtained = ?, c_10_sub_13_total_marks = ?, c_10_sub_14_name = ?, c_10_sub_14_marks_obtained = ?, c_10_sub_14_total_marks = ?, c_10_sub_15_name = ?, c_10_sub_15_marks_obtained = ?, c_10_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_10_year, c_10_board, c_10_roll_no, c_10_result, c_10_sub_1_name, c_10_sub_1_marks_obtained, c_10_sub_1_total_marks, c_10_sub_2_name, c_10_sub_2_marks_obtained, c_10_sub_2_total_marks, c_10_sub_3_name, c_10_sub_3_marks_obtained, c_10_sub_3_total_marks, c_10_sub_4_name, c_10_sub_4_marks_obtained, c_10_sub_4_total_marks, c_10_sub_5_name, c_10_sub_5_marks_obtained, c_10_sub_5_total_marks, c_10_sub_6_name, c_10_sub_6_marks_obtained, c_10_sub_6_total_marks, c_10_sub_7_name, c_10_sub_7_marks_obtained, c_10_sub_7_total_marks, c_10_sub_8_name, c_10_sub_8_marks_obtained, c_10_sub_8_total_marks, c_10_sub_9_name, c_10_sub_9_marks_obtained, c_10_sub_9_total_marks, c_10_sub_10_name, c_10_sub_10_marks_obtained, c_10_sub_10_total_marks, c_10_sub_11_name, c_10_sub_11_marks_obtained, c_10_sub_11_total_marks, c_10_sub_12_name, c_10_sub_12_marks_obtained, c_10_sub_12_total_marks, c_10_sub_13_name, c_10_sub_13_marks_obtained, c_10_sub_13_total_marks, c_10_sub_14_name, c_10_sub_14_marks_obtained, c_10_sub_14_total_marks, c_10_sub_15_name, c_10_sub_15_marks_obtained, c_10_sub_15_total_marks, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_c_11'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_10_info from the database
            cursor.execute("SELECT * FROM class_10 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            c_10_info = cursor.fetchone()

            # Pass the c_10_info to the template
            return render_template('Student/student_info_forms/form_c_10.html', class_10=c_10_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_c_11', methods=['GET', 'POST'])
def form_c_11():
    if request.method == 'POST':
        return form_c_11_post()
    else:
        # Fetch c_11_info from the database
        cursor.execute("SELECT * FROM class_11 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        c_11_info = cursor.fetchone()

        # If c_11_info is None, create a default c_11_info object
        if c_11_info is None:
            c_11_info = {
                ' c_11_year': '',
                ' c_11_board': '',
                ' c_11_roll_no': '',
                ' c_11_result': '',
                ' c_11_sub_1_name': '',
                ' c_11_sub_1_marks_obtained': '',
                ' c_11_sub_1_total_marks': '',
                ' c_11_sub_2_name': '',
                ' c_11_sub_2_marks_obtained': '',
                ' c_11_sub_2_total_marks': '',
                ' c_11_sub_3_name': '',
                ' c_11_sub_3_marks_obtained': '',
                ' c_11_sub_3_total_marks': '',
                ' c_11_sub_4_name': '',
                ' c_11_sub_4_marks_obtained': '',
                ' c_11_sub_4_total_marks': '',
                ' c_11_sub_5_name': '',
                ' c_11_sub_5_marks_obtained': '',
                ' c_11_sub_5_total_marks': ''
            }

        # Pass the c_11_info to the template
        return render_template('Student/student_info_forms/form_c_11.html', class_11=c_11_info)

def form_c_11_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            c_11_year = request.form['c_11_year']
            c_11_board = request.form['c_11_board']
            c_11_roll_no = request.form['c_11_roll_no']
            c_11_result = request.form['c_11_result']
            c_11_sub_1_name = request.form['c_11_sub_1_name']
            c_11_sub_1_marks_obtained = request.form['c_11_sub_1_marks_obtained']
            c_11_sub_1_total_marks = request.form['c_11_sub_1_total_marks']
            c_11_sub_2_name = request.form['c_11_sub_2_name']
            c_11_sub_2_marks_obtained = request.form['c_11_sub_2_marks_obtained']
            c_11_sub_2_total_marks = request.form['c_11_sub_2_total_marks']
            c_11_sub_3_name = request.form['c_11_sub_3_name']
            c_11_sub_3_marks_obtained = request.form['c_11_sub_3_marks_obtained']
            c_11_sub_3_total_marks = request.form['c_11_sub_3_total_marks']
            c_11_sub_4_name = request.form['c_11_sub_4_name']
            c_11_sub_4_marks_obtained = request.form['c_11_sub_4_marks_obtained']
            c_11_sub_4_total_marks = request.form['c_11_sub_4_total_marks']
            c_11_sub_5_name = request.form['c_11_sub_5_name']
            c_11_sub_5_marks_obtained = request.form['c_11_sub_5_marks_obtained']
            c_11_sub_5_total_marks = request.form['c_11_sub_5_total_marks']


            # Update c_11_info in the database
            cursor.execute("""
                UPDATE class_11
                SET c_11_year = ?, c_11_board = ?, c_11_roll_no = ?, c_11_result = ?, c_11_sub_1_name = ?, c_11_sub_1_marks_obtained = ?, c_11_sub_1_total_marks = ?, c_11_sub_2_name = ?, c_11_sub_2_marks_obtained = ?, c_11_sub_2_total_marks = ?, c_11_sub_3_name = ?, c_11_sub_3_marks_obtained = ?, c_11_sub_3_total_marks = ?, c_11_sub_4_name = ?, c_11_sub_4_marks_obtained = ?, c_11_sub_4_total_marks = ?, c_11_sub_5_name = ?, c_11_sub_5_marks_obtained = ?, c_11_sub_5_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_11_year, c_11_board, c_11_roll_no, c_11_result, c_11_sub_1_name, c_11_sub_1_marks_obtained, c_11_sub_1_total_marks, c_11_sub_2_name, c_11_sub_2_marks_obtained, c_11_sub_2_total_marks, c_11_sub_3_name, c_11_sub_3_marks_obtained, c_11_sub_3_total_marks, c_11_sub_4_name, c_11_sub_4_marks_obtained, c_11_sub_4_total_marks, c_11_sub_5_name, c_11_sub_5_marks_obtained, c_11_sub_5_total_marks, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_c_12'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_11_info from the database
            cursor.execute("SELECT * FROM class_11 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            c_11_info = cursor.fetchone()

            # Pass the c_11_info to the template
            return render_template('Student/student_info_forms/form_c_11.html', class_11=c_11_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_c_12', methods=['GET', 'POST'])
def form_c_12():
    if request.method == 'POST':
        return form_c_12_post()
    else:
        # Fetch c_12_info from the database
        cursor.execute("SELECT * FROM class_12 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        c_12_info = cursor.fetchone()

        # If c_12_info is None, create a default c_12_info object
        if c_12_info is None:
            c_12_info = {
                ' c_12_year': '',
                ' c_12_board': '',
                ' c_12_roll_no': '',
                ' c_12_result': '',
                ' c_12_sub_1_name': '',
                ' c_12_sub_1_marks_obtained': '',
                ' c_12_sub_1_total_marks': '',
                ' c_12_sub_2_name': '',
                ' c_12_sub_2_marks_obtained': '',
                ' c_12_sub_2_total_marks': '',
                ' c_12_sub_3_name': '',
                ' c_12_sub_3_marks_obtained': '',
                ' c_12_sub_3_total_marks': '',
                ' c_12_sub_4_name': '',
                ' c_12_sub_4_marks_obtained': '',
                ' c_12_sub_4_total_marks': '',
                ' c_12_sub_5_name': '',
                ' c_12_sub_5_marks_obtained': '',
                ' c_12_sub_5_total_marks': ''
            }

        # Pass the c_12_info to the template
        return render_template('Student/student_info_forms/form_c_12.html', class_12=c_12_info)

def form_c_12_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            c_12_year = request.form['c_12_year']
            c_12_board = request.form['c_12_board']
            c_12_roll_no = request.form['c_12_roll_no']
            c_12_result = request.form['c_12_result']
            c_12_sub_1_name = request.form['c_12_sub_1_name']
            c_12_sub_1_marks_obtained = request.form['c_12_sub_1_marks_obtained']
            c_12_sub_1_total_marks = request.form['c_12_sub_1_total_marks']
            c_12_sub_2_name = request.form['c_12_sub_2_name']
            c_12_sub_2_marks_obtained = request.form['c_12_sub_2_marks_obtained']
            c_12_sub_2_total_marks = request.form['c_12_sub_2_total_marks']
            c_12_sub_3_name = request.form['c_12_sub_3_name']
            c_12_sub_3_marks_obtained = request.form['c_12_sub_3_marks_obtained']
            c_12_sub_3_total_marks = request.form['c_12_sub_3_total_marks']
            c_12_sub_4_name = request.form['c_12_sub_4_name']
            c_12_sub_4_marks_obtained = request.form['c_12_sub_4_marks_obtained']
            c_12_sub_4_total_marks = request.form['c_12_sub_4_total_marks']
            c_12_sub_5_name = request.form['c_12_sub_5_name']
            c_12_sub_5_marks_obtained = request.form['c_12_sub_5_marks_obtained']
            c_12_sub_5_total_marks = request.form['c_12_sub_5_total_marks']


            # Update c_12_info in the database
            cursor.execute("""
                UPDATE class_12
                SET c_12_year = ?, c_12_board = ?, c_12_roll_no = ?, c_12_result = ?, c_12_sub_1_name = ?, c_12_sub_1_marks_obtained = ?, c_12_sub_1_total_marks = ?, c_12_sub_2_name = ?, c_12_sub_2_marks_obtained = ?, c_12_sub_2_total_marks = ?, c_12_sub_3_name = ?, c_12_sub_3_marks_obtained = ?, c_12_sub_3_total_marks = ?, c_12_sub_4_name = ?, c_12_sub_4_marks_obtained = ?, c_12_sub_4_total_marks = ?, c_12_sub_5_name = ?, c_12_sub_5_marks_obtained = ?, c_12_sub_5_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_12_year, c_12_board, c_12_roll_no, c_12_result, c_12_sub_1_name, c_12_sub_1_marks_obtained, c_12_sub_1_total_marks, c_12_sub_2_name, c_12_sub_2_marks_obtained, c_12_sub_2_total_marks, c_12_sub_3_name, c_12_sub_3_marks_obtained, c_12_sub_3_total_marks, c_12_sub_4_name, c_12_sub_4_marks_obtained, c_12_sub_4_total_marks, c_12_sub_5_name, c_12_sub_5_marks_obtained, c_12_sub_5_total_marks, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_ug_details'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_12_info from the database
            cursor.execute("SELECT * FROM class_12 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            c_12_info = cursor.fetchone()

            # Pass the c_12_info to the template
            return render_template('Student/student_info_forms/form_c_12.html', class_12=c_12_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_ug_details', methods=['GET', 'POST'])
def form_ug_details():
    if request.method == 'POST':
        return form_ug_details_post()
    else:
        # Fetch ug_details from the database
        cursor.execute("SELECT * FROM ug_details WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        ug_details = cursor.fetchone()

        # If ug_details is None, create a default ug_details object
        if ug_details is None:
            ug_details = {
                'aadhaar_no': '',
                'ug_enrollment_no': '',
                'ug_admission_year': '',
                'ug_state': '',
                'ug_district': '',
                'ug_qualification_level': '',
                'ug_stream': '',
                'ug_institute_name': '',
                'ug_institute_code': '',
                'ug_board_university': '',
                'ug_course_name': '',
                'ug_course_duration': '',
                'ug_year_of_study': '',
                'ug_year_1_status': '',
                'ug_year_1_admission_year': '',
                'ug_sem_1_status': '',
                'ug_sem_1_session': '',
                'ug_sem_1_roll_no': '',
                'ug_sem_2_status': '',
                'ug_sem_2_session': '',
                'ug_sem_2_roll_no': '',
                'ug_year_2_status': '',
                'ug_year_2_admission_year': '',
                'ug_sem_3_status': '',
                'ug_sem_3_session': '',
                'ug_sem_3_roll_no': '',
                'ug_sem_4_status': '',
                'ug_sem_4_session': '',
                'ug_sem_4_roll_no': '',
                'ug_year_3_status': '',
                'ug_year_3_admission_year': '',
                'ug_sem_5_status': '',
                'ug_sem_5_session': '',
                'ug_sem_5_roll_no': '',
                'ug_year_4_status': '',
                'ug_year_4_admission_year': '',
                'ug_sem_6_status': '',
                'ug_sem_6_session': '',
                'ug_sem_6_roll_no': '',
                'ug_year_5_status': '',
                'ug_year_5_admission_year': '',
                'ug_sem_7_status': '',
                'ug_sem_7_session': '',
                'ug_sem_7_roll_no': '',
                'ug_sem_8_status': '',
                'ug_sem_8_session': '',
                'ug_sem_8_roll_no': '',
                'ug_sem_9_status': '',
                'ug_sem_9_session': '',
                'ug_sem_9_roll_no': '',
                'ug_sem_10_status': '',
                'ug_sem_10_session': '',
                'ug_sem_10_roll_no': ''
            }

        # Pass the ug_details to the template
        return render_template('Student/student_info_forms/form_ug_details.html', ug_details=ug_details)

def form_ug_details_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = request.form.get('aadhaar_no')
            ug_enrollment_no = request.form.get('ug_enrollment_no')
            ug_admission_year = request.form.get('ug_admission_year')
            ug_state = request.form.get('ug_state')
            ug_district = request.form.get('ug_district')
            ug_qualification_level = request.form.get('ug_qualification_level')
            ug_stream = request.form.get('ug_stream')
            ug_institute_name = request.form.get('ug_institute_name')
            ug_institute_code = request.form.get('ug_institute_code')
            ug_board_university = request.form.get('ug_board_university')
            ug_course_name = request.form.get('ug_course_name')
            ug_course_duration = request.form.get('ug_course_duration')
            ug_year_of_study = request.form.get('ug_year_of_study')
            ug_year_1_status = request.form.get('ug_year_1_status')
            ug_year_1_admission_year = request.form.get('ug_year_1_admission_year')
            ug_sem_1_status = request.form.get('ug_sem_1_status')
            ug_sem_1_session = request.form.get('ug_sem_1_session')
            ug_sem_1_roll_no = request.form.get('ug_sem_1_roll_no')
            ug_sem_2_status = request.form.get('ug_sem_2_status')
            ug_sem_2_session = request.form.get('ug_sem_2_session')
            ug_sem_2_roll_no = request.form.get('ug_sem_2_roll_no')
            ug_year_2_status = request.form.get('ug_year_2_status')
            ug_year_2_admission_year = request.form.get('ug_year_2_admission_year')
            ug_sem_3_status = request.form.get('ug_sem_3_status')
            ug_sem_3_session = request.form.get('ug_sem_3_session')
            ug_sem_3_roll_no = request.form.get('ug_sem_3_roll_no')
            ug_sem_4_status = request.form.get('ug_sem_4_status')
            ug_sem_4_session = request.form.get('ug_sem_4_session')
            ug_sem_4_roll_no = request.form.get('ug_sem_4_roll_no')
            ug_year_3_status = request.form.get('ug_year_3_status')
            ug_year_3_admission_year = request.form.get('ug_year_3_admission_year')
            ug_sem_5_status = request.form.get('ug_sem_5_status')
            ug_sem_5_session = request.form.get('ug_sem_5_session')
            ug_sem_5_roll_no = request.form.get('ug_sem_5_roll_no')
            ug_sem_6_status = request.form.get('ug_sem_6_status')
            ug_sem_6_session = request.form.get('ug_sem_6_session')
            ug_sem_6_roll_no = request.form.get('ug_sem_6_roll_no')
            ug_year_4_status = request.form.get('ug_year_4_status')
            ug_year_4_admission_year = request.form.get('ug_year_4_admission_year')
            ug_sem_7_status = request.form.get('ug_sem_7_status')
            ug_sem_7_session = request.form.get('ug_sem_7_session')
            ug_sem_7_roll_no = request.form.get('ug_sem_7_roll_no')
            ug_sem_8_status = request.form.get('ug_sem_8_status')
            ug_sem_8_session = request.form.get('ug_sem_8_session')
            ug_sem_8_roll_no = request.form.get('ug_sem_8_roll_no')
            ug_year_5_status = request.form.get('ug_year_5_status')
            ug_year_5_admission_year = request.form.get('ug_year_5_admission_year')
            ug_sem_9_status = request.form.get('ug_sem_9_status')
            ug_sem_9_session = request.form.get('ug_sem_9_session')
            ug_sem_9_roll_no = request.form.get('ug_sem_9_roll_no')
            ug_sem_10_status = request.form.get('ug_sem_10_status')
            ug_sem_10_session = request.form.get('ug_sem_10_session')
            ug_sem_10_roll_no = request.form.get('ug_sem_10_roll_no')

            # Update ug_details in the database
            cursor.execute("""
                UPDATE ug_details
                SET ug_enrollment_no = ?, ug_admission_year = ?, ug_state = ?, ug_district = ?,
                    ug_qualification_level = ?, ug_stream = ?, ug_institute_name = ?, ug_institute_code = ?,
                    ug_board_university = ?, ug_course_name = ?, ug_course_duration = ?, ug_year_of_study = ?,
                    ug_year_1_status = ?, ug_year_1_admission_year = ?, ug_sem_1_status = ?, ug_sem_1_session = ?,
                    ug_sem_1_roll_no = ?, ug_sem_2_status = ?, ug_sem_2_session = ?, ug_sem_2_roll_no = ?,
                    ug_year_2_status = ?, ug_year_2_admission_year = ?, ug_sem_3_status = ?, ug_sem_3_session = ?,
                    ug_sem_3_roll_no = ?, ug_sem_4_status = ?, ug_sem_4_session = ?, ug_sem_4_roll_no = ?,
                    ug_year_3_status = ?, ug_year_3_admission_year = ?, ug_sem_5_status = ?, ug_sem_5_session = ?,
                    ug_sem_5_roll_no = ?, ug_sem_6_status = ?, ug_sem_6_session = ?, ug_sem_6_roll_no = ?,
                    ug_year_4_status = ?, ug_year_4_admission_year = ?, ug_sem_7_status = ?, ug_sem_7_session = ?,
                    ug_sem_7_roll_no = ?, ug_sem_8_status = ?, ug_sem_8_session = ?, ug_sem_8_roll_no = ?,
                    ug_year_5_status = ?, ug_year_5_admission_year = ?, ug_sem_9_status = ?, ug_sem_9_session = ?,
                    ug_sem_9_roll_no = ?, ug_sem_10_status = ?, ug_sem_10_session = ?, ug_sem_10_roll_no = ?
                WHERE aadhaar_no = ?
            """, (ug_enrollment_no, ug_admission_year, ug_state, ug_district, ug_qualification_level,
                  ug_stream, ug_institute_name, ug_institute_code, ug_board_university, ug_course_name,
                  ug_course_duration, ug_year_of_study, ug_year_1_status, ug_year_1_admission_year,
                  ug_sem_1_status, ug_sem_1_session, ug_sem_1_roll_no, ug_sem_2_status, ug_sem_2_session,
                  ug_sem_2_roll_no, ug_year_2_status, ug_year_2_admission_year, ug_sem_3_status, ug_sem_3_session,
                  ug_sem_3_roll_no, ug_sem_4_status, ug_sem_4_session, ug_sem_4_roll_no, ug_year_3_status,
                  ug_year_3_admission_year, ug_sem_5_status, ug_sem_5_session, ug_sem_5_roll_no, ug_sem_6_status,
                  ug_sem_6_session, ug_sem_6_roll_no, ug_year_4_status, ug_year_4_admission_year,
                  ug_sem_7_status, ug_sem_7_session, ug_sem_7_roll_no, ug_sem_8_status, ug_sem_8_session,
                  ug_sem_8_roll_no, ug_year_5_status, ug_year_5_admission_year, ug_sem_9_status, ug_sem_9_session,
                  ug_sem_9_roll_no, ug_sem_10_status, ug_sem_10_session, ug_sem_10_roll_no, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_ug_sem_1'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_12_info from the database
            cursor.execute("SELECT * FROM ug_details WHERE aadhaar_no = ?",(session['aadhaar_no'],))
            ug_details = cursor.fetchone()

            # Pass the ug_details to the template
            return render_template('Student/student_info_forms/form_ug_details.html', ug_details=ug_details)

    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_ug_sem_1', methods=['GET', 'POST'])
def form_ug_sem_1():
    try:
        if request.method == 'POST':
            return form_ug_sem_1_post()
        else:
            # Fetch ug_sem_1_info from the database
            cursor.execute("SELECT * FROM ug_sem_1 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_1_info = cursor.fetchone()

            # If ug_sem_1_info is None, create a default ug_sem_1_info object
            if ug_sem_1_info is None:
                ug_sem_1_info = {
                    'ug_enrollment_no': '',
                    'ug_sem_1_session': '',
                    'ug_sem_1_roll_no': '',
                    'ug_sem_1_result': '',
                    'ug_sem_1_sub_1_name': '',
                    'ug_sem_1_sub_1_marks_obtained': '',
                    'ug_sem_1_sub_1_total_marks': '',
                    'ug_sem_1_sub_2_name': '',
                    'ug_sem_1_sub_2_marks_obtained': '',
                    'ug_sem_1_sub_2_total_marks': '',
                    'ug_sem_1_sub_3_name': '',
                    'ug_sem_1_sub_3_marks_obtained': '',
                    'ug_sem_1_sub_3_total_marks': '',
                    'ug_sem_1_sub_4_name': '',
                    'ug_sem_1_sub_4_marks_obtained': '',
                    'ug_sem_1_sub_4_total_marks': '',
                    'ug_sem_1_sub_5_name': '',
                    'ug_sem_1_sub_5_marks_obtained': '',
                    'ug_sem_1_sub_5_total_marks': '',
                    'ug_sem_1_sub_6_name': '',
                    'ug_sem_1_sub_6_marks_obtained': '',
                    'ug_sem_1_sub_6_total_marks': '',
                    'ug_sem_1_sub_7_name': '',
                    'ug_sem_1_sub_7_marks_obtained': '',
                    'ug_sem_1_sub_7_total_marks': '',
                    'ug_sem_1_sub_8_name': '',
                    'ug_sem_1_sub_8_marks_obtained': '',
                    'ug_sem_1_sub_8_total_marks': '',
                    'ug_sem_1_sub_9_name': '',
                    'ug_sem_1_sub_9_marks_obtained': '',
                    'ug_sem_1_sub_9_total_marks': '',
                    'ug_sem_1_sub_10_name': '',
                    'ug_sem_1_sub_10_marks_obtained': '',
                    'ug_sem_1_sub_10_total_marks': '',
                    'ug_sem_1_sub_11_name': '',
                    'ug_sem_1_sub_11_marks_obtained': '',
                    'ug_sem_1_sub_11_total_marks': '',
                    'ug_sem_1_sub_12_name': '',
                    'ug_sem_1_sub_12_marks_obtained': '',
                    'ug_sem_1_sub_12_total_marks': '',
                    'ug_sem_1_sub_13_name': '',
                    'ug_sem_1_sub_13_marks_obtained': '',
                    'ug_sem_1_sub_13_total_marks': '',
                    'ug_sem_1_sub_14_name': '',
                    'ug_sem_1_sub_14_marks_obtained': '',
                    'ug_sem_1_sub_14_total_marks': '',
                    'ug_sem_1_sub_15_name': '',
                    'ug_sem_1_sub_15_marks_obtained': '',
                    'ug_sem_1_sub_15_total_marks': '',
                    'ug_sem_1_sub_16_name': '',
                    'ug_sem_1_sub_16_marks_obtained': '',
                    'ug_sem_1_sub_16_total_marks': '',
                    'ug_sem_1_sub_17_name': '',
                    'ug_sem_1_sub_17_marks_obtained': '',
                    'ug_sem_1_sub_17_total_marks': '',
                    'ug_sem_1_sub_18_name': '',
                    'ug_sem_1_sub_18_marks_obtained': '',
                    'ug_sem_1_sub_18_total_marks': '',
                    'ug_sem_1_sub_19_name': '',
                    'ug_sem_1_sub_19_marks_obtained': '',
                    'ug_sem_1_sub_19_total_marks': '',
                    'ug_sem_1_sub_20_name': '',
                    'ug_sem_1_sub_20_marks_obtained': '',
                    'ug_sem_1_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the ug_sem_1_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_1.html', ug_sem_1=ug_sem_1_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_ug_sem_1_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            ug_enrollment_no = request.form['ug_enrollment_no']
            ug_sem_1_session = request.form['ug_sem_1_session']
            ug_sem_1_roll_no = request.form['ug_sem_1_roll_no']
            ug_sem_1_result = request.form['ug_sem_1_result']
            ug_sem_1_sub_1_name = request.form['ug_sem_1_sub_1_name']
            ug_sem_1_sub_1_marks_obtained = request.form['ug_sem_1_sub_1_marks_obtained']
            ug_sem_1_sub_1_total_marks = request.form['ug_sem_1_sub_1_total_marks']
            ug_sem_1_sub_2_name = request.form['ug_sem_1_sub_2_name']
            ug_sem_1_sub_2_marks_obtained = request.form['ug_sem_1_sub_2_marks_obtained']
            ug_sem_1_sub_2_total_marks = request.form['ug_sem_1_sub_2_total_marks']
            ug_sem_1_sub_3_name = request.form['ug_sem_1_sub_3_name']
            ug_sem_1_sub_3_marks_obtained = request.form['ug_sem_1_sub_3_marks_obtained']
            ug_sem_1_sub_3_total_marks = request.form['ug_sem_1_sub_3_total_marks']
            ug_sem_1_sub_4_name = request.form['ug_sem_1_sub_4_name']
            ug_sem_1_sub_4_marks_obtained = request.form['ug_sem_1_sub_4_marks_obtained']
            ug_sem_1_sub_4_total_marks = request.form['ug_sem_1_sub_4_total_marks']
            ug_sem_1_sub_5_name = request.form['ug_sem_1_sub_5_name']
            ug_sem_1_sub_5_marks_obtained = request.form['ug_sem_1_sub_5_marks_obtained']
            ug_sem_1_sub_5_total_marks = request.form['ug_sem_1_sub_5_total_marks']
            ug_sem_1_sub_6_name = request.form['ug_sem_1_sub_6_name']
            ug_sem_1_sub_6_marks_obtained = request.form['ug_sem_1_sub_6_marks_obtained']
            ug_sem_1_sub_6_total_marks = request.form['ug_sem_1_sub_6_total_marks']
            ug_sem_1_sub_7_name = request.form['ug_sem_1_sub_7_name']
            ug_sem_1_sub_7_marks_obtained = request.form['ug_sem_1_sub_7_marks_obtained']
            ug_sem_1_sub_7_total_marks = request.form['ug_sem_1_sub_7_total_marks']
            ug_sem_1_sub_8_name = request.form['ug_sem_1_sub_8_name']
            ug_sem_1_sub_8_marks_obtained = request.form['ug_sem_1_sub_8_marks_obtained']
            ug_sem_1_sub_8_total_marks = request.form['ug_sem_1_sub_8_total_marks']
            ug_sem_1_sub_9_name = request.form['ug_sem_1_sub_9_name']
            ug_sem_1_sub_9_marks_obtained = request.form['ug_sem_1_sub_9_marks_obtained']
            ug_sem_1_sub_9_total_marks = request.form['ug_sem_1_sub_9_total_marks']
            ug_sem_1_sub_10_name = request.form['ug_sem_1_sub_10_name']
            ug_sem_1_sub_10_marks_obtained = request.form['ug_sem_1_sub_10_marks_obtained']
            ug_sem_1_sub_10_total_marks = request.form['ug_sem_1_sub_10_total_marks']
            ug_sem_1_sub_11_name = request.form['ug_sem_1_sub_11_name']
            ug_sem_1_sub_11_marks_obtained = request.form['ug_sem_1_sub_11_marks_obtained']
            ug_sem_1_sub_11_total_marks = request.form['ug_sem_1_sub_11_total_marks']
            ug_sem_1_sub_12_name = request.form['ug_sem_1_sub_12_name']
            ug_sem_1_sub_12_marks_obtained = request.form['ug_sem_1_sub_12_marks_obtained']
            ug_sem_1_sub_12_total_marks = request.form['ug_sem_1_sub_12_total_marks']
            ug_sem_1_sub_13_name = request.form['ug_sem_1_sub_13_name']
            ug_sem_1_sub_13_marks_obtained = request.form['ug_sem_1_sub_13_marks_obtained']
            ug_sem_1_sub_13_total_marks = request.form['ug_sem_1_sub_13_total_marks']
            ug_sem_1_sub_14_name = request.form['ug_sem_1_sub_14_name']
            ug_sem_1_sub_14_marks_obtained = request.form['ug_sem_1_sub_14_marks_obtained']
            ug_sem_1_sub_14_total_marks = request.form['ug_sem_1_sub_14_total_marks']
            ug_sem_1_sub_15_name = request.form['ug_sem_1_sub_15_name']
            ug_sem_1_sub_15_marks_obtained = request.form['ug_sem_1_sub_15_marks_obtained']
            ug_sem_1_sub_15_total_marks = request.form['ug_sem_1_sub_15_total_marks']
            ug_sem_1_sub_16_name = request.form['ug_sem_1_sub_16_name']
            ug_sem_1_sub_16_marks_obtained = request.form['ug_sem_1_sub_16_marks_obtained']
            ug_sem_1_sub_16_total_marks = request.form['ug_sem_1_sub_16_total_marks']
            ug_sem_1_sub_17_name = request.form['ug_sem_1_sub_17_name']
            ug_sem_1_sub_17_marks_obtained = request.form['ug_sem_1_sub_17_marks_obtained']
            ug_sem_1_sub_17_total_marks = request.form['ug_sem_1_sub_17_total_marks']
            ug_sem_1_sub_18_name = request.form['ug_sem_1_sub_18_name']
            ug_sem_1_sub_18_marks_obtained = request.form['ug_sem_1_sub_18_marks_obtained']
            ug_sem_1_sub_18_total_marks = request.form['ug_sem_1_sub_18_total_marks']
            ug_sem_1_sub_19_name = request.form['ug_sem_1_sub_19_name']
            ug_sem_1_sub_19_marks_obtained = request.form['ug_sem_1_sub_19_marks_obtained']
            ug_sem_1_sub_19_total_marks = request.form['ug_sem_1_sub_19_total_marks']
            ug_sem_1_sub_20_name = request.form['ug_sem_1_sub_20_name']
            ug_sem_1_sub_20_marks_obtained = request.form['ug_sem_1_sub_20_marks_obtained']
            ug_sem_1_sub_20_total_marks = request.form['ug_sem_1_sub_20_total_marks']


            # Update ug_sem_1_info in the database
            cursor.execute("""
                UPDATE ug_sem_1
                SET ug_enrollment_no = ?, ug_sem_1_session = ?, ug_sem_1_roll_no = ?, ug_sem_1_result = ?, ug_sem_1_sub_1_name = ?, ug_sem_1_sub_1_marks_obtained = ?, ug_sem_1_sub_1_total_marks = ?, ug_sem_1_sub_2_name = ?, ug_sem_1_sub_2_marks_obtained = ?, ug_sem_1_sub_2_total_marks = ?, ug_sem_1_sub_3_name = ?, ug_sem_1_sub_3_marks_obtained = ?, ug_sem_1_sub_3_total_marks = ?, ug_sem_1_sub_4_name = ?, ug_sem_1_sub_4_marks_obtained = ?, ug_sem_1_sub_4_total_marks = ?, ug_sem_1_sub_5_name = ?, ug_sem_1_sub_5_marks_obtained = ?, ug_sem_1_sub_5_total_marks = ?, ug_sem_1_sub_6_name = ?, ug_sem_1_sub_6_marks_obtained = ?, ug_sem_1_sub_6_total_marks = ?, ug_sem_1_sub_7_name = ?, ug_sem_1_sub_7_marks_obtained = ?, ug_sem_1_sub_7_total_marks = ?, ug_sem_1_sub_8_name = ?, ug_sem_1_sub_8_marks_obtained = ?, ug_sem_1_sub_8_total_marks = ?, ug_sem_1_sub_9_name = ?, ug_sem_1_sub_9_marks_obtained = ?, ug_sem_1_sub_9_total_marks = ?, ug_sem_1_sub_10_name = ?, ug_sem_1_sub_10_marks_obtained = ?, ug_sem_1_sub_10_total_marks = ?, ug_sem_1_sub_11_name = ?, ug_sem_1_sub_11_marks_obtained = ?, ug_sem_1_sub_11_total_marks = ?, ug_sem_1_sub_12_name = ?, ug_sem_1_sub_12_marks_obtained = ?, ug_sem_1_sub_12_total_marks = ?, ug_sem_1_sub_13_name = ?, ug_sem_1_sub_13_marks_obtained = ?, ug_sem_1_sub_13_total_marks = ?, ug_sem_1_sub_14_name = ?, ug_sem_1_sub_14_marks_obtained = ?, ug_sem_1_sub_14_total_marks = ?, ug_sem_1_sub_15_name = ?, ug_sem_1_sub_15_marks_obtained = ?, ug_sem_1_sub_15_total_marks = ?, ug_sem_1_sub_16_name = ?, ug_sem_1_sub_16_marks_obtained = ?, ug_sem_1_sub_16_total_marks = ?, ug_sem_1_sub_17_name = ?, ug_sem_1_sub_17_marks_obtained = ?, ug_sem_1_sub_17_total_marks = ?, ug_sem_1_sub_18_name = ?, ug_sem_1_sub_18_marks_obtained = ?, ug_sem_1_sub_18_total_marks = ?, ug_sem_1_sub_19_name = ?, ug_sem_1_sub_19_marks_obtained = ?, ug_sem_1_sub_19_total_marks = ?, ug_sem_1_sub_20_name = ?, ug_sem_1_sub_20_marks_obtained = ?, ug_sem_1_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(ug_enrollment_no,ug_sem_1_session,ug_sem_1_roll_no,ug_sem_1_result,ug_sem_1_sub_1_name,
                 ug_sem_1_sub_1_marks_obtained,ug_sem_1_sub_1_total_marks,ug_sem_1_sub_2_name,
                 ug_sem_1_sub_2_marks_obtained,ug_sem_1_sub_2_total_marks,ug_sem_1_sub_3_name,
                 ug_sem_1_sub_3_marks_obtained,ug_sem_1_sub_3_total_marks,ug_sem_1_sub_4_name,
                 ug_sem_1_sub_4_marks_obtained,ug_sem_1_sub_4_total_marks,ug_sem_1_sub_5_name,
                 ug_sem_1_sub_5_marks_obtained,ug_sem_1_sub_5_total_marks,ug_sem_1_sub_6_name,
                 ug_sem_1_sub_6_marks_obtained,ug_sem_1_sub_6_total_marks,ug_sem_1_sub_7_name,
                 ug_sem_1_sub_7_marks_obtained,ug_sem_1_sub_7_total_marks,ug_sem_1_sub_8_name,
                 ug_sem_1_sub_8_marks_obtained,ug_sem_1_sub_8_total_marks,ug_sem_1_sub_9_name,
                 ug_sem_1_sub_9_marks_obtained,ug_sem_1_sub_9_total_marks,ug_sem_1_sub_10_name,
                 ug_sem_1_sub_10_marks_obtained,ug_sem_1_sub_10_total_marks,ug_sem_1_sub_11_name,
                 ug_sem_1_sub_11_marks_obtained,ug_sem_1_sub_11_total_marks,ug_sem_1_sub_12_name,
                 ug_sem_1_sub_12_marks_obtained,ug_sem_1_sub_12_total_marks,ug_sem_1_sub_13_name,
                 ug_sem_1_sub_13_marks_obtained,ug_sem_1_sub_13_total_marks,ug_sem_1_sub_14_name,
                 ug_sem_1_sub_14_marks_obtained,ug_sem_1_sub_14_total_marks,ug_sem_1_sub_15_name,
                 ug_sem_1_sub_15_marks_obtained,ug_sem_1_sub_15_total_marks,ug_sem_1_sub_16_name,
                 ug_sem_1_sub_16_marks_obtained,ug_sem_1_sub_16_total_marks,ug_sem_1_sub_17_name,
                 ug_sem_1_sub_17_marks_obtained,ug_sem_1_sub_17_total_marks,ug_sem_1_sub_18_name,
                 ug_sem_1_sub_18_marks_obtained,ug_sem_1_sub_18_total_marks,ug_sem_1_sub_19_name,
                 ug_sem_1_sub_19_marks_obtained,ug_sem_1_sub_19_total_marks,ug_sem_1_sub_20_name,
                 ug_sem_1_sub_20_marks_obtained,ug_sem_1_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_ug_sem_2'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch ug_sem_1_info from the database
            cursor.execute("SELECT * FROM ug_sem_1 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_1_info = cursor.fetchone()

            # Pass the ug_sem_1_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_1.html', ug_sem_1=ug_sem_1_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_ug_sem_2', methods=['GET', 'POST'])
def form_ug_sem_2():
    try:
        if request.method == 'POST':
            return form_ug_sem_2_post()
        else:
            # Fetch ug_sem_2_info from the database
            cursor.execute("SELECT * FROM ug_sem_2 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_2_info = cursor.fetchone()

            # If ug_sem_2_info is None, create a default ug_sem_2_info object
            if ug_sem_2_info is None:
                ug_sem_2_info = {
                    'ug_enrollment_no': '',
                    'ug_sem_2_session': '',
                    'ug_sem_2_roll_no': '',
                    'ug_sem_2_result': '',
                    'ug_sem_2_sub_1_name': '',
                    'ug_sem_2_sub_1_marks_obtained': '',
                    'ug_sem_2_sub_1_total_marks': '',
                    'ug_sem_2_sub_2_name': '',
                    'ug_sem_2_sub_2_marks_obtained': '',
                    'ug_sem_2_sub_2_total_marks': '',
                    'ug_sem_2_sub_3_name': '',
                    'ug_sem_2_sub_3_marks_obtained': '',
                    'ug_sem_2_sub_3_total_marks': '',
                    'ug_sem_2_sub_4_name': '',
                    'ug_sem_2_sub_4_marks_obtained': '',
                    'ug_sem_2_sub_4_total_marks': '',
                    'ug_sem_2_sub_5_name': '',
                    'ug_sem_2_sub_5_marks_obtained': '',
                    'ug_sem_2_sub_5_total_marks': '',
                    'ug_sem_2_sub_6_name': '',
                    'ug_sem_2_sub_6_marks_obtained': '',
                    'ug_sem_2_sub_6_total_marks': '',
                    'ug_sem_2_sub_7_name': '',
                    'ug_sem_2_sub_7_marks_obtained': '',
                    'ug_sem_2_sub_7_total_marks': '',
                    'ug_sem_2_sub_8_name': '',
                    'ug_sem_2_sub_8_marks_obtained': '',
                    'ug_sem_2_sub_8_total_marks': '',
                    'ug_sem_2_sub_9_name': '',
                    'ug_sem_2_sub_9_marks_obtained': '',
                    'ug_sem_2_sub_9_total_marks': '',
                    'ug_sem_2_sub_10_name': '',
                    'ug_sem_2_sub_10_marks_obtained': '',
                    'ug_sem_2_sub_10_total_marks': '',
                    'ug_sem_2_sub_11_name': '',
                    'ug_sem_2_sub_11_marks_obtained': '',
                    'ug_sem_2_sub_11_total_marks': '',
                    'ug_sem_2_sub_12_name': '',
                    'ug_sem_2_sub_12_marks_obtained': '',
                    'ug_sem_2_sub_12_total_marks': '',
                    'ug_sem_2_sub_13_name': '',
                    'ug_sem_2_sub_13_marks_obtained': '',
                    'ug_sem_2_sub_13_total_marks': '',
                    'ug_sem_2_sub_14_name': '',
                    'ug_sem_2_sub_14_marks_obtained': '',
                    'ug_sem_2_sub_14_total_marks': '',
                    'ug_sem_2_sub_15_name': '',
                    'ug_sem_2_sub_15_marks_obtained': '',
                    'ug_sem_2_sub_15_total_marks': '',
                    'ug_sem_2_sub_16_name': '',
                    'ug_sem_2_sub_16_marks_obtained': '',
                    'ug_sem_2_sub_16_total_marks': '',
                    'ug_sem_2_sub_17_name': '',
                    'ug_sem_2_sub_17_marks_obtained': '',
                    'ug_sem_2_sub_17_total_marks': '',
                    'ug_sem_2_sub_18_name': '',
                    'ug_sem_2_sub_18_marks_obtained': '',
                    'ug_sem_2_sub_18_total_marks': '',
                    'ug_sem_2_sub_19_name': '',
                    'ug_sem_2_sub_19_marks_obtained': '',
                    'ug_sem_2_sub_19_total_marks': '',
                    'ug_sem_2_sub_20_name': '',
                    'ug_sem_2_sub_20_marks_obtained': '',
                    'ug_sem_2_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the ug_sem_2_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_2.html', ug_sem_2=ug_sem_2_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_ug_sem_2_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            ug_enrollment_no = request.form['ug_enrollment_no']
            ug_sem_2_session = request.form['ug_sem_2_session']
            ug_sem_2_roll_no = request.form['ug_sem_2_roll_no']
            ug_sem_2_result = request.form['ug_sem_2_result']
            ug_sem_2_sub_1_name = request.form['ug_sem_2_sub_1_name']
            ug_sem_2_sub_1_marks_obtained = request.form['ug_sem_2_sub_1_marks_obtained']
            ug_sem_2_sub_1_total_marks = request.form['ug_sem_2_sub_1_total_marks']
            ug_sem_2_sub_2_name = request.form['ug_sem_2_sub_2_name']
            ug_sem_2_sub_2_marks_obtained = request.form['ug_sem_2_sub_2_marks_obtained']
            ug_sem_2_sub_2_total_marks = request.form['ug_sem_2_sub_2_total_marks']
            ug_sem_2_sub_3_name = request.form['ug_sem_2_sub_3_name']
            ug_sem_2_sub_3_marks_obtained = request.form['ug_sem_2_sub_3_marks_obtained']
            ug_sem_2_sub_3_total_marks = request.form['ug_sem_2_sub_3_total_marks']
            ug_sem_2_sub_4_name = request.form['ug_sem_2_sub_4_name']
            ug_sem_2_sub_4_marks_obtained = request.form['ug_sem_2_sub_4_marks_obtained']
            ug_sem_2_sub_4_total_marks = request.form['ug_sem_2_sub_4_total_marks']
            ug_sem_2_sub_5_name = request.form['ug_sem_2_sub_5_name']
            ug_sem_2_sub_5_marks_obtained = request.form['ug_sem_2_sub_5_marks_obtained']
            ug_sem_2_sub_5_total_marks = request.form['ug_sem_2_sub_5_total_marks']
            ug_sem_2_sub_6_name = request.form['ug_sem_2_sub_6_name']
            ug_sem_2_sub_6_marks_obtained = request.form['ug_sem_2_sub_6_marks_obtained']
            ug_sem_2_sub_6_total_marks = request.form['ug_sem_2_sub_6_total_marks']
            ug_sem_2_sub_7_name = request.form['ug_sem_2_sub_7_name']
            ug_sem_2_sub_7_marks_obtained = request.form['ug_sem_2_sub_7_marks_obtained']
            ug_sem_2_sub_7_total_marks = request.form['ug_sem_2_sub_7_total_marks']
            ug_sem_2_sub_8_name = request.form['ug_sem_2_sub_8_name']
            ug_sem_2_sub_8_marks_obtained = request.form['ug_sem_2_sub_8_marks_obtained']
            ug_sem_2_sub_8_total_marks = request.form['ug_sem_2_sub_8_total_marks']
            ug_sem_2_sub_9_name = request.form['ug_sem_2_sub_9_name']
            ug_sem_2_sub_9_marks_obtained = request.form['ug_sem_2_sub_9_marks_obtained']
            ug_sem_2_sub_9_total_marks = request.form['ug_sem_2_sub_9_total_marks']
            ug_sem_2_sub_10_name = request.form['ug_sem_2_sub_10_name']
            ug_sem_2_sub_10_marks_obtained = request.form['ug_sem_2_sub_10_marks_obtained']
            ug_sem_2_sub_10_total_marks = request.form['ug_sem_2_sub_10_total_marks']
            ug_sem_2_sub_11_name = request.form['ug_sem_2_sub_11_name']
            ug_sem_2_sub_11_marks_obtained = request.form['ug_sem_2_sub_11_marks_obtained']
            ug_sem_2_sub_11_total_marks = request.form['ug_sem_2_sub_11_total_marks']
            ug_sem_2_sub_12_name = request.form['ug_sem_2_sub_12_name']
            ug_sem_2_sub_12_marks_obtained = request.form['ug_sem_2_sub_12_marks_obtained']
            ug_sem_2_sub_12_total_marks = request.form['ug_sem_2_sub_12_total_marks']
            ug_sem_2_sub_13_name = request.form['ug_sem_2_sub_13_name']
            ug_sem_2_sub_13_marks_obtained = request.form['ug_sem_2_sub_13_marks_obtained']
            ug_sem_2_sub_13_total_marks = request.form['ug_sem_2_sub_13_total_marks']
            ug_sem_2_sub_14_name = request.form['ug_sem_2_sub_14_name']
            ug_sem_2_sub_14_marks_obtained = request.form['ug_sem_2_sub_14_marks_obtained']
            ug_sem_2_sub_14_total_marks = request.form['ug_sem_2_sub_14_total_marks']
            ug_sem_2_sub_15_name = request.form['ug_sem_2_sub_15_name']
            ug_sem_2_sub_15_marks_obtained = request.form['ug_sem_2_sub_15_marks_obtained']
            ug_sem_2_sub_15_total_marks = request.form['ug_sem_2_sub_15_total_marks']
            ug_sem_2_sub_16_name = request.form['ug_sem_2_sub_16_name']
            ug_sem_2_sub_16_marks_obtained = request.form['ug_sem_2_sub_16_marks_obtained']
            ug_sem_2_sub_16_total_marks = request.form['ug_sem_2_sub_16_total_marks']
            ug_sem_2_sub_17_name = request.form['ug_sem_2_sub_17_name']
            ug_sem_2_sub_17_marks_obtained = request.form['ug_sem_2_sub_17_marks_obtained']
            ug_sem_2_sub_17_total_marks = request.form['ug_sem_2_sub_17_total_marks']
            ug_sem_2_sub_18_name = request.form['ug_sem_2_sub_18_name']
            ug_sem_2_sub_18_marks_obtained = request.form['ug_sem_2_sub_18_marks_obtained']
            ug_sem_2_sub_18_total_marks = request.form['ug_sem_2_sub_18_total_marks']
            ug_sem_2_sub_19_name = request.form['ug_sem_2_sub_19_name']
            ug_sem_2_sub_19_marks_obtained = request.form['ug_sem_2_sub_19_marks_obtained']
            ug_sem_2_sub_19_total_marks = request.form['ug_sem_2_sub_19_total_marks']
            ug_sem_2_sub_20_name = request.form['ug_sem_2_sub_20_name']
            ug_sem_2_sub_20_marks_obtained = request.form['ug_sem_2_sub_20_marks_obtained']
            ug_sem_2_sub_20_total_marks = request.form['ug_sem_2_sub_20_total_marks']


            # Update ug_sem_2_info in the database
            cursor.execute("""
                UPDATE ug_sem_2
                SET ug_enrollment_no = ?, ug_sem_2_session = ?, ug_sem_2_roll_no = ?, ug_sem_2_result = ?, ug_sem_2_sub_1_name = ?, ug_sem_2_sub_1_marks_obtained = ?, ug_sem_2_sub_1_total_marks = ?, ug_sem_2_sub_2_name = ?, ug_sem_2_sub_2_marks_obtained = ?, ug_sem_2_sub_2_total_marks = ?, ug_sem_2_sub_3_name = ?, ug_sem_2_sub_3_marks_obtained = ?, ug_sem_2_sub_3_total_marks = ?, ug_sem_2_sub_4_name = ?, ug_sem_2_sub_4_marks_obtained = ?, ug_sem_2_sub_4_total_marks = ?, ug_sem_2_sub_5_name = ?, ug_sem_2_sub_5_marks_obtained = ?, ug_sem_2_sub_5_total_marks = ?, ug_sem_2_sub_6_name = ?, ug_sem_2_sub_6_marks_obtained = ?, ug_sem_2_sub_6_total_marks = ?, ug_sem_2_sub_7_name = ?, ug_sem_2_sub_7_marks_obtained = ?, ug_sem_2_sub_7_total_marks = ?, ug_sem_2_sub_8_name = ?, ug_sem_2_sub_8_marks_obtained = ?, ug_sem_2_sub_8_total_marks = ?, ug_sem_2_sub_9_name = ?, ug_sem_2_sub_9_marks_obtained = ?, ug_sem_2_sub_9_total_marks = ?, ug_sem_2_sub_10_name = ?, ug_sem_2_sub_10_marks_obtained = ?, ug_sem_2_sub_10_total_marks = ?, ug_sem_2_sub_11_name = ?, ug_sem_2_sub_11_marks_obtained = ?, ug_sem_2_sub_11_total_marks = ?, ug_sem_2_sub_12_name = ?, ug_sem_2_sub_12_marks_obtained = ?, ug_sem_2_sub_12_total_marks = ?, ug_sem_2_sub_13_name = ?, ug_sem_2_sub_13_marks_obtained = ?, ug_sem_2_sub_13_total_marks = ?, ug_sem_2_sub_14_name = ?, ug_sem_2_sub_14_marks_obtained = ?, ug_sem_2_sub_14_total_marks = ?, ug_sem_2_sub_15_name = ?, ug_sem_2_sub_15_marks_obtained = ?, ug_sem_2_sub_15_total_marks = ?, ug_sem_2_sub_16_name = ?, ug_sem_2_sub_16_marks_obtained = ?, ug_sem_2_sub_16_total_marks = ?, ug_sem_2_sub_17_name = ?, ug_sem_2_sub_17_marks_obtained = ?, ug_sem_2_sub_17_total_marks = ?, ug_sem_2_sub_18_name = ?, ug_sem_2_sub_18_marks_obtained = ?, ug_sem_2_sub_18_total_marks = ?, ug_sem_2_sub_19_name = ?, ug_sem_2_sub_19_marks_obtained = ?, ug_sem_2_sub_19_total_marks = ?, ug_sem_2_sub_20_name = ?, ug_sem_2_sub_20_marks_obtained = ?, ug_sem_2_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(ug_enrollment_no,ug_sem_2_session,ug_sem_2_roll_no,ug_sem_2_result,ug_sem_2_sub_1_name,
                 ug_sem_2_sub_1_marks_obtained,ug_sem_2_sub_1_total_marks,ug_sem_2_sub_2_name,
                 ug_sem_2_sub_2_marks_obtained,ug_sem_2_sub_2_total_marks,ug_sem_2_sub_3_name,
                 ug_sem_2_sub_3_marks_obtained,ug_sem_2_sub_3_total_marks,ug_sem_2_sub_4_name,
                 ug_sem_2_sub_4_marks_obtained,ug_sem_2_sub_4_total_marks,ug_sem_2_sub_5_name,
                 ug_sem_2_sub_5_marks_obtained,ug_sem_2_sub_5_total_marks,ug_sem_2_sub_6_name,
                 ug_sem_2_sub_6_marks_obtained,ug_sem_2_sub_6_total_marks,ug_sem_2_sub_7_name,
                 ug_sem_2_sub_7_marks_obtained,ug_sem_2_sub_7_total_marks,ug_sem_2_sub_8_name,
                 ug_sem_2_sub_8_marks_obtained,ug_sem_2_sub_8_total_marks,ug_sem_2_sub_9_name,
                 ug_sem_2_sub_9_marks_obtained,ug_sem_2_sub_9_total_marks,ug_sem_2_sub_10_name,
                 ug_sem_2_sub_10_marks_obtained,ug_sem_2_sub_10_total_marks,ug_sem_2_sub_11_name,
                 ug_sem_2_sub_11_marks_obtained,ug_sem_2_sub_11_total_marks,ug_sem_2_sub_12_name,
                 ug_sem_2_sub_12_marks_obtained,ug_sem_2_sub_12_total_marks,ug_sem_2_sub_13_name,
                 ug_sem_2_sub_13_marks_obtained,ug_sem_2_sub_13_total_marks,ug_sem_2_sub_14_name,
                 ug_sem_2_sub_14_marks_obtained,ug_sem_2_sub_14_total_marks,ug_sem_2_sub_15_name,
                 ug_sem_2_sub_15_marks_obtained,ug_sem_2_sub_15_total_marks,ug_sem_2_sub_16_name,
                 ug_sem_2_sub_16_marks_obtained,ug_sem_2_sub_16_total_marks,ug_sem_2_sub_17_name,
                 ug_sem_2_sub_17_marks_obtained,ug_sem_2_sub_17_total_marks,ug_sem_2_sub_18_name,
                 ug_sem_2_sub_18_marks_obtained,ug_sem_2_sub_18_total_marks,ug_sem_2_sub_19_name,
                 ug_sem_2_sub_19_marks_obtained,ug_sem_2_sub_19_total_marks,ug_sem_2_sub_20_name,
                 ug_sem_2_sub_20_marks_obtained,ug_sem_2_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_ug_sem_3'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch ug_sem_2_info from the database
            cursor.execute("SELECT * FROM ug_sem_2 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_2_info = cursor.fetchone()

            # Pass the ug_sem_2_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_2.html', ug_sem_2=ug_sem_2_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_ug_sem_3', methods=['GET', 'POST'])
def form_ug_sem_3():
    try:
        if request.method == 'POST':
            return form_ug_sem_3_post()
        else:
            # Fetch ug_sem_3_info from the database
            cursor.execute("SELECT * FROM ug_sem_3 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_3_info = cursor.fetchone()

            # If ug_sem_3_info is None, create a default ug_sem_3_info object
            if ug_sem_3_info is None:
                ug_sem_3_info = {
                    'ug_enrollment_no': '',
                    'ug_sem_3_session': '',
                    'ug_sem_3_roll_no': '',
                    'ug_sem_3_result': '',
                    'ug_sem_3_sub_1_name': '',
                    'ug_sem_3_sub_1_marks_obtained': '',
                    'ug_sem_3_sub_1_total_marks': '',
                    'ug_sem_3_sub_2_name': '',
                    'ug_sem_3_sub_2_marks_obtained': '',
                    'ug_sem_3_sub_2_total_marks': '',
                    'ug_sem_3_sub_3_name': '',
                    'ug_sem_3_sub_3_marks_obtained': '',
                    'ug_sem_3_sub_3_total_marks': '',
                    'ug_sem_3_sub_4_name': '',
                    'ug_sem_3_sub_4_marks_obtained': '',
                    'ug_sem_3_sub_4_total_marks': '',
                    'ug_sem_3_sub_5_name': '',
                    'ug_sem_3_sub_5_marks_obtained': '',
                    'ug_sem_3_sub_5_total_marks': '',
                    'ug_sem_3_sub_6_name': '',
                    'ug_sem_3_sub_6_marks_obtained': '',
                    'ug_sem_3_sub_6_total_marks': '',
                    'ug_sem_3_sub_7_name': '',
                    'ug_sem_3_sub_7_marks_obtained': '',
                    'ug_sem_3_sub_7_total_marks': '',
                    'ug_sem_3_sub_8_name': '',
                    'ug_sem_3_sub_8_marks_obtained': '',
                    'ug_sem_3_sub_8_total_marks': '',
                    'ug_sem_3_sub_9_name': '',
                    'ug_sem_3_sub_9_marks_obtained': '',
                    'ug_sem_3_sub_9_total_marks': '',
                    'ug_sem_3_sub_10_name': '',
                    'ug_sem_3_sub_10_marks_obtained': '',
                    'ug_sem_3_sub_10_total_marks': '',
                    'ug_sem_3_sub_11_name': '',
                    'ug_sem_3_sub_11_marks_obtained': '',
                    'ug_sem_3_sub_11_total_marks': '',
                    'ug_sem_3_sub_12_name': '',
                    'ug_sem_3_sub_12_marks_obtained': '',
                    'ug_sem_3_sub_12_total_marks': '',
                    'ug_sem_3_sub_13_name': '',
                    'ug_sem_3_sub_13_marks_obtained': '',
                    'ug_sem_3_sub_13_total_marks': '',
                    'ug_sem_3_sub_14_name': '',
                    'ug_sem_3_sub_14_marks_obtained': '',
                    'ug_sem_3_sub_14_total_marks': '',
                    'ug_sem_3_sub_15_name': '',
                    'ug_sem_3_sub_15_marks_obtained': '',
                    'ug_sem_3_sub_15_total_marks': '',
                    'ug_sem_3_sub_16_name': '',
                    'ug_sem_3_sub_16_marks_obtained': '',
                    'ug_sem_3_sub_16_total_marks': '',
                    'ug_sem_3_sub_17_name': '',
                    'ug_sem_3_sub_17_marks_obtained': '',
                    'ug_sem_3_sub_17_total_marks': '',
                    'ug_sem_3_sub_18_name': '',
                    'ug_sem_3_sub_18_marks_obtained': '',
                    'ug_sem_3_sub_18_total_marks': '',
                    'ug_sem_3_sub_19_name': '',
                    'ug_sem_3_sub_19_marks_obtained': '',
                    'ug_sem_3_sub_19_total_marks': '',
                    'ug_sem_3_sub_20_name': '',
                    'ug_sem_3_sub_20_marks_obtained': '',
                    'ug_sem_3_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the ug_sem_3_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_3.html', ug_sem_3=ug_sem_3_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_ug_sem_3_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            ug_enrollment_no = request.form['ug_enrollment_no']
            ug_sem_3_session = request.form['ug_sem_3_session']
            ug_sem_3_roll_no = request.form['ug_sem_3_roll_no']
            ug_sem_3_result = request.form['ug_sem_3_result']
            ug_sem_3_sub_1_name = request.form['ug_sem_3_sub_1_name']
            ug_sem_3_sub_1_marks_obtained = request.form['ug_sem_3_sub_1_marks_obtained']
            ug_sem_3_sub_1_total_marks = request.form['ug_sem_3_sub_1_total_marks']
            ug_sem_3_sub_2_name = request.form['ug_sem_3_sub_2_name']
            ug_sem_3_sub_2_marks_obtained = request.form['ug_sem_3_sub_2_marks_obtained']
            ug_sem_3_sub_2_total_marks = request.form['ug_sem_3_sub_2_total_marks']
            ug_sem_3_sub_3_name = request.form['ug_sem_3_sub_3_name']
            ug_sem_3_sub_3_marks_obtained = request.form['ug_sem_3_sub_3_marks_obtained']
            ug_sem_3_sub_3_total_marks = request.form['ug_sem_3_sub_3_total_marks']
            ug_sem_3_sub_4_name = request.form['ug_sem_3_sub_4_name']
            ug_sem_3_sub_4_marks_obtained = request.form['ug_sem_3_sub_4_marks_obtained']
            ug_sem_3_sub_4_total_marks = request.form['ug_sem_3_sub_4_total_marks']
            ug_sem_3_sub_5_name = request.form['ug_sem_3_sub_5_name']
            ug_sem_3_sub_5_marks_obtained = request.form['ug_sem_3_sub_5_marks_obtained']
            ug_sem_3_sub_5_total_marks = request.form['ug_sem_3_sub_5_total_marks']
            ug_sem_3_sub_6_name = request.form['ug_sem_3_sub_6_name']
            ug_sem_3_sub_6_marks_obtained = request.form['ug_sem_3_sub_6_marks_obtained']
            ug_sem_3_sub_6_total_marks = request.form['ug_sem_3_sub_6_total_marks']
            ug_sem_3_sub_7_name = request.form['ug_sem_3_sub_7_name']
            ug_sem_3_sub_7_marks_obtained = request.form['ug_sem_3_sub_7_marks_obtained']
            ug_sem_3_sub_7_total_marks = request.form['ug_sem_3_sub_7_total_marks']
            ug_sem_3_sub_8_name = request.form['ug_sem_3_sub_8_name']
            ug_sem_3_sub_8_marks_obtained = request.form['ug_sem_3_sub_8_marks_obtained']
            ug_sem_3_sub_8_total_marks = request.form['ug_sem_3_sub_8_total_marks']
            ug_sem_3_sub_9_name = request.form['ug_sem_3_sub_9_name']
            ug_sem_3_sub_9_marks_obtained = request.form['ug_sem_3_sub_9_marks_obtained']
            ug_sem_3_sub_9_total_marks = request.form['ug_sem_3_sub_9_total_marks']
            ug_sem_3_sub_10_name = request.form['ug_sem_3_sub_10_name']
            ug_sem_3_sub_10_marks_obtained = request.form['ug_sem_3_sub_10_marks_obtained']
            ug_sem_3_sub_10_total_marks = request.form['ug_sem_3_sub_10_total_marks']
            ug_sem_3_sub_11_name = request.form['ug_sem_3_sub_11_name']
            ug_sem_3_sub_11_marks_obtained = request.form['ug_sem_3_sub_11_marks_obtained']
            ug_sem_3_sub_11_total_marks = request.form['ug_sem_3_sub_11_total_marks']
            ug_sem_3_sub_12_name = request.form['ug_sem_3_sub_12_name']
            ug_sem_3_sub_12_marks_obtained = request.form['ug_sem_3_sub_12_marks_obtained']
            ug_sem_3_sub_12_total_marks = request.form['ug_sem_3_sub_12_total_marks']
            ug_sem_3_sub_13_name = request.form['ug_sem_3_sub_13_name']
            ug_sem_3_sub_13_marks_obtained = request.form['ug_sem_3_sub_13_marks_obtained']
            ug_sem_3_sub_13_total_marks = request.form['ug_sem_3_sub_13_total_marks']
            ug_sem_3_sub_14_name = request.form['ug_sem_3_sub_14_name']
            ug_sem_3_sub_14_marks_obtained = request.form['ug_sem_3_sub_14_marks_obtained']
            ug_sem_3_sub_14_total_marks = request.form['ug_sem_3_sub_14_total_marks']
            ug_sem_3_sub_15_name = request.form['ug_sem_3_sub_15_name']
            ug_sem_3_sub_15_marks_obtained = request.form['ug_sem_3_sub_15_marks_obtained']
            ug_sem_3_sub_15_total_marks = request.form['ug_sem_3_sub_15_total_marks']
            ug_sem_3_sub_16_name = request.form['ug_sem_3_sub_16_name']
            ug_sem_3_sub_16_marks_obtained = request.form['ug_sem_3_sub_16_marks_obtained']
            ug_sem_3_sub_16_total_marks = request.form['ug_sem_3_sub_16_total_marks']
            ug_sem_3_sub_17_name = request.form['ug_sem_3_sub_17_name']
            ug_sem_3_sub_17_marks_obtained = request.form['ug_sem_3_sub_17_marks_obtained']
            ug_sem_3_sub_17_total_marks = request.form['ug_sem_3_sub_17_total_marks']
            ug_sem_3_sub_18_name = request.form['ug_sem_3_sub_18_name']
            ug_sem_3_sub_18_marks_obtained = request.form['ug_sem_3_sub_18_marks_obtained']
            ug_sem_3_sub_18_total_marks = request.form['ug_sem_3_sub_18_total_marks']
            ug_sem_3_sub_19_name = request.form['ug_sem_3_sub_19_name']
            ug_sem_3_sub_19_marks_obtained = request.form['ug_sem_3_sub_19_marks_obtained']
            ug_sem_3_sub_19_total_marks = request.form['ug_sem_3_sub_19_total_marks']
            ug_sem_3_sub_20_name = request.form['ug_sem_3_sub_20_name']
            ug_sem_3_sub_20_marks_obtained = request.form['ug_sem_3_sub_20_marks_obtained']
            ug_sem_3_sub_20_total_marks = request.form['ug_sem_3_sub_20_total_marks']


            # Update ug_sem_3_info in the database
            cursor.execute("""
                UPDATE ug_sem_3
                SET ug_enrollment_no = ?, ug_sem_3_session = ?, ug_sem_3_roll_no = ?, ug_sem_3_result = ?, ug_sem_3_sub_1_name = ?, ug_sem_3_sub_1_marks_obtained = ?, ug_sem_3_sub_1_total_marks = ?, ug_sem_3_sub_2_name = ?, ug_sem_3_sub_2_marks_obtained = ?, ug_sem_3_sub_2_total_marks = ?, ug_sem_3_sub_3_name = ?, ug_sem_3_sub_3_marks_obtained = ?, ug_sem_3_sub_3_total_marks = ?, ug_sem_3_sub_4_name = ?, ug_sem_3_sub_4_marks_obtained = ?, ug_sem_3_sub_4_total_marks = ?, ug_sem_3_sub_5_name = ?, ug_sem_3_sub_5_marks_obtained = ?, ug_sem_3_sub_5_total_marks = ?, ug_sem_3_sub_6_name = ?, ug_sem_3_sub_6_marks_obtained = ?, ug_sem_3_sub_6_total_marks = ?, ug_sem_3_sub_7_name = ?, ug_sem_3_sub_7_marks_obtained = ?, ug_sem_3_sub_7_total_marks = ?, ug_sem_3_sub_8_name = ?, ug_sem_3_sub_8_marks_obtained = ?, ug_sem_3_sub_8_total_marks = ?, ug_sem_3_sub_9_name = ?, ug_sem_3_sub_9_marks_obtained = ?, ug_sem_3_sub_9_total_marks = ?, ug_sem_3_sub_10_name = ?, ug_sem_3_sub_10_marks_obtained = ?, ug_sem_3_sub_10_total_marks = ?, ug_sem_3_sub_11_name = ?, ug_sem_3_sub_11_marks_obtained = ?, ug_sem_3_sub_11_total_marks = ?, ug_sem_3_sub_12_name = ?, ug_sem_3_sub_12_marks_obtained = ?, ug_sem_3_sub_12_total_marks = ?, ug_sem_3_sub_13_name = ?, ug_sem_3_sub_13_marks_obtained = ?, ug_sem_3_sub_13_total_marks = ?, ug_sem_3_sub_14_name = ?, ug_sem_3_sub_14_marks_obtained = ?, ug_sem_3_sub_14_total_marks = ?, ug_sem_3_sub_15_name = ?, ug_sem_3_sub_15_marks_obtained = ?, ug_sem_3_sub_15_total_marks = ?, ug_sem_3_sub_16_name = ?, ug_sem_3_sub_16_marks_obtained = ?, ug_sem_3_sub_16_total_marks = ?, ug_sem_3_sub_17_name = ?, ug_sem_3_sub_17_marks_obtained = ?, ug_sem_3_sub_17_total_marks = ?, ug_sem_3_sub_18_name = ?, ug_sem_3_sub_18_marks_obtained = ?, ug_sem_3_sub_18_total_marks = ?, ug_sem_3_sub_19_name = ?, ug_sem_3_sub_19_marks_obtained = ?, ug_sem_3_sub_19_total_marks = ?, ug_sem_3_sub_20_name = ?, ug_sem_3_sub_20_marks_obtained = ?, ug_sem_3_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(ug_enrollment_no,ug_sem_3_session,ug_sem_3_roll_no,ug_sem_3_result,ug_sem_3_sub_1_name,
                 ug_sem_3_sub_1_marks_obtained,ug_sem_3_sub_1_total_marks,ug_sem_3_sub_2_name,
                 ug_sem_3_sub_2_marks_obtained,ug_sem_3_sub_2_total_marks,ug_sem_3_sub_3_name,
                 ug_sem_3_sub_3_marks_obtained,ug_sem_3_sub_3_total_marks,ug_sem_3_sub_4_name,
                 ug_sem_3_sub_4_marks_obtained,ug_sem_3_sub_4_total_marks,ug_sem_3_sub_5_name,
                 ug_sem_3_sub_5_marks_obtained,ug_sem_3_sub_5_total_marks,ug_sem_3_sub_6_name,
                 ug_sem_3_sub_6_marks_obtained,ug_sem_3_sub_6_total_marks,ug_sem_3_sub_7_name,
                 ug_sem_3_sub_7_marks_obtained,ug_sem_3_sub_7_total_marks,ug_sem_3_sub_8_name,
                 ug_sem_3_sub_8_marks_obtained,ug_sem_3_sub_8_total_marks,ug_sem_3_sub_9_name,
                 ug_sem_3_sub_9_marks_obtained,ug_sem_3_sub_9_total_marks,ug_sem_3_sub_10_name,
                 ug_sem_3_sub_10_marks_obtained,ug_sem_3_sub_10_total_marks,ug_sem_3_sub_11_name,
                 ug_sem_3_sub_11_marks_obtained,ug_sem_3_sub_11_total_marks,ug_sem_3_sub_12_name,
                 ug_sem_3_sub_12_marks_obtained,ug_sem_3_sub_12_total_marks,ug_sem_3_sub_13_name,
                 ug_sem_3_sub_13_marks_obtained,ug_sem_3_sub_13_total_marks,ug_sem_3_sub_14_name,
                 ug_sem_3_sub_14_marks_obtained,ug_sem_3_sub_14_total_marks,ug_sem_3_sub_15_name,
                 ug_sem_3_sub_15_marks_obtained,ug_sem_3_sub_15_total_marks,ug_sem_3_sub_16_name,
                 ug_sem_3_sub_16_marks_obtained,ug_sem_3_sub_16_total_marks,ug_sem_3_sub_17_name,
                 ug_sem_3_sub_17_marks_obtained,ug_sem_3_sub_17_total_marks,ug_sem_3_sub_18_name,
                 ug_sem_3_sub_18_marks_obtained,ug_sem_3_sub_18_total_marks,ug_sem_3_sub_19_name,
                 ug_sem_3_sub_19_marks_obtained,ug_sem_3_sub_19_total_marks,ug_sem_3_sub_20_name,
                 ug_sem_3_sub_20_marks_obtained,ug_sem_3_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_ug_sem_4'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch ug_sem_3_info from the database
            cursor.execute("SELECT * FROM ug_sem_3 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_3_info = cursor.fetchone()

            # Pass the ug_sem_3_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_3.html', ug_sem_3=ug_sem_3_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_ug_sem_4', methods=['GET', 'POST'])
def form_ug_sem_4():
    try:
        if request.method == 'POST':
            return form_ug_sem_4_post()
        else:
            # Fetch ug_sem_4_info from the database
            cursor.execute("SELECT * FROM ug_sem_4 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_4_info = cursor.fetchone()

            # If ug_sem_4_info is None, create a default ug_sem_4_info object
            if ug_sem_4_info is None:
                ug_sem_4_info = {
                    'ug_enrollment_no': '',
                    'ug_sem_4_session': '',
                    'ug_sem_4_roll_no': '',
                    'ug_sem_4_result': '',
                    'ug_sem_4_sub_1_name': '',
                    'ug_sem_4_sub_1_marks_obtained': '',
                    'ug_sem_4_sub_1_total_marks': '',
                    'ug_sem_4_sub_2_name': '',
                    'ug_sem_4_sub_2_marks_obtained': '',
                    'ug_sem_4_sub_2_total_marks': '',
                    'ug_sem_4_sub_3_name': '',
                    'ug_sem_4_sub_3_marks_obtained': '',
                    'ug_sem_4_sub_3_total_marks': '',
                    'ug_sem_4_sub_4_name': '',
                    'ug_sem_4_sub_4_marks_obtained': '',
                    'ug_sem_4_sub_4_total_marks': '',
                    'ug_sem_4_sub_5_name': '',
                    'ug_sem_4_sub_5_marks_obtained': '',
                    'ug_sem_4_sub_5_total_marks': '',
                    'ug_sem_4_sub_6_name': '',
                    'ug_sem_4_sub_6_marks_obtained': '',
                    'ug_sem_4_sub_6_total_marks': '',
                    'ug_sem_4_sub_7_name': '',
                    'ug_sem_4_sub_7_marks_obtained': '',
                    'ug_sem_4_sub_7_total_marks': '',
                    'ug_sem_4_sub_8_name': '',
                    'ug_sem_4_sub_8_marks_obtained': '',
                    'ug_sem_4_sub_8_total_marks': '',
                    'ug_sem_4_sub_9_name': '',
                    'ug_sem_4_sub_9_marks_obtained': '',
                    'ug_sem_4_sub_9_total_marks': '',
                    'ug_sem_4_sub_10_name': '',
                    'ug_sem_4_sub_10_marks_obtained': '',
                    'ug_sem_4_sub_10_total_marks': '',
                    'ug_sem_4_sub_11_name': '',
                    'ug_sem_4_sub_11_marks_obtained': '',
                    'ug_sem_4_sub_11_total_marks': '',
                    'ug_sem_4_sub_12_name': '',
                    'ug_sem_4_sub_12_marks_obtained': '',
                    'ug_sem_4_sub_12_total_marks': '',
                    'ug_sem_4_sub_13_name': '',
                    'ug_sem_4_sub_13_marks_obtained': '',
                    'ug_sem_4_sub_13_total_marks': '',
                    'ug_sem_4_sub_14_name': '',
                    'ug_sem_4_sub_14_marks_obtained': '',
                    'ug_sem_4_sub_14_total_marks': '',
                    'ug_sem_4_sub_15_name': '',
                    'ug_sem_4_sub_15_marks_obtained': '',
                    'ug_sem_4_sub_15_total_marks': '',
                    'ug_sem_4_sub_16_name': '',
                    'ug_sem_4_sub_16_marks_obtained': '',
                    'ug_sem_4_sub_16_total_marks': '',
                    'ug_sem_4_sub_17_name': '',
                    'ug_sem_4_sub_17_marks_obtained': '',
                    'ug_sem_4_sub_17_total_marks': '',
                    'ug_sem_4_sub_18_name': '',
                    'ug_sem_4_sub_18_marks_obtained': '',
                    'ug_sem_4_sub_18_total_marks': '',
                    'ug_sem_4_sub_19_name': '',
                    'ug_sem_4_sub_19_marks_obtained': '',
                    'ug_sem_4_sub_19_total_marks': '',
                    'ug_sem_4_sub_20_name': '',
                    'ug_sem_4_sub_20_marks_obtained': '',
                    'ug_sem_4_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the ug_sem_4_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_4.html', ug_sem_4=ug_sem_4_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_ug_sem_4_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            ug_enrollment_no = request.form['ug_enrollment_no']
            ug_sem_4_session = request.form['ug_sem_4_session']
            ug_sem_4_roll_no = request.form['ug_sem_4_roll_no']
            ug_sem_4_result = request.form['ug_sem_4_result']
            ug_sem_4_sub_1_name = request.form['ug_sem_4_sub_1_name']
            ug_sem_4_sub_1_marks_obtained = request.form['ug_sem_4_sub_1_marks_obtained']
            ug_sem_4_sub_1_total_marks = request.form['ug_sem_4_sub_1_total_marks']
            ug_sem_4_sub_2_name = request.form['ug_sem_4_sub_2_name']
            ug_sem_4_sub_2_marks_obtained = request.form['ug_sem_4_sub_2_marks_obtained']
            ug_sem_4_sub_2_total_marks = request.form['ug_sem_4_sub_2_total_marks']
            ug_sem_4_sub_3_name = request.form['ug_sem_4_sub_3_name']
            ug_sem_4_sub_3_marks_obtained = request.form['ug_sem_4_sub_3_marks_obtained']
            ug_sem_4_sub_3_total_marks = request.form['ug_sem_4_sub_3_total_marks']
            ug_sem_4_sub_4_name = request.form['ug_sem_4_sub_4_name']
            ug_sem_4_sub_4_marks_obtained = request.form['ug_sem_4_sub_4_marks_obtained']
            ug_sem_4_sub_4_total_marks = request.form['ug_sem_4_sub_4_total_marks']
            ug_sem_4_sub_5_name = request.form['ug_sem_4_sub_5_name']
            ug_sem_4_sub_5_marks_obtained = request.form['ug_sem_4_sub_5_marks_obtained']
            ug_sem_4_sub_5_total_marks = request.form['ug_sem_4_sub_5_total_marks']
            ug_sem_4_sub_6_name = request.form['ug_sem_4_sub_6_name']
            ug_sem_4_sub_6_marks_obtained = request.form['ug_sem_4_sub_6_marks_obtained']
            ug_sem_4_sub_6_total_marks = request.form['ug_sem_4_sub_6_total_marks']
            ug_sem_4_sub_7_name = request.form['ug_sem_4_sub_7_name']
            ug_sem_4_sub_7_marks_obtained = request.form['ug_sem_4_sub_7_marks_obtained']
            ug_sem_4_sub_7_total_marks = request.form['ug_sem_4_sub_7_total_marks']
            ug_sem_4_sub_8_name = request.form['ug_sem_4_sub_8_name']
            ug_sem_4_sub_8_marks_obtained = request.form['ug_sem_4_sub_8_marks_obtained']
            ug_sem_4_sub_8_total_marks = request.form['ug_sem_4_sub_8_total_marks']
            ug_sem_4_sub_9_name = request.form['ug_sem_4_sub_9_name']
            ug_sem_4_sub_9_marks_obtained = request.form['ug_sem_4_sub_9_marks_obtained']
            ug_sem_4_sub_9_total_marks = request.form['ug_sem_4_sub_9_total_marks']
            ug_sem_4_sub_10_name = request.form['ug_sem_4_sub_10_name']
            ug_sem_4_sub_10_marks_obtained = request.form['ug_sem_4_sub_10_marks_obtained']
            ug_sem_4_sub_10_total_marks = request.form['ug_sem_4_sub_10_total_marks']
            ug_sem_4_sub_11_name = request.form['ug_sem_4_sub_11_name']
            ug_sem_4_sub_11_marks_obtained = request.form['ug_sem_4_sub_11_marks_obtained']
            ug_sem_4_sub_11_total_marks = request.form['ug_sem_4_sub_11_total_marks']
            ug_sem_4_sub_12_name = request.form['ug_sem_4_sub_12_name']
            ug_sem_4_sub_12_marks_obtained = request.form['ug_sem_4_sub_12_marks_obtained']
            ug_sem_4_sub_12_total_marks = request.form['ug_sem_4_sub_12_total_marks']
            ug_sem_4_sub_13_name = request.form['ug_sem_4_sub_13_name']
            ug_sem_4_sub_13_marks_obtained = request.form['ug_sem_4_sub_13_marks_obtained']
            ug_sem_4_sub_13_total_marks = request.form['ug_sem_4_sub_13_total_marks']
            ug_sem_4_sub_14_name = request.form['ug_sem_4_sub_14_name']
            ug_sem_4_sub_14_marks_obtained = request.form['ug_sem_4_sub_14_marks_obtained']
            ug_sem_4_sub_14_total_marks = request.form['ug_sem_4_sub_14_total_marks']
            ug_sem_4_sub_15_name = request.form['ug_sem_4_sub_15_name']
            ug_sem_4_sub_15_marks_obtained = request.form['ug_sem_4_sub_15_marks_obtained']
            ug_sem_4_sub_15_total_marks = request.form['ug_sem_4_sub_15_total_marks']
            ug_sem_4_sub_16_name = request.form['ug_sem_4_sub_16_name']
            ug_sem_4_sub_16_marks_obtained = request.form['ug_sem_4_sub_16_marks_obtained']
            ug_sem_4_sub_16_total_marks = request.form['ug_sem_4_sub_16_total_marks']
            ug_sem_4_sub_17_name = request.form['ug_sem_4_sub_17_name']
            ug_sem_4_sub_17_marks_obtained = request.form['ug_sem_4_sub_17_marks_obtained']
            ug_sem_4_sub_17_total_marks = request.form['ug_sem_4_sub_17_total_marks']
            ug_sem_4_sub_18_name = request.form['ug_sem_4_sub_18_name']
            ug_sem_4_sub_18_marks_obtained = request.form['ug_sem_4_sub_18_marks_obtained']
            ug_sem_4_sub_18_total_marks = request.form['ug_sem_4_sub_18_total_marks']
            ug_sem_4_sub_19_name = request.form['ug_sem_4_sub_19_name']
            ug_sem_4_sub_19_marks_obtained = request.form['ug_sem_4_sub_19_marks_obtained']
            ug_sem_4_sub_19_total_marks = request.form['ug_sem_4_sub_19_total_marks']
            ug_sem_4_sub_20_name = request.form['ug_sem_4_sub_20_name']
            ug_sem_4_sub_20_marks_obtained = request.form['ug_sem_4_sub_20_marks_obtained']
            ug_sem_4_sub_20_total_marks = request.form['ug_sem_4_sub_20_total_marks']


            # Update ug_sem_4_info in the database
            cursor.execute("""
                UPDATE ug_sem_4
                SET ug_enrollment_no = ?, ug_sem_4_session = ?, ug_sem_4_roll_no = ?, ug_sem_4_result = ?, ug_sem_4_sub_1_name = ?, ug_sem_4_sub_1_marks_obtained = ?, ug_sem_4_sub_1_total_marks = ?, ug_sem_4_sub_2_name = ?, ug_sem_4_sub_2_marks_obtained = ?, ug_sem_4_sub_2_total_marks = ?, ug_sem_4_sub_3_name = ?, ug_sem_4_sub_3_marks_obtained = ?, ug_sem_4_sub_3_total_marks = ?, ug_sem_4_sub_4_name = ?, ug_sem_4_sub_4_marks_obtained = ?, ug_sem_4_sub_4_total_marks = ?, ug_sem_4_sub_5_name = ?, ug_sem_4_sub_5_marks_obtained = ?, ug_sem_4_sub_5_total_marks = ?, ug_sem_4_sub_6_name = ?, ug_sem_4_sub_6_marks_obtained = ?, ug_sem_4_sub_6_total_marks = ?, ug_sem_4_sub_7_name = ?, ug_sem_4_sub_7_marks_obtained = ?, ug_sem_4_sub_7_total_marks = ?, ug_sem_4_sub_8_name = ?, ug_sem_4_sub_8_marks_obtained = ?, ug_sem_4_sub_8_total_marks = ?, ug_sem_4_sub_9_name = ?, ug_sem_4_sub_9_marks_obtained = ?, ug_sem_4_sub_9_total_marks = ?, ug_sem_4_sub_10_name = ?, ug_sem_4_sub_10_marks_obtained = ?, ug_sem_4_sub_10_total_marks = ?, ug_sem_4_sub_11_name = ?, ug_sem_4_sub_11_marks_obtained = ?, ug_sem_4_sub_11_total_marks = ?, ug_sem_4_sub_12_name = ?, ug_sem_4_sub_12_marks_obtained = ?, ug_sem_4_sub_12_total_marks = ?, ug_sem_4_sub_13_name = ?, ug_sem_4_sub_13_marks_obtained = ?, ug_sem_4_sub_13_total_marks = ?, ug_sem_4_sub_14_name = ?, ug_sem_4_sub_14_marks_obtained = ?, ug_sem_4_sub_14_total_marks = ?, ug_sem_4_sub_15_name = ?, ug_sem_4_sub_15_marks_obtained = ?, ug_sem_4_sub_15_total_marks = ?, ug_sem_4_sub_16_name = ?, ug_sem_4_sub_16_marks_obtained = ?, ug_sem_4_sub_16_total_marks = ?, ug_sem_4_sub_17_name = ?, ug_sem_4_sub_17_marks_obtained = ?, ug_sem_4_sub_17_total_marks = ?, ug_sem_4_sub_18_name = ?, ug_sem_4_sub_18_marks_obtained = ?, ug_sem_4_sub_18_total_marks = ?, ug_sem_4_sub_19_name = ?, ug_sem_4_sub_19_marks_obtained = ?, ug_sem_4_sub_19_total_marks = ?, ug_sem_4_sub_20_name = ?, ug_sem_4_sub_20_marks_obtained = ?, ug_sem_4_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(ug_enrollment_no,ug_sem_4_session,ug_sem_4_roll_no,ug_sem_4_result,ug_sem_4_sub_1_name,
                 ug_sem_4_sub_1_marks_obtained,ug_sem_4_sub_1_total_marks,ug_sem_4_sub_2_name,
                 ug_sem_4_sub_2_marks_obtained,ug_sem_4_sub_2_total_marks,ug_sem_4_sub_3_name,
                 ug_sem_4_sub_3_marks_obtained,ug_sem_4_sub_3_total_marks,ug_sem_4_sub_4_name,
                 ug_sem_4_sub_4_marks_obtained,ug_sem_4_sub_4_total_marks,ug_sem_4_sub_5_name,
                 ug_sem_4_sub_5_marks_obtained,ug_sem_4_sub_5_total_marks,ug_sem_4_sub_6_name,
                 ug_sem_4_sub_6_marks_obtained,ug_sem_4_sub_6_total_marks,ug_sem_4_sub_7_name,
                 ug_sem_4_sub_7_marks_obtained,ug_sem_4_sub_7_total_marks,ug_sem_4_sub_8_name,
                 ug_sem_4_sub_8_marks_obtained,ug_sem_4_sub_8_total_marks,ug_sem_4_sub_9_name,
                 ug_sem_4_sub_9_marks_obtained,ug_sem_4_sub_9_total_marks,ug_sem_4_sub_10_name,
                 ug_sem_4_sub_10_marks_obtained,ug_sem_4_sub_10_total_marks,ug_sem_4_sub_11_name,
                 ug_sem_4_sub_11_marks_obtained,ug_sem_4_sub_11_total_marks,ug_sem_4_sub_12_name,
                 ug_sem_4_sub_12_marks_obtained,ug_sem_4_sub_12_total_marks,ug_sem_4_sub_13_name,
                 ug_sem_4_sub_13_marks_obtained,ug_sem_4_sub_13_total_marks,ug_sem_4_sub_14_name,
                 ug_sem_4_sub_14_marks_obtained,ug_sem_4_sub_14_total_marks,ug_sem_4_sub_15_name,
                 ug_sem_4_sub_15_marks_obtained,ug_sem_4_sub_15_total_marks,ug_sem_4_sub_16_name,
                 ug_sem_4_sub_16_marks_obtained,ug_sem_4_sub_16_total_marks,ug_sem_4_sub_17_name,
                 ug_sem_4_sub_17_marks_obtained,ug_sem_4_sub_17_total_marks,ug_sem_4_sub_18_name,
                 ug_sem_4_sub_18_marks_obtained,ug_sem_4_sub_18_total_marks,ug_sem_4_sub_19_name,
                 ug_sem_4_sub_19_marks_obtained,ug_sem_4_sub_19_total_marks,ug_sem_4_sub_20_name,
                 ug_sem_4_sub_20_marks_obtained,ug_sem_4_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_ug_sem_5'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch ug_sem_4_info from the database
            cursor.execute("SELECT * FROM ug_sem_4 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_4_info = cursor.fetchone()

            # Pass the ug_sem_4_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_4.html', ug_sem_4=ug_sem_4_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_ug_sem_5', methods=['GET', 'POST'])
def form_ug_sem_5():
    try:
        if request.method == 'POST':
            return form_ug_sem_5_post()
        else:
            # Fetch ug_sem_5_info from the database
            cursor.execute("SELECT * FROM ug_sem_5 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_5_info = cursor.fetchone()

            # If ug_sem_5_info is None, create a default ug_sem_5_info object
            if ug_sem_5_info is None:
                ug_sem_5_info = {
                    'ug_enrollment_no': '',
                    'ug_sem_5_session': '',
                    'ug_sem_5_roll_no': '',
                    'ug_sem_5_result': '',
                    'ug_sem_5_sub_1_name': '',
                    'ug_sem_5_sub_1_marks_obtained': '',
                    'ug_sem_5_sub_1_total_marks': '',
                    'ug_sem_5_sub_2_name': '',
                    'ug_sem_5_sub_2_marks_obtained': '',
                    'ug_sem_5_sub_2_total_marks': '',
                    'ug_sem_5_sub_3_name': '',
                    'ug_sem_5_sub_3_marks_obtained': '',
                    'ug_sem_5_sub_3_total_marks': '',
                    'ug_sem_5_sub_4_name': '',
                    'ug_sem_5_sub_4_marks_obtained': '',
                    'ug_sem_5_sub_4_total_marks': '',
                    'ug_sem_5_sub_5_name': '',
                    'ug_sem_5_sub_5_marks_obtained': '',
                    'ug_sem_5_sub_5_total_marks': '',
                    'ug_sem_5_sub_6_name': '',
                    'ug_sem_5_sub_6_marks_obtained': '',
                    'ug_sem_5_sub_6_total_marks': '',
                    'ug_sem_5_sub_7_name': '',
                    'ug_sem_5_sub_7_marks_obtained': '',
                    'ug_sem_5_sub_7_total_marks': '',
                    'ug_sem_5_sub_8_name': '',
                    'ug_sem_5_sub_8_marks_obtained': '',
                    'ug_sem_5_sub_8_total_marks': '',
                    'ug_sem_5_sub_9_name': '',
                    'ug_sem_5_sub_9_marks_obtained': '',
                    'ug_sem_5_sub_9_total_marks': '',
                    'ug_sem_5_sub_10_name': '',
                    'ug_sem_5_sub_10_marks_obtained': '',
                    'ug_sem_5_sub_10_total_marks': '',
                    'ug_sem_5_sub_11_name': '',
                    'ug_sem_5_sub_11_marks_obtained': '',
                    'ug_sem_5_sub_11_total_marks': '',
                    'ug_sem_5_sub_12_name': '',
                    'ug_sem_5_sub_12_marks_obtained': '',
                    'ug_sem_5_sub_12_total_marks': '',
                    'ug_sem_5_sub_13_name': '',
                    'ug_sem_5_sub_13_marks_obtained': '',
                    'ug_sem_5_sub_13_total_marks': '',
                    'ug_sem_5_sub_14_name': '',
                    'ug_sem_5_sub_14_marks_obtained': '',
                    'ug_sem_5_sub_14_total_marks': '',
                    'ug_sem_5_sub_15_name': '',
                    'ug_sem_5_sub_15_marks_obtained': '',
                    'ug_sem_5_sub_15_total_marks': '',
                    'ug_sem_5_sub_16_name': '',
                    'ug_sem_5_sub_16_marks_obtained': '',
                    'ug_sem_5_sub_16_total_marks': '',
                    'ug_sem_5_sub_17_name': '',
                    'ug_sem_5_sub_17_marks_obtained': '',
                    'ug_sem_5_sub_17_total_marks': '',
                    'ug_sem_5_sub_18_name': '',
                    'ug_sem_5_sub_18_marks_obtained': '',
                    'ug_sem_5_sub_18_total_marks': '',
                    'ug_sem_5_sub_19_name': '',
                    'ug_sem_5_sub_19_marks_obtained': '',
                    'ug_sem_5_sub_19_total_marks': '',
                    'ug_sem_5_sub_20_name': '',
                    'ug_sem_5_sub_20_marks_obtained': '',
                    'ug_sem_5_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the ug_sem_5_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_5.html', ug_sem_5=ug_sem_5_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_ug_sem_5_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            ug_enrollment_no = request.form['ug_enrollment_no']
            ug_sem_5_session = request.form['ug_sem_5_session']
            ug_sem_5_roll_no = request.form['ug_sem_5_roll_no']
            ug_sem_5_result = request.form['ug_sem_5_result']
            ug_sem_5_sub_1_name = request.form['ug_sem_5_sub_1_name']
            ug_sem_5_sub_1_marks_obtained = request.form['ug_sem_5_sub_1_marks_obtained']
            ug_sem_5_sub_1_total_marks = request.form['ug_sem_5_sub_1_total_marks']
            ug_sem_5_sub_2_name = request.form['ug_sem_5_sub_2_name']
            ug_sem_5_sub_2_marks_obtained = request.form['ug_sem_5_sub_2_marks_obtained']
            ug_sem_5_sub_2_total_marks = request.form['ug_sem_5_sub_2_total_marks']
            ug_sem_5_sub_3_name = request.form['ug_sem_5_sub_3_name']
            ug_sem_5_sub_3_marks_obtained = request.form['ug_sem_5_sub_3_marks_obtained']
            ug_sem_5_sub_3_total_marks = request.form['ug_sem_5_sub_3_total_marks']
            ug_sem_5_sub_4_name = request.form['ug_sem_5_sub_4_name']
            ug_sem_5_sub_4_marks_obtained = request.form['ug_sem_5_sub_4_marks_obtained']
            ug_sem_5_sub_4_total_marks = request.form['ug_sem_5_sub_4_total_marks']
            ug_sem_5_sub_5_name = request.form['ug_sem_5_sub_5_name']
            ug_sem_5_sub_5_marks_obtained = request.form['ug_sem_5_sub_5_marks_obtained']
            ug_sem_5_sub_5_total_marks = request.form['ug_sem_5_sub_5_total_marks']
            ug_sem_5_sub_6_name = request.form['ug_sem_5_sub_6_name']
            ug_sem_5_sub_6_marks_obtained = request.form['ug_sem_5_sub_6_marks_obtained']
            ug_sem_5_sub_6_total_marks = request.form['ug_sem_5_sub_6_total_marks']
            ug_sem_5_sub_7_name = request.form['ug_sem_5_sub_7_name']
            ug_sem_5_sub_7_marks_obtained = request.form['ug_sem_5_sub_7_marks_obtained']
            ug_sem_5_sub_7_total_marks = request.form['ug_sem_5_sub_7_total_marks']
            ug_sem_5_sub_8_name = request.form['ug_sem_5_sub_8_name']
            ug_sem_5_sub_8_marks_obtained = request.form['ug_sem_5_sub_8_marks_obtained']
            ug_sem_5_sub_8_total_marks = request.form['ug_sem_5_sub_8_total_marks']
            ug_sem_5_sub_9_name = request.form['ug_sem_5_sub_9_name']
            ug_sem_5_sub_9_marks_obtained = request.form['ug_sem_5_sub_9_marks_obtained']
            ug_sem_5_sub_9_total_marks = request.form['ug_sem_5_sub_9_total_marks']
            ug_sem_5_sub_10_name = request.form['ug_sem_5_sub_10_name']
            ug_sem_5_sub_10_marks_obtained = request.form['ug_sem_5_sub_10_marks_obtained']
            ug_sem_5_sub_10_total_marks = request.form['ug_sem_5_sub_10_total_marks']
            ug_sem_5_sub_11_name = request.form['ug_sem_5_sub_11_name']
            ug_sem_5_sub_11_marks_obtained = request.form['ug_sem_5_sub_11_marks_obtained']
            ug_sem_5_sub_11_total_marks = request.form['ug_sem_5_sub_11_total_marks']
            ug_sem_5_sub_12_name = request.form['ug_sem_5_sub_12_name']
            ug_sem_5_sub_12_marks_obtained = request.form['ug_sem_5_sub_12_marks_obtained']
            ug_sem_5_sub_12_total_marks = request.form['ug_sem_5_sub_12_total_marks']
            ug_sem_5_sub_13_name = request.form['ug_sem_5_sub_13_name']
            ug_sem_5_sub_13_marks_obtained = request.form['ug_sem_5_sub_13_marks_obtained']
            ug_sem_5_sub_13_total_marks = request.form['ug_sem_5_sub_13_total_marks']
            ug_sem_5_sub_14_name = request.form['ug_sem_5_sub_14_name']
            ug_sem_5_sub_14_marks_obtained = request.form['ug_sem_5_sub_14_marks_obtained']
            ug_sem_5_sub_14_total_marks = request.form['ug_sem_5_sub_14_total_marks']
            ug_sem_5_sub_15_name = request.form['ug_sem_5_sub_15_name']
            ug_sem_5_sub_15_marks_obtained = request.form['ug_sem_5_sub_15_marks_obtained']
            ug_sem_5_sub_15_total_marks = request.form['ug_sem_5_sub_15_total_marks']
            ug_sem_5_sub_16_name = request.form['ug_sem_5_sub_16_name']
            ug_sem_5_sub_16_marks_obtained = request.form['ug_sem_5_sub_16_marks_obtained']
            ug_sem_5_sub_16_total_marks = request.form['ug_sem_5_sub_16_total_marks']
            ug_sem_5_sub_17_name = request.form['ug_sem_5_sub_17_name']
            ug_sem_5_sub_17_marks_obtained = request.form['ug_sem_5_sub_17_marks_obtained']
            ug_sem_5_sub_17_total_marks = request.form['ug_sem_5_sub_17_total_marks']
            ug_sem_5_sub_18_name = request.form['ug_sem_5_sub_18_name']
            ug_sem_5_sub_18_marks_obtained = request.form['ug_sem_5_sub_18_marks_obtained']
            ug_sem_5_sub_18_total_marks = request.form['ug_sem_5_sub_18_total_marks']
            ug_sem_5_sub_19_name = request.form['ug_sem_5_sub_19_name']
            ug_sem_5_sub_19_marks_obtained = request.form['ug_sem_5_sub_19_marks_obtained']
            ug_sem_5_sub_19_total_marks = request.form['ug_sem_5_sub_19_total_marks']
            ug_sem_5_sub_20_name = request.form['ug_sem_5_sub_20_name']
            ug_sem_5_sub_20_marks_obtained = request.form['ug_sem_5_sub_20_marks_obtained']
            ug_sem_5_sub_20_total_marks = request.form['ug_sem_5_sub_20_total_marks']


            # Update ug_sem_5_info in the database
            cursor.execute("""
                UPDATE ug_sem_5
                SET ug_enrollment_no = ?, ug_sem_5_session = ?, ug_sem_5_roll_no = ?, ug_sem_5_result = ?, ug_sem_5_sub_1_name = ?, ug_sem_5_sub_1_marks_obtained = ?, ug_sem_5_sub_1_total_marks = ?, ug_sem_5_sub_2_name = ?, ug_sem_5_sub_2_marks_obtained = ?, ug_sem_5_sub_2_total_marks = ?, ug_sem_5_sub_3_name = ?, ug_sem_5_sub_3_marks_obtained = ?, ug_sem_5_sub_3_total_marks = ?, ug_sem_5_sub_4_name = ?, ug_sem_5_sub_4_marks_obtained = ?, ug_sem_5_sub_4_total_marks = ?, ug_sem_5_sub_5_name = ?, ug_sem_5_sub_5_marks_obtained = ?, ug_sem_5_sub_5_total_marks = ?, ug_sem_5_sub_6_name = ?, ug_sem_5_sub_6_marks_obtained = ?, ug_sem_5_sub_6_total_marks = ?, ug_sem_5_sub_7_name = ?, ug_sem_5_sub_7_marks_obtained = ?, ug_sem_5_sub_7_total_marks = ?, ug_sem_5_sub_8_name = ?, ug_sem_5_sub_8_marks_obtained = ?, ug_sem_5_sub_8_total_marks = ?, ug_sem_5_sub_9_name = ?, ug_sem_5_sub_9_marks_obtained = ?, ug_sem_5_sub_9_total_marks = ?, ug_sem_5_sub_10_name = ?, ug_sem_5_sub_10_marks_obtained = ?, ug_sem_5_sub_10_total_marks = ?, ug_sem_5_sub_11_name = ?, ug_sem_5_sub_11_marks_obtained = ?, ug_sem_5_sub_11_total_marks = ?, ug_sem_5_sub_12_name = ?, ug_sem_5_sub_12_marks_obtained = ?, ug_sem_5_sub_12_total_marks = ?, ug_sem_5_sub_13_name = ?, ug_sem_5_sub_13_marks_obtained = ?, ug_sem_5_sub_13_total_marks = ?, ug_sem_5_sub_14_name = ?, ug_sem_5_sub_14_marks_obtained = ?, ug_sem_5_sub_14_total_marks = ?, ug_sem_5_sub_15_name = ?, ug_sem_5_sub_15_marks_obtained = ?, ug_sem_5_sub_15_total_marks = ?, ug_sem_5_sub_16_name = ?, ug_sem_5_sub_16_marks_obtained = ?, ug_sem_5_sub_16_total_marks = ?, ug_sem_5_sub_17_name = ?, ug_sem_5_sub_17_marks_obtained = ?, ug_sem_5_sub_17_total_marks = ?, ug_sem_5_sub_18_name = ?, ug_sem_5_sub_18_marks_obtained = ?, ug_sem_5_sub_18_total_marks = ?, ug_sem_5_sub_19_name = ?, ug_sem_5_sub_19_marks_obtained = ?, ug_sem_5_sub_19_total_marks = ?, ug_sem_5_sub_20_name = ?, ug_sem_5_sub_20_marks_obtained = ?, ug_sem_5_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(ug_enrollment_no,ug_sem_5_session,ug_sem_5_roll_no,ug_sem_5_result,ug_sem_5_sub_1_name,
                 ug_sem_5_sub_1_marks_obtained,ug_sem_5_sub_1_total_marks,ug_sem_5_sub_2_name,
                 ug_sem_5_sub_2_marks_obtained,ug_sem_5_sub_2_total_marks,ug_sem_5_sub_3_name,
                 ug_sem_5_sub_3_marks_obtained,ug_sem_5_sub_3_total_marks,ug_sem_5_sub_4_name,
                 ug_sem_5_sub_4_marks_obtained,ug_sem_5_sub_4_total_marks,ug_sem_5_sub_5_name,
                 ug_sem_5_sub_5_marks_obtained,ug_sem_5_sub_5_total_marks,ug_sem_5_sub_6_name,
                 ug_sem_5_sub_6_marks_obtained,ug_sem_5_sub_6_total_marks,ug_sem_5_sub_7_name,
                 ug_sem_5_sub_7_marks_obtained,ug_sem_5_sub_7_total_marks,ug_sem_5_sub_8_name,
                 ug_sem_5_sub_8_marks_obtained,ug_sem_5_sub_8_total_marks,ug_sem_5_sub_9_name,
                 ug_sem_5_sub_9_marks_obtained,ug_sem_5_sub_9_total_marks,ug_sem_5_sub_10_name,
                 ug_sem_5_sub_10_marks_obtained,ug_sem_5_sub_10_total_marks,ug_sem_5_sub_11_name,
                 ug_sem_5_sub_11_marks_obtained,ug_sem_5_sub_11_total_marks,ug_sem_5_sub_12_name,
                 ug_sem_5_sub_12_marks_obtained,ug_sem_5_sub_12_total_marks,ug_sem_5_sub_13_name,
                 ug_sem_5_sub_13_marks_obtained,ug_sem_5_sub_13_total_marks,ug_sem_5_sub_14_name,
                 ug_sem_5_sub_14_marks_obtained,ug_sem_5_sub_14_total_marks,ug_sem_5_sub_15_name,
                 ug_sem_5_sub_15_marks_obtained,ug_sem_5_sub_15_total_marks,ug_sem_5_sub_16_name,
                 ug_sem_5_sub_16_marks_obtained,ug_sem_5_sub_16_total_marks,ug_sem_5_sub_17_name,
                 ug_sem_5_sub_17_marks_obtained,ug_sem_5_sub_17_total_marks,ug_sem_5_sub_18_name,
                 ug_sem_5_sub_18_marks_obtained,ug_sem_5_sub_18_total_marks,ug_sem_5_sub_19_name,
                 ug_sem_5_sub_19_marks_obtained,ug_sem_5_sub_19_total_marks,ug_sem_5_sub_20_name,
                 ug_sem_5_sub_20_marks_obtained,ug_sem_5_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_ug_sem_6'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch ug_sem_5_info from the database
            cursor.execute("SELECT * FROM ug_sem_5 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_5_info = cursor.fetchone()

            # Pass the ug_sem_5_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_5.html', ug_sem_5=ug_sem_5_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_ug_sem_6', methods=['GET', 'POST'])
def form_ug_sem_6():
    try:
        if request.method == 'POST':
            return form_ug_sem_6_post()
        else:
            # Fetch ug_sem_6_info from the database
            cursor.execute("SELECT * FROM ug_sem_6 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_6_info = cursor.fetchone()

            # If ug_sem_6_info is None, create a default ug_sem_6_info object
            if ug_sem_6_info is None:
                ug_sem_6_info = {
                    'ug_enrollment_no': '',
                    'ug_sem_6_session': '',
                    'ug_sem_6_roll_no': '',
                    'ug_sem_6_result': '',
                    'ug_sem_6_sub_1_name': '',
                    'ug_sem_6_sub_1_marks_obtained': '',
                    'ug_sem_6_sub_1_total_marks': '',
                    'ug_sem_6_sub_2_name': '',
                    'ug_sem_6_sub_2_marks_obtained': '',
                    'ug_sem_6_sub_2_total_marks': '',
                    'ug_sem_6_sub_3_name': '',
                    'ug_sem_6_sub_3_marks_obtained': '',
                    'ug_sem_6_sub_3_total_marks': '',
                    'ug_sem_6_sub_4_name': '',
                    'ug_sem_6_sub_4_marks_obtained': '',
                    'ug_sem_6_sub_4_total_marks': '',
                    'ug_sem_6_sub_5_name': '',
                    'ug_sem_6_sub_5_marks_obtained': '',
                    'ug_sem_6_sub_5_total_marks': '',
                    'ug_sem_6_sub_6_name': '',
                    'ug_sem_6_sub_6_marks_obtained': '',
                    'ug_sem_6_sub_6_total_marks': '',
                    'ug_sem_6_sub_7_name': '',
                    'ug_sem_6_sub_7_marks_obtained': '',
                    'ug_sem_6_sub_7_total_marks': '',
                    'ug_sem_6_sub_8_name': '',
                    'ug_sem_6_sub_8_marks_obtained': '',
                    'ug_sem_6_sub_8_total_marks': '',
                    'ug_sem_6_sub_9_name': '',
                    'ug_sem_6_sub_9_marks_obtained': '',
                    'ug_sem_6_sub_9_total_marks': '',
                    'ug_sem_6_sub_10_name': '',
                    'ug_sem_6_sub_10_marks_obtained': '',
                    'ug_sem_6_sub_10_total_marks': '',
                    'ug_sem_6_sub_11_name': '',
                    'ug_sem_6_sub_11_marks_obtained': '',
                    'ug_sem_6_sub_11_total_marks': '',
                    'ug_sem_6_sub_12_name': '',
                    'ug_sem_6_sub_12_marks_obtained': '',
                    'ug_sem_6_sub_12_total_marks': '',
                    'ug_sem_6_sub_13_name': '',
                    'ug_sem_6_sub_13_marks_obtained': '',
                    'ug_sem_6_sub_13_total_marks': '',
                    'ug_sem_6_sub_14_name': '',
                    'ug_sem_6_sub_14_marks_obtained': '',
                    'ug_sem_6_sub_14_total_marks': '',
                    'ug_sem_6_sub_15_name': '',
                    'ug_sem_6_sub_15_marks_obtained': '',
                    'ug_sem_6_sub_15_total_marks': '',
                    'ug_sem_6_sub_16_name': '',
                    'ug_sem_6_sub_16_marks_obtained': '',
                    'ug_sem_6_sub_16_total_marks': '',
                    'ug_sem_6_sub_17_name': '',
                    'ug_sem_6_sub_17_marks_obtained': '',
                    'ug_sem_6_sub_17_total_marks': '',
                    'ug_sem_6_sub_18_name': '',
                    'ug_sem_6_sub_18_marks_obtained': '',
                    'ug_sem_6_sub_18_total_marks': '',
                    'ug_sem_6_sub_19_name': '',
                    'ug_sem_6_sub_19_marks_obtained': '',
                    'ug_sem_6_sub_19_total_marks': '',
                    'ug_sem_6_sub_20_name': '',
                    'ug_sem_6_sub_20_marks_obtained': '',
                    'ug_sem_6_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the ug_sem_6_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_6.html', ug_sem_6=ug_sem_6_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_ug_sem_6_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            ug_enrollment_no = request.form['ug_enrollment_no']
            ug_sem_6_session = request.form['ug_sem_6_session']
            ug_sem_6_roll_no = request.form['ug_sem_6_roll_no']
            ug_sem_6_result = request.form['ug_sem_6_result']
            ug_sem_6_sub_1_name = request.form['ug_sem_6_sub_1_name']
            ug_sem_6_sub_1_marks_obtained = request.form['ug_sem_6_sub_1_marks_obtained']
            ug_sem_6_sub_1_total_marks = request.form['ug_sem_6_sub_1_total_marks']
            ug_sem_6_sub_2_name = request.form['ug_sem_6_sub_2_name']
            ug_sem_6_sub_2_marks_obtained = request.form['ug_sem_6_sub_2_marks_obtained']
            ug_sem_6_sub_2_total_marks = request.form['ug_sem_6_sub_2_total_marks']
            ug_sem_6_sub_3_name = request.form['ug_sem_6_sub_3_name']
            ug_sem_6_sub_3_marks_obtained = request.form['ug_sem_6_sub_3_marks_obtained']
            ug_sem_6_sub_3_total_marks = request.form['ug_sem_6_sub_3_total_marks']
            ug_sem_6_sub_4_name = request.form['ug_sem_6_sub_4_name']
            ug_sem_6_sub_4_marks_obtained = request.form['ug_sem_6_sub_4_marks_obtained']
            ug_sem_6_sub_4_total_marks = request.form['ug_sem_6_sub_4_total_marks']
            ug_sem_6_sub_5_name = request.form['ug_sem_6_sub_5_name']
            ug_sem_6_sub_5_marks_obtained = request.form['ug_sem_6_sub_5_marks_obtained']
            ug_sem_6_sub_5_total_marks = request.form['ug_sem_6_sub_5_total_marks']
            ug_sem_6_sub_6_name = request.form['ug_sem_6_sub_6_name']
            ug_sem_6_sub_6_marks_obtained = request.form['ug_sem_6_sub_6_marks_obtained']
            ug_sem_6_sub_6_total_marks = request.form['ug_sem_6_sub_6_total_marks']
            ug_sem_6_sub_7_name = request.form['ug_sem_6_sub_7_name']
            ug_sem_6_sub_7_marks_obtained = request.form['ug_sem_6_sub_7_marks_obtained']
            ug_sem_6_sub_7_total_marks = request.form['ug_sem_6_sub_7_total_marks']
            ug_sem_6_sub_8_name = request.form['ug_sem_6_sub_8_name']
            ug_sem_6_sub_8_marks_obtained = request.form['ug_sem_6_sub_8_marks_obtained']
            ug_sem_6_sub_8_total_marks = request.form['ug_sem_6_sub_8_total_marks']
            ug_sem_6_sub_9_name = request.form['ug_sem_6_sub_9_name']
            ug_sem_6_sub_9_marks_obtained = request.form['ug_sem_6_sub_9_marks_obtained']
            ug_sem_6_sub_9_total_marks = request.form['ug_sem_6_sub_9_total_marks']
            ug_sem_6_sub_10_name = request.form['ug_sem_6_sub_10_name']
            ug_sem_6_sub_10_marks_obtained = request.form['ug_sem_6_sub_10_marks_obtained']
            ug_sem_6_sub_10_total_marks = request.form['ug_sem_6_sub_10_total_marks']
            ug_sem_6_sub_11_name = request.form['ug_sem_6_sub_11_name']
            ug_sem_6_sub_11_marks_obtained = request.form['ug_sem_6_sub_11_marks_obtained']
            ug_sem_6_sub_11_total_marks = request.form['ug_sem_6_sub_11_total_marks']
            ug_sem_6_sub_12_name = request.form['ug_sem_6_sub_12_name']
            ug_sem_6_sub_12_marks_obtained = request.form['ug_sem_6_sub_12_marks_obtained']
            ug_sem_6_sub_12_total_marks = request.form['ug_sem_6_sub_12_total_marks']
            ug_sem_6_sub_13_name = request.form['ug_sem_6_sub_13_name']
            ug_sem_6_sub_13_marks_obtained = request.form['ug_sem_6_sub_13_marks_obtained']
            ug_sem_6_sub_13_total_marks = request.form['ug_sem_6_sub_13_total_marks']
            ug_sem_6_sub_14_name = request.form['ug_sem_6_sub_14_name']
            ug_sem_6_sub_14_marks_obtained = request.form['ug_sem_6_sub_14_marks_obtained']
            ug_sem_6_sub_14_total_marks = request.form['ug_sem_6_sub_14_total_marks']
            ug_sem_6_sub_15_name = request.form['ug_sem_6_sub_15_name']
            ug_sem_6_sub_15_marks_obtained = request.form['ug_sem_6_sub_15_marks_obtained']
            ug_sem_6_sub_15_total_marks = request.form['ug_sem_6_sub_15_total_marks']
            ug_sem_6_sub_16_name = request.form['ug_sem_6_sub_16_name']
            ug_sem_6_sub_16_marks_obtained = request.form['ug_sem_6_sub_16_marks_obtained']
            ug_sem_6_sub_16_total_marks = request.form['ug_sem_6_sub_16_total_marks']
            ug_sem_6_sub_17_name = request.form['ug_sem_6_sub_17_name']
            ug_sem_6_sub_17_marks_obtained = request.form['ug_sem_6_sub_17_marks_obtained']
            ug_sem_6_sub_17_total_marks = request.form['ug_sem_6_sub_17_total_marks']
            ug_sem_6_sub_18_name = request.form['ug_sem_6_sub_18_name']
            ug_sem_6_sub_18_marks_obtained = request.form['ug_sem_6_sub_18_marks_obtained']
            ug_sem_6_sub_18_total_marks = request.form['ug_sem_6_sub_18_total_marks']
            ug_sem_6_sub_19_name = request.form['ug_sem_6_sub_19_name']
            ug_sem_6_sub_19_marks_obtained = request.form['ug_sem_6_sub_19_marks_obtained']
            ug_sem_6_sub_19_total_marks = request.form['ug_sem_6_sub_19_total_marks']
            ug_sem_6_sub_20_name = request.form['ug_sem_6_sub_20_name']
            ug_sem_6_sub_20_marks_obtained = request.form['ug_sem_6_sub_20_marks_obtained']
            ug_sem_6_sub_20_total_marks = request.form['ug_sem_6_sub_20_total_marks']


            # Update ug_sem_6_info in the database
            cursor.execute("""
                UPDATE ug_sem_6
                SET ug_enrollment_no = ?, ug_sem_6_session = ?, ug_sem_6_roll_no = ?, ug_sem_6_result = ?, ug_sem_6_sub_1_name = ?, ug_sem_6_sub_1_marks_obtained = ?, ug_sem_6_sub_1_total_marks = ?, ug_sem_6_sub_2_name = ?, ug_sem_6_sub_2_marks_obtained = ?, ug_sem_6_sub_2_total_marks = ?, ug_sem_6_sub_3_name = ?, ug_sem_6_sub_3_marks_obtained = ?, ug_sem_6_sub_3_total_marks = ?, ug_sem_6_sub_4_name = ?, ug_sem_6_sub_4_marks_obtained = ?, ug_sem_6_sub_4_total_marks = ?, ug_sem_6_sub_5_name = ?, ug_sem_6_sub_5_marks_obtained = ?, ug_sem_6_sub_5_total_marks = ?, ug_sem_6_sub_6_name = ?, ug_sem_6_sub_6_marks_obtained = ?, ug_sem_6_sub_6_total_marks = ?, ug_sem_6_sub_7_name = ?, ug_sem_6_sub_7_marks_obtained = ?, ug_sem_6_sub_7_total_marks = ?, ug_sem_6_sub_8_name = ?, ug_sem_6_sub_8_marks_obtained = ?, ug_sem_6_sub_8_total_marks = ?, ug_sem_6_sub_9_name = ?, ug_sem_6_sub_9_marks_obtained = ?, ug_sem_6_sub_9_total_marks = ?, ug_sem_6_sub_10_name = ?, ug_sem_6_sub_10_marks_obtained = ?, ug_sem_6_sub_10_total_marks = ?, ug_sem_6_sub_11_name = ?, ug_sem_6_sub_11_marks_obtained = ?, ug_sem_6_sub_11_total_marks = ?, ug_sem_6_sub_12_name = ?, ug_sem_6_sub_12_marks_obtained = ?, ug_sem_6_sub_12_total_marks = ?, ug_sem_6_sub_13_name = ?, ug_sem_6_sub_13_marks_obtained = ?, ug_sem_6_sub_13_total_marks = ?, ug_sem_6_sub_14_name = ?, ug_sem_6_sub_14_marks_obtained = ?, ug_sem_6_sub_14_total_marks = ?, ug_sem_6_sub_15_name = ?, ug_sem_6_sub_15_marks_obtained = ?, ug_sem_6_sub_15_total_marks = ?, ug_sem_6_sub_16_name = ?, ug_sem_6_sub_16_marks_obtained = ?, ug_sem_6_sub_16_total_marks = ?, ug_sem_6_sub_17_name = ?, ug_sem_6_sub_17_marks_obtained = ?, ug_sem_6_sub_17_total_marks = ?, ug_sem_6_sub_18_name = ?, ug_sem_6_sub_18_marks_obtained = ?, ug_sem_6_sub_18_total_marks = ?, ug_sem_6_sub_19_name = ?, ug_sem_6_sub_19_marks_obtained = ?, ug_sem_6_sub_19_total_marks = ?, ug_sem_6_sub_20_name = ?, ug_sem_6_sub_20_marks_obtained = ?, ug_sem_6_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(ug_enrollment_no,ug_sem_6_session,ug_sem_6_roll_no,ug_sem_6_result,ug_sem_6_sub_1_name,
                 ug_sem_6_sub_1_marks_obtained,ug_sem_6_sub_1_total_marks,ug_sem_6_sub_2_name,
                 ug_sem_6_sub_2_marks_obtained,ug_sem_6_sub_2_total_marks,ug_sem_6_sub_3_name,
                 ug_sem_6_sub_3_marks_obtained,ug_sem_6_sub_3_total_marks,ug_sem_6_sub_4_name,
                 ug_sem_6_sub_4_marks_obtained,ug_sem_6_sub_4_total_marks,ug_sem_6_sub_5_name,
                 ug_sem_6_sub_5_marks_obtained,ug_sem_6_sub_5_total_marks,ug_sem_6_sub_6_name,
                 ug_sem_6_sub_6_marks_obtained,ug_sem_6_sub_6_total_marks,ug_sem_6_sub_7_name,
                 ug_sem_6_sub_7_marks_obtained,ug_sem_6_sub_7_total_marks,ug_sem_6_sub_8_name,
                 ug_sem_6_sub_8_marks_obtained,ug_sem_6_sub_8_total_marks,ug_sem_6_sub_9_name,
                 ug_sem_6_sub_9_marks_obtained,ug_sem_6_sub_9_total_marks,ug_sem_6_sub_10_name,
                 ug_sem_6_sub_10_marks_obtained,ug_sem_6_sub_10_total_marks,ug_sem_6_sub_11_name,
                 ug_sem_6_sub_11_marks_obtained,ug_sem_6_sub_11_total_marks,ug_sem_6_sub_12_name,
                 ug_sem_6_sub_12_marks_obtained,ug_sem_6_sub_12_total_marks,ug_sem_6_sub_13_name,
                 ug_sem_6_sub_13_marks_obtained,ug_sem_6_sub_13_total_marks,ug_sem_6_sub_14_name,
                 ug_sem_6_sub_14_marks_obtained,ug_sem_6_sub_14_total_marks,ug_sem_6_sub_15_name,
                 ug_sem_6_sub_15_marks_obtained,ug_sem_6_sub_15_total_marks,ug_sem_6_sub_16_name,
                 ug_sem_6_sub_16_marks_obtained,ug_sem_6_sub_16_total_marks,ug_sem_6_sub_17_name,
                 ug_sem_6_sub_17_marks_obtained,ug_sem_6_sub_17_total_marks,ug_sem_6_sub_18_name,
                 ug_sem_6_sub_18_marks_obtained,ug_sem_6_sub_18_total_marks,ug_sem_6_sub_19_name,
                 ug_sem_6_sub_19_marks_obtained,ug_sem_6_sub_19_total_marks,ug_sem_6_sub_20_name,
                 ug_sem_6_sub_20_marks_obtained,ug_sem_6_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_ug_sem_7'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch ug_sem_6_info from the database
            cursor.execute("SELECT * FROM ug_sem_6 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_6_info = cursor.fetchone()

            # Pass the ug_sem_6_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_6.html', ug_sem_6=ug_sem_6_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_ug_sem_7', methods=['GET', 'POST'])
def form_ug_sem_7():
    try:
        if request.method == 'POST':
            return form_ug_sem_7_post()
        else:
            # Fetch ug_sem_7_info from the database
            cursor.execute("SELECT * FROM ug_sem_7 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_7_info = cursor.fetchone()

            # If ug_sem_7_info is None, create a default ug_sem_7_info object
            if ug_sem_7_info is None:
                ug_sem_7_info = {
                    'ug_enrollment_no': '',
                    'ug_sem_7_session': '',
                    'ug_sem_7_roll_no': '',
                    'ug_sem_7_result': '',
                    'ug_sem_7_sub_1_name': '',
                    'ug_sem_7_sub_1_marks_obtained': '',
                    'ug_sem_7_sub_1_total_marks': '',
                    'ug_sem_7_sub_2_name': '',
                    'ug_sem_7_sub_2_marks_obtained': '',
                    'ug_sem_7_sub_2_total_marks': '',
                    'ug_sem_7_sub_3_name': '',
                    'ug_sem_7_sub_3_marks_obtained': '',
                    'ug_sem_7_sub_3_total_marks': '',
                    'ug_sem_7_sub_4_name': '',
                    'ug_sem_7_sub_4_marks_obtained': '',
                    'ug_sem_7_sub_4_total_marks': '',
                    'ug_sem_7_sub_5_name': '',
                    'ug_sem_7_sub_5_marks_obtained': '',
                    'ug_sem_7_sub_5_total_marks': '',
                    'ug_sem_7_sub_6_name': '',
                    'ug_sem_7_sub_6_marks_obtained': '',
                    'ug_sem_7_sub_6_total_marks': '',
                    'ug_sem_7_sub_7_name': '',
                    'ug_sem_7_sub_7_marks_obtained': '',
                    'ug_sem_7_sub_7_total_marks': '',
                    'ug_sem_7_sub_8_name': '',
                    'ug_sem_7_sub_8_marks_obtained': '',
                    'ug_sem_7_sub_8_total_marks': '',
                    'ug_sem_7_sub_9_name': '',
                    'ug_sem_7_sub_9_marks_obtained': '',
                    'ug_sem_7_sub_9_total_marks': '',
                    'ug_sem_7_sub_10_name': '',
                    'ug_sem_7_sub_10_marks_obtained': '',
                    'ug_sem_7_sub_10_total_marks': '',
                    'ug_sem_7_sub_11_name': '',
                    'ug_sem_7_sub_11_marks_obtained': '',
                    'ug_sem_7_sub_11_total_marks': '',
                    'ug_sem_7_sub_12_name': '',
                    'ug_sem_7_sub_12_marks_obtained': '',
                    'ug_sem_7_sub_12_total_marks': '',
                    'ug_sem_7_sub_13_name': '',
                    'ug_sem_7_sub_13_marks_obtained': '',
                    'ug_sem_7_sub_13_total_marks': '',
                    'ug_sem_7_sub_14_name': '',
                    'ug_sem_7_sub_14_marks_obtained': '',
                    'ug_sem_7_sub_14_total_marks': '',
                    'ug_sem_7_sub_15_name': '',
                    'ug_sem_7_sub_15_marks_obtained': '',
                    'ug_sem_7_sub_15_total_marks': '',
                    'ug_sem_7_sub_16_name': '',
                    'ug_sem_7_sub_16_marks_obtained': '',
                    'ug_sem_7_sub_16_total_marks': '',
                    'ug_sem_7_sub_17_name': '',
                    'ug_sem_7_sub_17_marks_obtained': '',
                    'ug_sem_7_sub_17_total_marks': '',
                    'ug_sem_7_sub_18_name': '',
                    'ug_sem_7_sub_18_marks_obtained': '',
                    'ug_sem_7_sub_18_total_marks': '',
                    'ug_sem_7_sub_19_name': '',
                    'ug_sem_7_sub_19_marks_obtained': '',
                    'ug_sem_7_sub_19_total_marks': '',
                    'ug_sem_7_sub_20_name': '',
                    'ug_sem_7_sub_20_marks_obtained': '',
                    'ug_sem_7_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the ug_sem_7_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_7.html', ug_sem_7=ug_sem_7_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_ug_sem_7_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            ug_enrollment_no = request.form['ug_enrollment_no']
            ug_sem_7_session = request.form['ug_sem_7_session']
            ug_sem_7_roll_no = request.form['ug_sem_7_roll_no']
            ug_sem_7_result = request.form['ug_sem_7_result']
            ug_sem_7_sub_1_name = request.form['ug_sem_7_sub_1_name']
            ug_sem_7_sub_1_marks_obtained = request.form['ug_sem_7_sub_1_marks_obtained']
            ug_sem_7_sub_1_total_marks = request.form['ug_sem_7_sub_1_total_marks']
            ug_sem_7_sub_2_name = request.form['ug_sem_7_sub_2_name']
            ug_sem_7_sub_2_marks_obtained = request.form['ug_sem_7_sub_2_marks_obtained']
            ug_sem_7_sub_2_total_marks = request.form['ug_sem_7_sub_2_total_marks']
            ug_sem_7_sub_3_name = request.form['ug_sem_7_sub_3_name']
            ug_sem_7_sub_3_marks_obtained = request.form['ug_sem_7_sub_3_marks_obtained']
            ug_sem_7_sub_3_total_marks = request.form['ug_sem_7_sub_3_total_marks']
            ug_sem_7_sub_4_name = request.form['ug_sem_7_sub_4_name']
            ug_sem_7_sub_4_marks_obtained = request.form['ug_sem_7_sub_4_marks_obtained']
            ug_sem_7_sub_4_total_marks = request.form['ug_sem_7_sub_4_total_marks']
            ug_sem_7_sub_5_name = request.form['ug_sem_7_sub_5_name']
            ug_sem_7_sub_5_marks_obtained = request.form['ug_sem_7_sub_5_marks_obtained']
            ug_sem_7_sub_5_total_marks = request.form['ug_sem_7_sub_5_total_marks']
            ug_sem_7_sub_6_name = request.form['ug_sem_7_sub_6_name']
            ug_sem_7_sub_6_marks_obtained = request.form['ug_sem_7_sub_6_marks_obtained']
            ug_sem_7_sub_6_total_marks = request.form['ug_sem_7_sub_6_total_marks']
            ug_sem_7_sub_7_name = request.form['ug_sem_7_sub_7_name']
            ug_sem_7_sub_7_marks_obtained = request.form['ug_sem_7_sub_7_marks_obtained']
            ug_sem_7_sub_7_total_marks = request.form['ug_sem_7_sub_7_total_marks']
            ug_sem_7_sub_8_name = request.form['ug_sem_7_sub_8_name']
            ug_sem_7_sub_8_marks_obtained = request.form['ug_sem_7_sub_8_marks_obtained']
            ug_sem_7_sub_8_total_marks = request.form['ug_sem_7_sub_8_total_marks']
            ug_sem_7_sub_9_name = request.form['ug_sem_7_sub_9_name']
            ug_sem_7_sub_9_marks_obtained = request.form['ug_sem_7_sub_9_marks_obtained']
            ug_sem_7_sub_9_total_marks = request.form['ug_sem_7_sub_9_total_marks']
            ug_sem_7_sub_10_name = request.form['ug_sem_7_sub_10_name']
            ug_sem_7_sub_10_marks_obtained = request.form['ug_sem_7_sub_10_marks_obtained']
            ug_sem_7_sub_10_total_marks = request.form['ug_sem_7_sub_10_total_marks']
            ug_sem_7_sub_11_name = request.form['ug_sem_7_sub_11_name']
            ug_sem_7_sub_11_marks_obtained = request.form['ug_sem_7_sub_11_marks_obtained']
            ug_sem_7_sub_11_total_marks = request.form['ug_sem_7_sub_11_total_marks']
            ug_sem_7_sub_12_name = request.form['ug_sem_7_sub_12_name']
            ug_sem_7_sub_12_marks_obtained = request.form['ug_sem_7_sub_12_marks_obtained']
            ug_sem_7_sub_12_total_marks = request.form['ug_sem_7_sub_12_total_marks']
            ug_sem_7_sub_13_name = request.form['ug_sem_7_sub_13_name']
            ug_sem_7_sub_13_marks_obtained = request.form['ug_sem_7_sub_13_marks_obtained']
            ug_sem_7_sub_13_total_marks = request.form['ug_sem_7_sub_13_total_marks']
            ug_sem_7_sub_14_name = request.form['ug_sem_7_sub_14_name']
            ug_sem_7_sub_14_marks_obtained = request.form['ug_sem_7_sub_14_marks_obtained']
            ug_sem_7_sub_14_total_marks = request.form['ug_sem_7_sub_14_total_marks']
            ug_sem_7_sub_15_name = request.form['ug_sem_7_sub_15_name']
            ug_sem_7_sub_15_marks_obtained = request.form['ug_sem_7_sub_15_marks_obtained']
            ug_sem_7_sub_15_total_marks = request.form['ug_sem_7_sub_15_total_marks']
            ug_sem_7_sub_16_name = request.form['ug_sem_7_sub_16_name']
            ug_sem_7_sub_16_marks_obtained = request.form['ug_sem_7_sub_16_marks_obtained']
            ug_sem_7_sub_16_total_marks = request.form['ug_sem_7_sub_16_total_marks']
            ug_sem_7_sub_17_name = request.form['ug_sem_7_sub_17_name']
            ug_sem_7_sub_17_marks_obtained = request.form['ug_sem_7_sub_17_marks_obtained']
            ug_sem_7_sub_17_total_marks = request.form['ug_sem_7_sub_17_total_marks']
            ug_sem_7_sub_18_name = request.form['ug_sem_7_sub_18_name']
            ug_sem_7_sub_18_marks_obtained = request.form['ug_sem_7_sub_18_marks_obtained']
            ug_sem_7_sub_18_total_marks = request.form['ug_sem_7_sub_18_total_marks']
            ug_sem_7_sub_19_name = request.form['ug_sem_7_sub_19_name']
            ug_sem_7_sub_19_marks_obtained = request.form['ug_sem_7_sub_19_marks_obtained']
            ug_sem_7_sub_19_total_marks = request.form['ug_sem_7_sub_19_total_marks']
            ug_sem_7_sub_20_name = request.form['ug_sem_7_sub_20_name']
            ug_sem_7_sub_20_marks_obtained = request.form['ug_sem_7_sub_20_marks_obtained']
            ug_sem_7_sub_20_total_marks = request.form['ug_sem_7_sub_20_total_marks']


            # Update ug_sem_7_info in the database
            cursor.execute("""
                UPDATE ug_sem_7
                SET ug_enrollment_no = ?, ug_sem_7_session = ?, ug_sem_7_roll_no = ?, ug_sem_7_result = ?, ug_sem_7_sub_1_name = ?, ug_sem_7_sub_1_marks_obtained = ?, ug_sem_7_sub_1_total_marks = ?, ug_sem_7_sub_2_name = ?, ug_sem_7_sub_2_marks_obtained = ?, ug_sem_7_sub_2_total_marks = ?, ug_sem_7_sub_3_name = ?, ug_sem_7_sub_3_marks_obtained = ?, ug_sem_7_sub_3_total_marks = ?, ug_sem_7_sub_4_name = ?, ug_sem_7_sub_4_marks_obtained = ?, ug_sem_7_sub_4_total_marks = ?, ug_sem_7_sub_5_name = ?, ug_sem_7_sub_5_marks_obtained = ?, ug_sem_7_sub_5_total_marks = ?, ug_sem_7_sub_6_name = ?, ug_sem_7_sub_6_marks_obtained = ?, ug_sem_7_sub_6_total_marks = ?, ug_sem_7_sub_7_name = ?, ug_sem_7_sub_7_marks_obtained = ?, ug_sem_7_sub_7_total_marks = ?, ug_sem_7_sub_8_name = ?, ug_sem_7_sub_8_marks_obtained = ?, ug_sem_7_sub_8_total_marks = ?, ug_sem_7_sub_9_name = ?, ug_sem_7_sub_9_marks_obtained = ?, ug_sem_7_sub_9_total_marks = ?, ug_sem_7_sub_10_name = ?, ug_sem_7_sub_10_marks_obtained = ?, ug_sem_7_sub_10_total_marks = ?, ug_sem_7_sub_11_name = ?, ug_sem_7_sub_11_marks_obtained = ?, ug_sem_7_sub_11_total_marks = ?, ug_sem_7_sub_12_name = ?, ug_sem_7_sub_12_marks_obtained = ?, ug_sem_7_sub_12_total_marks = ?, ug_sem_7_sub_13_name = ?, ug_sem_7_sub_13_marks_obtained = ?, ug_sem_7_sub_13_total_marks = ?, ug_sem_7_sub_14_name = ?, ug_sem_7_sub_14_marks_obtained = ?, ug_sem_7_sub_14_total_marks = ?, ug_sem_7_sub_15_name = ?, ug_sem_7_sub_15_marks_obtained = ?, ug_sem_7_sub_15_total_marks = ?, ug_sem_7_sub_16_name = ?, ug_sem_7_sub_16_marks_obtained = ?, ug_sem_7_sub_16_total_marks = ?, ug_sem_7_sub_17_name = ?, ug_sem_7_sub_17_marks_obtained = ?, ug_sem_7_sub_17_total_marks = ?, ug_sem_7_sub_18_name = ?, ug_sem_7_sub_18_marks_obtained = ?, ug_sem_7_sub_18_total_marks = ?, ug_sem_7_sub_19_name = ?, ug_sem_7_sub_19_marks_obtained = ?, ug_sem_7_sub_19_total_marks = ?, ug_sem_7_sub_20_name = ?, ug_sem_7_sub_20_marks_obtained = ?, ug_sem_7_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(ug_enrollment_no,ug_sem_7_session,ug_sem_7_roll_no,ug_sem_7_result,ug_sem_7_sub_1_name,
                 ug_sem_7_sub_1_marks_obtained,ug_sem_7_sub_1_total_marks,ug_sem_7_sub_2_name,
                 ug_sem_7_sub_2_marks_obtained,ug_sem_7_sub_2_total_marks,ug_sem_7_sub_3_name,
                 ug_sem_7_sub_3_marks_obtained,ug_sem_7_sub_3_total_marks,ug_sem_7_sub_4_name,
                 ug_sem_7_sub_4_marks_obtained,ug_sem_7_sub_4_total_marks,ug_sem_7_sub_5_name,
                 ug_sem_7_sub_5_marks_obtained,ug_sem_7_sub_5_total_marks,ug_sem_7_sub_6_name,
                 ug_sem_7_sub_6_marks_obtained,ug_sem_7_sub_6_total_marks,ug_sem_7_sub_7_name,
                 ug_sem_7_sub_7_marks_obtained,ug_sem_7_sub_7_total_marks,ug_sem_7_sub_8_name,
                 ug_sem_7_sub_8_marks_obtained,ug_sem_7_sub_8_total_marks,ug_sem_7_sub_9_name,
                 ug_sem_7_sub_9_marks_obtained,ug_sem_7_sub_9_total_marks,ug_sem_7_sub_10_name,
                 ug_sem_7_sub_10_marks_obtained,ug_sem_7_sub_10_total_marks,ug_sem_7_sub_11_name,
                 ug_sem_7_sub_11_marks_obtained,ug_sem_7_sub_11_total_marks,ug_sem_7_sub_12_name,
                 ug_sem_7_sub_12_marks_obtained,ug_sem_7_sub_12_total_marks,ug_sem_7_sub_13_name,
                 ug_sem_7_sub_13_marks_obtained,ug_sem_7_sub_13_total_marks,ug_sem_7_sub_14_name,
                 ug_sem_7_sub_14_marks_obtained,ug_sem_7_sub_14_total_marks,ug_sem_7_sub_15_name,
                 ug_sem_7_sub_15_marks_obtained,ug_sem_7_sub_15_total_marks,ug_sem_7_sub_16_name,
                 ug_sem_7_sub_16_marks_obtained,ug_sem_7_sub_16_total_marks,ug_sem_7_sub_17_name,
                 ug_sem_7_sub_17_marks_obtained,ug_sem_7_sub_17_total_marks,ug_sem_7_sub_18_name,
                 ug_sem_7_sub_18_marks_obtained,ug_sem_7_sub_18_total_marks,ug_sem_7_sub_19_name,
                 ug_sem_7_sub_19_marks_obtained,ug_sem_7_sub_19_total_marks,ug_sem_7_sub_20_name,
                 ug_sem_7_sub_20_marks_obtained,ug_sem_7_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_ug_sem_8'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch ug_sem_7_info from the database
            cursor.execute("SELECT * FROM ug_sem_7 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_7_info = cursor.fetchone()

            # Pass the ug_sem_7_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_7.html', ug_sem_7=ug_sem_7_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_ug_sem_8', methods=['GET', 'POST'])
def form_ug_sem_8():
    try:
        if request.method == 'POST':
            return form_ug_sem_8_post()
        else:
            # Fetch ug_sem_8_info from the database
            cursor.execute("SELECT * FROM ug_sem_8 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_8_info = cursor.fetchone()

            # If ug_sem_8_info is None, create a default ug_sem_8_info object
            if ug_sem_8_info is None:
                ug_sem_8_info = {
                    'ug_enrollment_no': '',
                    'ug_sem_8_session': '',
                    'ug_sem_8_roll_no': '',
                    'ug_sem_8_result': '',
                    'ug_sem_8_sub_1_name': '',
                    'ug_sem_8_sub_1_marks_obtained': '',
                    'ug_sem_8_sub_1_total_marks': '',
                    'ug_sem_8_sub_2_name': '',
                    'ug_sem_8_sub_2_marks_obtained': '',
                    'ug_sem_8_sub_2_total_marks': '',
                    'ug_sem_8_sub_3_name': '',
                    'ug_sem_8_sub_3_marks_obtained': '',
                    'ug_sem_8_sub_3_total_marks': '',
                    'ug_sem_8_sub_4_name': '',
                    'ug_sem_8_sub_4_marks_obtained': '',
                    'ug_sem_8_sub_4_total_marks': '',
                    'ug_sem_8_sub_5_name': '',
                    'ug_sem_8_sub_5_marks_obtained': '',
                    'ug_sem_8_sub_5_total_marks': '',
                    'ug_sem_8_sub_6_name': '',
                    'ug_sem_8_sub_6_marks_obtained': '',
                    'ug_sem_8_sub_6_total_marks': '',
                    'ug_sem_8_sub_7_name': '',
                    'ug_sem_8_sub_7_marks_obtained': '',
                    'ug_sem_8_sub_7_total_marks': '',
                    'ug_sem_8_sub_8_name': '',
                    'ug_sem_8_sub_8_marks_obtained': '',
                    'ug_sem_8_sub_8_total_marks': '',
                    'ug_sem_8_sub_9_name': '',
                    'ug_sem_8_sub_9_marks_obtained': '',
                    'ug_sem_8_sub_9_total_marks': '',
                    'ug_sem_8_sub_10_name': '',
                    'ug_sem_8_sub_10_marks_obtained': '',
                    'ug_sem_8_sub_10_total_marks': '',
                    'ug_sem_8_sub_11_name': '',
                    'ug_sem_8_sub_11_marks_obtained': '',
                    'ug_sem_8_sub_11_total_marks': '',
                    'ug_sem_8_sub_12_name': '',
                    'ug_sem_8_sub_12_marks_obtained': '',
                    'ug_sem_8_sub_12_total_marks': '',
                    'ug_sem_8_sub_13_name': '',
                    'ug_sem_8_sub_13_marks_obtained': '',
                    'ug_sem_8_sub_13_total_marks': '',
                    'ug_sem_8_sub_14_name': '',
                    'ug_sem_8_sub_14_marks_obtained': '',
                    'ug_sem_8_sub_14_total_marks': '',
                    'ug_sem_8_sub_15_name': '',
                    'ug_sem_8_sub_15_marks_obtained': '',
                    'ug_sem_8_sub_15_total_marks': '',
                    'ug_sem_8_sub_16_name': '',
                    'ug_sem_8_sub_16_marks_obtained': '',
                    'ug_sem_8_sub_16_total_marks': '',
                    'ug_sem_8_sub_17_name': '',
                    'ug_sem_8_sub_17_marks_obtained': '',
                    'ug_sem_8_sub_17_total_marks': '',
                    'ug_sem_8_sub_18_name': '',
                    'ug_sem_8_sub_18_marks_obtained': '',
                    'ug_sem_8_sub_18_total_marks': '',
                    'ug_sem_8_sub_19_name': '',
                    'ug_sem_8_sub_19_marks_obtained': '',
                    'ug_sem_8_sub_19_total_marks': '',
                    'ug_sem_8_sub_20_name': '',
                    'ug_sem_8_sub_20_marks_obtained': '',
                    'ug_sem_8_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the ug_sem_8_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_8.html', ug_sem_8=ug_sem_8_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_ug_sem_8_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            ug_enrollment_no = request.form['ug_enrollment_no']
            ug_sem_8_session = request.form['ug_sem_8_session']
            ug_sem_8_roll_no = request.form['ug_sem_8_roll_no']
            ug_sem_8_result = request.form['ug_sem_8_result']
            ug_sem_8_sub_1_name = request.form['ug_sem_8_sub_1_name']
            ug_sem_8_sub_1_marks_obtained = request.form['ug_sem_8_sub_1_marks_obtained']
            ug_sem_8_sub_1_total_marks = request.form['ug_sem_8_sub_1_total_marks']
            ug_sem_8_sub_2_name = request.form['ug_sem_8_sub_2_name']
            ug_sem_8_sub_2_marks_obtained = request.form['ug_sem_8_sub_2_marks_obtained']
            ug_sem_8_sub_2_total_marks = request.form['ug_sem_8_sub_2_total_marks']
            ug_sem_8_sub_3_name = request.form['ug_sem_8_sub_3_name']
            ug_sem_8_sub_3_marks_obtained = request.form['ug_sem_8_sub_3_marks_obtained']
            ug_sem_8_sub_3_total_marks = request.form['ug_sem_8_sub_3_total_marks']
            ug_sem_8_sub_4_name = request.form['ug_sem_8_sub_4_name']
            ug_sem_8_sub_4_marks_obtained = request.form['ug_sem_8_sub_4_marks_obtained']
            ug_sem_8_sub_4_total_marks = request.form['ug_sem_8_sub_4_total_marks']
            ug_sem_8_sub_5_name = request.form['ug_sem_8_sub_5_name']
            ug_sem_8_sub_5_marks_obtained = request.form['ug_sem_8_sub_5_marks_obtained']
            ug_sem_8_sub_5_total_marks = request.form['ug_sem_8_sub_5_total_marks']
            ug_sem_8_sub_6_name = request.form['ug_sem_8_sub_6_name']
            ug_sem_8_sub_6_marks_obtained = request.form['ug_sem_8_sub_6_marks_obtained']
            ug_sem_8_sub_6_total_marks = request.form['ug_sem_8_sub_6_total_marks']
            ug_sem_8_sub_7_name = request.form['ug_sem_8_sub_7_name']
            ug_sem_8_sub_7_marks_obtained = request.form['ug_sem_8_sub_7_marks_obtained']
            ug_sem_8_sub_7_total_marks = request.form['ug_sem_8_sub_7_total_marks']
            ug_sem_8_sub_8_name = request.form['ug_sem_8_sub_8_name']
            ug_sem_8_sub_8_marks_obtained = request.form['ug_sem_8_sub_8_marks_obtained']
            ug_sem_8_sub_8_total_marks = request.form['ug_sem_8_sub_8_total_marks']
            ug_sem_8_sub_9_name = request.form['ug_sem_8_sub_9_name']
            ug_sem_8_sub_9_marks_obtained = request.form['ug_sem_8_sub_9_marks_obtained']
            ug_sem_8_sub_9_total_marks = request.form['ug_sem_8_sub_9_total_marks']
            ug_sem_8_sub_10_name = request.form['ug_sem_8_sub_10_name']
            ug_sem_8_sub_10_marks_obtained = request.form['ug_sem_8_sub_10_marks_obtained']
            ug_sem_8_sub_10_total_marks = request.form['ug_sem_8_sub_10_total_marks']
            ug_sem_8_sub_11_name = request.form['ug_sem_8_sub_11_name']
            ug_sem_8_sub_11_marks_obtained = request.form['ug_sem_8_sub_11_marks_obtained']
            ug_sem_8_sub_11_total_marks = request.form['ug_sem_8_sub_11_total_marks']
            ug_sem_8_sub_12_name = request.form['ug_sem_8_sub_12_name']
            ug_sem_8_sub_12_marks_obtained = request.form['ug_sem_8_sub_12_marks_obtained']
            ug_sem_8_sub_12_total_marks = request.form['ug_sem_8_sub_12_total_marks']
            ug_sem_8_sub_13_name = request.form['ug_sem_8_sub_13_name']
            ug_sem_8_sub_13_marks_obtained = request.form['ug_sem_8_sub_13_marks_obtained']
            ug_sem_8_sub_13_total_marks = request.form['ug_sem_8_sub_13_total_marks']
            ug_sem_8_sub_14_name = request.form['ug_sem_8_sub_14_name']
            ug_sem_8_sub_14_marks_obtained = request.form['ug_sem_8_sub_14_marks_obtained']
            ug_sem_8_sub_14_total_marks = request.form['ug_sem_8_sub_14_total_marks']
            ug_sem_8_sub_15_name = request.form['ug_sem_8_sub_15_name']
            ug_sem_8_sub_15_marks_obtained = request.form['ug_sem_8_sub_15_marks_obtained']
            ug_sem_8_sub_15_total_marks = request.form['ug_sem_8_sub_15_total_marks']
            ug_sem_8_sub_16_name = request.form['ug_sem_8_sub_16_name']
            ug_sem_8_sub_16_marks_obtained = request.form['ug_sem_8_sub_16_marks_obtained']
            ug_sem_8_sub_16_total_marks = request.form['ug_sem_8_sub_16_total_marks']
            ug_sem_8_sub_17_name = request.form['ug_sem_8_sub_17_name']
            ug_sem_8_sub_17_marks_obtained = request.form['ug_sem_8_sub_17_marks_obtained']
            ug_sem_8_sub_17_total_marks = request.form['ug_sem_8_sub_17_total_marks']
            ug_sem_8_sub_18_name = request.form['ug_sem_8_sub_18_name']
            ug_sem_8_sub_18_marks_obtained = request.form['ug_sem_8_sub_18_marks_obtained']
            ug_sem_8_sub_18_total_marks = request.form['ug_sem_8_sub_18_total_marks']
            ug_sem_8_sub_19_name = request.form['ug_sem_8_sub_19_name']
            ug_sem_8_sub_19_marks_obtained = request.form['ug_sem_8_sub_19_marks_obtained']
            ug_sem_8_sub_19_total_marks = request.form['ug_sem_8_sub_19_total_marks']
            ug_sem_8_sub_20_name = request.form['ug_sem_8_sub_20_name']
            ug_sem_8_sub_20_marks_obtained = request.form['ug_sem_8_sub_20_marks_obtained']
            ug_sem_8_sub_20_total_marks = request.form['ug_sem_8_sub_20_total_marks']


            # Update ug_sem_8_info in the database
            cursor.execute("""
                UPDATE ug_sem_8
                SET ug_enrollment_no = ?, ug_sem_8_session = ?, ug_sem_8_roll_no = ?, ug_sem_8_result = ?, ug_sem_8_sub_1_name = ?, ug_sem_8_sub_1_marks_obtained = ?, ug_sem_8_sub_1_total_marks = ?, ug_sem_8_sub_2_name = ?, ug_sem_8_sub_2_marks_obtained = ?, ug_sem_8_sub_2_total_marks = ?, ug_sem_8_sub_3_name = ?, ug_sem_8_sub_3_marks_obtained = ?, ug_sem_8_sub_3_total_marks = ?, ug_sem_8_sub_4_name = ?, ug_sem_8_sub_4_marks_obtained = ?, ug_sem_8_sub_4_total_marks = ?, ug_sem_8_sub_5_name = ?, ug_sem_8_sub_5_marks_obtained = ?, ug_sem_8_sub_5_total_marks = ?, ug_sem_8_sub_6_name = ?, ug_sem_8_sub_6_marks_obtained = ?, ug_sem_8_sub_6_total_marks = ?, ug_sem_8_sub_7_name = ?, ug_sem_8_sub_7_marks_obtained = ?, ug_sem_8_sub_7_total_marks = ?, ug_sem_8_sub_8_name = ?, ug_sem_8_sub_8_marks_obtained = ?, ug_sem_8_sub_8_total_marks = ?, ug_sem_8_sub_9_name = ?, ug_sem_8_sub_9_marks_obtained = ?, ug_sem_8_sub_9_total_marks = ?, ug_sem_8_sub_10_name = ?, ug_sem_8_sub_10_marks_obtained = ?, ug_sem_8_sub_10_total_marks = ?, ug_sem_8_sub_11_name = ?, ug_sem_8_sub_11_marks_obtained = ?, ug_sem_8_sub_11_total_marks = ?, ug_sem_8_sub_12_name = ?, ug_sem_8_sub_12_marks_obtained = ?, ug_sem_8_sub_12_total_marks = ?, ug_sem_8_sub_13_name = ?, ug_sem_8_sub_13_marks_obtained = ?, ug_sem_8_sub_13_total_marks = ?, ug_sem_8_sub_14_name = ?, ug_sem_8_sub_14_marks_obtained = ?, ug_sem_8_sub_14_total_marks = ?, ug_sem_8_sub_15_name = ?, ug_sem_8_sub_15_marks_obtained = ?, ug_sem_8_sub_15_total_marks = ?, ug_sem_8_sub_16_name = ?, ug_sem_8_sub_16_marks_obtained = ?, ug_sem_8_sub_16_total_marks = ?, ug_sem_8_sub_17_name = ?, ug_sem_8_sub_17_marks_obtained = ?, ug_sem_8_sub_17_total_marks = ?, ug_sem_8_sub_18_name = ?, ug_sem_8_sub_18_marks_obtained = ?, ug_sem_8_sub_18_total_marks = ?, ug_sem_8_sub_19_name = ?, ug_sem_8_sub_19_marks_obtained = ?, ug_sem_8_sub_19_total_marks = ?, ug_sem_8_sub_20_name = ?, ug_sem_8_sub_20_marks_obtained = ?, ug_sem_8_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(ug_enrollment_no,ug_sem_8_session,ug_sem_8_roll_no,ug_sem_8_result,ug_sem_8_sub_1_name,
                 ug_sem_8_sub_1_marks_obtained,ug_sem_8_sub_1_total_marks,ug_sem_8_sub_2_name,
                 ug_sem_8_sub_2_marks_obtained,ug_sem_8_sub_2_total_marks,ug_sem_8_sub_3_name,
                 ug_sem_8_sub_3_marks_obtained,ug_sem_8_sub_3_total_marks,ug_sem_8_sub_4_name,
                 ug_sem_8_sub_4_marks_obtained,ug_sem_8_sub_4_total_marks,ug_sem_8_sub_5_name,
                 ug_sem_8_sub_5_marks_obtained,ug_sem_8_sub_5_total_marks,ug_sem_8_sub_6_name,
                 ug_sem_8_sub_6_marks_obtained,ug_sem_8_sub_6_total_marks,ug_sem_8_sub_7_name,
                 ug_sem_8_sub_7_marks_obtained,ug_sem_8_sub_7_total_marks,ug_sem_8_sub_8_name,
                 ug_sem_8_sub_8_marks_obtained,ug_sem_8_sub_8_total_marks,ug_sem_8_sub_9_name,
                 ug_sem_8_sub_9_marks_obtained,ug_sem_8_sub_9_total_marks,ug_sem_8_sub_10_name,
                 ug_sem_8_sub_10_marks_obtained,ug_sem_8_sub_10_total_marks,ug_sem_8_sub_11_name,
                 ug_sem_8_sub_11_marks_obtained,ug_sem_8_sub_11_total_marks,ug_sem_8_sub_12_name,
                 ug_sem_8_sub_12_marks_obtained,ug_sem_8_sub_12_total_marks,ug_sem_8_sub_13_name,
                 ug_sem_8_sub_13_marks_obtained,ug_sem_8_sub_13_total_marks,ug_sem_8_sub_14_name,
                 ug_sem_8_sub_14_marks_obtained,ug_sem_8_sub_14_total_marks,ug_sem_8_sub_15_name,
                 ug_sem_8_sub_15_marks_obtained,ug_sem_8_sub_15_total_marks,ug_sem_8_sub_16_name,
                 ug_sem_8_sub_16_marks_obtained,ug_sem_8_sub_16_total_marks,ug_sem_8_sub_17_name,
                 ug_sem_8_sub_17_marks_obtained,ug_sem_8_sub_17_total_marks,ug_sem_8_sub_18_name,
                 ug_sem_8_sub_18_marks_obtained,ug_sem_8_sub_18_total_marks,ug_sem_8_sub_19_name,
                 ug_sem_8_sub_19_marks_obtained,ug_sem_8_sub_19_total_marks,ug_sem_8_sub_20_name,
                 ug_sem_8_sub_20_marks_obtained,ug_sem_8_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_ug_sem_9'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch ug_sem_8_info from the database
            cursor.execute("SELECT * FROM ug_sem_8 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_8_info = cursor.fetchone()

            # Pass the ug_sem_8_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_8.html', ug_sem_8=ug_sem_8_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_ug_sem_9', methods=['GET', 'POST'])
def form_ug_sem_9():
    try:
        if request.method == 'POST':
            return form_ug_sem_9_post()
        else:
            # Fetch ug_sem_9_info from the database
            cursor.execute("SELECT * FROM ug_sem_9 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_9_info = cursor.fetchone()

            # If ug_sem_9_info is None, create a default ug_sem_9_info object
            if ug_sem_9_info is None:
                ug_sem_9_info = {
                    'ug_enrollment_no': '',
                    'ug_sem_9_session': '',
                    'ug_sem_9_roll_no': '',
                    'ug_sem_9_result': '',
                    'ug_sem_9_sub_1_name': '',
                    'ug_sem_9_sub_1_marks_obtained': '',
                    'ug_sem_9_sub_1_total_marks': '',
                    'ug_sem_9_sub_2_name': '',
                    'ug_sem_9_sub_2_marks_obtained': '',
                    'ug_sem_9_sub_2_total_marks': '',
                    'ug_sem_9_sub_3_name': '',
                    'ug_sem_9_sub_3_marks_obtained': '',
                    'ug_sem_9_sub_3_total_marks': '',
                    'ug_sem_9_sub_4_name': '',
                    'ug_sem_9_sub_4_marks_obtained': '',
                    'ug_sem_9_sub_4_total_marks': '',
                    'ug_sem_9_sub_5_name': '',
                    'ug_sem_9_sub_5_marks_obtained': '',
                    'ug_sem_9_sub_5_total_marks': '',
                    'ug_sem_9_sub_6_name': '',
                    'ug_sem_9_sub_6_marks_obtained': '',
                    'ug_sem_9_sub_6_total_marks': '',
                    'ug_sem_9_sub_7_name': '',
                    'ug_sem_9_sub_7_marks_obtained': '',
                    'ug_sem_9_sub_7_total_marks': '',
                    'ug_sem_9_sub_8_name': '',
                    'ug_sem_9_sub_8_marks_obtained': '',
                    'ug_sem_9_sub_8_total_marks': '',
                    'ug_sem_9_sub_9_name': '',
                    'ug_sem_9_sub_9_marks_obtained': '',
                    'ug_sem_9_sub_9_total_marks': '',
                    'ug_sem_9_sub_10_name': '',
                    'ug_sem_9_sub_10_marks_obtained': '',
                    'ug_sem_9_sub_10_total_marks': '',
                    'ug_sem_9_sub_11_name': '',
                    'ug_sem_9_sub_11_marks_obtained': '',
                    'ug_sem_9_sub_11_total_marks': '',
                    'ug_sem_9_sub_12_name': '',
                    'ug_sem_9_sub_12_marks_obtained': '',
                    'ug_sem_9_sub_12_total_marks': '',
                    'ug_sem_9_sub_13_name': '',
                    'ug_sem_9_sub_13_marks_obtained': '',
                    'ug_sem_9_sub_13_total_marks': '',
                    'ug_sem_9_sub_14_name': '',
                    'ug_sem_9_sub_14_marks_obtained': '',
                    'ug_sem_9_sub_14_total_marks': '',
                    'ug_sem_9_sub_15_name': '',
                    'ug_sem_9_sub_15_marks_obtained': '',
                    'ug_sem_9_sub_15_total_marks': '',
                    'ug_sem_9_sub_16_name': '',
                    'ug_sem_9_sub_16_marks_obtained': '',
                    'ug_sem_9_sub_16_total_marks': '',
                    'ug_sem_9_sub_17_name': '',
                    'ug_sem_9_sub_17_marks_obtained': '',
                    'ug_sem_9_sub_17_total_marks': '',
                    'ug_sem_9_sub_18_name': '',
                    'ug_sem_9_sub_18_marks_obtained': '',
                    'ug_sem_9_sub_18_total_marks': '',
                    'ug_sem_9_sub_19_name': '',
                    'ug_sem_9_sub_19_marks_obtained': '',
                    'ug_sem_9_sub_19_total_marks': '',
                    'ug_sem_9_sub_20_name': '',
                    'ug_sem_9_sub_20_marks_obtained': '',
                    'ug_sem_9_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the ug_sem_9_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_9.html', ug_sem_9=ug_sem_9_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_ug_sem_9_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            ug_enrollment_no = request.form['ug_enrollment_no']
            ug_sem_9_session = request.form['ug_sem_9_session']
            ug_sem_9_roll_no = request.form['ug_sem_9_roll_no']
            ug_sem_9_result = request.form['ug_sem_9_result']
            ug_sem_9_sub_1_name = request.form['ug_sem_9_sub_1_name']
            ug_sem_9_sub_1_marks_obtained = request.form['ug_sem_9_sub_1_marks_obtained']
            ug_sem_9_sub_1_total_marks = request.form['ug_sem_9_sub_1_total_marks']
            ug_sem_9_sub_2_name = request.form['ug_sem_9_sub_2_name']
            ug_sem_9_sub_2_marks_obtained = request.form['ug_sem_9_sub_2_marks_obtained']
            ug_sem_9_sub_2_total_marks = request.form['ug_sem_9_sub_2_total_marks']
            ug_sem_9_sub_3_name = request.form['ug_sem_9_sub_3_name']
            ug_sem_9_sub_3_marks_obtained = request.form['ug_sem_9_sub_3_marks_obtained']
            ug_sem_9_sub_3_total_marks = request.form['ug_sem_9_sub_3_total_marks']
            ug_sem_9_sub_4_name = request.form['ug_sem_9_sub_4_name']
            ug_sem_9_sub_4_marks_obtained = request.form['ug_sem_9_sub_4_marks_obtained']
            ug_sem_9_sub_4_total_marks = request.form['ug_sem_9_sub_4_total_marks']
            ug_sem_9_sub_5_name = request.form['ug_sem_9_sub_5_name']
            ug_sem_9_sub_5_marks_obtained = request.form['ug_sem_9_sub_5_marks_obtained']
            ug_sem_9_sub_5_total_marks = request.form['ug_sem_9_sub_5_total_marks']
            ug_sem_9_sub_6_name = request.form['ug_sem_9_sub_6_name']
            ug_sem_9_sub_6_marks_obtained = request.form['ug_sem_9_sub_6_marks_obtained']
            ug_sem_9_sub_6_total_marks = request.form['ug_sem_9_sub_6_total_marks']
            ug_sem_9_sub_7_name = request.form['ug_sem_9_sub_7_name']
            ug_sem_9_sub_7_marks_obtained = request.form['ug_sem_9_sub_7_marks_obtained']
            ug_sem_9_sub_7_total_marks = request.form['ug_sem_9_sub_7_total_marks']
            ug_sem_9_sub_8_name = request.form['ug_sem_9_sub_8_name']
            ug_sem_9_sub_8_marks_obtained = request.form['ug_sem_9_sub_8_marks_obtained']
            ug_sem_9_sub_8_total_marks = request.form['ug_sem_9_sub_8_total_marks']
            ug_sem_9_sub_9_name = request.form['ug_sem_9_sub_9_name']
            ug_sem_9_sub_9_marks_obtained = request.form['ug_sem_9_sub_9_marks_obtained']
            ug_sem_9_sub_9_total_marks = request.form['ug_sem_9_sub_9_total_marks']
            ug_sem_9_sub_10_name = request.form['ug_sem_9_sub_10_name']
            ug_sem_9_sub_10_marks_obtained = request.form['ug_sem_9_sub_10_marks_obtained']
            ug_sem_9_sub_10_total_marks = request.form['ug_sem_9_sub_10_total_marks']
            ug_sem_9_sub_11_name = request.form['ug_sem_9_sub_11_name']
            ug_sem_9_sub_11_marks_obtained = request.form['ug_sem_9_sub_11_marks_obtained']
            ug_sem_9_sub_11_total_marks = request.form['ug_sem_9_sub_11_total_marks']
            ug_sem_9_sub_12_name = request.form['ug_sem_9_sub_12_name']
            ug_sem_9_sub_12_marks_obtained = request.form['ug_sem_9_sub_12_marks_obtained']
            ug_sem_9_sub_12_total_marks = request.form['ug_sem_9_sub_12_total_marks']
            ug_sem_9_sub_13_name = request.form['ug_sem_9_sub_13_name']
            ug_sem_9_sub_13_marks_obtained = request.form['ug_sem_9_sub_13_marks_obtained']
            ug_sem_9_sub_13_total_marks = request.form['ug_sem_9_sub_13_total_marks']
            ug_sem_9_sub_14_name = request.form['ug_sem_9_sub_14_name']
            ug_sem_9_sub_14_marks_obtained = request.form['ug_sem_9_sub_14_marks_obtained']
            ug_sem_9_sub_14_total_marks = request.form['ug_sem_9_sub_14_total_marks']
            ug_sem_9_sub_15_name = request.form['ug_sem_9_sub_15_name']
            ug_sem_9_sub_15_marks_obtained = request.form['ug_sem_9_sub_15_marks_obtained']
            ug_sem_9_sub_15_total_marks = request.form['ug_sem_9_sub_15_total_marks']
            ug_sem_9_sub_16_name = request.form['ug_sem_9_sub_16_name']
            ug_sem_9_sub_16_marks_obtained = request.form['ug_sem_9_sub_16_marks_obtained']
            ug_sem_9_sub_16_total_marks = request.form['ug_sem_9_sub_16_total_marks']
            ug_sem_9_sub_17_name = request.form['ug_sem_9_sub_17_name']
            ug_sem_9_sub_17_marks_obtained = request.form['ug_sem_9_sub_17_marks_obtained']
            ug_sem_9_sub_17_total_marks = request.form['ug_sem_9_sub_17_total_marks']
            ug_sem_9_sub_18_name = request.form['ug_sem_9_sub_18_name']
            ug_sem_9_sub_18_marks_obtained = request.form['ug_sem_9_sub_18_marks_obtained']
            ug_sem_9_sub_18_total_marks = request.form['ug_sem_9_sub_18_total_marks']
            ug_sem_9_sub_19_name = request.form['ug_sem_9_sub_19_name']
            ug_sem_9_sub_19_marks_obtained = request.form['ug_sem_9_sub_19_marks_obtained']
            ug_sem_9_sub_19_total_marks = request.form['ug_sem_9_sub_19_total_marks']
            ug_sem_9_sub_20_name = request.form['ug_sem_9_sub_20_name']
            ug_sem_9_sub_20_marks_obtained = request.form['ug_sem_9_sub_20_marks_obtained']
            ug_sem_9_sub_20_total_marks = request.form['ug_sem_9_sub_20_total_marks']


            # Update ug_sem_9_info in the database
            cursor.execute("""
                UPDATE ug_sem_9
                SET ug_enrollment_no = ?, ug_sem_9_session = ?, ug_sem_9_roll_no = ?, ug_sem_9_result = ?, ug_sem_9_sub_1_name = ?, ug_sem_9_sub_1_marks_obtained = ?, ug_sem_9_sub_1_total_marks = ?, ug_sem_9_sub_2_name = ?, ug_sem_9_sub_2_marks_obtained = ?, ug_sem_9_sub_2_total_marks = ?, ug_sem_9_sub_3_name = ?, ug_sem_9_sub_3_marks_obtained = ?, ug_sem_9_sub_3_total_marks = ?, ug_sem_9_sub_4_name = ?, ug_sem_9_sub_4_marks_obtained = ?, ug_sem_9_sub_4_total_marks = ?, ug_sem_9_sub_5_name = ?, ug_sem_9_sub_5_marks_obtained = ?, ug_sem_9_sub_5_total_marks = ?, ug_sem_9_sub_6_name = ?, ug_sem_9_sub_6_marks_obtained = ?, ug_sem_9_sub_6_total_marks = ?, ug_sem_9_sub_7_name = ?, ug_sem_9_sub_7_marks_obtained = ?, ug_sem_9_sub_7_total_marks = ?, ug_sem_9_sub_8_name = ?, ug_sem_9_sub_8_marks_obtained = ?, ug_sem_9_sub_8_total_marks = ?, ug_sem_9_sub_9_name = ?, ug_sem_9_sub_9_marks_obtained = ?, ug_sem_9_sub_9_total_marks = ?, ug_sem_9_sub_10_name = ?, ug_sem_9_sub_10_marks_obtained = ?, ug_sem_9_sub_10_total_marks = ?, ug_sem_9_sub_11_name = ?, ug_sem_9_sub_11_marks_obtained = ?, ug_sem_9_sub_11_total_marks = ?, ug_sem_9_sub_12_name = ?, ug_sem_9_sub_12_marks_obtained = ?, ug_sem_9_sub_12_total_marks = ?, ug_sem_9_sub_13_name = ?, ug_sem_9_sub_13_marks_obtained = ?, ug_sem_9_sub_13_total_marks = ?, ug_sem_9_sub_14_name = ?, ug_sem_9_sub_14_marks_obtained = ?, ug_sem_9_sub_14_total_marks = ?, ug_sem_9_sub_15_name = ?, ug_sem_9_sub_15_marks_obtained = ?, ug_sem_9_sub_15_total_marks = ?, ug_sem_9_sub_16_name = ?, ug_sem_9_sub_16_marks_obtained = ?, ug_sem_9_sub_16_total_marks = ?, ug_sem_9_sub_17_name = ?, ug_sem_9_sub_17_marks_obtained = ?, ug_sem_9_sub_17_total_marks = ?, ug_sem_9_sub_18_name = ?, ug_sem_9_sub_18_marks_obtained = ?, ug_sem_9_sub_18_total_marks = ?, ug_sem_9_sub_19_name = ?, ug_sem_9_sub_19_marks_obtained = ?, ug_sem_9_sub_19_total_marks = ?, ug_sem_9_sub_20_name = ?, ug_sem_9_sub_20_marks_obtained = ?, ug_sem_9_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(ug_enrollment_no,ug_sem_9_session,ug_sem_9_roll_no,ug_sem_9_result,ug_sem_9_sub_1_name,
                 ug_sem_9_sub_1_marks_obtained,ug_sem_9_sub_1_total_marks,ug_sem_9_sub_2_name,
                 ug_sem_9_sub_2_marks_obtained,ug_sem_9_sub_2_total_marks,ug_sem_9_sub_3_name,
                 ug_sem_9_sub_3_marks_obtained,ug_sem_9_sub_3_total_marks,ug_sem_9_sub_4_name,
                 ug_sem_9_sub_4_marks_obtained,ug_sem_9_sub_4_total_marks,ug_sem_9_sub_5_name,
                 ug_sem_9_sub_5_marks_obtained,ug_sem_9_sub_5_total_marks,ug_sem_9_sub_6_name,
                 ug_sem_9_sub_6_marks_obtained,ug_sem_9_sub_6_total_marks,ug_sem_9_sub_7_name,
                 ug_sem_9_sub_7_marks_obtained,ug_sem_9_sub_7_total_marks,ug_sem_9_sub_8_name,
                 ug_sem_9_sub_8_marks_obtained,ug_sem_9_sub_8_total_marks,ug_sem_9_sub_9_name,
                 ug_sem_9_sub_9_marks_obtained,ug_sem_9_sub_9_total_marks,ug_sem_9_sub_10_name,
                 ug_sem_9_sub_10_marks_obtained,ug_sem_9_sub_10_total_marks,ug_sem_9_sub_11_name,
                 ug_sem_9_sub_11_marks_obtained,ug_sem_9_sub_11_total_marks,ug_sem_9_sub_12_name,
                 ug_sem_9_sub_12_marks_obtained,ug_sem_9_sub_12_total_marks,ug_sem_9_sub_13_name,
                 ug_sem_9_sub_13_marks_obtained,ug_sem_9_sub_13_total_marks,ug_sem_9_sub_14_name,
                 ug_sem_9_sub_14_marks_obtained,ug_sem_9_sub_14_total_marks,ug_sem_9_sub_15_name,
                 ug_sem_9_sub_15_marks_obtained,ug_sem_9_sub_15_total_marks,ug_sem_9_sub_16_name,
                 ug_sem_9_sub_16_marks_obtained,ug_sem_9_sub_16_total_marks,ug_sem_9_sub_17_name,
                 ug_sem_9_sub_17_marks_obtained,ug_sem_9_sub_17_total_marks,ug_sem_9_sub_18_name,
                 ug_sem_9_sub_18_marks_obtained,ug_sem_9_sub_18_total_marks,ug_sem_9_sub_19_name,
                 ug_sem_9_sub_19_marks_obtained,ug_sem_9_sub_19_total_marks,ug_sem_9_sub_20_name,
                 ug_sem_9_sub_20_marks_obtained,ug_sem_9_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_ug_sem_10'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch ug_sem_9_info from the database
            cursor.execute("SELECT * FROM ug_sem_9 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_9_info = cursor.fetchone()

            # Pass the ug_sem_9_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_9.html', ug_sem_9=ug_sem_9_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_ug_sem_10', methods=['GET', 'POST'])
def form_ug_sem_10():
    try:
        if request.method == 'POST':
            return form_ug_sem_10_post()
        else:
            # Fetch ug_sem_10_info from the database
            cursor.execute("SELECT * FROM ug_sem_10 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_10_info = cursor.fetchone()

            # If ug_sem_10_info is None, create a default ug_sem_10_info object
            if ug_sem_10_info is None:
                ug_sem_10_info = {
                    'ug_enrollment_no': '',
                    'ug_sem_10_session': '',
                    'ug_sem_10_roll_no': '',
                    'ug_sem_10_result': '',
                    'ug_sem_10_sub_1_name': '',
                    'ug_sem_10_sub_1_marks_obtained': '',
                    'ug_sem_10_sub_1_total_marks': '',
                    'ug_sem_10_sub_2_name': '',
                    'ug_sem_10_sub_2_marks_obtained': '',
                    'ug_sem_10_sub_2_total_marks': '',
                    'ug_sem_10_sub_3_name': '',
                    'ug_sem_10_sub_3_marks_obtained': '',
                    'ug_sem_10_sub_3_total_marks': '',
                    'ug_sem_10_sub_4_name': '',
                    'ug_sem_10_sub_4_marks_obtained': '',
                    'ug_sem_10_sub_4_total_marks': '',
                    'ug_sem_10_sub_5_name': '',
                    'ug_sem_10_sub_5_marks_obtained': '',
                    'ug_sem_10_sub_5_total_marks': '',
                    'ug_sem_10_sub_6_name': '',
                    'ug_sem_10_sub_6_marks_obtained': '',
                    'ug_sem_10_sub_6_total_marks': '',
                    'ug_sem_10_sub_7_name': '',
                    'ug_sem_10_sub_7_marks_obtained': '',
                    'ug_sem_10_sub_7_total_marks': '',
                    'ug_sem_10_sub_8_name': '',
                    'ug_sem_10_sub_8_marks_obtained': '',
                    'ug_sem_10_sub_8_total_marks': '',
                    'ug_sem_10_sub_9_name': '',
                    'ug_sem_10_sub_9_marks_obtained': '',
                    'ug_sem_10_sub_9_total_marks': '',
                    'ug_sem_10_sub_10_name': '',
                    'ug_sem_10_sub_10_marks_obtained': '',
                    'ug_sem_10_sub_10_total_marks': '',
                    'ug_sem_10_sub_11_name': '',
                    'ug_sem_10_sub_11_marks_obtained': '',
                    'ug_sem_10_sub_11_total_marks': '',
                    'ug_sem_10_sub_12_name': '',
                    'ug_sem_10_sub_12_marks_obtained': '',
                    'ug_sem_10_sub_12_total_marks': '',
                    'ug_sem_10_sub_13_name': '',
                    'ug_sem_10_sub_13_marks_obtained': '',
                    'ug_sem_10_sub_13_total_marks': '',
                    'ug_sem_10_sub_14_name': '',
                    'ug_sem_10_sub_14_marks_obtained': '',
                    'ug_sem_10_sub_14_total_marks': '',
                    'ug_sem_10_sub_15_name': '',
                    'ug_sem_10_sub_15_marks_obtained': '',
                    'ug_sem_10_sub_15_total_marks': '',
                    'ug_sem_10_sub_16_name': '',
                    'ug_sem_10_sub_16_marks_obtained': '',
                    'ug_sem_10_sub_16_total_marks': '',
                    'ug_sem_10_sub_17_name': '',
                    'ug_sem_10_sub_17_marks_obtained': '',
                    'ug_sem_10_sub_17_total_marks': '',
                    'ug_sem_10_sub_18_name': '',
                    'ug_sem_10_sub_18_marks_obtained': '',
                    'ug_sem_10_sub_18_total_marks': '',
                    'ug_sem_10_sub_19_name': '',
                    'ug_sem_10_sub_19_marks_obtained': '',
                    'ug_sem_10_sub_19_total_marks': '',
                    'ug_sem_10_sub_20_name': '',
                    'ug_sem_10_sub_20_marks_obtained': '',
                    'ug_sem_10_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the ug_sem_10_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_10.html', ug_sem_10=ug_sem_10_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_ug_sem_10_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            ug_enrollment_no = request.form['ug_enrollment_no']
            ug_sem_10_session = request.form['ug_sem_10_session']
            ug_sem_10_roll_no = request.form['ug_sem_10_roll_no']
            ug_sem_10_result = request.form['ug_sem_10_result']
            ug_sem_10_sub_1_name = request.form['ug_sem_10_sub_1_name']
            ug_sem_10_sub_1_marks_obtained = request.form['ug_sem_10_sub_1_marks_obtained']
            ug_sem_10_sub_1_total_marks = request.form['ug_sem_10_sub_1_total_marks']
            ug_sem_10_sub_2_name = request.form['ug_sem_10_sub_2_name']
            ug_sem_10_sub_2_marks_obtained = request.form['ug_sem_10_sub_2_marks_obtained']
            ug_sem_10_sub_2_total_marks = request.form['ug_sem_10_sub_2_total_marks']
            ug_sem_10_sub_3_name = request.form['ug_sem_10_sub_3_name']
            ug_sem_10_sub_3_marks_obtained = request.form['ug_sem_10_sub_3_marks_obtained']
            ug_sem_10_sub_3_total_marks = request.form['ug_sem_10_sub_3_total_marks']
            ug_sem_10_sub_4_name = request.form['ug_sem_10_sub_4_name']
            ug_sem_10_sub_4_marks_obtained = request.form['ug_sem_10_sub_4_marks_obtained']
            ug_sem_10_sub_4_total_marks = request.form['ug_sem_10_sub_4_total_marks']
            ug_sem_10_sub_5_name = request.form['ug_sem_10_sub_5_name']
            ug_sem_10_sub_5_marks_obtained = request.form['ug_sem_10_sub_5_marks_obtained']
            ug_sem_10_sub_5_total_marks = request.form['ug_sem_10_sub_5_total_marks']
            ug_sem_10_sub_6_name = request.form['ug_sem_10_sub_6_name']
            ug_sem_10_sub_6_marks_obtained = request.form['ug_sem_10_sub_6_marks_obtained']
            ug_sem_10_sub_6_total_marks = request.form['ug_sem_10_sub_6_total_marks']
            ug_sem_10_sub_7_name = request.form['ug_sem_10_sub_7_name']
            ug_sem_10_sub_7_marks_obtained = request.form['ug_sem_10_sub_7_marks_obtained']
            ug_sem_10_sub_7_total_marks = request.form['ug_sem_10_sub_7_total_marks']
            ug_sem_10_sub_8_name = request.form['ug_sem_10_sub_8_name']
            ug_sem_10_sub_8_marks_obtained = request.form['ug_sem_10_sub_8_marks_obtained']
            ug_sem_10_sub_8_total_marks = request.form['ug_sem_10_sub_8_total_marks']
            ug_sem_10_sub_9_name = request.form['ug_sem_10_sub_9_name']
            ug_sem_10_sub_9_marks_obtained = request.form['ug_sem_10_sub_9_marks_obtained']
            ug_sem_10_sub_9_total_marks = request.form['ug_sem_10_sub_9_total_marks']
            ug_sem_10_sub_10_name = request.form['ug_sem_10_sub_10_name']
            ug_sem_10_sub_10_marks_obtained = request.form['ug_sem_10_sub_10_marks_obtained']
            ug_sem_10_sub_10_total_marks = request.form['ug_sem_10_sub_10_total_marks']
            ug_sem_10_sub_11_name = request.form['ug_sem_10_sub_11_name']
            ug_sem_10_sub_11_marks_obtained = request.form['ug_sem_10_sub_11_marks_obtained']
            ug_sem_10_sub_11_total_marks = request.form['ug_sem_10_sub_11_total_marks']
            ug_sem_10_sub_12_name = request.form['ug_sem_10_sub_12_name']
            ug_sem_10_sub_12_marks_obtained = request.form['ug_sem_10_sub_12_marks_obtained']
            ug_sem_10_sub_12_total_marks = request.form['ug_sem_10_sub_12_total_marks']
            ug_sem_10_sub_13_name = request.form['ug_sem_10_sub_13_name']
            ug_sem_10_sub_13_marks_obtained = request.form['ug_sem_10_sub_13_marks_obtained']
            ug_sem_10_sub_13_total_marks = request.form['ug_sem_10_sub_13_total_marks']
            ug_sem_10_sub_14_name = request.form['ug_sem_10_sub_14_name']
            ug_sem_10_sub_14_marks_obtained = request.form['ug_sem_10_sub_14_marks_obtained']
            ug_sem_10_sub_14_total_marks = request.form['ug_sem_10_sub_14_total_marks']
            ug_sem_10_sub_15_name = request.form['ug_sem_10_sub_15_name']
            ug_sem_10_sub_15_marks_obtained = request.form['ug_sem_10_sub_15_marks_obtained']
            ug_sem_10_sub_15_total_marks = request.form['ug_sem_10_sub_15_total_marks']
            ug_sem_10_sub_16_name = request.form['ug_sem_10_sub_16_name']
            ug_sem_10_sub_16_marks_obtained = request.form['ug_sem_10_sub_16_marks_obtained']
            ug_sem_10_sub_16_total_marks = request.form['ug_sem_10_sub_16_total_marks']
            ug_sem_10_sub_17_name = request.form['ug_sem_10_sub_17_name']
            ug_sem_10_sub_17_marks_obtained = request.form['ug_sem_10_sub_17_marks_obtained']
            ug_sem_10_sub_17_total_marks = request.form['ug_sem_10_sub_17_total_marks']
            ug_sem_10_sub_18_name = request.form['ug_sem_10_sub_18_name']
            ug_sem_10_sub_18_marks_obtained = request.form['ug_sem_10_sub_18_marks_obtained']
            ug_sem_10_sub_18_total_marks = request.form['ug_sem_10_sub_18_total_marks']
            ug_sem_10_sub_19_name = request.form['ug_sem_10_sub_19_name']
            ug_sem_10_sub_19_marks_obtained = request.form['ug_sem_10_sub_19_marks_obtained']
            ug_sem_10_sub_19_total_marks = request.form['ug_sem_10_sub_19_total_marks']
            ug_sem_10_sub_20_name = request.form['ug_sem_10_sub_20_name']
            ug_sem_10_sub_20_marks_obtained = request.form['ug_sem_10_sub_20_marks_obtained']
            ug_sem_10_sub_20_total_marks = request.form['ug_sem_10_sub_20_total_marks']


            # Update ug_sem_10_info in the database
            cursor.execute("""
                UPDATE ug_sem_10
                SET ug_enrollment_no = ?, ug_sem_10_session = ?, ug_sem_10_roll_no = ?, ug_sem_10_result = ?, ug_sem_10_sub_1_name = ?, ug_sem_10_sub_1_marks_obtained = ?, ug_sem_10_sub_1_total_marks = ?, ug_sem_10_sub_2_name = ?, ug_sem_10_sub_2_marks_obtained = ?, ug_sem_10_sub_2_total_marks = ?, ug_sem_10_sub_3_name = ?, ug_sem_10_sub_3_marks_obtained = ?, ug_sem_10_sub_3_total_marks = ?, ug_sem_10_sub_4_name = ?, ug_sem_10_sub_4_marks_obtained = ?, ug_sem_10_sub_4_total_marks = ?, ug_sem_10_sub_5_name = ?, ug_sem_10_sub_5_marks_obtained = ?, ug_sem_10_sub_5_total_marks = ?, ug_sem_10_sub_6_name = ?, ug_sem_10_sub_6_marks_obtained = ?, ug_sem_10_sub_6_total_marks = ?, ug_sem_10_sub_7_name = ?, ug_sem_10_sub_7_marks_obtained = ?, ug_sem_10_sub_7_total_marks = ?, ug_sem_10_sub_8_name = ?, ug_sem_10_sub_8_marks_obtained = ?, ug_sem_10_sub_8_total_marks = ?, ug_sem_10_sub_9_name = ?, ug_sem_10_sub_9_marks_obtained = ?, ug_sem_10_sub_9_total_marks = ?, ug_sem_10_sub_10_name = ?, ug_sem_10_sub_10_marks_obtained = ?, ug_sem_10_sub_10_total_marks = ?, ug_sem_10_sub_11_name = ?, ug_sem_10_sub_11_marks_obtained = ?, ug_sem_10_sub_11_total_marks = ?, ug_sem_10_sub_12_name = ?, ug_sem_10_sub_12_marks_obtained = ?, ug_sem_10_sub_12_total_marks = ?, ug_sem_10_sub_13_name = ?, ug_sem_10_sub_13_marks_obtained = ?, ug_sem_10_sub_13_total_marks = ?, ug_sem_10_sub_14_name = ?, ug_sem_10_sub_14_marks_obtained = ?, ug_sem_10_sub_14_total_marks = ?, ug_sem_10_sub_15_name = ?, ug_sem_10_sub_15_marks_obtained = ?, ug_sem_10_sub_15_total_marks = ?, ug_sem_10_sub_16_name = ?, ug_sem_10_sub_16_marks_obtained = ?, ug_sem_10_sub_16_total_marks = ?, ug_sem_10_sub_17_name = ?, ug_sem_10_sub_17_marks_obtained = ?, ug_sem_10_sub_17_total_marks = ?, ug_sem_10_sub_18_name = ?, ug_sem_10_sub_18_marks_obtained = ?, ug_sem_10_sub_18_total_marks = ?, ug_sem_10_sub_19_name = ?, ug_sem_10_sub_19_marks_obtained = ?, ug_sem_10_sub_19_total_marks = ?, ug_sem_10_sub_20_name = ?, ug_sem_10_sub_20_marks_obtained = ?, ug_sem_10_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(ug_enrollment_no,ug_sem_10_session,ug_sem_10_roll_no,ug_sem_10_result,ug_sem_10_sub_1_name,
                 ug_sem_10_sub_1_marks_obtained,ug_sem_10_sub_1_total_marks,ug_sem_10_sub_2_name,
                 ug_sem_10_sub_2_marks_obtained,ug_sem_10_sub_2_total_marks,ug_sem_10_sub_3_name,
                 ug_sem_10_sub_3_marks_obtained,ug_sem_10_sub_3_total_marks,ug_sem_10_sub_4_name,
                 ug_sem_10_sub_4_marks_obtained,ug_sem_10_sub_4_total_marks,ug_sem_10_sub_5_name,
                 ug_sem_10_sub_5_marks_obtained,ug_sem_10_sub_5_total_marks,ug_sem_10_sub_6_name,
                 ug_sem_10_sub_6_marks_obtained,ug_sem_10_sub_6_total_marks,ug_sem_10_sub_7_name,
                 ug_sem_10_sub_7_marks_obtained,ug_sem_10_sub_7_total_marks,ug_sem_10_sub_8_name,
                 ug_sem_10_sub_8_marks_obtained,ug_sem_10_sub_8_total_marks,ug_sem_10_sub_9_name,
                 ug_sem_10_sub_9_marks_obtained,ug_sem_10_sub_9_total_marks,ug_sem_10_sub_10_name,
                 ug_sem_10_sub_10_marks_obtained,ug_sem_10_sub_10_total_marks,ug_sem_10_sub_11_name,
                 ug_sem_10_sub_11_marks_obtained,ug_sem_10_sub_11_total_marks,ug_sem_10_sub_12_name,
                 ug_sem_10_sub_12_marks_obtained,ug_sem_10_sub_12_total_marks,ug_sem_10_sub_13_name,
                 ug_sem_10_sub_13_marks_obtained,ug_sem_10_sub_13_total_marks,ug_sem_10_sub_14_name,
                 ug_sem_10_sub_14_marks_obtained,ug_sem_10_sub_14_total_marks,ug_sem_10_sub_15_name,
                 ug_sem_10_sub_15_marks_obtained,ug_sem_10_sub_15_total_marks,ug_sem_10_sub_16_name,
                 ug_sem_10_sub_16_marks_obtained,ug_sem_10_sub_16_total_marks,ug_sem_10_sub_17_name,
                 ug_sem_10_sub_17_marks_obtained,ug_sem_10_sub_17_total_marks,ug_sem_10_sub_18_name,
                 ug_sem_10_sub_18_marks_obtained,ug_sem_10_sub_18_total_marks,ug_sem_10_sub_19_name,
                 ug_sem_10_sub_19_marks_obtained,ug_sem_10_sub_19_total_marks,ug_sem_10_sub_20_name,
                 ug_sem_10_sub_20_marks_obtained,ug_sem_10_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_pg_details'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch ug_sem_10_info from the database
            cursor.execute("SELECT * FROM ug_sem_10 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            ug_sem_10_info = cursor.fetchone()

            # Pass the ug_sem_10_info to the template
            return render_template('Student/student_info_forms/form_ug_sem_10.html', ug_sem_10=ug_sem_10_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_pg_details', methods=['GET', 'POST'])
def form_pg_details():
    if request.method == 'POST':
        return form_pg_details_post()
    else:
        # Fetch pg_details from the database
        cursor.execute("SELECT * FROM pg_details WHERE aadhaar_no = ?", (session['aadhaar_no'],))
        pg_details = cursor.fetchone()

        # If pg_details is None, create a default pg_details object
        if pg_details is None:
            pg_details = {
                'aadhaar_no': '',
                'pg_enrollment_no': '',
                'pg_admission_year': '',
                'pg_state': '',
                'pg_district': '',
                'pg_qualification_level': '',
                'pg_stream': '',
                'pg_institute_name': '',
                'pg_institute_code': '',
                'pg_board_university': '',
                'pg_course_name': '',
                'pg_course_duration': '',
                'pg_year_of_study': '',
                'pg_year_1_status': '',
                'pg_year_1_admission_year': '',
                'pg_sem_1_status': '',
                'pg_sem_1_session': '',
                'pg_sem_1_roll_no': '',
                'pg_sem_2_status': '',
                'pg_sem_2_session': '',
                'pg_sem_2_roll_no': '',
                'pg_year_2_status': '',
                'pg_year_2_admission_year': '',
                'pg_sem_3_status': '',
                'pg_sem_3_session': '',
                'pg_sem_3_roll_no': '',
                'pg_sem_4_status': '',
                'pg_sem_4_session': '',
                'pg_sem_4_roll_no': '',
                'pg_year_3_status': '',
                'pg_year_3_admission_year': '',
                'pg_sem_5_status': '',
                'pg_sem_5_session': '',
                'pg_sem_5_roll_no': '',
                'pg_year_4_status': '',
                'pg_year_4_admission_year': '',
                'pg_sem_6_status': '',
                'pg_sem_6_session': '',
                'pg_sem_6_roll_no': '',
                'pg_year_5_status': '',
                'pg_year_5_admission_year': '',
                'pg_sem_7_status': '',
                'pg_sem_7_session': '',
                'pg_sem_7_roll_no': '',
                'pg_sem_8_status': '',
                'pg_sem_8_session': '',
                'pg_sem_8_roll_no': '',
                'pg_sem_9_status': '',
                'pg_sem_9_session': '',
                'pg_sem_9_roll_no': '',
                'pg_sem_10_status': '',
                'pg_sem_10_session': '',
                'pg_sem_10_roll_no': ''
            }

        # Pass the pg_details to the template
        return render_template('Student/student_info_forms/form_pg_details.html', pg_details=pg_details)


def form_pg_details_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = request.form.get('aadhaar_no')
            pg_enrollment_no = request.form.get('pg_enrollment_no')
            pg_admission_year = request.form.get('pg_admission_year')
            pg_state = request.form.get('pg_state')
            pg_district = request.form.get('pg_district')
            pg_qualification_level = request.form.get('pg_qualification_level')
            pg_stream = request.form.get('pg_stream')
            pg_institute_name = request.form.get('pg_institute_name')
            pg_institute_code = request.form.get('pg_institute_code')
            pg_board_university = request.form.get('pg_board_university')
            pg_course_name = request.form.get('pg_course_name')
            pg_course_duration = request.form.get('pg_course_duration')
            pg_year_of_study = request.form.get('pg_year_of_study')
            pg_year_1_status = request.form.get('pg_year_1_status')
            pg_year_1_admission_year = request.form.get('pg_year_1_admission_year')
            pg_sem_1_status = request.form.get('pg_sem_1_status')
            pg_sem_1_session = request.form.get('pg_sem_1_session')
            pg_sem_1_roll_no = request.form.get('pg_sem_1_roll_no')
            pg_sem_2_status = request.form.get('pg_sem_2_status')
            pg_sem_2_session = request.form.get('pg_sem_2_session')
            pg_sem_2_roll_no = request.form.get('pg_sem_2_roll_no')
            pg_year_2_status = request.form.get('pg_year_2_status')
            pg_year_2_admission_year = request.form.get('pg_year_2_admission_year')
            pg_sem_3_status = request.form.get('pg_sem_3_status')
            pg_sem_3_session = request.form.get('pg_sem_3_session')
            pg_sem_3_roll_no = request.form.get('pg_sem_3_roll_no')
            pg_sem_4_status = request.form.get('pg_sem_4_status')
            pg_sem_4_session = request.form.get('pg_sem_4_session')
            pg_sem_4_roll_no = request.form.get('pg_sem_4_roll_no')
            pg_year_3_status = request.form.get('pg_year_3_status')
            pg_year_3_admission_year = request.form.get('pg_year_3_admission_year')
            pg_sem_5_status = request.form.get('pg_sem_5_status')
            pg_sem_5_session = request.form.get('pg_sem_5_session')
            pg_sem_5_roll_no = request.form.get('pg_sem_5_roll_no')
            pg_sem_6_status = request.form.get('pg_sem_6_status')
            pg_sem_6_session = request.form.get('pg_sem_6_session')
            pg_sem_6_roll_no = request.form.get('pg_sem_6_roll_no')
            pg_year_4_status = request.form.get('pg_year_4_status')
            pg_year_4_admission_year = request.form.get('pg_year_4_admission_year')
            pg_sem_7_status = request.form.get('pg_sem_7_status')
            pg_sem_7_session = request.form.get('pg_sem_7_session')
            pg_sem_7_roll_no = request.form.get('pg_sem_7_roll_no')
            pg_sem_8_status = request.form.get('pg_sem_8_status')
            pg_sem_8_session = request.form.get('pg_sem_8_session')
            pg_sem_8_roll_no = request.form.get('pg_sem_8_roll_no')
            pg_year_5_status = request.form.get('pg_year_5_status')
            pg_year_5_admission_year = request.form.get('pg_year_5_admission_year')
            pg_sem_9_status = request.form.get('pg_sem_9_status')
            pg_sem_9_session = request.form.get('pg_sem_9_session')
            pg_sem_9_roll_no = request.form.get('pg_sem_9_roll_no')
            pg_sem_10_status = request.form.get('pg_sem_10_status')
            pg_sem_10_session = request.form.get('pg_sem_10_session')
            pg_sem_10_roll_no = request.form.get('pg_sem_10_roll_no')

            # Update pg_details in the database
            cursor.execute("""
                UPDATE pg_details
                SET pg_enrollment_no = ?, pg_admission_year = ?, pg_state = ?, pg_district = ?,
                    pg_qualification_level = ?, pg_stream = ?, pg_institute_name = ?, pg_institute_code = ?,
                    pg_board_university = ?, pg_course_name = ?, pg_course_duration = ?, pg_year_of_study = ?,
                    pg_year_1_status = ?, pg_year_1_admission_year = ?, pg_sem_1_status = ?, pg_sem_1_session = ?,
                    pg_sem_1_roll_no = ?, pg_sem_2_status = ?, pg_sem_2_session = ?, pg_sem_2_roll_no = ?,
                    pg_year_2_status = ?, pg_year_2_admission_year = ?, pg_sem_3_status = ?, pg_sem_3_session = ?,
                    pg_sem_3_roll_no = ?, pg_sem_4_status = ?, pg_sem_4_session = ?, pg_sem_4_roll_no = ?,
                    pg_year_3_status = ?, pg_year_3_admission_year = ?, pg_sem_5_status = ?, pg_sem_5_session = ?,
                    pg_sem_5_roll_no = ?, pg_sem_6_status = ?, pg_sem_6_session = ?, pg_sem_6_roll_no = ?,
                    pg_year_4_status = ?, pg_year_4_admission_year = ?, pg_sem_7_status = ?, pg_sem_7_session = ?,
                    pg_sem_7_roll_no = ?, pg_sem_8_status = ?, pg_sem_8_session = ?, pg_sem_8_roll_no = ?,
                    pg_year_5_status = ?, pg_year_5_admission_year = ?, pg_sem_9_status = ?, pg_sem_9_session = ?,
                    pg_sem_9_roll_no = ?, pg_sem_10_status = ?, pg_sem_10_session = ?, pg_sem_10_roll_no = ?
                WHERE aadhaar_no = ?
            """, (pg_enrollment_no, pg_admission_year, pg_state, pg_district, pg_qualification_level,
                  pg_stream, pg_institute_name, pg_institute_code, pg_board_university, pg_course_name,
                  pg_course_duration, pg_year_of_study, pg_year_1_status, pg_year_1_admission_year,
                  pg_sem_1_status, pg_sem_1_session, pg_sem_1_roll_no, pg_sem_2_status, pg_sem_2_session,
                  pg_sem_2_roll_no, pg_year_2_status, pg_year_2_admission_year, pg_sem_3_status, pg_sem_3_session,
                  pg_sem_3_roll_no, pg_sem_4_status, pg_sem_4_session, pg_sem_4_roll_no, pg_year_3_status,
                  pg_year_3_admission_year, pg_sem_5_status, pg_sem_5_session, pg_sem_5_roll_no, pg_sem_6_status,
                  pg_sem_6_session, pg_sem_6_roll_no, pg_year_4_status, pg_year_4_admission_year,
                  pg_sem_7_status, pg_sem_7_session, pg_sem_7_roll_no, pg_sem_8_status, pg_sem_8_session,
                  pg_sem_8_roll_no, pg_year_5_status, pg_year_5_admission_year, pg_sem_9_status, pg_sem_9_session,
                  pg_sem_9_roll_no, pg_sem_10_status, pg_sem_10_session, pg_sem_10_roll_no, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_pg_sem_1'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_12_info from the database
            cursor.execute("SELECT * FROM pg_details WHERE aadhaar_no = ?",(session['aadhaar_no'],))
            pg_details = cursor.fetchone()

            # Pass the pg_details to the template
            return render_template('Student/student_info_forms/form_pg_details.html', pg_details=pg_details)

    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_pg_sem_1', methods=['GET', 'POST'])
def form_pg_sem_1():
    try:
        if request.method == 'POST':
            return form_pg_sem_1_post()
        else:
            # Fetch pg_sem_1_info from the database
            cursor.execute("SELECT * FROM pg_sem_1 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_1_info = cursor.fetchone()

            # If pg_sem_1_info is None, create a default pg_sem_1_info object
            if pg_sem_1_info is None:
                pg_sem_1_info = {
                    'pg_enrollment_no': '',
                    'pg_sem_1_session': '',
                    'pg_sem_1_roll_no': '',
                    'pg_sem_1_result': '',
                    'pg_sem_1_sub_1_name': '',
                    'pg_sem_1_sub_1_marks_obtained': '',
                    'pg_sem_1_sub_1_total_marks': '',
                    'pg_sem_1_sub_2_name': '',
                    'pg_sem_1_sub_2_marks_obtained': '',
                    'pg_sem_1_sub_2_total_marks': '',
                    'pg_sem_1_sub_3_name': '',
                    'pg_sem_1_sub_3_marks_obtained': '',
                    'pg_sem_1_sub_3_total_marks': '',
                    'pg_sem_1_sub_4_name': '',
                    'pg_sem_1_sub_4_marks_obtained': '',
                    'pg_sem_1_sub_4_total_marks': '',
                    'pg_sem_1_sub_5_name': '',
                    'pg_sem_1_sub_5_marks_obtained': '',
                    'pg_sem_1_sub_5_total_marks': '',
                    'pg_sem_1_sub_6_name': '',
                    'pg_sem_1_sub_6_marks_obtained': '',
                    'pg_sem_1_sub_6_total_marks': '',
                    'pg_sem_1_sub_7_name': '',
                    'pg_sem_1_sub_7_marks_obtained': '',
                    'pg_sem_1_sub_7_total_marks': '',
                    'pg_sem_1_sub_8_name': '',
                    'pg_sem_1_sub_8_marks_obtained': '',
                    'pg_sem_1_sub_8_total_marks': '',
                    'pg_sem_1_sub_9_name': '',
                    'pg_sem_1_sub_9_marks_obtained': '',
                    'pg_sem_1_sub_9_total_marks': '',
                    'pg_sem_1_sub_10_name': '',
                    'pg_sem_1_sub_10_marks_obtained': '',
                    'pg_sem_1_sub_10_total_marks': '',
                    'pg_sem_1_sub_11_name': '',
                    'pg_sem_1_sub_11_marks_obtained': '',
                    'pg_sem_1_sub_11_total_marks': '',
                    'pg_sem_1_sub_12_name': '',
                    'pg_sem_1_sub_12_marks_obtained': '',
                    'pg_sem_1_sub_12_total_marks': '',
                    'pg_sem_1_sub_13_name': '',
                    'pg_sem_1_sub_13_marks_obtained': '',
                    'pg_sem_1_sub_13_total_marks': '',
                    'pg_sem_1_sub_14_name': '',
                    'pg_sem_1_sub_14_marks_obtained': '',
                    'pg_sem_1_sub_14_total_marks': '',
                    'pg_sem_1_sub_15_name': '',
                    'pg_sem_1_sub_15_marks_obtained': '',
                    'pg_sem_1_sub_15_total_marks': '',
                    'pg_sem_1_sub_16_name': '',
                    'pg_sem_1_sub_16_marks_obtained': '',
                    'pg_sem_1_sub_16_total_marks': '',
                    'pg_sem_1_sub_17_name': '',
                    'pg_sem_1_sub_17_marks_obtained': '',
                    'pg_sem_1_sub_17_total_marks': '',
                    'pg_sem_1_sub_18_name': '',
                    'pg_sem_1_sub_18_marks_obtained': '',
                    'pg_sem_1_sub_18_total_marks': '',
                    'pg_sem_1_sub_19_name': '',
                    'pg_sem_1_sub_19_marks_obtained': '',
                    'pg_sem_1_sub_19_total_marks': '',
                    'pg_sem_1_sub_20_name': '',
                    'pg_sem_1_sub_20_marks_obtained': '',
                    'pg_sem_1_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the pg_sem_1_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_1.html', pg_sem_1=pg_sem_1_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_pg_sem_1_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            pg_enrollment_no = request.form['pg_enrollment_no']
            pg_sem_1_session = request.form['pg_sem_1_session']
            pg_sem_1_roll_no = request.form['pg_sem_1_roll_no']
            pg_sem_1_result = request.form['pg_sem_1_result']
            pg_sem_1_sub_1_name = request.form['pg_sem_1_sub_1_name']
            pg_sem_1_sub_1_marks_obtained = request.form['pg_sem_1_sub_1_marks_obtained']
            pg_sem_1_sub_1_total_marks = request.form['pg_sem_1_sub_1_total_marks']
            pg_sem_1_sub_2_name = request.form['pg_sem_1_sub_2_name']
            pg_sem_1_sub_2_marks_obtained = request.form['pg_sem_1_sub_2_marks_obtained']
            pg_sem_1_sub_2_total_marks = request.form['pg_sem_1_sub_2_total_marks']
            pg_sem_1_sub_3_name = request.form['pg_sem_1_sub_3_name']
            pg_sem_1_sub_3_marks_obtained = request.form['pg_sem_1_sub_3_marks_obtained']
            pg_sem_1_sub_3_total_marks = request.form['pg_sem_1_sub_3_total_marks']
            pg_sem_1_sub_4_name = request.form['pg_sem_1_sub_4_name']
            pg_sem_1_sub_4_marks_obtained = request.form['pg_sem_1_sub_4_marks_obtained']
            pg_sem_1_sub_4_total_marks = request.form['pg_sem_1_sub_4_total_marks']
            pg_sem_1_sub_5_name = request.form['pg_sem_1_sub_5_name']
            pg_sem_1_sub_5_marks_obtained = request.form['pg_sem_1_sub_5_marks_obtained']
            pg_sem_1_sub_5_total_marks = request.form['pg_sem_1_sub_5_total_marks']
            pg_sem_1_sub_6_name = request.form['pg_sem_1_sub_6_name']
            pg_sem_1_sub_6_marks_obtained = request.form['pg_sem_1_sub_6_marks_obtained']
            pg_sem_1_sub_6_total_marks = request.form['pg_sem_1_sub_6_total_marks']
            pg_sem_1_sub_7_name = request.form['pg_sem_1_sub_7_name']
            pg_sem_1_sub_7_marks_obtained = request.form['pg_sem_1_sub_7_marks_obtained']
            pg_sem_1_sub_7_total_marks = request.form['pg_sem_1_sub_7_total_marks']
            pg_sem_1_sub_8_name = request.form['pg_sem_1_sub_8_name']
            pg_sem_1_sub_8_marks_obtained = request.form['pg_sem_1_sub_8_marks_obtained']
            pg_sem_1_sub_8_total_marks = request.form['pg_sem_1_sub_8_total_marks']
            pg_sem_1_sub_9_name = request.form['pg_sem_1_sub_9_name']
            pg_sem_1_sub_9_marks_obtained = request.form['pg_sem_1_sub_9_marks_obtained']
            pg_sem_1_sub_9_total_marks = request.form['pg_sem_1_sub_9_total_marks']
            pg_sem_1_sub_10_name = request.form['pg_sem_1_sub_10_name']
            pg_sem_1_sub_10_marks_obtained = request.form['pg_sem_1_sub_10_marks_obtained']
            pg_sem_1_sub_10_total_marks = request.form['pg_sem_1_sub_10_total_marks']
            pg_sem_1_sub_11_name = request.form['pg_sem_1_sub_11_name']
            pg_sem_1_sub_11_marks_obtained = request.form['pg_sem_1_sub_11_marks_obtained']
            pg_sem_1_sub_11_total_marks = request.form['pg_sem_1_sub_11_total_marks']
            pg_sem_1_sub_12_name = request.form['pg_sem_1_sub_12_name']
            pg_sem_1_sub_12_marks_obtained = request.form['pg_sem_1_sub_12_marks_obtained']
            pg_sem_1_sub_12_total_marks = request.form['pg_sem_1_sub_12_total_marks']
            pg_sem_1_sub_13_name = request.form['pg_sem_1_sub_13_name']
            pg_sem_1_sub_13_marks_obtained = request.form['pg_sem_1_sub_13_marks_obtained']
            pg_sem_1_sub_13_total_marks = request.form['pg_sem_1_sub_13_total_marks']
            pg_sem_1_sub_14_name = request.form['pg_sem_1_sub_14_name']
            pg_sem_1_sub_14_marks_obtained = request.form['pg_sem_1_sub_14_marks_obtained']
            pg_sem_1_sub_14_total_marks = request.form['pg_sem_1_sub_14_total_marks']
            pg_sem_1_sub_15_name = request.form['pg_sem_1_sub_15_name']
            pg_sem_1_sub_15_marks_obtained = request.form['pg_sem_1_sub_15_marks_obtained']
            pg_sem_1_sub_15_total_marks = request.form['pg_sem_1_sub_15_total_marks']
            pg_sem_1_sub_16_name = request.form['pg_sem_1_sub_16_name']
            pg_sem_1_sub_16_marks_obtained = request.form['pg_sem_1_sub_16_marks_obtained']
            pg_sem_1_sub_16_total_marks = request.form['pg_sem_1_sub_16_total_marks']
            pg_sem_1_sub_17_name = request.form['pg_sem_1_sub_17_name']
            pg_sem_1_sub_17_marks_obtained = request.form['pg_sem_1_sub_17_marks_obtained']
            pg_sem_1_sub_17_total_marks = request.form['pg_sem_1_sub_17_total_marks']
            pg_sem_1_sub_18_name = request.form['pg_sem_1_sub_18_name']
            pg_sem_1_sub_18_marks_obtained = request.form['pg_sem_1_sub_18_marks_obtained']
            pg_sem_1_sub_18_total_marks = request.form['pg_sem_1_sub_18_total_marks']
            pg_sem_1_sub_19_name = request.form['pg_sem_1_sub_19_name']
            pg_sem_1_sub_19_marks_obtained = request.form['pg_sem_1_sub_19_marks_obtained']
            pg_sem_1_sub_19_total_marks = request.form['pg_sem_1_sub_19_total_marks']
            pg_sem_1_sub_20_name = request.form['pg_sem_1_sub_20_name']
            pg_sem_1_sub_20_marks_obtained = request.form['pg_sem_1_sub_20_marks_obtained']
            pg_sem_1_sub_20_total_marks = request.form['pg_sem_1_sub_20_total_marks']


            # Update pg_sem_1_info in the database
            cursor.execute("""
                UPDATE pg_sem_1
                SET pg_enrollment_no = ?, pg_sem_1_session = ?, pg_sem_1_roll_no = ?, pg_sem_1_result = ?, pg_sem_1_sub_1_name = ?, pg_sem_1_sub_1_marks_obtained = ?, pg_sem_1_sub_1_total_marks = ?, pg_sem_1_sub_2_name = ?, pg_sem_1_sub_2_marks_obtained = ?, pg_sem_1_sub_2_total_marks = ?, pg_sem_1_sub_3_name = ?, pg_sem_1_sub_3_marks_obtained = ?, pg_sem_1_sub_3_total_marks = ?, pg_sem_1_sub_4_name = ?, pg_sem_1_sub_4_marks_obtained = ?, pg_sem_1_sub_4_total_marks = ?, pg_sem_1_sub_5_name = ?, pg_sem_1_sub_5_marks_obtained = ?, pg_sem_1_sub_5_total_marks = ?, pg_sem_1_sub_6_name = ?, pg_sem_1_sub_6_marks_obtained = ?, pg_sem_1_sub_6_total_marks = ?, pg_sem_1_sub_7_name = ?, pg_sem_1_sub_7_marks_obtained = ?, pg_sem_1_sub_7_total_marks = ?, pg_sem_1_sub_8_name = ?, pg_sem_1_sub_8_marks_obtained = ?, pg_sem_1_sub_8_total_marks = ?, pg_sem_1_sub_9_name = ?, pg_sem_1_sub_9_marks_obtained = ?, pg_sem_1_sub_9_total_marks = ?, pg_sem_1_sub_10_name = ?, pg_sem_1_sub_10_marks_obtained = ?, pg_sem_1_sub_10_total_marks = ?, pg_sem_1_sub_11_name = ?, pg_sem_1_sub_11_marks_obtained = ?, pg_sem_1_sub_11_total_marks = ?, pg_sem_1_sub_12_name = ?, pg_sem_1_sub_12_marks_obtained = ?, pg_sem_1_sub_12_total_marks = ?, pg_sem_1_sub_13_name = ?, pg_sem_1_sub_13_marks_obtained = ?, pg_sem_1_sub_13_total_marks = ?, pg_sem_1_sub_14_name = ?, pg_sem_1_sub_14_marks_obtained = ?, pg_sem_1_sub_14_total_marks = ?, pg_sem_1_sub_15_name = ?, pg_sem_1_sub_15_marks_obtained = ?, pg_sem_1_sub_15_total_marks = ?, pg_sem_1_sub_16_name = ?, pg_sem_1_sub_16_marks_obtained = ?, pg_sem_1_sub_16_total_marks = ?, pg_sem_1_sub_17_name = ?, pg_sem_1_sub_17_marks_obtained = ?, pg_sem_1_sub_17_total_marks = ?, pg_sem_1_sub_18_name = ?, pg_sem_1_sub_18_marks_obtained = ?, pg_sem_1_sub_18_total_marks = ?, pg_sem_1_sub_19_name = ?, pg_sem_1_sub_19_marks_obtained = ?, pg_sem_1_sub_19_total_marks = ?, pg_sem_1_sub_20_name = ?, pg_sem_1_sub_20_marks_obtained = ?, pg_sem_1_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(pg_enrollment_no,pg_sem_1_session,pg_sem_1_roll_no,pg_sem_1_result,pg_sem_1_sub_1_name,
                 pg_sem_1_sub_1_marks_obtained,pg_sem_1_sub_1_total_marks,pg_sem_1_sub_2_name,
                 pg_sem_1_sub_2_marks_obtained,pg_sem_1_sub_2_total_marks,pg_sem_1_sub_3_name,
                 pg_sem_1_sub_3_marks_obtained,pg_sem_1_sub_3_total_marks,pg_sem_1_sub_4_name,
                 pg_sem_1_sub_4_marks_obtained,pg_sem_1_sub_4_total_marks,pg_sem_1_sub_5_name,
                 pg_sem_1_sub_5_marks_obtained,pg_sem_1_sub_5_total_marks,pg_sem_1_sub_6_name,
                 pg_sem_1_sub_6_marks_obtained,pg_sem_1_sub_6_total_marks,pg_sem_1_sub_7_name,
                 pg_sem_1_sub_7_marks_obtained,pg_sem_1_sub_7_total_marks,pg_sem_1_sub_8_name,
                 pg_sem_1_sub_8_marks_obtained,pg_sem_1_sub_8_total_marks,pg_sem_1_sub_9_name,
                 pg_sem_1_sub_9_marks_obtained,pg_sem_1_sub_9_total_marks,pg_sem_1_sub_10_name,
                 pg_sem_1_sub_10_marks_obtained,pg_sem_1_sub_10_total_marks,pg_sem_1_sub_11_name,
                 pg_sem_1_sub_11_marks_obtained,pg_sem_1_sub_11_total_marks,pg_sem_1_sub_12_name,
                 pg_sem_1_sub_12_marks_obtained,pg_sem_1_sub_12_total_marks,pg_sem_1_sub_13_name,
                 pg_sem_1_sub_13_marks_obtained,pg_sem_1_sub_13_total_marks,pg_sem_1_sub_14_name,
                 pg_sem_1_sub_14_marks_obtained,pg_sem_1_sub_14_total_marks,pg_sem_1_sub_15_name,
                 pg_sem_1_sub_15_marks_obtained,pg_sem_1_sub_15_total_marks,pg_sem_1_sub_16_name,
                 pg_sem_1_sub_16_marks_obtained,pg_sem_1_sub_16_total_marks,pg_sem_1_sub_17_name,
                 pg_sem_1_sub_17_marks_obtained,pg_sem_1_sub_17_total_marks,pg_sem_1_sub_18_name,
                 pg_sem_1_sub_18_marks_obtained,pg_sem_1_sub_18_total_marks,pg_sem_1_sub_19_name,
                 pg_sem_1_sub_19_marks_obtained,pg_sem_1_sub_19_total_marks,pg_sem_1_sub_20_name,
                 pg_sem_1_sub_20_marks_obtained,pg_sem_1_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_pg_sem_2'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch pg_sem_1_info from the database
            cursor.execute("SELECT * FROM pg_sem_1 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_1_info = cursor.fetchone()

            # Pass the pg_sem_1_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_1.html', pg_sem_1=pg_sem_1_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_pg_sem_2', methods=['GET', 'POST'])
def form_pg_sem_2():
    try:
        if request.method == 'POST':
            return form_pg_sem_2_post()
        else:
            # Fetch pg_sem_2_info from the database
            cursor.execute("SELECT * FROM pg_sem_2 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_2_info = cursor.fetchone()

            # If pg_sem_2_info is None, create a default pg_sem_2_info object
            if pg_sem_2_info is None:
                pg_sem_2_info = {
                    'pg_enrollment_no': '',
                    'pg_sem_2_session': '',
                    'pg_sem_2_roll_no': '',
                    'pg_sem_2_result': '',
                    'pg_sem_2_sub_1_name': '',
                    'pg_sem_2_sub_1_marks_obtained': '',
                    'pg_sem_2_sub_1_total_marks': '',
                    'pg_sem_2_sub_2_name': '',
                    'pg_sem_2_sub_2_marks_obtained': '',
                    'pg_sem_2_sub_2_total_marks': '',
                    'pg_sem_2_sub_3_name': '',
                    'pg_sem_2_sub_3_marks_obtained': '',
                    'pg_sem_2_sub_3_total_marks': '',
                    'pg_sem_2_sub_4_name': '',
                    'pg_sem_2_sub_4_marks_obtained': '',
                    'pg_sem_2_sub_4_total_marks': '',
                    'pg_sem_2_sub_5_name': '',
                    'pg_sem_2_sub_5_marks_obtained': '',
                    'pg_sem_2_sub_5_total_marks': '',
                    'pg_sem_2_sub_6_name': '',
                    'pg_sem_2_sub_6_marks_obtained': '',
                    'pg_sem_2_sub_6_total_marks': '',
                    'pg_sem_2_sub_7_name': '',
                    'pg_sem_2_sub_7_marks_obtained': '',
                    'pg_sem_2_sub_7_total_marks': '',
                    'pg_sem_2_sub_8_name': '',
                    'pg_sem_2_sub_8_marks_obtained': '',
                    'pg_sem_2_sub_8_total_marks': '',
                    'pg_sem_2_sub_9_name': '',
                    'pg_sem_2_sub_9_marks_obtained': '',
                    'pg_sem_2_sub_9_total_marks': '',
                    'pg_sem_2_sub_10_name': '',
                    'pg_sem_2_sub_10_marks_obtained': '',
                    'pg_sem_2_sub_10_total_marks': '',
                    'pg_sem_2_sub_11_name': '',
                    'pg_sem_2_sub_11_marks_obtained': '',
                    'pg_sem_2_sub_11_total_marks': '',
                    'pg_sem_2_sub_12_name': '',
                    'pg_sem_2_sub_12_marks_obtained': '',
                    'pg_sem_2_sub_12_total_marks': '',
                    'pg_sem_2_sub_13_name': '',
                    'pg_sem_2_sub_13_marks_obtained': '',
                    'pg_sem_2_sub_13_total_marks': '',
                    'pg_sem_2_sub_14_name': '',
                    'pg_sem_2_sub_14_marks_obtained': '',
                    'pg_sem_2_sub_14_total_marks': '',
                    'pg_sem_2_sub_15_name': '',
                    'pg_sem_2_sub_15_marks_obtained': '',
                    'pg_sem_2_sub_15_total_marks': '',
                    'pg_sem_2_sub_16_name': '',
                    'pg_sem_2_sub_16_marks_obtained': '',
                    'pg_sem_2_sub_16_total_marks': '',
                    'pg_sem_2_sub_17_name': '',
                    'pg_sem_2_sub_17_marks_obtained': '',
                    'pg_sem_2_sub_17_total_marks': '',
                    'pg_sem_2_sub_18_name': '',
                    'pg_sem_2_sub_18_marks_obtained': '',
                    'pg_sem_2_sub_18_total_marks': '',
                    'pg_sem_2_sub_19_name': '',
                    'pg_sem_2_sub_19_marks_obtained': '',
                    'pg_sem_2_sub_19_total_marks': '',
                    'pg_sem_2_sub_20_name': '',
                    'pg_sem_2_sub_20_marks_obtained': '',
                    'pg_sem_2_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the pg_sem_2_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_2.html', pg_sem_2=pg_sem_2_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_pg_sem_2_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            pg_enrollment_no = request.form['pg_enrollment_no']
            pg_sem_2_session = request.form['pg_sem_2_session']
            pg_sem_2_roll_no = request.form['pg_sem_2_roll_no']
            pg_sem_2_result = request.form['pg_sem_2_result']
            pg_sem_2_sub_1_name = request.form['pg_sem_2_sub_1_name']
            pg_sem_2_sub_1_marks_obtained = request.form['pg_sem_2_sub_1_marks_obtained']
            pg_sem_2_sub_1_total_marks = request.form['pg_sem_2_sub_1_total_marks']
            pg_sem_2_sub_2_name = request.form['pg_sem_2_sub_2_name']
            pg_sem_2_sub_2_marks_obtained = request.form['pg_sem_2_sub_2_marks_obtained']
            pg_sem_2_sub_2_total_marks = request.form['pg_sem_2_sub_2_total_marks']
            pg_sem_2_sub_3_name = request.form['pg_sem_2_sub_3_name']
            pg_sem_2_sub_3_marks_obtained = request.form['pg_sem_2_sub_3_marks_obtained']
            pg_sem_2_sub_3_total_marks = request.form['pg_sem_2_sub_3_total_marks']
            pg_sem_2_sub_4_name = request.form['pg_sem_2_sub_4_name']
            pg_sem_2_sub_4_marks_obtained = request.form['pg_sem_2_sub_4_marks_obtained']
            pg_sem_2_sub_4_total_marks = request.form['pg_sem_2_sub_4_total_marks']
            pg_sem_2_sub_5_name = request.form['pg_sem_2_sub_5_name']
            pg_sem_2_sub_5_marks_obtained = request.form['pg_sem_2_sub_5_marks_obtained']
            pg_sem_2_sub_5_total_marks = request.form['pg_sem_2_sub_5_total_marks']
            pg_sem_2_sub_6_name = request.form['pg_sem_2_sub_6_name']
            pg_sem_2_sub_6_marks_obtained = request.form['pg_sem_2_sub_6_marks_obtained']
            pg_sem_2_sub_6_total_marks = request.form['pg_sem_2_sub_6_total_marks']
            pg_sem_2_sub_7_name = request.form['pg_sem_2_sub_7_name']
            pg_sem_2_sub_7_marks_obtained = request.form['pg_sem_2_sub_7_marks_obtained']
            pg_sem_2_sub_7_total_marks = request.form['pg_sem_2_sub_7_total_marks']
            pg_sem_2_sub_8_name = request.form['pg_sem_2_sub_8_name']
            pg_sem_2_sub_8_marks_obtained = request.form['pg_sem_2_sub_8_marks_obtained']
            pg_sem_2_sub_8_total_marks = request.form['pg_sem_2_sub_8_total_marks']
            pg_sem_2_sub_9_name = request.form['pg_sem_2_sub_9_name']
            pg_sem_2_sub_9_marks_obtained = request.form['pg_sem_2_sub_9_marks_obtained']
            pg_sem_2_sub_9_total_marks = request.form['pg_sem_2_sub_9_total_marks']
            pg_sem_2_sub_10_name = request.form['pg_sem_2_sub_10_name']
            pg_sem_2_sub_10_marks_obtained = request.form['pg_sem_2_sub_10_marks_obtained']
            pg_sem_2_sub_10_total_marks = request.form['pg_sem_2_sub_10_total_marks']
            pg_sem_2_sub_11_name = request.form['pg_sem_2_sub_11_name']
            pg_sem_2_sub_11_marks_obtained = request.form['pg_sem_2_sub_11_marks_obtained']
            pg_sem_2_sub_11_total_marks = request.form['pg_sem_2_sub_11_total_marks']
            pg_sem_2_sub_12_name = request.form['pg_sem_2_sub_12_name']
            pg_sem_2_sub_12_marks_obtained = request.form['pg_sem_2_sub_12_marks_obtained']
            pg_sem_2_sub_12_total_marks = request.form['pg_sem_2_sub_12_total_marks']
            pg_sem_2_sub_13_name = request.form['pg_sem_2_sub_13_name']
            pg_sem_2_sub_13_marks_obtained = request.form['pg_sem_2_sub_13_marks_obtained']
            pg_sem_2_sub_13_total_marks = request.form['pg_sem_2_sub_13_total_marks']
            pg_sem_2_sub_14_name = request.form['pg_sem_2_sub_14_name']
            pg_sem_2_sub_14_marks_obtained = request.form['pg_sem_2_sub_14_marks_obtained']
            pg_sem_2_sub_14_total_marks = request.form['pg_sem_2_sub_14_total_marks']
            pg_sem_2_sub_15_name = request.form['pg_sem_2_sub_15_name']
            pg_sem_2_sub_15_marks_obtained = request.form['pg_sem_2_sub_15_marks_obtained']
            pg_sem_2_sub_15_total_marks = request.form['pg_sem_2_sub_15_total_marks']
            pg_sem_2_sub_16_name = request.form['pg_sem_2_sub_16_name']
            pg_sem_2_sub_16_marks_obtained = request.form['pg_sem_2_sub_16_marks_obtained']
            pg_sem_2_sub_16_total_marks = request.form['pg_sem_2_sub_16_total_marks']
            pg_sem_2_sub_17_name = request.form['pg_sem_2_sub_17_name']
            pg_sem_2_sub_17_marks_obtained = request.form['pg_sem_2_sub_17_marks_obtained']
            pg_sem_2_sub_17_total_marks = request.form['pg_sem_2_sub_17_total_marks']
            pg_sem_2_sub_18_name = request.form['pg_sem_2_sub_18_name']
            pg_sem_2_sub_18_marks_obtained = request.form['pg_sem_2_sub_18_marks_obtained']
            pg_sem_2_sub_18_total_marks = request.form['pg_sem_2_sub_18_total_marks']
            pg_sem_2_sub_19_name = request.form['pg_sem_2_sub_19_name']
            pg_sem_2_sub_19_marks_obtained = request.form['pg_sem_2_sub_19_marks_obtained']
            pg_sem_2_sub_19_total_marks = request.form['pg_sem_2_sub_19_total_marks']
            pg_sem_2_sub_20_name = request.form['pg_sem_2_sub_20_name']
            pg_sem_2_sub_20_marks_obtained = request.form['pg_sem_2_sub_20_marks_obtained']
            pg_sem_2_sub_20_total_marks = request.form['pg_sem_2_sub_20_total_marks']


            # Update pg_sem_2_info in the database
            cursor.execute("""
                UPDATE pg_sem_2
                SET pg_enrollment_no = ?, pg_sem_2_session = ?, pg_sem_2_roll_no = ?, pg_sem_2_result = ?, pg_sem_2_sub_1_name = ?, pg_sem_2_sub_1_marks_obtained = ?, pg_sem_2_sub_1_total_marks = ?, pg_sem_2_sub_2_name = ?, pg_sem_2_sub_2_marks_obtained = ?, pg_sem_2_sub_2_total_marks = ?, pg_sem_2_sub_3_name = ?, pg_sem_2_sub_3_marks_obtained = ?, pg_sem_2_sub_3_total_marks = ?, pg_sem_2_sub_4_name = ?, pg_sem_2_sub_4_marks_obtained = ?, pg_sem_2_sub_4_total_marks = ?, pg_sem_2_sub_5_name = ?, pg_sem_2_sub_5_marks_obtained = ?, pg_sem_2_sub_5_total_marks = ?, pg_sem_2_sub_6_name = ?, pg_sem_2_sub_6_marks_obtained = ?, pg_sem_2_sub_6_total_marks = ?, pg_sem_2_sub_7_name = ?, pg_sem_2_sub_7_marks_obtained = ?, pg_sem_2_sub_7_total_marks = ?, pg_sem_2_sub_8_name = ?, pg_sem_2_sub_8_marks_obtained = ?, pg_sem_2_sub_8_total_marks = ?, pg_sem_2_sub_9_name = ?, pg_sem_2_sub_9_marks_obtained = ?, pg_sem_2_sub_9_total_marks = ?, pg_sem_2_sub_10_name = ?, pg_sem_2_sub_10_marks_obtained = ?, pg_sem_2_sub_10_total_marks = ?, pg_sem_2_sub_11_name = ?, pg_sem_2_sub_11_marks_obtained = ?, pg_sem_2_sub_11_total_marks = ?, pg_sem_2_sub_12_name = ?, pg_sem_2_sub_12_marks_obtained = ?, pg_sem_2_sub_12_total_marks = ?, pg_sem_2_sub_13_name = ?, pg_sem_2_sub_13_marks_obtained = ?, pg_sem_2_sub_13_total_marks = ?, pg_sem_2_sub_14_name = ?, pg_sem_2_sub_14_marks_obtained = ?, pg_sem_2_sub_14_total_marks = ?, pg_sem_2_sub_15_name = ?, pg_sem_2_sub_15_marks_obtained = ?, pg_sem_2_sub_15_total_marks = ?, pg_sem_2_sub_16_name = ?, pg_sem_2_sub_16_marks_obtained = ?, pg_sem_2_sub_16_total_marks = ?, pg_sem_2_sub_17_name = ?, pg_sem_2_sub_17_marks_obtained = ?, pg_sem_2_sub_17_total_marks = ?, pg_sem_2_sub_18_name = ?, pg_sem_2_sub_18_marks_obtained = ?, pg_sem_2_sub_18_total_marks = ?, pg_sem_2_sub_19_name = ?, pg_sem_2_sub_19_marks_obtained = ?, pg_sem_2_sub_19_total_marks = ?, pg_sem_2_sub_20_name = ?, pg_sem_2_sub_20_marks_obtained = ?, pg_sem_2_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(pg_enrollment_no,pg_sem_2_session,pg_sem_2_roll_no,pg_sem_2_result,pg_sem_2_sub_1_name,
                 pg_sem_2_sub_1_marks_obtained,pg_sem_2_sub_1_total_marks,pg_sem_2_sub_2_name,
                 pg_sem_2_sub_2_marks_obtained,pg_sem_2_sub_2_total_marks,pg_sem_2_sub_3_name,
                 pg_sem_2_sub_3_marks_obtained,pg_sem_2_sub_3_total_marks,pg_sem_2_sub_4_name,
                 pg_sem_2_sub_4_marks_obtained,pg_sem_2_sub_4_total_marks,pg_sem_2_sub_5_name,
                 pg_sem_2_sub_5_marks_obtained,pg_sem_2_sub_5_total_marks,pg_sem_2_sub_6_name,
                 pg_sem_2_sub_6_marks_obtained,pg_sem_2_sub_6_total_marks,pg_sem_2_sub_7_name,
                 pg_sem_2_sub_7_marks_obtained,pg_sem_2_sub_7_total_marks,pg_sem_2_sub_8_name,
                 pg_sem_2_sub_8_marks_obtained,pg_sem_2_sub_8_total_marks,pg_sem_2_sub_9_name,
                 pg_sem_2_sub_9_marks_obtained,pg_sem_2_sub_9_total_marks,pg_sem_2_sub_10_name,
                 pg_sem_2_sub_10_marks_obtained,pg_sem_2_sub_10_total_marks,pg_sem_2_sub_11_name,
                 pg_sem_2_sub_11_marks_obtained,pg_sem_2_sub_11_total_marks,pg_sem_2_sub_12_name,
                 pg_sem_2_sub_12_marks_obtained,pg_sem_2_sub_12_total_marks,pg_sem_2_sub_13_name,
                 pg_sem_2_sub_13_marks_obtained,pg_sem_2_sub_13_total_marks,pg_sem_2_sub_14_name,
                 pg_sem_2_sub_14_marks_obtained,pg_sem_2_sub_14_total_marks,pg_sem_2_sub_15_name,
                 pg_sem_2_sub_15_marks_obtained,pg_sem_2_sub_15_total_marks,pg_sem_2_sub_16_name,
                 pg_sem_2_sub_16_marks_obtained,pg_sem_2_sub_16_total_marks,pg_sem_2_sub_17_name,
                 pg_sem_2_sub_17_marks_obtained,pg_sem_2_sub_17_total_marks,pg_sem_2_sub_18_name,
                 pg_sem_2_sub_18_marks_obtained,pg_sem_2_sub_18_total_marks,pg_sem_2_sub_19_name,
                 pg_sem_2_sub_19_marks_obtained,pg_sem_2_sub_19_total_marks,pg_sem_2_sub_20_name,
                 pg_sem_2_sub_20_marks_obtained,pg_sem_2_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_pg_sem_3'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch pg_sem_2_info from the database
            cursor.execute("SELECT * FROM pg_sem_2 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_2_info = cursor.fetchone()

            # Pass the pg_sem_2_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_2.html', pg_sem_2=pg_sem_2_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_pg_sem_3', methods=['GET', 'POST'])
def form_pg_sem_3():
    try:
        if request.method == 'POST':
            return form_pg_sem_3_post()
        else:
            # Fetch pg_sem_3_info from the database
            cursor.execute("SELECT * FROM pg_sem_3 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_3_info = cursor.fetchone()

            # If pg_sem_3_info is None, create a default pg_sem_3_info object
            if pg_sem_3_info is None:
                pg_sem_3_info = {
                    'pg_enrollment_no': '',
                    'pg_sem_3_session': '',
                    'pg_sem_3_roll_no': '',
                    'pg_sem_3_result': '',
                    'pg_sem_3_sub_1_name': '',
                    'pg_sem_3_sub_1_marks_obtained': '',
                    'pg_sem_3_sub_1_total_marks': '',
                    'pg_sem_3_sub_2_name': '',
                    'pg_sem_3_sub_2_marks_obtained': '',
                    'pg_sem_3_sub_2_total_marks': '',
                    'pg_sem_3_sub_3_name': '',
                    'pg_sem_3_sub_3_marks_obtained': '',
                    'pg_sem_3_sub_3_total_marks': '',
                    'pg_sem_3_sub_4_name': '',
                    'pg_sem_3_sub_4_marks_obtained': '',
                    'pg_sem_3_sub_4_total_marks': '',
                    'pg_sem_3_sub_5_name': '',
                    'pg_sem_3_sub_5_marks_obtained': '',
                    'pg_sem_3_sub_5_total_marks': '',
                    'pg_sem_3_sub_6_name': '',
                    'pg_sem_3_sub_6_marks_obtained': '',
                    'pg_sem_3_sub_6_total_marks': '',
                    'pg_sem_3_sub_7_name': '',
                    'pg_sem_3_sub_7_marks_obtained': '',
                    'pg_sem_3_sub_7_total_marks': '',
                    'pg_sem_3_sub_8_name': '',
                    'pg_sem_3_sub_8_marks_obtained': '',
                    'pg_sem_3_sub_8_total_marks': '',
                    'pg_sem_3_sub_9_name': '',
                    'pg_sem_3_sub_9_marks_obtained': '',
                    'pg_sem_3_sub_9_total_marks': '',
                    'pg_sem_3_sub_10_name': '',
                    'pg_sem_3_sub_10_marks_obtained': '',
                    'pg_sem_3_sub_10_total_marks': '',
                    'pg_sem_3_sub_11_name': '',
                    'pg_sem_3_sub_11_marks_obtained': '',
                    'pg_sem_3_sub_11_total_marks': '',
                    'pg_sem_3_sub_12_name': '',
                    'pg_sem_3_sub_12_marks_obtained': '',
                    'pg_sem_3_sub_12_total_marks': '',
                    'pg_sem_3_sub_13_name': '',
                    'pg_sem_3_sub_13_marks_obtained': '',
                    'pg_sem_3_sub_13_total_marks': '',
                    'pg_sem_3_sub_14_name': '',
                    'pg_sem_3_sub_14_marks_obtained': '',
                    'pg_sem_3_sub_14_total_marks': '',
                    'pg_sem_3_sub_15_name': '',
                    'pg_sem_3_sub_15_marks_obtained': '',
                    'pg_sem_3_sub_15_total_marks': '',
                    'pg_sem_3_sub_16_name': '',
                    'pg_sem_3_sub_16_marks_obtained': '',
                    'pg_sem_3_sub_16_total_marks': '',
                    'pg_sem_3_sub_17_name': '',
                    'pg_sem_3_sub_17_marks_obtained': '',
                    'pg_sem_3_sub_17_total_marks': '',
                    'pg_sem_3_sub_18_name': '',
                    'pg_sem_3_sub_18_marks_obtained': '',
                    'pg_sem_3_sub_18_total_marks': '',
                    'pg_sem_3_sub_19_name': '',
                    'pg_sem_3_sub_19_marks_obtained': '',
                    'pg_sem_3_sub_19_total_marks': '',
                    'pg_sem_3_sub_20_name': '',
                    'pg_sem_3_sub_20_marks_obtained': '',
                    'pg_sem_3_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the pg_sem_3_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_3.html', pg_sem_3=pg_sem_3_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_pg_sem_3_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            pg_enrollment_no = request.form['pg_enrollment_no']
            pg_sem_3_session = request.form['pg_sem_3_session']
            pg_sem_3_roll_no = request.form['pg_sem_3_roll_no']
            pg_sem_3_result = request.form['pg_sem_3_result']
            pg_sem_3_sub_1_name = request.form['pg_sem_3_sub_1_name']
            pg_sem_3_sub_1_marks_obtained = request.form['pg_sem_3_sub_1_marks_obtained']
            pg_sem_3_sub_1_total_marks = request.form['pg_sem_3_sub_1_total_marks']
            pg_sem_3_sub_2_name = request.form['pg_sem_3_sub_2_name']
            pg_sem_3_sub_2_marks_obtained = request.form['pg_sem_3_sub_2_marks_obtained']
            pg_sem_3_sub_2_total_marks = request.form['pg_sem_3_sub_2_total_marks']
            pg_sem_3_sub_3_name = request.form['pg_sem_3_sub_3_name']
            pg_sem_3_sub_3_marks_obtained = request.form['pg_sem_3_sub_3_marks_obtained']
            pg_sem_3_sub_3_total_marks = request.form['pg_sem_3_sub_3_total_marks']
            pg_sem_3_sub_4_name = request.form['pg_sem_3_sub_4_name']
            pg_sem_3_sub_4_marks_obtained = request.form['pg_sem_3_sub_4_marks_obtained']
            pg_sem_3_sub_4_total_marks = request.form['pg_sem_3_sub_4_total_marks']
            pg_sem_3_sub_5_name = request.form['pg_sem_3_sub_5_name']
            pg_sem_3_sub_5_marks_obtained = request.form['pg_sem_3_sub_5_marks_obtained']
            pg_sem_3_sub_5_total_marks = request.form['pg_sem_3_sub_5_total_marks']
            pg_sem_3_sub_6_name = request.form['pg_sem_3_sub_6_name']
            pg_sem_3_sub_6_marks_obtained = request.form['pg_sem_3_sub_6_marks_obtained']
            pg_sem_3_sub_6_total_marks = request.form['pg_sem_3_sub_6_total_marks']
            pg_sem_3_sub_7_name = request.form['pg_sem_3_sub_7_name']
            pg_sem_3_sub_7_marks_obtained = request.form['pg_sem_3_sub_7_marks_obtained']
            pg_sem_3_sub_7_total_marks = request.form['pg_sem_3_sub_7_total_marks']
            pg_sem_3_sub_8_name = request.form['pg_sem_3_sub_8_name']
            pg_sem_3_sub_8_marks_obtained = request.form['pg_sem_3_sub_8_marks_obtained']
            pg_sem_3_sub_8_total_marks = request.form['pg_sem_3_sub_8_total_marks']
            pg_sem_3_sub_9_name = request.form['pg_sem_3_sub_9_name']
            pg_sem_3_sub_9_marks_obtained = request.form['pg_sem_3_sub_9_marks_obtained']
            pg_sem_3_sub_9_total_marks = request.form['pg_sem_3_sub_9_total_marks']
            pg_sem_3_sub_10_name = request.form['pg_sem_3_sub_10_name']
            pg_sem_3_sub_10_marks_obtained = request.form['pg_sem_3_sub_10_marks_obtained']
            pg_sem_3_sub_10_total_marks = request.form['pg_sem_3_sub_10_total_marks']
            pg_sem_3_sub_11_name = request.form['pg_sem_3_sub_11_name']
            pg_sem_3_sub_11_marks_obtained = request.form['pg_sem_3_sub_11_marks_obtained']
            pg_sem_3_sub_11_total_marks = request.form['pg_sem_3_sub_11_total_marks']
            pg_sem_3_sub_12_name = request.form['pg_sem_3_sub_12_name']
            pg_sem_3_sub_12_marks_obtained = request.form['pg_sem_3_sub_12_marks_obtained']
            pg_sem_3_sub_12_total_marks = request.form['pg_sem_3_sub_12_total_marks']
            pg_sem_3_sub_13_name = request.form['pg_sem_3_sub_13_name']
            pg_sem_3_sub_13_marks_obtained = request.form['pg_sem_3_sub_13_marks_obtained']
            pg_sem_3_sub_13_total_marks = request.form['pg_sem_3_sub_13_total_marks']
            pg_sem_3_sub_14_name = request.form['pg_sem_3_sub_14_name']
            pg_sem_3_sub_14_marks_obtained = request.form['pg_sem_3_sub_14_marks_obtained']
            pg_sem_3_sub_14_total_marks = request.form['pg_sem_3_sub_14_total_marks']
            pg_sem_3_sub_15_name = request.form['pg_sem_3_sub_15_name']
            pg_sem_3_sub_15_marks_obtained = request.form['pg_sem_3_sub_15_marks_obtained']
            pg_sem_3_sub_15_total_marks = request.form['pg_sem_3_sub_15_total_marks']
            pg_sem_3_sub_16_name = request.form['pg_sem_3_sub_16_name']
            pg_sem_3_sub_16_marks_obtained = request.form['pg_sem_3_sub_16_marks_obtained']
            pg_sem_3_sub_16_total_marks = request.form['pg_sem_3_sub_16_total_marks']
            pg_sem_3_sub_17_name = request.form['pg_sem_3_sub_17_name']
            pg_sem_3_sub_17_marks_obtained = request.form['pg_sem_3_sub_17_marks_obtained']
            pg_sem_3_sub_17_total_marks = request.form['pg_sem_3_sub_17_total_marks']
            pg_sem_3_sub_18_name = request.form['pg_sem_3_sub_18_name']
            pg_sem_3_sub_18_marks_obtained = request.form['pg_sem_3_sub_18_marks_obtained']
            pg_sem_3_sub_18_total_marks = request.form['pg_sem_3_sub_18_total_marks']
            pg_sem_3_sub_19_name = request.form['pg_sem_3_sub_19_name']
            pg_sem_3_sub_19_marks_obtained = request.form['pg_sem_3_sub_19_marks_obtained']
            pg_sem_3_sub_19_total_marks = request.form['pg_sem_3_sub_19_total_marks']
            pg_sem_3_sub_20_name = request.form['pg_sem_3_sub_20_name']
            pg_sem_3_sub_20_marks_obtained = request.form['pg_sem_3_sub_20_marks_obtained']
            pg_sem_3_sub_20_total_marks = request.form['pg_sem_3_sub_20_total_marks']


            # Update pg_sem_3_info in the database
            cursor.execute("""
                UPDATE pg_sem_3
                SET pg_enrollment_no = ?, pg_sem_3_session = ?, pg_sem_3_roll_no = ?, pg_sem_3_result = ?, pg_sem_3_sub_1_name = ?, pg_sem_3_sub_1_marks_obtained = ?, pg_sem_3_sub_1_total_marks = ?, pg_sem_3_sub_2_name = ?, pg_sem_3_sub_2_marks_obtained = ?, pg_sem_3_sub_2_total_marks = ?, pg_sem_3_sub_3_name = ?, pg_sem_3_sub_3_marks_obtained = ?, pg_sem_3_sub_3_total_marks = ?, pg_sem_3_sub_4_name = ?, pg_sem_3_sub_4_marks_obtained = ?, pg_sem_3_sub_4_total_marks = ?, pg_sem_3_sub_5_name = ?, pg_sem_3_sub_5_marks_obtained = ?, pg_sem_3_sub_5_total_marks = ?, pg_sem_3_sub_6_name = ?, pg_sem_3_sub_6_marks_obtained = ?, pg_sem_3_sub_6_total_marks = ?, pg_sem_3_sub_7_name = ?, pg_sem_3_sub_7_marks_obtained = ?, pg_sem_3_sub_7_total_marks = ?, pg_sem_3_sub_8_name = ?, pg_sem_3_sub_8_marks_obtained = ?, pg_sem_3_sub_8_total_marks = ?, pg_sem_3_sub_9_name = ?, pg_sem_3_sub_9_marks_obtained = ?, pg_sem_3_sub_9_total_marks = ?, pg_sem_3_sub_10_name = ?, pg_sem_3_sub_10_marks_obtained = ?, pg_sem_3_sub_10_total_marks = ?, pg_sem_3_sub_11_name = ?, pg_sem_3_sub_11_marks_obtained = ?, pg_sem_3_sub_11_total_marks = ?, pg_sem_3_sub_12_name = ?, pg_sem_3_sub_12_marks_obtained = ?, pg_sem_3_sub_12_total_marks = ?, pg_sem_3_sub_13_name = ?, pg_sem_3_sub_13_marks_obtained = ?, pg_sem_3_sub_13_total_marks = ?, pg_sem_3_sub_14_name = ?, pg_sem_3_sub_14_marks_obtained = ?, pg_sem_3_sub_14_total_marks = ?, pg_sem_3_sub_15_name = ?, pg_sem_3_sub_15_marks_obtained = ?, pg_sem_3_sub_15_total_marks = ?, pg_sem_3_sub_16_name = ?, pg_sem_3_sub_16_marks_obtained = ?, pg_sem_3_sub_16_total_marks = ?, pg_sem_3_sub_17_name = ?, pg_sem_3_sub_17_marks_obtained = ?, pg_sem_3_sub_17_total_marks = ?, pg_sem_3_sub_18_name = ?, pg_sem_3_sub_18_marks_obtained = ?, pg_sem_3_sub_18_total_marks = ?, pg_sem_3_sub_19_name = ?, pg_sem_3_sub_19_marks_obtained = ?, pg_sem_3_sub_19_total_marks = ?, pg_sem_3_sub_20_name = ?, pg_sem_3_sub_20_marks_obtained = ?, pg_sem_3_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(pg_enrollment_no,pg_sem_3_session,pg_sem_3_roll_no,pg_sem_3_result,pg_sem_3_sub_1_name,
                 pg_sem_3_sub_1_marks_obtained,pg_sem_3_sub_1_total_marks,pg_sem_3_sub_2_name,
                 pg_sem_3_sub_2_marks_obtained,pg_sem_3_sub_2_total_marks,pg_sem_3_sub_3_name,
                 pg_sem_3_sub_3_marks_obtained,pg_sem_3_sub_3_total_marks,pg_sem_3_sub_4_name,
                 pg_sem_3_sub_4_marks_obtained,pg_sem_3_sub_4_total_marks,pg_sem_3_sub_5_name,
                 pg_sem_3_sub_5_marks_obtained,pg_sem_3_sub_5_total_marks,pg_sem_3_sub_6_name,
                 pg_sem_3_sub_6_marks_obtained,pg_sem_3_sub_6_total_marks,pg_sem_3_sub_7_name,
                 pg_sem_3_sub_7_marks_obtained,pg_sem_3_sub_7_total_marks,pg_sem_3_sub_8_name,
                 pg_sem_3_sub_8_marks_obtained,pg_sem_3_sub_8_total_marks,pg_sem_3_sub_9_name,
                 pg_sem_3_sub_9_marks_obtained,pg_sem_3_sub_9_total_marks,pg_sem_3_sub_10_name,
                 pg_sem_3_sub_10_marks_obtained,pg_sem_3_sub_10_total_marks,pg_sem_3_sub_11_name,
                 pg_sem_3_sub_11_marks_obtained,pg_sem_3_sub_11_total_marks,pg_sem_3_sub_12_name,
                 pg_sem_3_sub_12_marks_obtained,pg_sem_3_sub_12_total_marks,pg_sem_3_sub_13_name,
                 pg_sem_3_sub_13_marks_obtained,pg_sem_3_sub_13_total_marks,pg_sem_3_sub_14_name,
                 pg_sem_3_sub_14_marks_obtained,pg_sem_3_sub_14_total_marks,pg_sem_3_sub_15_name,
                 pg_sem_3_sub_15_marks_obtained,pg_sem_3_sub_15_total_marks,pg_sem_3_sub_16_name,
                 pg_sem_3_sub_16_marks_obtained,pg_sem_3_sub_16_total_marks,pg_sem_3_sub_17_name,
                 pg_sem_3_sub_17_marks_obtained,pg_sem_3_sub_17_total_marks,pg_sem_3_sub_18_name,
                 pg_sem_3_sub_18_marks_obtained,pg_sem_3_sub_18_total_marks,pg_sem_3_sub_19_name,
                 pg_sem_3_sub_19_marks_obtained,pg_sem_3_sub_19_total_marks,pg_sem_3_sub_20_name,
                 pg_sem_3_sub_20_marks_obtained,pg_sem_3_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_pg_sem_4'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch pg_sem_3_info from the database
            cursor.execute("SELECT * FROM pg_sem_3 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_3_info = cursor.fetchone()

            # Pass the pg_sem_3_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_3.html', pg_sem_3=pg_sem_3_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_pg_sem_4', methods=['GET', 'POST'])
def form_pg_sem_4():
    try:
        if request.method == 'POST':
            return form_pg_sem_4_post()
        else:
            # Fetch pg_sem_4_info from the database
            cursor.execute("SELECT * FROM pg_sem_4 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_4_info = cursor.fetchone()

            # If pg_sem_4_info is None, create a default pg_sem_4_info object
            if pg_sem_4_info is None:
                pg_sem_4_info = {
                    'pg_enrollment_no': '',
                    'pg_sem_4_session': '',
                    'pg_sem_4_roll_no': '',
                    'pg_sem_4_result': '',
                    'pg_sem_4_sub_1_name': '',
                    'pg_sem_4_sub_1_marks_obtained': '',
                    'pg_sem_4_sub_1_total_marks': '',
                    'pg_sem_4_sub_2_name': '',
                    'pg_sem_4_sub_2_marks_obtained': '',
                    'pg_sem_4_sub_2_total_marks': '',
                    'pg_sem_4_sub_3_name': '',
                    'pg_sem_4_sub_3_marks_obtained': '',
                    'pg_sem_4_sub_3_total_marks': '',
                    'pg_sem_4_sub_4_name': '',
                    'pg_sem_4_sub_4_marks_obtained': '',
                    'pg_sem_4_sub_4_total_marks': '',
                    'pg_sem_4_sub_5_name': '',
                    'pg_sem_4_sub_5_marks_obtained': '',
                    'pg_sem_4_sub_5_total_marks': '',
                    'pg_sem_4_sub_6_name': '',
                    'pg_sem_4_sub_6_marks_obtained': '',
                    'pg_sem_4_sub_6_total_marks': '',
                    'pg_sem_4_sub_7_name': '',
                    'pg_sem_4_sub_7_marks_obtained': '',
                    'pg_sem_4_sub_7_total_marks': '',
                    'pg_sem_4_sub_8_name': '',
                    'pg_sem_4_sub_8_marks_obtained': '',
                    'pg_sem_4_sub_8_total_marks': '',
                    'pg_sem_4_sub_9_name': '',
                    'pg_sem_4_sub_9_marks_obtained': '',
                    'pg_sem_4_sub_9_total_marks': '',
                    'pg_sem_4_sub_10_name': '',
                    'pg_sem_4_sub_10_marks_obtained': '',
                    'pg_sem_4_sub_10_total_marks': '',
                    'pg_sem_4_sub_11_name': '',
                    'pg_sem_4_sub_11_marks_obtained': '',
                    'pg_sem_4_sub_11_total_marks': '',
                    'pg_sem_4_sub_12_name': '',
                    'pg_sem_4_sub_12_marks_obtained': '',
                    'pg_sem_4_sub_12_total_marks': '',
                    'pg_sem_4_sub_13_name': '',
                    'pg_sem_4_sub_13_marks_obtained': '',
                    'pg_sem_4_sub_13_total_marks': '',
                    'pg_sem_4_sub_14_name': '',
                    'pg_sem_4_sub_14_marks_obtained': '',
                    'pg_sem_4_sub_14_total_marks': '',
                    'pg_sem_4_sub_15_name': '',
                    'pg_sem_4_sub_15_marks_obtained': '',
                    'pg_sem_4_sub_15_total_marks': '',
                    'pg_sem_4_sub_16_name': '',
                    'pg_sem_4_sub_16_marks_obtained': '',
                    'pg_sem_4_sub_16_total_marks': '',
                    'pg_sem_4_sub_17_name': '',
                    'pg_sem_4_sub_17_marks_obtained': '',
                    'pg_sem_4_sub_17_total_marks': '',
                    'pg_sem_4_sub_18_name': '',
                    'pg_sem_4_sub_18_marks_obtained': '',
                    'pg_sem_4_sub_18_total_marks': '',
                    'pg_sem_4_sub_19_name': '',
                    'pg_sem_4_sub_19_marks_obtained': '',
                    'pg_sem_4_sub_19_total_marks': '',
                    'pg_sem_4_sub_20_name': '',
                    'pg_sem_4_sub_20_marks_obtained': '',
                    'pg_sem_4_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the pg_sem_4_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_4.html', pg_sem_4=pg_sem_4_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_pg_sem_4_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            pg_enrollment_no = request.form['pg_enrollment_no']
            pg_sem_4_session = request.form['pg_sem_4_session']
            pg_sem_4_roll_no = request.form['pg_sem_4_roll_no']
            pg_sem_4_result = request.form['pg_sem_4_result']
            pg_sem_4_sub_1_name = request.form['pg_sem_4_sub_1_name']
            pg_sem_4_sub_1_marks_obtained = request.form['pg_sem_4_sub_1_marks_obtained']
            pg_sem_4_sub_1_total_marks = request.form['pg_sem_4_sub_1_total_marks']
            pg_sem_4_sub_2_name = request.form['pg_sem_4_sub_2_name']
            pg_sem_4_sub_2_marks_obtained = request.form['pg_sem_4_sub_2_marks_obtained']
            pg_sem_4_sub_2_total_marks = request.form['pg_sem_4_sub_2_total_marks']
            pg_sem_4_sub_3_name = request.form['pg_sem_4_sub_3_name']
            pg_sem_4_sub_3_marks_obtained = request.form['pg_sem_4_sub_3_marks_obtained']
            pg_sem_4_sub_3_total_marks = request.form['pg_sem_4_sub_3_total_marks']
            pg_sem_4_sub_4_name = request.form['pg_sem_4_sub_4_name']
            pg_sem_4_sub_4_marks_obtained = request.form['pg_sem_4_sub_4_marks_obtained']
            pg_sem_4_sub_4_total_marks = request.form['pg_sem_4_sub_4_total_marks']
            pg_sem_4_sub_5_name = request.form['pg_sem_4_sub_5_name']
            pg_sem_4_sub_5_marks_obtained = request.form['pg_sem_4_sub_5_marks_obtained']
            pg_sem_4_sub_5_total_marks = request.form['pg_sem_4_sub_5_total_marks']
            pg_sem_4_sub_6_name = request.form['pg_sem_4_sub_6_name']
            pg_sem_4_sub_6_marks_obtained = request.form['pg_sem_4_sub_6_marks_obtained']
            pg_sem_4_sub_6_total_marks = request.form['pg_sem_4_sub_6_total_marks']
            pg_sem_4_sub_7_name = request.form['pg_sem_4_sub_7_name']
            pg_sem_4_sub_7_marks_obtained = request.form['pg_sem_4_sub_7_marks_obtained']
            pg_sem_4_sub_7_total_marks = request.form['pg_sem_4_sub_7_total_marks']
            pg_sem_4_sub_8_name = request.form['pg_sem_4_sub_8_name']
            pg_sem_4_sub_8_marks_obtained = request.form['pg_sem_4_sub_8_marks_obtained']
            pg_sem_4_sub_8_total_marks = request.form['pg_sem_4_sub_8_total_marks']
            pg_sem_4_sub_9_name = request.form['pg_sem_4_sub_9_name']
            pg_sem_4_sub_9_marks_obtained = request.form['pg_sem_4_sub_9_marks_obtained']
            pg_sem_4_sub_9_total_marks = request.form['pg_sem_4_sub_9_total_marks']
            pg_sem_4_sub_10_name = request.form['pg_sem_4_sub_10_name']
            pg_sem_4_sub_10_marks_obtained = request.form['pg_sem_4_sub_10_marks_obtained']
            pg_sem_4_sub_10_total_marks = request.form['pg_sem_4_sub_10_total_marks']
            pg_sem_4_sub_11_name = request.form['pg_sem_4_sub_11_name']
            pg_sem_4_sub_11_marks_obtained = request.form['pg_sem_4_sub_11_marks_obtained']
            pg_sem_4_sub_11_total_marks = request.form['pg_sem_4_sub_11_total_marks']
            pg_sem_4_sub_12_name = request.form['pg_sem_4_sub_12_name']
            pg_sem_4_sub_12_marks_obtained = request.form['pg_sem_4_sub_12_marks_obtained']
            pg_sem_4_sub_12_total_marks = request.form['pg_sem_4_sub_12_total_marks']
            pg_sem_4_sub_13_name = request.form['pg_sem_4_sub_13_name']
            pg_sem_4_sub_13_marks_obtained = request.form['pg_sem_4_sub_13_marks_obtained']
            pg_sem_4_sub_13_total_marks = request.form['pg_sem_4_sub_13_total_marks']
            pg_sem_4_sub_14_name = request.form['pg_sem_4_sub_14_name']
            pg_sem_4_sub_14_marks_obtained = request.form['pg_sem_4_sub_14_marks_obtained']
            pg_sem_4_sub_14_total_marks = request.form['pg_sem_4_sub_14_total_marks']
            pg_sem_4_sub_15_name = request.form['pg_sem_4_sub_15_name']
            pg_sem_4_sub_15_marks_obtained = request.form['pg_sem_4_sub_15_marks_obtained']
            pg_sem_4_sub_15_total_marks = request.form['pg_sem_4_sub_15_total_marks']
            pg_sem_4_sub_16_name = request.form['pg_sem_4_sub_16_name']
            pg_sem_4_sub_16_marks_obtained = request.form['pg_sem_4_sub_16_marks_obtained']
            pg_sem_4_sub_16_total_marks = request.form['pg_sem_4_sub_16_total_marks']
            pg_sem_4_sub_17_name = request.form['pg_sem_4_sub_17_name']
            pg_sem_4_sub_17_marks_obtained = request.form['pg_sem_4_sub_17_marks_obtained']
            pg_sem_4_sub_17_total_marks = request.form['pg_sem_4_sub_17_total_marks']
            pg_sem_4_sub_18_name = request.form['pg_sem_4_sub_18_name']
            pg_sem_4_sub_18_marks_obtained = request.form['pg_sem_4_sub_18_marks_obtained']
            pg_sem_4_sub_18_total_marks = request.form['pg_sem_4_sub_18_total_marks']
            pg_sem_4_sub_19_name = request.form['pg_sem_4_sub_19_name']
            pg_sem_4_sub_19_marks_obtained = request.form['pg_sem_4_sub_19_marks_obtained']
            pg_sem_4_sub_19_total_marks = request.form['pg_sem_4_sub_19_total_marks']
            pg_sem_4_sub_20_name = request.form['pg_sem_4_sub_20_name']
            pg_sem_4_sub_20_marks_obtained = request.form['pg_sem_4_sub_20_marks_obtained']
            pg_sem_4_sub_20_total_marks = request.form['pg_sem_4_sub_20_total_marks']


            # Update pg_sem_4_info in the database
            cursor.execute("""
                UPDATE pg_sem_4
                SET pg_enrollment_no = ?, pg_sem_4_session = ?, pg_sem_4_roll_no = ?, pg_sem_4_result = ?, pg_sem_4_sub_1_name = ?, pg_sem_4_sub_1_marks_obtained = ?, pg_sem_4_sub_1_total_marks = ?, pg_sem_4_sub_2_name = ?, pg_sem_4_sub_2_marks_obtained = ?, pg_sem_4_sub_2_total_marks = ?, pg_sem_4_sub_3_name = ?, pg_sem_4_sub_3_marks_obtained = ?, pg_sem_4_sub_3_total_marks = ?, pg_sem_4_sub_4_name = ?, pg_sem_4_sub_4_marks_obtained = ?, pg_sem_4_sub_4_total_marks = ?, pg_sem_4_sub_5_name = ?, pg_sem_4_sub_5_marks_obtained = ?, pg_sem_4_sub_5_total_marks = ?, pg_sem_4_sub_6_name = ?, pg_sem_4_sub_6_marks_obtained = ?, pg_sem_4_sub_6_total_marks = ?, pg_sem_4_sub_7_name = ?, pg_sem_4_sub_7_marks_obtained = ?, pg_sem_4_sub_7_total_marks = ?, pg_sem_4_sub_8_name = ?, pg_sem_4_sub_8_marks_obtained = ?, pg_sem_4_sub_8_total_marks = ?, pg_sem_4_sub_9_name = ?, pg_sem_4_sub_9_marks_obtained = ?, pg_sem_4_sub_9_total_marks = ?, pg_sem_4_sub_10_name = ?, pg_sem_4_sub_10_marks_obtained = ?, pg_sem_4_sub_10_total_marks = ?, pg_sem_4_sub_11_name = ?, pg_sem_4_sub_11_marks_obtained = ?, pg_sem_4_sub_11_total_marks = ?, pg_sem_4_sub_12_name = ?, pg_sem_4_sub_12_marks_obtained = ?, pg_sem_4_sub_12_total_marks = ?, pg_sem_4_sub_13_name = ?, pg_sem_4_sub_13_marks_obtained = ?, pg_sem_4_sub_13_total_marks = ?, pg_sem_4_sub_14_name = ?, pg_sem_4_sub_14_marks_obtained = ?, pg_sem_4_sub_14_total_marks = ?, pg_sem_4_sub_15_name = ?, pg_sem_4_sub_15_marks_obtained = ?, pg_sem_4_sub_15_total_marks = ?, pg_sem_4_sub_16_name = ?, pg_sem_4_sub_16_marks_obtained = ?, pg_sem_4_sub_16_total_marks = ?, pg_sem_4_sub_17_name = ?, pg_sem_4_sub_17_marks_obtained = ?, pg_sem_4_sub_17_total_marks = ?, pg_sem_4_sub_18_name = ?, pg_sem_4_sub_18_marks_obtained = ?, pg_sem_4_sub_18_total_marks = ?, pg_sem_4_sub_19_name = ?, pg_sem_4_sub_19_marks_obtained = ?, pg_sem_4_sub_19_total_marks = ?, pg_sem_4_sub_20_name = ?, pg_sem_4_sub_20_marks_obtained = ?, pg_sem_4_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(pg_enrollment_no,pg_sem_4_session,pg_sem_4_roll_no,pg_sem_4_result,pg_sem_4_sub_1_name,
                 pg_sem_4_sub_1_marks_obtained,pg_sem_4_sub_1_total_marks,pg_sem_4_sub_2_name,
                 pg_sem_4_sub_2_marks_obtained,pg_sem_4_sub_2_total_marks,pg_sem_4_sub_3_name,
                 pg_sem_4_sub_3_marks_obtained,pg_sem_4_sub_3_total_marks,pg_sem_4_sub_4_name,
                 pg_sem_4_sub_4_marks_obtained,pg_sem_4_sub_4_total_marks,pg_sem_4_sub_5_name,
                 pg_sem_4_sub_5_marks_obtained,pg_sem_4_sub_5_total_marks,pg_sem_4_sub_6_name,
                 pg_sem_4_sub_6_marks_obtained,pg_sem_4_sub_6_total_marks,pg_sem_4_sub_7_name,
                 pg_sem_4_sub_7_marks_obtained,pg_sem_4_sub_7_total_marks,pg_sem_4_sub_8_name,
                 pg_sem_4_sub_8_marks_obtained,pg_sem_4_sub_8_total_marks,pg_sem_4_sub_9_name,
                 pg_sem_4_sub_9_marks_obtained,pg_sem_4_sub_9_total_marks,pg_sem_4_sub_10_name,
                 pg_sem_4_sub_10_marks_obtained,pg_sem_4_sub_10_total_marks,pg_sem_4_sub_11_name,
                 pg_sem_4_sub_11_marks_obtained,pg_sem_4_sub_11_total_marks,pg_sem_4_sub_12_name,
                 pg_sem_4_sub_12_marks_obtained,pg_sem_4_sub_12_total_marks,pg_sem_4_sub_13_name,
                 pg_sem_4_sub_13_marks_obtained,pg_sem_4_sub_13_total_marks,pg_sem_4_sub_14_name,
                 pg_sem_4_sub_14_marks_obtained,pg_sem_4_sub_14_total_marks,pg_sem_4_sub_15_name,
                 pg_sem_4_sub_15_marks_obtained,pg_sem_4_sub_15_total_marks,pg_sem_4_sub_16_name,
                 pg_sem_4_sub_16_marks_obtained,pg_sem_4_sub_16_total_marks,pg_sem_4_sub_17_name,
                 pg_sem_4_sub_17_marks_obtained,pg_sem_4_sub_17_total_marks,pg_sem_4_sub_18_name,
                 pg_sem_4_sub_18_marks_obtained,pg_sem_4_sub_18_total_marks,pg_sem_4_sub_19_name,
                 pg_sem_4_sub_19_marks_obtained,pg_sem_4_sub_19_total_marks,pg_sem_4_sub_20_name,
                 pg_sem_4_sub_20_marks_obtained,pg_sem_4_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_pg_sem_5'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch pg_sem_4_info from the database
            cursor.execute("SELECT * FROM pg_sem_4 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_4_info = cursor.fetchone()

            # Pass the pg_sem_4_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_4.html', pg_sem_4=pg_sem_4_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_pg_sem_5', methods=['GET', 'POST'])
def form_pg_sem_5():
    try:
        if request.method == 'POST':
            return form_pg_sem_5_post()
        else:
            # Fetch pg_sem_5_info from the database
            cursor.execute("SELECT * FROM pg_sem_5 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_5_info = cursor.fetchone()

            # If pg_sem_5_info is None, create a default pg_sem_5_info object
            if pg_sem_5_info is None:
                pg_sem_5_info = {
                    'pg_enrollment_no': '',
                    'pg_sem_5_session': '',
                    'pg_sem_5_roll_no': '',
                    'pg_sem_5_result': '',
                    'pg_sem_5_sub_1_name': '',
                    'pg_sem_5_sub_1_marks_obtained': '',
                    'pg_sem_5_sub_1_total_marks': '',
                    'pg_sem_5_sub_2_name': '',
                    'pg_sem_5_sub_2_marks_obtained': '',
                    'pg_sem_5_sub_2_total_marks': '',
                    'pg_sem_5_sub_3_name': '',
                    'pg_sem_5_sub_3_marks_obtained': '',
                    'pg_sem_5_sub_3_total_marks': '',
                    'pg_sem_5_sub_4_name': '',
                    'pg_sem_5_sub_4_marks_obtained': '',
                    'pg_sem_5_sub_4_total_marks': '',
                    'pg_sem_5_sub_5_name': '',
                    'pg_sem_5_sub_5_marks_obtained': '',
                    'pg_sem_5_sub_5_total_marks': '',
                    'pg_sem_5_sub_6_name': '',
                    'pg_sem_5_sub_6_marks_obtained': '',
                    'pg_sem_5_sub_6_total_marks': '',
                    'pg_sem_5_sub_7_name': '',
                    'pg_sem_5_sub_7_marks_obtained': '',
                    'pg_sem_5_sub_7_total_marks': '',
                    'pg_sem_5_sub_8_name': '',
                    'pg_sem_5_sub_8_marks_obtained': '',
                    'pg_sem_5_sub_8_total_marks': '',
                    'pg_sem_5_sub_9_name': '',
                    'pg_sem_5_sub_9_marks_obtained': '',
                    'pg_sem_5_sub_9_total_marks': '',
                    'pg_sem_5_sub_10_name': '',
                    'pg_sem_5_sub_10_marks_obtained': '',
                    'pg_sem_5_sub_10_total_marks': '',
                    'pg_sem_5_sub_11_name': '',
                    'pg_sem_5_sub_11_marks_obtained': '',
                    'pg_sem_5_sub_11_total_marks': '',
                    'pg_sem_5_sub_12_name': '',
                    'pg_sem_5_sub_12_marks_obtained': '',
                    'pg_sem_5_sub_12_total_marks': '',
                    'pg_sem_5_sub_13_name': '',
                    'pg_sem_5_sub_13_marks_obtained': '',
                    'pg_sem_5_sub_13_total_marks': '',
                    'pg_sem_5_sub_14_name': '',
                    'pg_sem_5_sub_14_marks_obtained': '',
                    'pg_sem_5_sub_14_total_marks': '',
                    'pg_sem_5_sub_15_name': '',
                    'pg_sem_5_sub_15_marks_obtained': '',
                    'pg_sem_5_sub_15_total_marks': '',
                    'pg_sem_5_sub_16_name': '',
                    'pg_sem_5_sub_16_marks_obtained': '',
                    'pg_sem_5_sub_16_total_marks': '',
                    'pg_sem_5_sub_17_name': '',
                    'pg_sem_5_sub_17_marks_obtained': '',
                    'pg_sem_5_sub_17_total_marks': '',
                    'pg_sem_5_sub_18_name': '',
                    'pg_sem_5_sub_18_marks_obtained': '',
                    'pg_sem_5_sub_18_total_marks': '',
                    'pg_sem_5_sub_19_name': '',
                    'pg_sem_5_sub_19_marks_obtained': '',
                    'pg_sem_5_sub_19_total_marks': '',
                    'pg_sem_5_sub_20_name': '',
                    'pg_sem_5_sub_20_marks_obtained': '',
                    'pg_sem_5_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the pg_sem_5_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_5.html', pg_sem_5=pg_sem_5_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_pg_sem_5_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            pg_enrollment_no = request.form['pg_enrollment_no']
            pg_sem_5_session = request.form['pg_sem_5_session']
            pg_sem_5_roll_no = request.form['pg_sem_5_roll_no']
            pg_sem_5_result = request.form['pg_sem_5_result']
            pg_sem_5_sub_1_name = request.form['pg_sem_5_sub_1_name']
            pg_sem_5_sub_1_marks_obtained = request.form['pg_sem_5_sub_1_marks_obtained']
            pg_sem_5_sub_1_total_marks = request.form['pg_sem_5_sub_1_total_marks']
            pg_sem_5_sub_2_name = request.form['pg_sem_5_sub_2_name']
            pg_sem_5_sub_2_marks_obtained = request.form['pg_sem_5_sub_2_marks_obtained']
            pg_sem_5_sub_2_total_marks = request.form['pg_sem_5_sub_2_total_marks']
            pg_sem_5_sub_3_name = request.form['pg_sem_5_sub_3_name']
            pg_sem_5_sub_3_marks_obtained = request.form['pg_sem_5_sub_3_marks_obtained']
            pg_sem_5_sub_3_total_marks = request.form['pg_sem_5_sub_3_total_marks']
            pg_sem_5_sub_4_name = request.form['pg_sem_5_sub_4_name']
            pg_sem_5_sub_4_marks_obtained = request.form['pg_sem_5_sub_4_marks_obtained']
            pg_sem_5_sub_4_total_marks = request.form['pg_sem_5_sub_4_total_marks']
            pg_sem_5_sub_5_name = request.form['pg_sem_5_sub_5_name']
            pg_sem_5_sub_5_marks_obtained = request.form['pg_sem_5_sub_5_marks_obtained']
            pg_sem_5_sub_5_total_marks = request.form['pg_sem_5_sub_5_total_marks']
            pg_sem_5_sub_6_name = request.form['pg_sem_5_sub_6_name']
            pg_sem_5_sub_6_marks_obtained = request.form['pg_sem_5_sub_6_marks_obtained']
            pg_sem_5_sub_6_total_marks = request.form['pg_sem_5_sub_6_total_marks']
            pg_sem_5_sub_7_name = request.form['pg_sem_5_sub_7_name']
            pg_sem_5_sub_7_marks_obtained = request.form['pg_sem_5_sub_7_marks_obtained']
            pg_sem_5_sub_7_total_marks = request.form['pg_sem_5_sub_7_total_marks']
            pg_sem_5_sub_8_name = request.form['pg_sem_5_sub_8_name']
            pg_sem_5_sub_8_marks_obtained = request.form['pg_sem_5_sub_8_marks_obtained']
            pg_sem_5_sub_8_total_marks = request.form['pg_sem_5_sub_8_total_marks']
            pg_sem_5_sub_9_name = request.form['pg_sem_5_sub_9_name']
            pg_sem_5_sub_9_marks_obtained = request.form['pg_sem_5_sub_9_marks_obtained']
            pg_sem_5_sub_9_total_marks = request.form['pg_sem_5_sub_9_total_marks']
            pg_sem_5_sub_10_name = request.form['pg_sem_5_sub_10_name']
            pg_sem_5_sub_10_marks_obtained = request.form['pg_sem_5_sub_10_marks_obtained']
            pg_sem_5_sub_10_total_marks = request.form['pg_sem_5_sub_10_total_marks']
            pg_sem_5_sub_11_name = request.form['pg_sem_5_sub_11_name']
            pg_sem_5_sub_11_marks_obtained = request.form['pg_sem_5_sub_11_marks_obtained']
            pg_sem_5_sub_11_total_marks = request.form['pg_sem_5_sub_11_total_marks']
            pg_sem_5_sub_12_name = request.form['pg_sem_5_sub_12_name']
            pg_sem_5_sub_12_marks_obtained = request.form['pg_sem_5_sub_12_marks_obtained']
            pg_sem_5_sub_12_total_marks = request.form['pg_sem_5_sub_12_total_marks']
            pg_sem_5_sub_13_name = request.form['pg_sem_5_sub_13_name']
            pg_sem_5_sub_13_marks_obtained = request.form['pg_sem_5_sub_13_marks_obtained']
            pg_sem_5_sub_13_total_marks = request.form['pg_sem_5_sub_13_total_marks']
            pg_sem_5_sub_14_name = request.form['pg_sem_5_sub_14_name']
            pg_sem_5_sub_14_marks_obtained = request.form['pg_sem_5_sub_14_marks_obtained']
            pg_sem_5_sub_14_total_marks = request.form['pg_sem_5_sub_14_total_marks']
            pg_sem_5_sub_15_name = request.form['pg_sem_5_sub_15_name']
            pg_sem_5_sub_15_marks_obtained = request.form['pg_sem_5_sub_15_marks_obtained']
            pg_sem_5_sub_15_total_marks = request.form['pg_sem_5_sub_15_total_marks']
            pg_sem_5_sub_16_name = request.form['pg_sem_5_sub_16_name']
            pg_sem_5_sub_16_marks_obtained = request.form['pg_sem_5_sub_16_marks_obtained']
            pg_sem_5_sub_16_total_marks = request.form['pg_sem_5_sub_16_total_marks']
            pg_sem_5_sub_17_name = request.form['pg_sem_5_sub_17_name']
            pg_sem_5_sub_17_marks_obtained = request.form['pg_sem_5_sub_17_marks_obtained']
            pg_sem_5_sub_17_total_marks = request.form['pg_sem_5_sub_17_total_marks']
            pg_sem_5_sub_18_name = request.form['pg_sem_5_sub_18_name']
            pg_sem_5_sub_18_marks_obtained = request.form['pg_sem_5_sub_18_marks_obtained']
            pg_sem_5_sub_18_total_marks = request.form['pg_sem_5_sub_18_total_marks']
            pg_sem_5_sub_19_name = request.form['pg_sem_5_sub_19_name']
            pg_sem_5_sub_19_marks_obtained = request.form['pg_sem_5_sub_19_marks_obtained']
            pg_sem_5_sub_19_total_marks = request.form['pg_sem_5_sub_19_total_marks']
            pg_sem_5_sub_20_name = request.form['pg_sem_5_sub_20_name']
            pg_sem_5_sub_20_marks_obtained = request.form['pg_sem_5_sub_20_marks_obtained']
            pg_sem_5_sub_20_total_marks = request.form['pg_sem_5_sub_20_total_marks']


            # Update pg_sem_5_info in the database
            cursor.execute("""
                UPDATE pg_sem_5
                SET pg_enrollment_no = ?, pg_sem_5_session = ?, pg_sem_5_roll_no = ?, pg_sem_5_result = ?, pg_sem_5_sub_1_name = ?, pg_sem_5_sub_1_marks_obtained = ?, pg_sem_5_sub_1_total_marks = ?, pg_sem_5_sub_2_name = ?, pg_sem_5_sub_2_marks_obtained = ?, pg_sem_5_sub_2_total_marks = ?, pg_sem_5_sub_3_name = ?, pg_sem_5_sub_3_marks_obtained = ?, pg_sem_5_sub_3_total_marks = ?, pg_sem_5_sub_4_name = ?, pg_sem_5_sub_4_marks_obtained = ?, pg_sem_5_sub_4_total_marks = ?, pg_sem_5_sub_5_name = ?, pg_sem_5_sub_5_marks_obtained = ?, pg_sem_5_sub_5_total_marks = ?, pg_sem_5_sub_6_name = ?, pg_sem_5_sub_6_marks_obtained = ?, pg_sem_5_sub_6_total_marks = ?, pg_sem_5_sub_7_name = ?, pg_sem_5_sub_7_marks_obtained = ?, pg_sem_5_sub_7_total_marks = ?, pg_sem_5_sub_8_name = ?, pg_sem_5_sub_8_marks_obtained = ?, pg_sem_5_sub_8_total_marks = ?, pg_sem_5_sub_9_name = ?, pg_sem_5_sub_9_marks_obtained = ?, pg_sem_5_sub_9_total_marks = ?, pg_sem_5_sub_10_name = ?, pg_sem_5_sub_10_marks_obtained = ?, pg_sem_5_sub_10_total_marks = ?, pg_sem_5_sub_11_name = ?, pg_sem_5_sub_11_marks_obtained = ?, pg_sem_5_sub_11_total_marks = ?, pg_sem_5_sub_12_name = ?, pg_sem_5_sub_12_marks_obtained = ?, pg_sem_5_sub_12_total_marks = ?, pg_sem_5_sub_13_name = ?, pg_sem_5_sub_13_marks_obtained = ?, pg_sem_5_sub_13_total_marks = ?, pg_sem_5_sub_14_name = ?, pg_sem_5_sub_14_marks_obtained = ?, pg_sem_5_sub_14_total_marks = ?, pg_sem_5_sub_15_name = ?, pg_sem_5_sub_15_marks_obtained = ?, pg_sem_5_sub_15_total_marks = ?, pg_sem_5_sub_16_name = ?, pg_sem_5_sub_16_marks_obtained = ?, pg_sem_5_sub_16_total_marks = ?, pg_sem_5_sub_17_name = ?, pg_sem_5_sub_17_marks_obtained = ?, pg_sem_5_sub_17_total_marks = ?, pg_sem_5_sub_18_name = ?, pg_sem_5_sub_18_marks_obtained = ?, pg_sem_5_sub_18_total_marks = ?, pg_sem_5_sub_19_name = ?, pg_sem_5_sub_19_marks_obtained = ?, pg_sem_5_sub_19_total_marks = ?, pg_sem_5_sub_20_name = ?, pg_sem_5_sub_20_marks_obtained = ?, pg_sem_5_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(pg_enrollment_no,pg_sem_5_session,pg_sem_5_roll_no,pg_sem_5_result,pg_sem_5_sub_1_name,
                 pg_sem_5_sub_1_marks_obtained,pg_sem_5_sub_1_total_marks,pg_sem_5_sub_2_name,
                 pg_sem_5_sub_2_marks_obtained,pg_sem_5_sub_2_total_marks,pg_sem_5_sub_3_name,
                 pg_sem_5_sub_3_marks_obtained,pg_sem_5_sub_3_total_marks,pg_sem_5_sub_4_name,
                 pg_sem_5_sub_4_marks_obtained,pg_sem_5_sub_4_total_marks,pg_sem_5_sub_5_name,
                 pg_sem_5_sub_5_marks_obtained,pg_sem_5_sub_5_total_marks,pg_sem_5_sub_6_name,
                 pg_sem_5_sub_6_marks_obtained,pg_sem_5_sub_6_total_marks,pg_sem_5_sub_7_name,
                 pg_sem_5_sub_7_marks_obtained,pg_sem_5_sub_7_total_marks,pg_sem_5_sub_8_name,
                 pg_sem_5_sub_8_marks_obtained,pg_sem_5_sub_8_total_marks,pg_sem_5_sub_9_name,
                 pg_sem_5_sub_9_marks_obtained,pg_sem_5_sub_9_total_marks,pg_sem_5_sub_10_name,
                 pg_sem_5_sub_10_marks_obtained,pg_sem_5_sub_10_total_marks,pg_sem_5_sub_11_name,
                 pg_sem_5_sub_11_marks_obtained,pg_sem_5_sub_11_total_marks,pg_sem_5_sub_12_name,
                 pg_sem_5_sub_12_marks_obtained,pg_sem_5_sub_12_total_marks,pg_sem_5_sub_13_name,
                 pg_sem_5_sub_13_marks_obtained,pg_sem_5_sub_13_total_marks,pg_sem_5_sub_14_name,
                 pg_sem_5_sub_14_marks_obtained,pg_sem_5_sub_14_total_marks,pg_sem_5_sub_15_name,
                 pg_sem_5_sub_15_marks_obtained,pg_sem_5_sub_15_total_marks,pg_sem_5_sub_16_name,
                 pg_sem_5_sub_16_marks_obtained,pg_sem_5_sub_16_total_marks,pg_sem_5_sub_17_name,
                 pg_sem_5_sub_17_marks_obtained,pg_sem_5_sub_17_total_marks,pg_sem_5_sub_18_name,
                 pg_sem_5_sub_18_marks_obtained,pg_sem_5_sub_18_total_marks,pg_sem_5_sub_19_name,
                 pg_sem_5_sub_19_marks_obtained,pg_sem_5_sub_19_total_marks,pg_sem_5_sub_20_name,
                 pg_sem_5_sub_20_marks_obtained,pg_sem_5_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_pg_sem_6'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch pg_sem_5_info from the database
            cursor.execute("SELECT * FROM pg_sem_5 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_5_info = cursor.fetchone()

            # Pass the pg_sem_5_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_5.html', pg_sem_5=pg_sem_5_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_pg_sem_6', methods=['GET', 'POST'])
def form_pg_sem_6():
    try:
        if request.method == 'POST':
            return form_pg_sem_6_post()
        else:
            # Fetch pg_sem_6_info from the database
            cursor.execute("SELECT * FROM pg_sem_6 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_6_info = cursor.fetchone()

            # If pg_sem_6_info is None, create a default pg_sem_6_info object
            if pg_sem_6_info is None:
                pg_sem_6_info = {
                    'pg_enrollment_no': '',
                    'pg_sem_6_session': '',
                    'pg_sem_6_roll_no': '',
                    'pg_sem_6_result': '',
                    'pg_sem_6_sub_1_name': '',
                    'pg_sem_6_sub_1_marks_obtained': '',
                    'pg_sem_6_sub_1_total_marks': '',
                    'pg_sem_6_sub_2_name': '',
                    'pg_sem_6_sub_2_marks_obtained': '',
                    'pg_sem_6_sub_2_total_marks': '',
                    'pg_sem_6_sub_3_name': '',
                    'pg_sem_6_sub_3_marks_obtained': '',
                    'pg_sem_6_sub_3_total_marks': '',
                    'pg_sem_6_sub_4_name': '',
                    'pg_sem_6_sub_4_marks_obtained': '',
                    'pg_sem_6_sub_4_total_marks': '',
                    'pg_sem_6_sub_5_name': '',
                    'pg_sem_6_sub_5_marks_obtained': '',
                    'pg_sem_6_sub_5_total_marks': '',
                    'pg_sem_6_sub_6_name': '',
                    'pg_sem_6_sub_6_marks_obtained': '',
                    'pg_sem_6_sub_6_total_marks': '',
                    'pg_sem_6_sub_7_name': '',
                    'pg_sem_6_sub_7_marks_obtained': '',
                    'pg_sem_6_sub_7_total_marks': '',
                    'pg_sem_6_sub_8_name': '',
                    'pg_sem_6_sub_8_marks_obtained': '',
                    'pg_sem_6_sub_8_total_marks': '',
                    'pg_sem_6_sub_9_name': '',
                    'pg_sem_6_sub_9_marks_obtained': '',
                    'pg_sem_6_sub_9_total_marks': '',
                    'pg_sem_6_sub_10_name': '',
                    'pg_sem_6_sub_10_marks_obtained': '',
                    'pg_sem_6_sub_10_total_marks': '',
                    'pg_sem_6_sub_11_name': '',
                    'pg_sem_6_sub_11_marks_obtained': '',
                    'pg_sem_6_sub_11_total_marks': '',
                    'pg_sem_6_sub_12_name': '',
                    'pg_sem_6_sub_12_marks_obtained': '',
                    'pg_sem_6_sub_12_total_marks': '',
                    'pg_sem_6_sub_13_name': '',
                    'pg_sem_6_sub_13_marks_obtained': '',
                    'pg_sem_6_sub_13_total_marks': '',
                    'pg_sem_6_sub_14_name': '',
                    'pg_sem_6_sub_14_marks_obtained': '',
                    'pg_sem_6_sub_14_total_marks': '',
                    'pg_sem_6_sub_15_name': '',
                    'pg_sem_6_sub_15_marks_obtained': '',
                    'pg_sem_6_sub_15_total_marks': '',
                    'pg_sem_6_sub_16_name': '',
                    'pg_sem_6_sub_16_marks_obtained': '',
                    'pg_sem_6_sub_16_total_marks': '',
                    'pg_sem_6_sub_17_name': '',
                    'pg_sem_6_sub_17_marks_obtained': '',
                    'pg_sem_6_sub_17_total_marks': '',
                    'pg_sem_6_sub_18_name': '',
                    'pg_sem_6_sub_18_marks_obtained': '',
                    'pg_sem_6_sub_18_total_marks': '',
                    'pg_sem_6_sub_19_name': '',
                    'pg_sem_6_sub_19_marks_obtained': '',
                    'pg_sem_6_sub_19_total_marks': '',
                    'pg_sem_6_sub_20_name': '',
                    'pg_sem_6_sub_20_marks_obtained': '',
                    'pg_sem_6_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the pg_sem_6_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_6.html', pg_sem_6=pg_sem_6_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_pg_sem_6_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            pg_enrollment_no = request.form['pg_enrollment_no']
            pg_sem_6_session = request.form['pg_sem_6_session']
            pg_sem_6_roll_no = request.form['pg_sem_6_roll_no']
            pg_sem_6_result = request.form['pg_sem_6_result']
            pg_sem_6_sub_1_name = request.form['pg_sem_6_sub_1_name']
            pg_sem_6_sub_1_marks_obtained = request.form['pg_sem_6_sub_1_marks_obtained']
            pg_sem_6_sub_1_total_marks = request.form['pg_sem_6_sub_1_total_marks']
            pg_sem_6_sub_2_name = request.form['pg_sem_6_sub_2_name']
            pg_sem_6_sub_2_marks_obtained = request.form['pg_sem_6_sub_2_marks_obtained']
            pg_sem_6_sub_2_total_marks = request.form['pg_sem_6_sub_2_total_marks']
            pg_sem_6_sub_3_name = request.form['pg_sem_6_sub_3_name']
            pg_sem_6_sub_3_marks_obtained = request.form['pg_sem_6_sub_3_marks_obtained']
            pg_sem_6_sub_3_total_marks = request.form['pg_sem_6_sub_3_total_marks']
            pg_sem_6_sub_4_name = request.form['pg_sem_6_sub_4_name']
            pg_sem_6_sub_4_marks_obtained = request.form['pg_sem_6_sub_4_marks_obtained']
            pg_sem_6_sub_4_total_marks = request.form['pg_sem_6_sub_4_total_marks']
            pg_sem_6_sub_5_name = request.form['pg_sem_6_sub_5_name']
            pg_sem_6_sub_5_marks_obtained = request.form['pg_sem_6_sub_5_marks_obtained']
            pg_sem_6_sub_5_total_marks = request.form['pg_sem_6_sub_5_total_marks']
            pg_sem_6_sub_6_name = request.form['pg_sem_6_sub_6_name']
            pg_sem_6_sub_6_marks_obtained = request.form['pg_sem_6_sub_6_marks_obtained']
            pg_sem_6_sub_6_total_marks = request.form['pg_sem_6_sub_6_total_marks']
            pg_sem_6_sub_7_name = request.form['pg_sem_6_sub_7_name']
            pg_sem_6_sub_7_marks_obtained = request.form['pg_sem_6_sub_7_marks_obtained']
            pg_sem_6_sub_7_total_marks = request.form['pg_sem_6_sub_7_total_marks']
            pg_sem_6_sub_8_name = request.form['pg_sem_6_sub_8_name']
            pg_sem_6_sub_8_marks_obtained = request.form['pg_sem_6_sub_8_marks_obtained']
            pg_sem_6_sub_8_total_marks = request.form['pg_sem_6_sub_8_total_marks']
            pg_sem_6_sub_9_name = request.form['pg_sem_6_sub_9_name']
            pg_sem_6_sub_9_marks_obtained = request.form['pg_sem_6_sub_9_marks_obtained']
            pg_sem_6_sub_9_total_marks = request.form['pg_sem_6_sub_9_total_marks']
            pg_sem_6_sub_10_name = request.form['pg_sem_6_sub_10_name']
            pg_sem_6_sub_10_marks_obtained = request.form['pg_sem_6_sub_10_marks_obtained']
            pg_sem_6_sub_10_total_marks = request.form['pg_sem_6_sub_10_total_marks']
            pg_sem_6_sub_11_name = request.form['pg_sem_6_sub_11_name']
            pg_sem_6_sub_11_marks_obtained = request.form['pg_sem_6_sub_11_marks_obtained']
            pg_sem_6_sub_11_total_marks = request.form['pg_sem_6_sub_11_total_marks']
            pg_sem_6_sub_12_name = request.form['pg_sem_6_sub_12_name']
            pg_sem_6_sub_12_marks_obtained = request.form['pg_sem_6_sub_12_marks_obtained']
            pg_sem_6_sub_12_total_marks = request.form['pg_sem_6_sub_12_total_marks']
            pg_sem_6_sub_13_name = request.form['pg_sem_6_sub_13_name']
            pg_sem_6_sub_13_marks_obtained = request.form['pg_sem_6_sub_13_marks_obtained']
            pg_sem_6_sub_13_total_marks = request.form['pg_sem_6_sub_13_total_marks']
            pg_sem_6_sub_14_name = request.form['pg_sem_6_sub_14_name']
            pg_sem_6_sub_14_marks_obtained = request.form['pg_sem_6_sub_14_marks_obtained']
            pg_sem_6_sub_14_total_marks = request.form['pg_sem_6_sub_14_total_marks']
            pg_sem_6_sub_15_name = request.form['pg_sem_6_sub_15_name']
            pg_sem_6_sub_15_marks_obtained = request.form['pg_sem_6_sub_15_marks_obtained']
            pg_sem_6_sub_15_total_marks = request.form['pg_sem_6_sub_15_total_marks']
            pg_sem_6_sub_16_name = request.form['pg_sem_6_sub_16_name']
            pg_sem_6_sub_16_marks_obtained = request.form['pg_sem_6_sub_16_marks_obtained']
            pg_sem_6_sub_16_total_marks = request.form['pg_sem_6_sub_16_total_marks']
            pg_sem_6_sub_17_name = request.form['pg_sem_6_sub_17_name']
            pg_sem_6_sub_17_marks_obtained = request.form['pg_sem_6_sub_17_marks_obtained']
            pg_sem_6_sub_17_total_marks = request.form['pg_sem_6_sub_17_total_marks']
            pg_sem_6_sub_18_name = request.form['pg_sem_6_sub_18_name']
            pg_sem_6_sub_18_marks_obtained = request.form['pg_sem_6_sub_18_marks_obtained']
            pg_sem_6_sub_18_total_marks = request.form['pg_sem_6_sub_18_total_marks']
            pg_sem_6_sub_19_name = request.form['pg_sem_6_sub_19_name']
            pg_sem_6_sub_19_marks_obtained = request.form['pg_sem_6_sub_19_marks_obtained']
            pg_sem_6_sub_19_total_marks = request.form['pg_sem_6_sub_19_total_marks']
            pg_sem_6_sub_20_name = request.form['pg_sem_6_sub_20_name']
            pg_sem_6_sub_20_marks_obtained = request.form['pg_sem_6_sub_20_marks_obtained']
            pg_sem_6_sub_20_total_marks = request.form['pg_sem_6_sub_20_total_marks']


            # Update pg_sem_6_info in the database
            cursor.execute("""
                UPDATE pg_sem_6
                SET pg_enrollment_no = ?, pg_sem_6_session = ?, pg_sem_6_roll_no = ?, pg_sem_6_result = ?, pg_sem_6_sub_1_name = ?, pg_sem_6_sub_1_marks_obtained = ?, pg_sem_6_sub_1_total_marks = ?, pg_sem_6_sub_2_name = ?, pg_sem_6_sub_2_marks_obtained = ?, pg_sem_6_sub_2_total_marks = ?, pg_sem_6_sub_3_name = ?, pg_sem_6_sub_3_marks_obtained = ?, pg_sem_6_sub_3_total_marks = ?, pg_sem_6_sub_4_name = ?, pg_sem_6_sub_4_marks_obtained = ?, pg_sem_6_sub_4_total_marks = ?, pg_sem_6_sub_5_name = ?, pg_sem_6_sub_5_marks_obtained = ?, pg_sem_6_sub_5_total_marks = ?, pg_sem_6_sub_6_name = ?, pg_sem_6_sub_6_marks_obtained = ?, pg_sem_6_sub_6_total_marks = ?, pg_sem_6_sub_7_name = ?, pg_sem_6_sub_7_marks_obtained = ?, pg_sem_6_sub_7_total_marks = ?, pg_sem_6_sub_8_name = ?, pg_sem_6_sub_8_marks_obtained = ?, pg_sem_6_sub_8_total_marks = ?, pg_sem_6_sub_9_name = ?, pg_sem_6_sub_9_marks_obtained = ?, pg_sem_6_sub_9_total_marks = ?, pg_sem_6_sub_10_name = ?, pg_sem_6_sub_10_marks_obtained = ?, pg_sem_6_sub_10_total_marks = ?, pg_sem_6_sub_11_name = ?, pg_sem_6_sub_11_marks_obtained = ?, pg_sem_6_sub_11_total_marks = ?, pg_sem_6_sub_12_name = ?, pg_sem_6_sub_12_marks_obtained = ?, pg_sem_6_sub_12_total_marks = ?, pg_sem_6_sub_13_name = ?, pg_sem_6_sub_13_marks_obtained = ?, pg_sem_6_sub_13_total_marks = ?, pg_sem_6_sub_14_name = ?, pg_sem_6_sub_14_marks_obtained = ?, pg_sem_6_sub_14_total_marks = ?, pg_sem_6_sub_15_name = ?, pg_sem_6_sub_15_marks_obtained = ?, pg_sem_6_sub_15_total_marks = ?, pg_sem_6_sub_16_name = ?, pg_sem_6_sub_16_marks_obtained = ?, pg_sem_6_sub_16_total_marks = ?, pg_sem_6_sub_17_name = ?, pg_sem_6_sub_17_marks_obtained = ?, pg_sem_6_sub_17_total_marks = ?, pg_sem_6_sub_18_name = ?, pg_sem_6_sub_18_marks_obtained = ?, pg_sem_6_sub_18_total_marks = ?, pg_sem_6_sub_19_name = ?, pg_sem_6_sub_19_marks_obtained = ?, pg_sem_6_sub_19_total_marks = ?, pg_sem_6_sub_20_name = ?, pg_sem_6_sub_20_marks_obtained = ?, pg_sem_6_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(pg_enrollment_no,pg_sem_6_session,pg_sem_6_roll_no,pg_sem_6_result,pg_sem_6_sub_1_name,
                 pg_sem_6_sub_1_marks_obtained,pg_sem_6_sub_1_total_marks,pg_sem_6_sub_2_name,
                 pg_sem_6_sub_2_marks_obtained,pg_sem_6_sub_2_total_marks,pg_sem_6_sub_3_name,
                 pg_sem_6_sub_3_marks_obtained,pg_sem_6_sub_3_total_marks,pg_sem_6_sub_4_name,
                 pg_sem_6_sub_4_marks_obtained,pg_sem_6_sub_4_total_marks,pg_sem_6_sub_5_name,
                 pg_sem_6_sub_5_marks_obtained,pg_sem_6_sub_5_total_marks,pg_sem_6_sub_6_name,
                 pg_sem_6_sub_6_marks_obtained,pg_sem_6_sub_6_total_marks,pg_sem_6_sub_7_name,
                 pg_sem_6_sub_7_marks_obtained,pg_sem_6_sub_7_total_marks,pg_sem_6_sub_8_name,
                 pg_sem_6_sub_8_marks_obtained,pg_sem_6_sub_8_total_marks,pg_sem_6_sub_9_name,
                 pg_sem_6_sub_9_marks_obtained,pg_sem_6_sub_9_total_marks,pg_sem_6_sub_10_name,
                 pg_sem_6_sub_10_marks_obtained,pg_sem_6_sub_10_total_marks,pg_sem_6_sub_11_name,
                 pg_sem_6_sub_11_marks_obtained,pg_sem_6_sub_11_total_marks,pg_sem_6_sub_12_name,
                 pg_sem_6_sub_12_marks_obtained,pg_sem_6_sub_12_total_marks,pg_sem_6_sub_13_name,
                 pg_sem_6_sub_13_marks_obtained,pg_sem_6_sub_13_total_marks,pg_sem_6_sub_14_name,
                 pg_sem_6_sub_14_marks_obtained,pg_sem_6_sub_14_total_marks,pg_sem_6_sub_15_name,
                 pg_sem_6_sub_15_marks_obtained,pg_sem_6_sub_15_total_marks,pg_sem_6_sub_16_name,
                 pg_sem_6_sub_16_marks_obtained,pg_sem_6_sub_16_total_marks,pg_sem_6_sub_17_name,
                 pg_sem_6_sub_17_marks_obtained,pg_sem_6_sub_17_total_marks,pg_sem_6_sub_18_name,
                 pg_sem_6_sub_18_marks_obtained,pg_sem_6_sub_18_total_marks,pg_sem_6_sub_19_name,
                 pg_sem_6_sub_19_marks_obtained,pg_sem_6_sub_19_total_marks,pg_sem_6_sub_20_name,
                 pg_sem_6_sub_20_marks_obtained,pg_sem_6_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_pg_sem_7'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch pg_sem_6_info from the database
            cursor.execute("SELECT * FROM pg_sem_6 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_6_info = cursor.fetchone()

            # Pass the pg_sem_6_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_6.html', pg_sem_6=pg_sem_6_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_pg_sem_7', methods=['GET', 'POST'])
def form_pg_sem_7():
    try:
        if request.method == 'POST':
            return form_pg_sem_7_post()
        else:
            # Fetch pg_sem_7_info from the database
            cursor.execute("SELECT * FROM pg_sem_7 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_7_info = cursor.fetchone()

            # If pg_sem_7_info is None, create a default pg_sem_7_info object
            if pg_sem_7_info is None:
                pg_sem_7_info = {
                    'pg_enrollment_no': '',
                    'pg_sem_7_session': '',
                    'pg_sem_7_roll_no': '',
                    'pg_sem_7_result': '',
                    'pg_sem_7_sub_1_name': '',
                    'pg_sem_7_sub_1_marks_obtained': '',
                    'pg_sem_7_sub_1_total_marks': '',
                    'pg_sem_7_sub_2_name': '',
                    'pg_sem_7_sub_2_marks_obtained': '',
                    'pg_sem_7_sub_2_total_marks': '',
                    'pg_sem_7_sub_3_name': '',
                    'pg_sem_7_sub_3_marks_obtained': '',
                    'pg_sem_7_sub_3_total_marks': '',
                    'pg_sem_7_sub_4_name': '',
                    'pg_sem_7_sub_4_marks_obtained': '',
                    'pg_sem_7_sub_4_total_marks': '',
                    'pg_sem_7_sub_5_name': '',
                    'pg_sem_7_sub_5_marks_obtained': '',
                    'pg_sem_7_sub_5_total_marks': '',
                    'pg_sem_7_sub_6_name': '',
                    'pg_sem_7_sub_6_marks_obtained': '',
                    'pg_sem_7_sub_6_total_marks': '',
                    'pg_sem_7_sub_7_name': '',
                    'pg_sem_7_sub_7_marks_obtained': '',
                    'pg_sem_7_sub_7_total_marks': '',
                    'pg_sem_7_sub_8_name': '',
                    'pg_sem_7_sub_8_marks_obtained': '',
                    'pg_sem_7_sub_8_total_marks': '',
                    'pg_sem_7_sub_9_name': '',
                    'pg_sem_7_sub_9_marks_obtained': '',
                    'pg_sem_7_sub_9_total_marks': '',
                    'pg_sem_7_sub_10_name': '',
                    'pg_sem_7_sub_10_marks_obtained': '',
                    'pg_sem_7_sub_10_total_marks': '',
                    'pg_sem_7_sub_11_name': '',
                    'pg_sem_7_sub_11_marks_obtained': '',
                    'pg_sem_7_sub_11_total_marks': '',
                    'pg_sem_7_sub_12_name': '',
                    'pg_sem_7_sub_12_marks_obtained': '',
                    'pg_sem_7_sub_12_total_marks': '',
                    'pg_sem_7_sub_13_name': '',
                    'pg_sem_7_sub_13_marks_obtained': '',
                    'pg_sem_7_sub_13_total_marks': '',
                    'pg_sem_7_sub_14_name': '',
                    'pg_sem_7_sub_14_marks_obtained': '',
                    'pg_sem_7_sub_14_total_marks': '',
                    'pg_sem_7_sub_15_name': '',
                    'pg_sem_7_sub_15_marks_obtained': '',
                    'pg_sem_7_sub_15_total_marks': '',
                    'pg_sem_7_sub_16_name': '',
                    'pg_sem_7_sub_16_marks_obtained': '',
                    'pg_sem_7_sub_16_total_marks': '',
                    'pg_sem_7_sub_17_name': '',
                    'pg_sem_7_sub_17_marks_obtained': '',
                    'pg_sem_7_sub_17_total_marks': '',
                    'pg_sem_7_sub_18_name': '',
                    'pg_sem_7_sub_18_marks_obtained': '',
                    'pg_sem_7_sub_18_total_marks': '',
                    'pg_sem_7_sub_19_name': '',
                    'pg_sem_7_sub_19_marks_obtained': '',
                    'pg_sem_7_sub_19_total_marks': '',
                    'pg_sem_7_sub_20_name': '',
                    'pg_sem_7_sub_20_marks_obtained': '',
                    'pg_sem_7_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the pg_sem_7_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_7.html', pg_sem_7=pg_sem_7_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_pg_sem_7_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            pg_enrollment_no = request.form['pg_enrollment_no']
            pg_sem_7_session = request.form['pg_sem_7_session']
            pg_sem_7_roll_no = request.form['pg_sem_7_roll_no']
            pg_sem_7_result = request.form['pg_sem_7_result']
            pg_sem_7_sub_1_name = request.form['pg_sem_7_sub_1_name']
            pg_sem_7_sub_1_marks_obtained = request.form['pg_sem_7_sub_1_marks_obtained']
            pg_sem_7_sub_1_total_marks = request.form['pg_sem_7_sub_1_total_marks']
            pg_sem_7_sub_2_name = request.form['pg_sem_7_sub_2_name']
            pg_sem_7_sub_2_marks_obtained = request.form['pg_sem_7_sub_2_marks_obtained']
            pg_sem_7_sub_2_total_marks = request.form['pg_sem_7_sub_2_total_marks']
            pg_sem_7_sub_3_name = request.form['pg_sem_7_sub_3_name']
            pg_sem_7_sub_3_marks_obtained = request.form['pg_sem_7_sub_3_marks_obtained']
            pg_sem_7_sub_3_total_marks = request.form['pg_sem_7_sub_3_total_marks']
            pg_sem_7_sub_4_name = request.form['pg_sem_7_sub_4_name']
            pg_sem_7_sub_4_marks_obtained = request.form['pg_sem_7_sub_4_marks_obtained']
            pg_sem_7_sub_4_total_marks = request.form['pg_sem_7_sub_4_total_marks']
            pg_sem_7_sub_5_name = request.form['pg_sem_7_sub_5_name']
            pg_sem_7_sub_5_marks_obtained = request.form['pg_sem_7_sub_5_marks_obtained']
            pg_sem_7_sub_5_total_marks = request.form['pg_sem_7_sub_5_total_marks']
            pg_sem_7_sub_6_name = request.form['pg_sem_7_sub_6_name']
            pg_sem_7_sub_6_marks_obtained = request.form['pg_sem_7_sub_6_marks_obtained']
            pg_sem_7_sub_6_total_marks = request.form['pg_sem_7_sub_6_total_marks']
            pg_sem_7_sub_7_name = request.form['pg_sem_7_sub_7_name']
            pg_sem_7_sub_7_marks_obtained = request.form['pg_sem_7_sub_7_marks_obtained']
            pg_sem_7_sub_7_total_marks = request.form['pg_sem_7_sub_7_total_marks']
            pg_sem_7_sub_8_name = request.form['pg_sem_7_sub_8_name']
            pg_sem_7_sub_8_marks_obtained = request.form['pg_sem_7_sub_8_marks_obtained']
            pg_sem_7_sub_8_total_marks = request.form['pg_sem_7_sub_8_total_marks']
            pg_sem_7_sub_9_name = request.form['pg_sem_7_sub_9_name']
            pg_sem_7_sub_9_marks_obtained = request.form['pg_sem_7_sub_9_marks_obtained']
            pg_sem_7_sub_9_total_marks = request.form['pg_sem_7_sub_9_total_marks']
            pg_sem_7_sub_10_name = request.form['pg_sem_7_sub_10_name']
            pg_sem_7_sub_10_marks_obtained = request.form['pg_sem_7_sub_10_marks_obtained']
            pg_sem_7_sub_10_total_marks = request.form['pg_sem_7_sub_10_total_marks']
            pg_sem_7_sub_11_name = request.form['pg_sem_7_sub_11_name']
            pg_sem_7_sub_11_marks_obtained = request.form['pg_sem_7_sub_11_marks_obtained']
            pg_sem_7_sub_11_total_marks = request.form['pg_sem_7_sub_11_total_marks']
            pg_sem_7_sub_12_name = request.form['pg_sem_7_sub_12_name']
            pg_sem_7_sub_12_marks_obtained = request.form['pg_sem_7_sub_12_marks_obtained']
            pg_sem_7_sub_12_total_marks = request.form['pg_sem_7_sub_12_total_marks']
            pg_sem_7_sub_13_name = request.form['pg_sem_7_sub_13_name']
            pg_sem_7_sub_13_marks_obtained = request.form['pg_sem_7_sub_13_marks_obtained']
            pg_sem_7_sub_13_total_marks = request.form['pg_sem_7_sub_13_total_marks']
            pg_sem_7_sub_14_name = request.form['pg_sem_7_sub_14_name']
            pg_sem_7_sub_14_marks_obtained = request.form['pg_sem_7_sub_14_marks_obtained']
            pg_sem_7_sub_14_total_marks = request.form['pg_sem_7_sub_14_total_marks']
            pg_sem_7_sub_15_name = request.form['pg_sem_7_sub_15_name']
            pg_sem_7_sub_15_marks_obtained = request.form['pg_sem_7_sub_15_marks_obtained']
            pg_sem_7_sub_15_total_marks = request.form['pg_sem_7_sub_15_total_marks']
            pg_sem_7_sub_16_name = request.form['pg_sem_7_sub_16_name']
            pg_sem_7_sub_16_marks_obtained = request.form['pg_sem_7_sub_16_marks_obtained']
            pg_sem_7_sub_16_total_marks = request.form['pg_sem_7_sub_16_total_marks']
            pg_sem_7_sub_17_name = request.form['pg_sem_7_sub_17_name']
            pg_sem_7_sub_17_marks_obtained = request.form['pg_sem_7_sub_17_marks_obtained']
            pg_sem_7_sub_17_total_marks = request.form['pg_sem_7_sub_17_total_marks']
            pg_sem_7_sub_18_name = request.form['pg_sem_7_sub_18_name']
            pg_sem_7_sub_18_marks_obtained = request.form['pg_sem_7_sub_18_marks_obtained']
            pg_sem_7_sub_18_total_marks = request.form['pg_sem_7_sub_18_total_marks']
            pg_sem_7_sub_19_name = request.form['pg_sem_7_sub_19_name']
            pg_sem_7_sub_19_marks_obtained = request.form['pg_sem_7_sub_19_marks_obtained']
            pg_sem_7_sub_19_total_marks = request.form['pg_sem_7_sub_19_total_marks']
            pg_sem_7_sub_20_name = request.form['pg_sem_7_sub_20_name']
            pg_sem_7_sub_20_marks_obtained = request.form['pg_sem_7_sub_20_marks_obtained']
            pg_sem_7_sub_20_total_marks = request.form['pg_sem_7_sub_20_total_marks']


            # Update pg_sem_7_info in the database
            cursor.execute("""
                UPDATE pg_sem_7
                SET pg_enrollment_no = ?, pg_sem_7_session = ?, pg_sem_7_roll_no = ?, pg_sem_7_result = ?, pg_sem_7_sub_1_name = ?, pg_sem_7_sub_1_marks_obtained = ?, pg_sem_7_sub_1_total_marks = ?, pg_sem_7_sub_2_name = ?, pg_sem_7_sub_2_marks_obtained = ?, pg_sem_7_sub_2_total_marks = ?, pg_sem_7_sub_3_name = ?, pg_sem_7_sub_3_marks_obtained = ?, pg_sem_7_sub_3_total_marks = ?, pg_sem_7_sub_4_name = ?, pg_sem_7_sub_4_marks_obtained = ?, pg_sem_7_sub_4_total_marks = ?, pg_sem_7_sub_5_name = ?, pg_sem_7_sub_5_marks_obtained = ?, pg_sem_7_sub_5_total_marks = ?, pg_sem_7_sub_6_name = ?, pg_sem_7_sub_6_marks_obtained = ?, pg_sem_7_sub_6_total_marks = ?, pg_sem_7_sub_7_name = ?, pg_sem_7_sub_7_marks_obtained = ?, pg_sem_7_sub_7_total_marks = ?, pg_sem_7_sub_8_name = ?, pg_sem_7_sub_8_marks_obtained = ?, pg_sem_7_sub_8_total_marks = ?, pg_sem_7_sub_9_name = ?, pg_sem_7_sub_9_marks_obtained = ?, pg_sem_7_sub_9_total_marks = ?, pg_sem_7_sub_10_name = ?, pg_sem_7_sub_10_marks_obtained = ?, pg_sem_7_sub_10_total_marks = ?, pg_sem_7_sub_11_name = ?, pg_sem_7_sub_11_marks_obtained = ?, pg_sem_7_sub_11_total_marks = ?, pg_sem_7_sub_12_name = ?, pg_sem_7_sub_12_marks_obtained = ?, pg_sem_7_sub_12_total_marks = ?, pg_sem_7_sub_13_name = ?, pg_sem_7_sub_13_marks_obtained = ?, pg_sem_7_sub_13_total_marks = ?, pg_sem_7_sub_14_name = ?, pg_sem_7_sub_14_marks_obtained = ?, pg_sem_7_sub_14_total_marks = ?, pg_sem_7_sub_15_name = ?, pg_sem_7_sub_15_marks_obtained = ?, pg_sem_7_sub_15_total_marks = ?, pg_sem_7_sub_16_name = ?, pg_sem_7_sub_16_marks_obtained = ?, pg_sem_7_sub_16_total_marks = ?, pg_sem_7_sub_17_name = ?, pg_sem_7_sub_17_marks_obtained = ?, pg_sem_7_sub_17_total_marks = ?, pg_sem_7_sub_18_name = ?, pg_sem_7_sub_18_marks_obtained = ?, pg_sem_7_sub_18_total_marks = ?, pg_sem_7_sub_19_name = ?, pg_sem_7_sub_19_marks_obtained = ?, pg_sem_7_sub_19_total_marks = ?, pg_sem_7_sub_20_name = ?, pg_sem_7_sub_20_marks_obtained = ?, pg_sem_7_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(pg_enrollment_no,pg_sem_7_session,pg_sem_7_roll_no,pg_sem_7_result,pg_sem_7_sub_1_name,
                 pg_sem_7_sub_1_marks_obtained,pg_sem_7_sub_1_total_marks,pg_sem_7_sub_2_name,
                 pg_sem_7_sub_2_marks_obtained,pg_sem_7_sub_2_total_marks,pg_sem_7_sub_3_name,
                 pg_sem_7_sub_3_marks_obtained,pg_sem_7_sub_3_total_marks,pg_sem_7_sub_4_name,
                 pg_sem_7_sub_4_marks_obtained,pg_sem_7_sub_4_total_marks,pg_sem_7_sub_5_name,
                 pg_sem_7_sub_5_marks_obtained,pg_sem_7_sub_5_total_marks,pg_sem_7_sub_6_name,
                 pg_sem_7_sub_6_marks_obtained,pg_sem_7_sub_6_total_marks,pg_sem_7_sub_7_name,
                 pg_sem_7_sub_7_marks_obtained,pg_sem_7_sub_7_total_marks,pg_sem_7_sub_8_name,
                 pg_sem_7_sub_8_marks_obtained,pg_sem_7_sub_8_total_marks,pg_sem_7_sub_9_name,
                 pg_sem_7_sub_9_marks_obtained,pg_sem_7_sub_9_total_marks,pg_sem_7_sub_10_name,
                 pg_sem_7_sub_10_marks_obtained,pg_sem_7_sub_10_total_marks,pg_sem_7_sub_11_name,
                 pg_sem_7_sub_11_marks_obtained,pg_sem_7_sub_11_total_marks,pg_sem_7_sub_12_name,
                 pg_sem_7_sub_12_marks_obtained,pg_sem_7_sub_12_total_marks,pg_sem_7_sub_13_name,
                 pg_sem_7_sub_13_marks_obtained,pg_sem_7_sub_13_total_marks,pg_sem_7_sub_14_name,
                 pg_sem_7_sub_14_marks_obtained,pg_sem_7_sub_14_total_marks,pg_sem_7_sub_15_name,
                 pg_sem_7_sub_15_marks_obtained,pg_sem_7_sub_15_total_marks,pg_sem_7_sub_16_name,
                 pg_sem_7_sub_16_marks_obtained,pg_sem_7_sub_16_total_marks,pg_sem_7_sub_17_name,
                 pg_sem_7_sub_17_marks_obtained,pg_sem_7_sub_17_total_marks,pg_sem_7_sub_18_name,
                 pg_sem_7_sub_18_marks_obtained,pg_sem_7_sub_18_total_marks,pg_sem_7_sub_19_name,
                 pg_sem_7_sub_19_marks_obtained,pg_sem_7_sub_19_total_marks,pg_sem_7_sub_20_name,
                 pg_sem_7_sub_20_marks_obtained,pg_sem_7_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_pg_sem_8'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch pg_sem_7_info from the database
            cursor.execute("SELECT * FROM pg_sem_7 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_7_info = cursor.fetchone()

            # Pass the pg_sem_7_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_7.html', pg_sem_7=pg_sem_7_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_pg_sem_8', methods=['GET', 'POST'])
def form_pg_sem_8():
    try:
        if request.method == 'POST':
            return form_pg_sem_8_post()
        else:
            # Fetch pg_sem_8_info from the database
            cursor.execute("SELECT * FROM pg_sem_8 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_8_info = cursor.fetchone()

            # If pg_sem_8_info is None, create a default pg_sem_8_info object
            if pg_sem_8_info is None:
                pg_sem_8_info = {
                    'pg_enrollment_no': '',
                    'pg_sem_8_session': '',
                    'pg_sem_8_roll_no': '',
                    'pg_sem_8_result': '',
                    'pg_sem_8_sub_1_name': '',
                    'pg_sem_8_sub_1_marks_obtained': '',
                    'pg_sem_8_sub_1_total_marks': '',
                    'pg_sem_8_sub_2_name': '',
                    'pg_sem_8_sub_2_marks_obtained': '',
                    'pg_sem_8_sub_2_total_marks': '',
                    'pg_sem_8_sub_3_name': '',
                    'pg_sem_8_sub_3_marks_obtained': '',
                    'pg_sem_8_sub_3_total_marks': '',
                    'pg_sem_8_sub_4_name': '',
                    'pg_sem_8_sub_4_marks_obtained': '',
                    'pg_sem_8_sub_4_total_marks': '',
                    'pg_sem_8_sub_5_name': '',
                    'pg_sem_8_sub_5_marks_obtained': '',
                    'pg_sem_8_sub_5_total_marks': '',
                    'pg_sem_8_sub_6_name': '',
                    'pg_sem_8_sub_6_marks_obtained': '',
                    'pg_sem_8_sub_6_total_marks': '',
                    'pg_sem_8_sub_7_name': '',
                    'pg_sem_8_sub_7_marks_obtained': '',
                    'pg_sem_8_sub_7_total_marks': '',
                    'pg_sem_8_sub_8_name': '',
                    'pg_sem_8_sub_8_marks_obtained': '',
                    'pg_sem_8_sub_8_total_marks': '',
                    'pg_sem_8_sub_9_name': '',
                    'pg_sem_8_sub_9_marks_obtained': '',
                    'pg_sem_8_sub_9_total_marks': '',
                    'pg_sem_8_sub_10_name': '',
                    'pg_sem_8_sub_10_marks_obtained': '',
                    'pg_sem_8_sub_10_total_marks': '',
                    'pg_sem_8_sub_11_name': '',
                    'pg_sem_8_sub_11_marks_obtained': '',
                    'pg_sem_8_sub_11_total_marks': '',
                    'pg_sem_8_sub_12_name': '',
                    'pg_sem_8_sub_12_marks_obtained': '',
                    'pg_sem_8_sub_12_total_marks': '',
                    'pg_sem_8_sub_13_name': '',
                    'pg_sem_8_sub_13_marks_obtained': '',
                    'pg_sem_8_sub_13_total_marks': '',
                    'pg_sem_8_sub_14_name': '',
                    'pg_sem_8_sub_14_marks_obtained': '',
                    'pg_sem_8_sub_14_total_marks': '',
                    'pg_sem_8_sub_15_name': '',
                    'pg_sem_8_sub_15_marks_obtained': '',
                    'pg_sem_8_sub_15_total_marks': '',
                    'pg_sem_8_sub_16_name': '',
                    'pg_sem_8_sub_16_marks_obtained': '',
                    'pg_sem_8_sub_16_total_marks': '',
                    'pg_sem_8_sub_17_name': '',
                    'pg_sem_8_sub_17_marks_obtained': '',
                    'pg_sem_8_sub_17_total_marks': '',
                    'pg_sem_8_sub_18_name': '',
                    'pg_sem_8_sub_18_marks_obtained': '',
                    'pg_sem_8_sub_18_total_marks': '',
                    'pg_sem_8_sub_19_name': '',
                    'pg_sem_8_sub_19_marks_obtained': '',
                    'pg_sem_8_sub_19_total_marks': '',
                    'pg_sem_8_sub_20_name': '',
                    'pg_sem_8_sub_20_marks_obtained': '',
                    'pg_sem_8_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the pg_sem_8_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_8.html', pg_sem_8=pg_sem_8_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_pg_sem_8_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            pg_enrollment_no = request.form['pg_enrollment_no']
            pg_sem_8_session = request.form['pg_sem_8_session']
            pg_sem_8_roll_no = request.form['pg_sem_8_roll_no']
            pg_sem_8_result = request.form['pg_sem_8_result']
            pg_sem_8_sub_1_name = request.form['pg_sem_8_sub_1_name']
            pg_sem_8_sub_1_marks_obtained = request.form['pg_sem_8_sub_1_marks_obtained']
            pg_sem_8_sub_1_total_marks = request.form['pg_sem_8_sub_1_total_marks']
            pg_sem_8_sub_2_name = request.form['pg_sem_8_sub_2_name']
            pg_sem_8_sub_2_marks_obtained = request.form['pg_sem_8_sub_2_marks_obtained']
            pg_sem_8_sub_2_total_marks = request.form['pg_sem_8_sub_2_total_marks']
            pg_sem_8_sub_3_name = request.form['pg_sem_8_sub_3_name']
            pg_sem_8_sub_3_marks_obtained = request.form['pg_sem_8_sub_3_marks_obtained']
            pg_sem_8_sub_3_total_marks = request.form['pg_sem_8_sub_3_total_marks']
            pg_sem_8_sub_4_name = request.form['pg_sem_8_sub_4_name']
            pg_sem_8_sub_4_marks_obtained = request.form['pg_sem_8_sub_4_marks_obtained']
            pg_sem_8_sub_4_total_marks = request.form['pg_sem_8_sub_4_total_marks']
            pg_sem_8_sub_5_name = request.form['pg_sem_8_sub_5_name']
            pg_sem_8_sub_5_marks_obtained = request.form['pg_sem_8_sub_5_marks_obtained']
            pg_sem_8_sub_5_total_marks = request.form['pg_sem_8_sub_5_total_marks']
            pg_sem_8_sub_6_name = request.form['pg_sem_8_sub_6_name']
            pg_sem_8_sub_6_marks_obtained = request.form['pg_sem_8_sub_6_marks_obtained']
            pg_sem_8_sub_6_total_marks = request.form['pg_sem_8_sub_6_total_marks']
            pg_sem_8_sub_7_name = request.form['pg_sem_8_sub_7_name']
            pg_sem_8_sub_7_marks_obtained = request.form['pg_sem_8_sub_7_marks_obtained']
            pg_sem_8_sub_7_total_marks = request.form['pg_sem_8_sub_7_total_marks']
            pg_sem_8_sub_8_name = request.form['pg_sem_8_sub_8_name']
            pg_sem_8_sub_8_marks_obtained = request.form['pg_sem_8_sub_8_marks_obtained']
            pg_sem_8_sub_8_total_marks = request.form['pg_sem_8_sub_8_total_marks']
            pg_sem_8_sub_9_name = request.form['pg_sem_8_sub_9_name']
            pg_sem_8_sub_9_marks_obtained = request.form['pg_sem_8_sub_9_marks_obtained']
            pg_sem_8_sub_9_total_marks = request.form['pg_sem_8_sub_9_total_marks']
            pg_sem_8_sub_10_name = request.form['pg_sem_8_sub_10_name']
            pg_sem_8_sub_10_marks_obtained = request.form['pg_sem_8_sub_10_marks_obtained']
            pg_sem_8_sub_10_total_marks = request.form['pg_sem_8_sub_10_total_marks']
            pg_sem_8_sub_11_name = request.form['pg_sem_8_sub_11_name']
            pg_sem_8_sub_11_marks_obtained = request.form['pg_sem_8_sub_11_marks_obtained']
            pg_sem_8_sub_11_total_marks = request.form['pg_sem_8_sub_11_total_marks']
            pg_sem_8_sub_12_name = request.form['pg_sem_8_sub_12_name']
            pg_sem_8_sub_12_marks_obtained = request.form['pg_sem_8_sub_12_marks_obtained']
            pg_sem_8_sub_12_total_marks = request.form['pg_sem_8_sub_12_total_marks']
            pg_sem_8_sub_13_name = request.form['pg_sem_8_sub_13_name']
            pg_sem_8_sub_13_marks_obtained = request.form['pg_sem_8_sub_13_marks_obtained']
            pg_sem_8_sub_13_total_marks = request.form['pg_sem_8_sub_13_total_marks']
            pg_sem_8_sub_14_name = request.form['pg_sem_8_sub_14_name']
            pg_sem_8_sub_14_marks_obtained = request.form['pg_sem_8_sub_14_marks_obtained']
            pg_sem_8_sub_14_total_marks = request.form['pg_sem_8_sub_14_total_marks']
            pg_sem_8_sub_15_name = request.form['pg_sem_8_sub_15_name']
            pg_sem_8_sub_15_marks_obtained = request.form['pg_sem_8_sub_15_marks_obtained']
            pg_sem_8_sub_15_total_marks = request.form['pg_sem_8_sub_15_total_marks']
            pg_sem_8_sub_16_name = request.form['pg_sem_8_sub_16_name']
            pg_sem_8_sub_16_marks_obtained = request.form['pg_sem_8_sub_16_marks_obtained']
            pg_sem_8_sub_16_total_marks = request.form['pg_sem_8_sub_16_total_marks']
            pg_sem_8_sub_17_name = request.form['pg_sem_8_sub_17_name']
            pg_sem_8_sub_17_marks_obtained = request.form['pg_sem_8_sub_17_marks_obtained']
            pg_sem_8_sub_17_total_marks = request.form['pg_sem_8_sub_17_total_marks']
            pg_sem_8_sub_18_name = request.form['pg_sem_8_sub_18_name']
            pg_sem_8_sub_18_marks_obtained = request.form['pg_sem_8_sub_18_marks_obtained']
            pg_sem_8_sub_18_total_marks = request.form['pg_sem_8_sub_18_total_marks']
            pg_sem_8_sub_19_name = request.form['pg_sem_8_sub_19_name']
            pg_sem_8_sub_19_marks_obtained = request.form['pg_sem_8_sub_19_marks_obtained']
            pg_sem_8_sub_19_total_marks = request.form['pg_sem_8_sub_19_total_marks']
            pg_sem_8_sub_20_name = request.form['pg_sem_8_sub_20_name']
            pg_sem_8_sub_20_marks_obtained = request.form['pg_sem_8_sub_20_marks_obtained']
            pg_sem_8_sub_20_total_marks = request.form['pg_sem_8_sub_20_total_marks']


            # Update pg_sem_8_info in the database
            cursor.execute("""
                UPDATE pg_sem_8
                SET pg_enrollment_no = ?, pg_sem_8_session = ?, pg_sem_8_roll_no = ?, pg_sem_8_result = ?, pg_sem_8_sub_1_name = ?, pg_sem_8_sub_1_marks_obtained = ?, pg_sem_8_sub_1_total_marks = ?, pg_sem_8_sub_2_name = ?, pg_sem_8_sub_2_marks_obtained = ?, pg_sem_8_sub_2_total_marks = ?, pg_sem_8_sub_3_name = ?, pg_sem_8_sub_3_marks_obtained = ?, pg_sem_8_sub_3_total_marks = ?, pg_sem_8_sub_4_name = ?, pg_sem_8_sub_4_marks_obtained = ?, pg_sem_8_sub_4_total_marks = ?, pg_sem_8_sub_5_name = ?, pg_sem_8_sub_5_marks_obtained = ?, pg_sem_8_sub_5_total_marks = ?, pg_sem_8_sub_6_name = ?, pg_sem_8_sub_6_marks_obtained = ?, pg_sem_8_sub_6_total_marks = ?, pg_sem_8_sub_7_name = ?, pg_sem_8_sub_7_marks_obtained = ?, pg_sem_8_sub_7_total_marks = ?, pg_sem_8_sub_8_name = ?, pg_sem_8_sub_8_marks_obtained = ?, pg_sem_8_sub_8_total_marks = ?, pg_sem_8_sub_9_name = ?, pg_sem_8_sub_9_marks_obtained = ?, pg_sem_8_sub_9_total_marks = ?, pg_sem_8_sub_10_name = ?, pg_sem_8_sub_10_marks_obtained = ?, pg_sem_8_sub_10_total_marks = ?, pg_sem_8_sub_11_name = ?, pg_sem_8_sub_11_marks_obtained = ?, pg_sem_8_sub_11_total_marks = ?, pg_sem_8_sub_12_name = ?, pg_sem_8_sub_12_marks_obtained = ?, pg_sem_8_sub_12_total_marks = ?, pg_sem_8_sub_13_name = ?, pg_sem_8_sub_13_marks_obtained = ?, pg_sem_8_sub_13_total_marks = ?, pg_sem_8_sub_14_name = ?, pg_sem_8_sub_14_marks_obtained = ?, pg_sem_8_sub_14_total_marks = ?, pg_sem_8_sub_15_name = ?, pg_sem_8_sub_15_marks_obtained = ?, pg_sem_8_sub_15_total_marks = ?, pg_sem_8_sub_16_name = ?, pg_sem_8_sub_16_marks_obtained = ?, pg_sem_8_sub_16_total_marks = ?, pg_sem_8_sub_17_name = ?, pg_sem_8_sub_17_marks_obtained = ?, pg_sem_8_sub_17_total_marks = ?, pg_sem_8_sub_18_name = ?, pg_sem_8_sub_18_marks_obtained = ?, pg_sem_8_sub_18_total_marks = ?, pg_sem_8_sub_19_name = ?, pg_sem_8_sub_19_marks_obtained = ?, pg_sem_8_sub_19_total_marks = ?, pg_sem_8_sub_20_name = ?, pg_sem_8_sub_20_marks_obtained = ?, pg_sem_8_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(pg_enrollment_no,pg_sem_8_session,pg_sem_8_roll_no,pg_sem_8_result,pg_sem_8_sub_1_name,
                 pg_sem_8_sub_1_marks_obtained,pg_sem_8_sub_1_total_marks,pg_sem_8_sub_2_name,
                 pg_sem_8_sub_2_marks_obtained,pg_sem_8_sub_2_total_marks,pg_sem_8_sub_3_name,
                 pg_sem_8_sub_3_marks_obtained,pg_sem_8_sub_3_total_marks,pg_sem_8_sub_4_name,
                 pg_sem_8_sub_4_marks_obtained,pg_sem_8_sub_4_total_marks,pg_sem_8_sub_5_name,
                 pg_sem_8_sub_5_marks_obtained,pg_sem_8_sub_5_total_marks,pg_sem_8_sub_6_name,
                 pg_sem_8_sub_6_marks_obtained,pg_sem_8_sub_6_total_marks,pg_sem_8_sub_7_name,
                 pg_sem_8_sub_7_marks_obtained,pg_sem_8_sub_7_total_marks,pg_sem_8_sub_8_name,
                 pg_sem_8_sub_8_marks_obtained,pg_sem_8_sub_8_total_marks,pg_sem_8_sub_9_name,
                 pg_sem_8_sub_9_marks_obtained,pg_sem_8_sub_9_total_marks,pg_sem_8_sub_10_name,
                 pg_sem_8_sub_10_marks_obtained,pg_sem_8_sub_10_total_marks,pg_sem_8_sub_11_name,
                 pg_sem_8_sub_11_marks_obtained,pg_sem_8_sub_11_total_marks,pg_sem_8_sub_12_name,
                 pg_sem_8_sub_12_marks_obtained,pg_sem_8_sub_12_total_marks,pg_sem_8_sub_13_name,
                 pg_sem_8_sub_13_marks_obtained,pg_sem_8_sub_13_total_marks,pg_sem_8_sub_14_name,
                 pg_sem_8_sub_14_marks_obtained,pg_sem_8_sub_14_total_marks,pg_sem_8_sub_15_name,
                 pg_sem_8_sub_15_marks_obtained,pg_sem_8_sub_15_total_marks,pg_sem_8_sub_16_name,
                 pg_sem_8_sub_16_marks_obtained,pg_sem_8_sub_16_total_marks,pg_sem_8_sub_17_name,
                 pg_sem_8_sub_17_marks_obtained,pg_sem_8_sub_17_total_marks,pg_sem_8_sub_18_name,
                 pg_sem_8_sub_18_marks_obtained,pg_sem_8_sub_18_total_marks,pg_sem_8_sub_19_name,
                 pg_sem_8_sub_19_marks_obtained,pg_sem_8_sub_19_total_marks,pg_sem_8_sub_20_name,
                 pg_sem_8_sub_20_marks_obtained,pg_sem_8_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_pg_sem_9'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch pg_sem_8_info from the database
            cursor.execute("SELECT * FROM pg_sem_8 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_8_info = cursor.fetchone()

            # Pass the pg_sem_8_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_8.html', pg_sem_8=pg_sem_8_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_pg_sem_9', methods=['GET', 'POST'])
def form_pg_sem_9():
    try:
        if request.method == 'POST':
            return form_pg_sem_9_post()
        else:
            # Fetch pg_sem_9_info from the database
            cursor.execute("SELECT * FROM pg_sem_9 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_9_info = cursor.fetchone()

            # If pg_sem_9_info is None, create a default pg_sem_9_info object
            if pg_sem_9_info is None:
                pg_sem_9_info = {
                    'pg_enrollment_no': '',
                    'pg_sem_9_session': '',
                    'pg_sem_9_roll_no': '',
                    'pg_sem_9_result': '',
                    'pg_sem_9_sub_1_name': '',
                    'pg_sem_9_sub_1_marks_obtained': '',
                    'pg_sem_9_sub_1_total_marks': '',
                    'pg_sem_9_sub_2_name': '',
                    'pg_sem_9_sub_2_marks_obtained': '',
                    'pg_sem_9_sub_2_total_marks': '',
                    'pg_sem_9_sub_3_name': '',
                    'pg_sem_9_sub_3_marks_obtained': '',
                    'pg_sem_9_sub_3_total_marks': '',
                    'pg_sem_9_sub_4_name': '',
                    'pg_sem_9_sub_4_marks_obtained': '',
                    'pg_sem_9_sub_4_total_marks': '',
                    'pg_sem_9_sub_5_name': '',
                    'pg_sem_9_sub_5_marks_obtained': '',
                    'pg_sem_9_sub_5_total_marks': '',
                    'pg_sem_9_sub_6_name': '',
                    'pg_sem_9_sub_6_marks_obtained': '',
                    'pg_sem_9_sub_6_total_marks': '',
                    'pg_sem_9_sub_7_name': '',
                    'pg_sem_9_sub_7_marks_obtained': '',
                    'pg_sem_9_sub_7_total_marks': '',
                    'pg_sem_9_sub_8_name': '',
                    'pg_sem_9_sub_8_marks_obtained': '',
                    'pg_sem_9_sub_8_total_marks': '',
                    'pg_sem_9_sub_9_name': '',
                    'pg_sem_9_sub_9_marks_obtained': '',
                    'pg_sem_9_sub_9_total_marks': '',
                    'pg_sem_9_sub_10_name': '',
                    'pg_sem_9_sub_10_marks_obtained': '',
                    'pg_sem_9_sub_10_total_marks': '',
                    'pg_sem_9_sub_11_name': '',
                    'pg_sem_9_sub_11_marks_obtained': '',
                    'pg_sem_9_sub_11_total_marks': '',
                    'pg_sem_9_sub_12_name': '',
                    'pg_sem_9_sub_12_marks_obtained': '',
                    'pg_sem_9_sub_12_total_marks': '',
                    'pg_sem_9_sub_13_name': '',
                    'pg_sem_9_sub_13_marks_obtained': '',
                    'pg_sem_9_sub_13_total_marks': '',
                    'pg_sem_9_sub_14_name': '',
                    'pg_sem_9_sub_14_marks_obtained': '',
                    'pg_sem_9_sub_14_total_marks': '',
                    'pg_sem_9_sub_15_name': '',
                    'pg_sem_9_sub_15_marks_obtained': '',
                    'pg_sem_9_sub_15_total_marks': '',
                    'pg_sem_9_sub_16_name': '',
                    'pg_sem_9_sub_16_marks_obtained': '',
                    'pg_sem_9_sub_16_total_marks': '',
                    'pg_sem_9_sub_17_name': '',
                    'pg_sem_9_sub_17_marks_obtained': '',
                    'pg_sem_9_sub_17_total_marks': '',
                    'pg_sem_9_sub_18_name': '',
                    'pg_sem_9_sub_18_marks_obtained': '',
                    'pg_sem_9_sub_18_total_marks': '',
                    'pg_sem_9_sub_19_name': '',
                    'pg_sem_9_sub_19_marks_obtained': '',
                    'pg_sem_9_sub_19_total_marks': '',
                    'pg_sem_9_sub_20_name': '',
                    'pg_sem_9_sub_20_marks_obtained': '',
                    'pg_sem_9_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the pg_sem_9_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_9.html', pg_sem_9=pg_sem_9_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_pg_sem_9_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            pg_enrollment_no = request.form['pg_enrollment_no']
            pg_sem_9_session = request.form['pg_sem_9_session']
            pg_sem_9_roll_no = request.form['pg_sem_9_roll_no']
            pg_sem_9_result = request.form['pg_sem_9_result']
            pg_sem_9_sub_1_name = request.form['pg_sem_9_sub_1_name']
            pg_sem_9_sub_1_marks_obtained = request.form['pg_sem_9_sub_1_marks_obtained']
            pg_sem_9_sub_1_total_marks = request.form['pg_sem_9_sub_1_total_marks']
            pg_sem_9_sub_2_name = request.form['pg_sem_9_sub_2_name']
            pg_sem_9_sub_2_marks_obtained = request.form['pg_sem_9_sub_2_marks_obtained']
            pg_sem_9_sub_2_total_marks = request.form['pg_sem_9_sub_2_total_marks']
            pg_sem_9_sub_3_name = request.form['pg_sem_9_sub_3_name']
            pg_sem_9_sub_3_marks_obtained = request.form['pg_sem_9_sub_3_marks_obtained']
            pg_sem_9_sub_3_total_marks = request.form['pg_sem_9_sub_3_total_marks']
            pg_sem_9_sub_4_name = request.form['pg_sem_9_sub_4_name']
            pg_sem_9_sub_4_marks_obtained = request.form['pg_sem_9_sub_4_marks_obtained']
            pg_sem_9_sub_4_total_marks = request.form['pg_sem_9_sub_4_total_marks']
            pg_sem_9_sub_5_name = request.form['pg_sem_9_sub_5_name']
            pg_sem_9_sub_5_marks_obtained = request.form['pg_sem_9_sub_5_marks_obtained']
            pg_sem_9_sub_5_total_marks = request.form['pg_sem_9_sub_5_total_marks']
            pg_sem_9_sub_6_name = request.form['pg_sem_9_sub_6_name']
            pg_sem_9_sub_6_marks_obtained = request.form['pg_sem_9_sub_6_marks_obtained']
            pg_sem_9_sub_6_total_marks = request.form['pg_sem_9_sub_6_total_marks']
            pg_sem_9_sub_7_name = request.form['pg_sem_9_sub_7_name']
            pg_sem_9_sub_7_marks_obtained = request.form['pg_sem_9_sub_7_marks_obtained']
            pg_sem_9_sub_7_total_marks = request.form['pg_sem_9_sub_7_total_marks']
            pg_sem_9_sub_8_name = request.form['pg_sem_9_sub_8_name']
            pg_sem_9_sub_8_marks_obtained = request.form['pg_sem_9_sub_8_marks_obtained']
            pg_sem_9_sub_8_total_marks = request.form['pg_sem_9_sub_8_total_marks']
            pg_sem_9_sub_9_name = request.form['pg_sem_9_sub_9_name']
            pg_sem_9_sub_9_marks_obtained = request.form['pg_sem_9_sub_9_marks_obtained']
            pg_sem_9_sub_9_total_marks = request.form['pg_sem_9_sub_9_total_marks']
            pg_sem_9_sub_10_name = request.form['pg_sem_9_sub_10_name']
            pg_sem_9_sub_10_marks_obtained = request.form['pg_sem_9_sub_10_marks_obtained']
            pg_sem_9_sub_10_total_marks = request.form['pg_sem_9_sub_10_total_marks']
            pg_sem_9_sub_11_name = request.form['pg_sem_9_sub_11_name']
            pg_sem_9_sub_11_marks_obtained = request.form['pg_sem_9_sub_11_marks_obtained']
            pg_sem_9_sub_11_total_marks = request.form['pg_sem_9_sub_11_total_marks']
            pg_sem_9_sub_12_name = request.form['pg_sem_9_sub_12_name']
            pg_sem_9_sub_12_marks_obtained = request.form['pg_sem_9_sub_12_marks_obtained']
            pg_sem_9_sub_12_total_marks = request.form['pg_sem_9_sub_12_total_marks']
            pg_sem_9_sub_13_name = request.form['pg_sem_9_sub_13_name']
            pg_sem_9_sub_13_marks_obtained = request.form['pg_sem_9_sub_13_marks_obtained']
            pg_sem_9_sub_13_total_marks = request.form['pg_sem_9_sub_13_total_marks']
            pg_sem_9_sub_14_name = request.form['pg_sem_9_sub_14_name']
            pg_sem_9_sub_14_marks_obtained = request.form['pg_sem_9_sub_14_marks_obtained']
            pg_sem_9_sub_14_total_marks = request.form['pg_sem_9_sub_14_total_marks']
            pg_sem_9_sub_15_name = request.form['pg_sem_9_sub_15_name']
            pg_sem_9_sub_15_marks_obtained = request.form['pg_sem_9_sub_15_marks_obtained']
            pg_sem_9_sub_15_total_marks = request.form['pg_sem_9_sub_15_total_marks']
            pg_sem_9_sub_16_name = request.form['pg_sem_9_sub_16_name']
            pg_sem_9_sub_16_marks_obtained = request.form['pg_sem_9_sub_16_marks_obtained']
            pg_sem_9_sub_16_total_marks = request.form['pg_sem_9_sub_16_total_marks']
            pg_sem_9_sub_17_name = request.form['pg_sem_9_sub_17_name']
            pg_sem_9_sub_17_marks_obtained = request.form['pg_sem_9_sub_17_marks_obtained']
            pg_sem_9_sub_17_total_marks = request.form['pg_sem_9_sub_17_total_marks']
            pg_sem_9_sub_18_name = request.form['pg_sem_9_sub_18_name']
            pg_sem_9_sub_18_marks_obtained = request.form['pg_sem_9_sub_18_marks_obtained']
            pg_sem_9_sub_18_total_marks = request.form['pg_sem_9_sub_18_total_marks']
            pg_sem_9_sub_19_name = request.form['pg_sem_9_sub_19_name']
            pg_sem_9_sub_19_marks_obtained = request.form['pg_sem_9_sub_19_marks_obtained']
            pg_sem_9_sub_19_total_marks = request.form['pg_sem_9_sub_19_total_marks']
            pg_sem_9_sub_20_name = request.form['pg_sem_9_sub_20_name']
            pg_sem_9_sub_20_marks_obtained = request.form['pg_sem_9_sub_20_marks_obtained']
            pg_sem_9_sub_20_total_marks = request.form['pg_sem_9_sub_20_total_marks']


            # Update pg_sem_9_info in the database
            cursor.execute("""
                UPDATE pg_sem_9
                SET pg_enrollment_no = ?, pg_sem_9_session = ?, pg_sem_9_roll_no = ?, pg_sem_9_result = ?, pg_sem_9_sub_1_name = ?, pg_sem_9_sub_1_marks_obtained = ?, pg_sem_9_sub_1_total_marks = ?, pg_sem_9_sub_2_name = ?, pg_sem_9_sub_2_marks_obtained = ?, pg_sem_9_sub_2_total_marks = ?, pg_sem_9_sub_3_name = ?, pg_sem_9_sub_3_marks_obtained = ?, pg_sem_9_sub_3_total_marks = ?, pg_sem_9_sub_4_name = ?, pg_sem_9_sub_4_marks_obtained = ?, pg_sem_9_sub_4_total_marks = ?, pg_sem_9_sub_5_name = ?, pg_sem_9_sub_5_marks_obtained = ?, pg_sem_9_sub_5_total_marks = ?, pg_sem_9_sub_6_name = ?, pg_sem_9_sub_6_marks_obtained = ?, pg_sem_9_sub_6_total_marks = ?, pg_sem_9_sub_7_name = ?, pg_sem_9_sub_7_marks_obtained = ?, pg_sem_9_sub_7_total_marks = ?, pg_sem_9_sub_8_name = ?, pg_sem_9_sub_8_marks_obtained = ?, pg_sem_9_sub_8_total_marks = ?, pg_sem_9_sub_9_name = ?, pg_sem_9_sub_9_marks_obtained = ?, pg_sem_9_sub_9_total_marks = ?, pg_sem_9_sub_10_name = ?, pg_sem_9_sub_10_marks_obtained = ?, pg_sem_9_sub_10_total_marks = ?, pg_sem_9_sub_11_name = ?, pg_sem_9_sub_11_marks_obtained = ?, pg_sem_9_sub_11_total_marks = ?, pg_sem_9_sub_12_name = ?, pg_sem_9_sub_12_marks_obtained = ?, pg_sem_9_sub_12_total_marks = ?, pg_sem_9_sub_13_name = ?, pg_sem_9_sub_13_marks_obtained = ?, pg_sem_9_sub_13_total_marks = ?, pg_sem_9_sub_14_name = ?, pg_sem_9_sub_14_marks_obtained = ?, pg_sem_9_sub_14_total_marks = ?, pg_sem_9_sub_15_name = ?, pg_sem_9_sub_15_marks_obtained = ?, pg_sem_9_sub_15_total_marks = ?, pg_sem_9_sub_16_name = ?, pg_sem_9_sub_16_marks_obtained = ?, pg_sem_9_sub_16_total_marks = ?, pg_sem_9_sub_17_name = ?, pg_sem_9_sub_17_marks_obtained = ?, pg_sem_9_sub_17_total_marks = ?, pg_sem_9_sub_18_name = ?, pg_sem_9_sub_18_marks_obtained = ?, pg_sem_9_sub_18_total_marks = ?, pg_sem_9_sub_19_name = ?, pg_sem_9_sub_19_marks_obtained = ?, pg_sem_9_sub_19_total_marks = ?, pg_sem_9_sub_20_name = ?, pg_sem_9_sub_20_marks_obtained = ?, pg_sem_9_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(pg_enrollment_no,pg_sem_9_session,pg_sem_9_roll_no,pg_sem_9_result,pg_sem_9_sub_1_name,
                 pg_sem_9_sub_1_marks_obtained,pg_sem_9_sub_1_total_marks,pg_sem_9_sub_2_name,
                 pg_sem_9_sub_2_marks_obtained,pg_sem_9_sub_2_total_marks,pg_sem_9_sub_3_name,
                 pg_sem_9_sub_3_marks_obtained,pg_sem_9_sub_3_total_marks,pg_sem_9_sub_4_name,
                 pg_sem_9_sub_4_marks_obtained,pg_sem_9_sub_4_total_marks,pg_sem_9_sub_5_name,
                 pg_sem_9_sub_5_marks_obtained,pg_sem_9_sub_5_total_marks,pg_sem_9_sub_6_name,
                 pg_sem_9_sub_6_marks_obtained,pg_sem_9_sub_6_total_marks,pg_sem_9_sub_7_name,
                 pg_sem_9_sub_7_marks_obtained,pg_sem_9_sub_7_total_marks,pg_sem_9_sub_8_name,
                 pg_sem_9_sub_8_marks_obtained,pg_sem_9_sub_8_total_marks,pg_sem_9_sub_9_name,
                 pg_sem_9_sub_9_marks_obtained,pg_sem_9_sub_9_total_marks,pg_sem_9_sub_10_name,
                 pg_sem_9_sub_10_marks_obtained,pg_sem_9_sub_10_total_marks,pg_sem_9_sub_11_name,
                 pg_sem_9_sub_11_marks_obtained,pg_sem_9_sub_11_total_marks,pg_sem_9_sub_12_name,
                 pg_sem_9_sub_12_marks_obtained,pg_sem_9_sub_12_total_marks,pg_sem_9_sub_13_name,
                 pg_sem_9_sub_13_marks_obtained,pg_sem_9_sub_13_total_marks,pg_sem_9_sub_14_name,
                 pg_sem_9_sub_14_marks_obtained,pg_sem_9_sub_14_total_marks,pg_sem_9_sub_15_name,
                 pg_sem_9_sub_15_marks_obtained,pg_sem_9_sub_15_total_marks,pg_sem_9_sub_16_name,
                 pg_sem_9_sub_16_marks_obtained,pg_sem_9_sub_16_total_marks,pg_sem_9_sub_17_name,
                 pg_sem_9_sub_17_marks_obtained,pg_sem_9_sub_17_total_marks,pg_sem_9_sub_18_name,
                 pg_sem_9_sub_18_marks_obtained,pg_sem_9_sub_18_total_marks,pg_sem_9_sub_19_name,
                 pg_sem_9_sub_19_marks_obtained,pg_sem_9_sub_19_total_marks,pg_sem_9_sub_20_name,
                 pg_sem_9_sub_20_marks_obtained,pg_sem_9_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_pg_sem_10'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch pg_sem_9_info from the database
            cursor.execute("SELECT * FROM pg_sem_9 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_9_info = cursor.fetchone()

            # Pass the pg_sem_9_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_9.html', pg_sem_9=pg_sem_9_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

@app.route('/form_pg_sem_10', methods=['GET', 'POST'])
def form_pg_sem_10():
    try:
        if request.method == 'POST':
            return form_pg_sem_10_post()
        else:
            # Fetch pg_sem_10_info from the database
            cursor.execute("SELECT * FROM pg_sem_10 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_10_info = cursor.fetchone()

            # If pg_sem_10_info is None, create a default pg_sem_10_info object
            if pg_sem_10_info is None:
                pg_sem_10_info = {
                    'pg_enrollment_no': '',
                    'pg_sem_10_session': '',
                    'pg_sem_10_roll_no': '',
                    'pg_sem_10_result': '',
                    'pg_sem_10_sub_1_name': '',
                    'pg_sem_10_sub_1_marks_obtained': '',
                    'pg_sem_10_sub_1_total_marks': '',
                    'pg_sem_10_sub_2_name': '',
                    'pg_sem_10_sub_2_marks_obtained': '',
                    'pg_sem_10_sub_2_total_marks': '',
                    'pg_sem_10_sub_3_name': '',
                    'pg_sem_10_sub_3_marks_obtained': '',
                    'pg_sem_10_sub_3_total_marks': '',
                    'pg_sem_10_sub_4_name': '',
                    'pg_sem_10_sub_4_marks_obtained': '',
                    'pg_sem_10_sub_4_total_marks': '',
                    'pg_sem_10_sub_5_name': '',
                    'pg_sem_10_sub_5_marks_obtained': '',
                    'pg_sem_10_sub_5_total_marks': '',
                    'pg_sem_10_sub_6_name': '',
                    'pg_sem_10_sub_6_marks_obtained': '',
                    'pg_sem_10_sub_6_total_marks': '',
                    'pg_sem_10_sub_7_name': '',
                    'pg_sem_10_sub_7_marks_obtained': '',
                    'pg_sem_10_sub_7_total_marks': '',
                    'pg_sem_10_sub_8_name': '',
                    'pg_sem_10_sub_8_marks_obtained': '',
                    'pg_sem_10_sub_8_total_marks': '',
                    'pg_sem_10_sub_9_name': '',
                    'pg_sem_10_sub_9_marks_obtained': '',
                    'pg_sem_10_sub_9_total_marks': '',
                    'pg_sem_10_sub_10_name': '',
                    'pg_sem_10_sub_10_marks_obtained': '',
                    'pg_sem_10_sub_10_total_marks': '',
                    'pg_sem_10_sub_11_name': '',
                    'pg_sem_10_sub_11_marks_obtained': '',
                    'pg_sem_10_sub_11_total_marks': '',
                    'pg_sem_10_sub_12_name': '',
                    'pg_sem_10_sub_12_marks_obtained': '',
                    'pg_sem_10_sub_12_total_marks': '',
                    'pg_sem_10_sub_13_name': '',
                    'pg_sem_10_sub_13_marks_obtained': '',
                    'pg_sem_10_sub_13_total_marks': '',
                    'pg_sem_10_sub_14_name': '',
                    'pg_sem_10_sub_14_marks_obtained': '',
                    'pg_sem_10_sub_14_total_marks': '',
                    'pg_sem_10_sub_15_name': '',
                    'pg_sem_10_sub_15_marks_obtained': '',
                    'pg_sem_10_sub_15_total_marks': '',
                    'pg_sem_10_sub_16_name': '',
                    'pg_sem_10_sub_16_marks_obtained': '',
                    'pg_sem_10_sub_16_total_marks': '',
                    'pg_sem_10_sub_17_name': '',
                    'pg_sem_10_sub_17_marks_obtained': '',
                    'pg_sem_10_sub_17_total_marks': '',
                    'pg_sem_10_sub_18_name': '',
                    'pg_sem_10_sub_18_marks_obtained': '',
                    'pg_sem_10_sub_18_total_marks': '',
                    'pg_sem_10_sub_19_name': '',
                    'pg_sem_10_sub_19_marks_obtained': '',
                    'pg_sem_10_sub_19_total_marks': '',
                    'pg_sem_10_sub_20_name': '',
                    'pg_sem_10_sub_20_marks_obtained': '',
                    'pg_sem_10_sub_20_total_marks': ''

                    # Add more fields as needed
                }

            # Pass the pg_sem_10_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_10.html', pg_sem_10=pg_sem_10_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

def form_pg_sem_10_post():
    try:
        if request.method == 'POST':
            # Get form data
            aadhaar_no = session['aadhaar_no']
            pg_enrollment_no = request.form['pg_enrollment_no']
            pg_sem_10_session = request.form['pg_sem_10_session']
            pg_sem_10_roll_no = request.form['pg_sem_10_roll_no']
            pg_sem_10_result = request.form['pg_sem_10_result']
            pg_sem_10_sub_1_name = request.form['pg_sem_10_sub_1_name']
            pg_sem_10_sub_1_marks_obtained = request.form['pg_sem_10_sub_1_marks_obtained']
            pg_sem_10_sub_1_total_marks = request.form['pg_sem_10_sub_1_total_marks']
            pg_sem_10_sub_2_name = request.form['pg_sem_10_sub_2_name']
            pg_sem_10_sub_2_marks_obtained = request.form['pg_sem_10_sub_2_marks_obtained']
            pg_sem_10_sub_2_total_marks = request.form['pg_sem_10_sub_2_total_marks']
            pg_sem_10_sub_3_name = request.form['pg_sem_10_sub_3_name']
            pg_sem_10_sub_3_marks_obtained = request.form['pg_sem_10_sub_3_marks_obtained']
            pg_sem_10_sub_3_total_marks = request.form['pg_sem_10_sub_3_total_marks']
            pg_sem_10_sub_4_name = request.form['pg_sem_10_sub_4_name']
            pg_sem_10_sub_4_marks_obtained = request.form['pg_sem_10_sub_4_marks_obtained']
            pg_sem_10_sub_4_total_marks = request.form['pg_sem_10_sub_4_total_marks']
            pg_sem_10_sub_5_name = request.form['pg_sem_10_sub_5_name']
            pg_sem_10_sub_5_marks_obtained = request.form['pg_sem_10_sub_5_marks_obtained']
            pg_sem_10_sub_5_total_marks = request.form['pg_sem_10_sub_5_total_marks']
            pg_sem_10_sub_6_name = request.form['pg_sem_10_sub_6_name']
            pg_sem_10_sub_6_marks_obtained = request.form['pg_sem_10_sub_6_marks_obtained']
            pg_sem_10_sub_6_total_marks = request.form['pg_sem_10_sub_6_total_marks']
            pg_sem_10_sub_7_name = request.form['pg_sem_10_sub_7_name']
            pg_sem_10_sub_7_marks_obtained = request.form['pg_sem_10_sub_7_marks_obtained']
            pg_sem_10_sub_7_total_marks = request.form['pg_sem_10_sub_7_total_marks']
            pg_sem_10_sub_8_name = request.form['pg_sem_10_sub_8_name']
            pg_sem_10_sub_8_marks_obtained = request.form['pg_sem_10_sub_8_marks_obtained']
            pg_sem_10_sub_8_total_marks = request.form['pg_sem_10_sub_8_total_marks']
            pg_sem_10_sub_9_name = request.form['pg_sem_10_sub_9_name']
            pg_sem_10_sub_9_marks_obtained = request.form['pg_sem_10_sub_9_marks_obtained']
            pg_sem_10_sub_9_total_marks = request.form['pg_sem_10_sub_9_total_marks']
            pg_sem_10_sub_10_name = request.form['pg_sem_10_sub_10_name']
            pg_sem_10_sub_10_marks_obtained = request.form['pg_sem_10_sub_10_marks_obtained']
            pg_sem_10_sub_10_total_marks = request.form['pg_sem_10_sub_10_total_marks']
            pg_sem_10_sub_11_name = request.form['pg_sem_10_sub_11_name']
            pg_sem_10_sub_11_marks_obtained = request.form['pg_sem_10_sub_11_marks_obtained']
            pg_sem_10_sub_11_total_marks = request.form['pg_sem_10_sub_11_total_marks']
            pg_sem_10_sub_12_name = request.form['pg_sem_10_sub_12_name']
            pg_sem_10_sub_12_marks_obtained = request.form['pg_sem_10_sub_12_marks_obtained']
            pg_sem_10_sub_12_total_marks = request.form['pg_sem_10_sub_12_total_marks']
            pg_sem_10_sub_13_name = request.form['pg_sem_10_sub_13_name']
            pg_sem_10_sub_13_marks_obtained = request.form['pg_sem_10_sub_13_marks_obtained']
            pg_sem_10_sub_13_total_marks = request.form['pg_sem_10_sub_13_total_marks']
            pg_sem_10_sub_14_name = request.form['pg_sem_10_sub_14_name']
            pg_sem_10_sub_14_marks_obtained = request.form['pg_sem_10_sub_14_marks_obtained']
            pg_sem_10_sub_14_total_marks = request.form['pg_sem_10_sub_14_total_marks']
            pg_sem_10_sub_15_name = request.form['pg_sem_10_sub_15_name']
            pg_sem_10_sub_15_marks_obtained = request.form['pg_sem_10_sub_15_marks_obtained']
            pg_sem_10_sub_15_total_marks = request.form['pg_sem_10_sub_15_total_marks']
            pg_sem_10_sub_16_name = request.form['pg_sem_10_sub_16_name']
            pg_sem_10_sub_16_marks_obtained = request.form['pg_sem_10_sub_16_marks_obtained']
            pg_sem_10_sub_16_total_marks = request.form['pg_sem_10_sub_16_total_marks']
            pg_sem_10_sub_17_name = request.form['pg_sem_10_sub_17_name']
            pg_sem_10_sub_17_marks_obtained = request.form['pg_sem_10_sub_17_marks_obtained']
            pg_sem_10_sub_17_total_marks = request.form['pg_sem_10_sub_17_total_marks']
            pg_sem_10_sub_18_name = request.form['pg_sem_10_sub_18_name']
            pg_sem_10_sub_18_marks_obtained = request.form['pg_sem_10_sub_18_marks_obtained']
            pg_sem_10_sub_18_total_marks = request.form['pg_sem_10_sub_18_total_marks']
            pg_sem_10_sub_19_name = request.form['pg_sem_10_sub_19_name']
            pg_sem_10_sub_19_marks_obtained = request.form['pg_sem_10_sub_19_marks_obtained']
            pg_sem_10_sub_19_total_marks = request.form['pg_sem_10_sub_19_total_marks']
            pg_sem_10_sub_20_name = request.form['pg_sem_10_sub_20_name']
            pg_sem_10_sub_20_marks_obtained = request.form['pg_sem_10_sub_20_marks_obtained']
            pg_sem_10_sub_20_total_marks = request.form['pg_sem_10_sub_20_total_marks']


            # Update pg_sem_10_info in the database
            cursor.execute("""
                UPDATE pg_sem_10
                SET pg_enrollment_no = ?, pg_sem_10_session = ?, pg_sem_10_roll_no = ?, pg_sem_10_result = ?, pg_sem_10_sub_1_name = ?, pg_sem_10_sub_1_marks_obtained = ?, pg_sem_10_sub_1_total_marks = ?, pg_sem_10_sub_2_name = ?, pg_sem_10_sub_2_marks_obtained = ?, pg_sem_10_sub_2_total_marks = ?, pg_sem_10_sub_3_name = ?, pg_sem_10_sub_3_marks_obtained = ?, pg_sem_10_sub_3_total_marks = ?, pg_sem_10_sub_4_name = ?, pg_sem_10_sub_4_marks_obtained = ?, pg_sem_10_sub_4_total_marks = ?, pg_sem_10_sub_5_name = ?, pg_sem_10_sub_5_marks_obtained = ?, pg_sem_10_sub_5_total_marks = ?, pg_sem_10_sub_6_name = ?, pg_sem_10_sub_6_marks_obtained = ?, pg_sem_10_sub_6_total_marks = ?, pg_sem_10_sub_7_name = ?, pg_sem_10_sub_7_marks_obtained = ?, pg_sem_10_sub_7_total_marks = ?, pg_sem_10_sub_8_name = ?, pg_sem_10_sub_8_marks_obtained = ?, pg_sem_10_sub_8_total_marks = ?, pg_sem_10_sub_9_name = ?, pg_sem_10_sub_9_marks_obtained = ?, pg_sem_10_sub_9_total_marks = ?, pg_sem_10_sub_10_name = ?, pg_sem_10_sub_10_marks_obtained = ?, pg_sem_10_sub_10_total_marks = ?, pg_sem_10_sub_11_name = ?, pg_sem_10_sub_11_marks_obtained = ?, pg_sem_10_sub_11_total_marks = ?, pg_sem_10_sub_12_name = ?, pg_sem_10_sub_12_marks_obtained = ?, pg_sem_10_sub_12_total_marks = ?, pg_sem_10_sub_13_name = ?, pg_sem_10_sub_13_marks_obtained = ?, pg_sem_10_sub_13_total_marks = ?, pg_sem_10_sub_14_name = ?, pg_sem_10_sub_14_marks_obtained = ?, pg_sem_10_sub_14_total_marks = ?, pg_sem_10_sub_15_name = ?, pg_sem_10_sub_15_marks_obtained = ?, pg_sem_10_sub_15_total_marks = ?, pg_sem_10_sub_16_name = ?, pg_sem_10_sub_16_marks_obtained = ?, pg_sem_10_sub_16_total_marks = ?, pg_sem_10_sub_17_name = ?, pg_sem_10_sub_17_marks_obtained = ?, pg_sem_10_sub_17_total_marks = ?, pg_sem_10_sub_18_name = ?, pg_sem_10_sub_18_marks_obtained = ?, pg_sem_10_sub_18_total_marks = ?, pg_sem_10_sub_19_name = ?, pg_sem_10_sub_19_marks_obtained = ?, pg_sem_10_sub_19_total_marks = ?, pg_sem_10_sub_20_name = ?, pg_sem_10_sub_20_marks_obtained = ?, pg_sem_10_sub_20_total_marks = ?
                WHERE aadhaar_no = ?
            """,(pg_enrollment_no,pg_sem_10_session,pg_sem_10_roll_no,pg_sem_10_result,pg_sem_10_sub_1_name,
                 pg_sem_10_sub_1_marks_obtained,pg_sem_10_sub_1_total_marks,pg_sem_10_sub_2_name,
                 pg_sem_10_sub_2_marks_obtained,pg_sem_10_sub_2_total_marks,pg_sem_10_sub_3_name,
                 pg_sem_10_sub_3_marks_obtained,pg_sem_10_sub_3_total_marks,pg_sem_10_sub_4_name,
                 pg_sem_10_sub_4_marks_obtained,pg_sem_10_sub_4_total_marks,pg_sem_10_sub_5_name,
                 pg_sem_10_sub_5_marks_obtained,pg_sem_10_sub_5_total_marks,pg_sem_10_sub_6_name,
                 pg_sem_10_sub_6_marks_obtained,pg_sem_10_sub_6_total_marks,pg_sem_10_sub_7_name,
                 pg_sem_10_sub_7_marks_obtained,pg_sem_10_sub_7_total_marks,pg_sem_10_sub_8_name,
                 pg_sem_10_sub_8_marks_obtained,pg_sem_10_sub_8_total_marks,pg_sem_10_sub_9_name,
                 pg_sem_10_sub_9_marks_obtained,pg_sem_10_sub_9_total_marks,pg_sem_10_sub_10_name,
                 pg_sem_10_sub_10_marks_obtained,pg_sem_10_sub_10_total_marks,pg_sem_10_sub_11_name,
                 pg_sem_10_sub_11_marks_obtained,pg_sem_10_sub_11_total_marks,pg_sem_10_sub_12_name,
                 pg_sem_10_sub_12_marks_obtained,pg_sem_10_sub_12_total_marks,pg_sem_10_sub_13_name,
                 pg_sem_10_sub_13_marks_obtained,pg_sem_10_sub_13_total_marks,pg_sem_10_sub_14_name,
                 pg_sem_10_sub_14_marks_obtained,pg_sem_10_sub_14_total_marks,pg_sem_10_sub_15_name,
                 pg_sem_10_sub_15_marks_obtained,pg_sem_10_sub_15_total_marks,pg_sem_10_sub_16_name,
                 pg_sem_10_sub_16_marks_obtained,pg_sem_10_sub_16_total_marks,pg_sem_10_sub_17_name,
                 pg_sem_10_sub_17_marks_obtained,pg_sem_10_sub_17_total_marks,pg_sem_10_sub_18_name,
                 pg_sem_10_sub_18_marks_obtained,pg_sem_10_sub_18_total_marks,pg_sem_10_sub_19_name,
                 pg_sem_10_sub_19_marks_obtained,pg_sem_10_sub_19_total_marks,pg_sem_10_sub_20_name,
                 pg_sem_10_sub_20_marks_obtained,pg_sem_10_sub_20_total_marks,aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('student_profile'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch pg_sem_10_info from the database
            cursor.execute("SELECT * FROM pg_sem_10 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            pg_sem_10_info = cursor.fetchone()

            # Pass the pg_sem_10_info to the template
            return render_template('Student/student_info_forms/form_pg_sem_10.html', pg_sem_10=pg_sem_10_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500

# Routes for student form
############################################

@app.route('/student_dashboard/gc1')
def gc1():
    pie_charts_html = []
    j=1
    for i in range(1, 6):
        # Execute the SQL query
        cursor.execute(f"SELECT c_{j}_sub_{i}_name, c_{j}_sub_{i}_marks_obtained, c_{j}_sub_{i}_total_marks FROM class_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for class {j}</p>")

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Academic Performance/gc1.html', pie_charts=pie_charts_html)

@app.route('/student_dashboard/gc2')
def gc2():
    pie_charts_html = []
    j=2
    for i in range(1, 6):
        # Execute the SQL query
        cursor.execute(f"SELECT c_{j}_sub_{i}_name, c_{j}_sub_{i}_marks_obtained, c_{j}_sub_{i}_total_marks FROM class_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for class {j}</p>")

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Academic Performance/gc2.html', pie_charts=pie_charts_html)

@app.route('/student_dashboard/gc3')
def gc3():
    pie_charts_html = []
    j=3
    for i in range(1, 6):
        # Execute the SQL query
        cursor.execute(f"SELECT c_{j}_sub_{i}_name, c_{j}_sub_{i}_marks_obtained, c_{j}_sub_{i}_total_marks FROM class_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for class {j}</p>")

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Academic Performance/gc3.html', pie_charts=pie_charts_html)

@app.route('/student_dashboard/gc4')
def gc4():
    pie_charts_html = []
    j=4
    for i in range(1, 6):
        # Execute the SQL query
        cursor.execute(f"SELECT c_{j}_sub_{i}_name, c_{j}_sub_{i}_marks_obtained, c_{j}_sub_{i}_total_marks FROM class_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for class {j}</p>")

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Academic Performance/gc4.html', pie_charts=pie_charts_html)

@app.route('/student_dashboard/gc5')
def gc5():
    pie_charts_html = []
    j=5
    for i in range(1, 6):
        # Execute the SQL query
        cursor.execute(f"SELECT c_{j}_sub_{i}_name, c_{j}_sub_{i}_marks_obtained, c_{j}_sub_{i}_total_marks FROM class_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for class {j}</p>")

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Academic Performance/gc5.html', pie_charts=pie_charts_html)

@app.route('/student_dashboard/gc6')
def gc6():
    pie_charts_html = []
    j=6
    for i in range(1, 6):
        # Execute the SQL query
        cursor.execute(f"SELECT c_{j}_sub_{i}_name, c_{j}_sub_{i}_marks_obtained, c_{j}_sub_{i}_total_marks FROM class_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for class {j}</p>")

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Academic Performance/gc6.html', pie_charts=pie_charts_html)

@app.route('/student_dashboard/gc7')
def gc7():
    pie_charts_html = []
    j=7
    for i in range(1, 6):
        # Execute the SQL query
        cursor.execute(f"SELECT c_{j}_sub_{i}_name, c_{j}_sub_{i}_marks_obtained, c_{j}_sub_{i}_total_marks FROM class_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for class {j}</p>")

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Academic Performance/gc7.html', pie_charts=pie_charts_html)

@app.route('/student_dashboard/gc8')
def gc8():
    pie_charts_html = []
    j=8
    for i in range(1, 6):
        # Execute the SQL query
        cursor.execute(f"SELECT c_{j}_sub_{i}_name, c_{j}_sub_{i}_marks_obtained, c_{j}_sub_{i}_total_marks FROM class_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for class {j}</p>")

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Academic Performance/gc8.html', pie_charts=pie_charts_html)

@app.route('/student_dashboard/gc9')
def gc9():
    pie_charts_html = []
    j=9
    for i in range(1, 6):
        # Execute the SQL query
        cursor.execute(f"SELECT c_{j}_sub_{i}_name, c_{j}_sub_{i}_marks_obtained, c_{j}_sub_{i}_total_marks FROM class_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for class {j}</p>")

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Academic Performance/gc9.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/gc10')
def gc10():
    pie_charts_html = []
    j=10
    for i in range(1, 6):
        # Execute the SQL query
        cursor.execute(f"SELECT c_{j}_sub_{i}_name, c_{j}_sub_{i}_marks_obtained, c_{j}_sub_{i}_total_marks FROM class_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for class {j}</p>")

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Academic Performance/gc10.html', pie_charts=pie_charts_html)

@app.route('/student_dashboard/gc11')
def gc11():
    pie_charts_html = []
    j=11
    for i in range(1, 6):
        # Execute the SQL query
        cursor.execute(f"SELECT c_{j}_sub_{i}_name, c_{j}_sub_{i}_marks_obtained, c_{j}_sub_{i}_total_marks FROM class_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for class {j}</p>")

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Academic Performance/gc11.html', pie_charts=pie_charts_html)

@app.route('/student_dashboard/gc12')
def gc12():
    pie_charts_html = []
    j=12
    for i in range(1, 6):
        # Execute the SQL query
        cursor.execute(f"SELECT c_{j}_sub_{i}_name, c_{j}_sub_{i}_marks_obtained, c_{j}_sub_{i}_total_marks FROM class_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for class {j}</p>")

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Academic Performance/gc12.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_ug_sem_1')
def g_ug_sem_1():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 1  # Assuming the semester number is 1 for undergraduate semester 1

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT ug_sem_{j}_sub_{i}_name, ug_sem_{j}_sub_{i}_marks_obtained, ug_sem_{j}_sub_{i}_total_marks FROM ug_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_ug_sem_1.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_ug_sem_1.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_ug_sem_2')
def g_ug_sem_2():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 2  # Assuming the semester number is 2 for undergraduate semester 2

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT ug_sem_{j}_sub_{i}_name, ug_sem_{j}_sub_{i}_marks_obtained, ug_sem_{j}_sub_{i}_total_marks FROM ug_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_ug_sem_2.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_ug_sem_2.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_ug_sem_3')
def g_ug_sem_3():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 3  # Assuming the semester number is 3 for undergraduate semester 3

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT ug_sem_{j}_sub_{i}_name, ug_sem_{j}_sub_{i}_marks_obtained, ug_sem_{j}_sub_{i}_total_marks FROM ug_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_ug_sem_3.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_ug_sem_3.html', pie_charts=pie_charts_html)



@app.route('/student_dashboard/g_ug_sem_4')
def g_ug_sem_4():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 4  # Assuming the semester number is 4 for undergraduate semester 4

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT ug_sem_{j}_sub_{i}_name, ug_sem_{j}_sub_{i}_marks_obtained, ug_sem_{j}_sub_{i}_total_marks FROM ug_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_ug_sem_4.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_ug_sem_4.html', pie_charts=pie_charts_html)



@app.route('/student_dashboard/g_ug_sem_5')
def g_ug_sem_5():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 5  # Assuming the semester number is 5 for undergraduate semester 5

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT ug_sem_{j}_sub_{i}_name, ug_sem_{j}_sub_{i}_marks_obtained, ug_sem_{j}_sub_{i}_total_marks FROM ug_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_ug_sem_5.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_ug_sem_5.html', pie_charts=pie_charts_html)



@app.route('/student_dashboard/g_ug_sem_6')
def g_ug_sem_6():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 6  # Assuming the semester number is 6 for undergraduate semester 6

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT ug_sem_{j}_sub_{i}_name, ug_sem_{j}_sub_{i}_marks_obtained, ug_sem_{j}_sub_{i}_total_marks FROM ug_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_ug_sem_6.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_ug_sem_6.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_ug_sem_7')
def g_ug_sem_7():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 7  # Assuming the semester number is 7 for undergraduate semester 7

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT ug_sem_{j}_sub_{i}_name, ug_sem_{j}_sub_{i}_marks_obtained, ug_sem_{j}_sub_{i}_total_marks FROM ug_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_ug_sem_7.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_ug_sem_7.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_ug_sem_8')
def g_ug_sem_8():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 8  # Assuming the semester number is 8 for undergraduate semester 8

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT ug_sem_{j}_sub_{i}_name, ug_sem_{j}_sub_{i}_marks_obtained, ug_sem_{j}_sub_{i}_total_marks FROM ug_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_ug_sem_8.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_ug_sem_8.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_ug_sem_9')
def g_ug_sem_9():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 9  # Assuming the semester number is 9 for undergraduate semester 9

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT ug_sem_{j}_sub_{i}_name, ug_sem_{j}_sub_{i}_marks_obtained, ug_sem_{j}_sub_{i}_total_marks FROM ug_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_ug_sem_9.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_ug_sem_9.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_ug_sem_10')
def g_ug_sem_10():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 10  # Assuming the semester number is 10 for undergraduate semester 10

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT ug_sem_{j}_sub_{i}_name, ug_sem_{j}_sub_{i}_marks_obtained, ug_sem_{j}_sub_{i}_total_marks FROM ug_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_ug_sem_10.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_ug_sem_10.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_pg_sem_1')
def g_pg_sem_1():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 1  # Assuming the semester number is 1 for postgraduate semester 1

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT pg_sem_{j}_sub_{i}_name, pg_sem_{j}_sub_{i}_marks_obtained, pg_sem_{j}_sub_{i}_total_marks FROM pg_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks',data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig,ax = plt.subplots(figsize=(5,5))
                ax.pie(sizes,labels=labels,autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_pg_sem_1.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_pg_sem_1.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_pg_sem_2')
def g_pg_sem_2():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 2  # Assuming the semester number is 2 for postgraduate semester 2

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT pg_sem_{j}_sub_{i}_name, pg_sem_{j}_sub_{i}_marks_obtained, pg_sem_{j}_sub_{i}_total_marks FROM pg_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_pg_sem_2.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_pg_sem_2.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_pg_sem_3')
def g_pg_sem_3():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 3  # Assuming the semester number is 3 for postgraduate semester 3

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT pg_sem_{j}_sub_{i}_name, pg_sem_{j}_sub_{i}_marks_obtained, pg_sem_{j}_sub_{i}_total_marks FROM pg_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_pg_sem_3.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_pg_sem_3.html', pie_charts=pie_charts_html)



@app.route('/student_dashboard/g_pg_sem_4')
def g_pg_sem_4():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 4  # Assuming the semester number is 4 for postgraduate semester 4

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT pg_sem_{j}_sub_{i}_name, pg_sem_{j}_sub_{i}_marks_obtained, pg_sem_{j}_sub_{i}_total_marks FROM pg_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_pg_sem_4.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_pg_sem_4.html', pie_charts=pie_charts_html)



@app.route('/student_dashboard/g_pg_sem_5')
def g_pg_sem_5():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 5  # Assuming the semester number is 5 for postgraduate semester 5

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT pg_sem_{j}_sub_{i}_name, pg_sem_{j}_sub_{i}_marks_obtained, pg_sem_{j}_sub_{i}_total_marks FROM pg_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_pg_sem_5.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_pg_sem_5.html', pie_charts=pie_charts_html)



@app.route('/student_dashboard/g_pg_sem_6')
def g_pg_sem_6():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 6  # Assuming the semester number is 6 for postgraduate semester 6

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT pg_sem_{j}_sub_{i}_name, pg_sem_{j}_sub_{i}_marks_obtained, pg_sem_{j}_sub_{i}_total_marks FROM pg_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_pg_sem_6.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_pg_sem_6.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_pg_sem_7')
def g_pg_sem_7():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 7  # Assuming the semester number is 7 for postgraduate semester 7

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT pg_sem_{j}_sub_{i}_name, pg_sem_{j}_sub_{i}_marks_obtained, pg_sem_{j}_sub_{i}_total_marks FROM pg_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_pg_sem_7.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_pg_sem_7.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_pg_sem_8')
def g_pg_sem_8():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 8  # Assuming the semester number is 8 for postgraduate semester 8

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT pg_sem_{j}_sub_{i}_name, pg_sem_{j}_sub_{i}_marks_obtained, pg_sem_{j}_sub_{i}_total_marks FROM pg_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_pg_sem_8.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_pg_sem_8.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_pg_sem_9')
def g_pg_sem_9():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 9  # Assuming the semester number is 9 for postgraduate semester 9

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT pg_sem_{j}_sub_{i}_name, pg_sem_{j}_sub_{i}_marks_obtained, pg_sem_{j}_sub_{i}_total_marks FROM pg_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_pg_sem_9.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_pg_sem_9.html', pie_charts=pie_charts_html)


@app.route('/student_dashboard/g_pg_sem_10')
def g_pg_sem_10():
    pie_charts_html = []  # This list will store HTML representations of pie charts
    j = 10  # Assuming the semester number is 10 for postgraduate semester 10

    for i in range(1, 6):
        # Execute the SQL query to fetch data for the ith subject
        cursor.execute(f"SELECT pg_sem_{j}_sub_{i}_name, pg_sem_{j}_sub_{i}_marks_obtained, pg_sem_{j}_sub_{i}_total_marks FROM pg_sem_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        if data is None:
            # If no data is available for the subject, display an error
            pie_charts_html.append(f"<p>Error: Marks not available for subject {i}</p>")
        else:
            if None in data:
                # If any value is null, display an error for marks not available for that subject
                pie_charts_html.append(f"<p>Error: Marks not available for subject {data[0]}</p>")
            else:
                # Plot the pie chart
                labels = [data[0] + ' obtained marks', data[0] + ' total marks']
                sizes = [data[1],str(int(data[2]) - int(data[1]))]  # Calculating remaining marks
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title(data[0] + ' Marks Distribution')

                # Convert the plot to HTML
                pie_chart_html = mpld3.fig_to_html(fig)
                pie_charts_html.append(pie_chart_html)

                # Close the plot to prevent memory leaks
                plt.close(fig)

    # If no information is present at all, display an error
    if not any(html for html in pie_charts_html):
        pie_charts_html.append(f"<p>Error: No information available for semester {j}</p>")

    # Render the g_pg_sem_10.html template and pass the pie chart HTML
    return render_template('Academic Performance/g_pg_sem_10.html', pie_charts=pie_charts_html)



@app.route('/student_dashboard/report_c1')
def report_c1():
    i = 1  # Assuming the class is 1

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch c_1_info from the database
    cursor.execute("SELECT * FROM class_1 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    c_1_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in class 1
        cursor.execute(
            f"SELECT c_1_sub_{j}_name, c_1_sub_{j}_marks_obtained, c_1_sub_{j}_total_marks, c_1_sub_{j}_percentage, c_1_sub_{j}_grade FROM class_1 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_c1.html template and pass the student and class 1 information
    return render_template('Reports/report_c1.html',student=student_details,class_1=c_1_info,rows=rows)

@app.route('/student_dashboard/report_c2')
def report_c2():
    i = 2  # Assuming the class is 2

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch c_2_info from the database
    cursor.execute("SELECT * FROM class_2 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    c_2_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in class 2
        cursor.execute(
            f"SELECT c_2_sub_{j}_name, c_2_sub_{j}_marks_obtained, c_2_sub_{j}_total_marks, c_2_sub_{j}_percentage, c_2_sub_{j}_grade FROM class_2 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_c1.html template and pass the student and class 2 information
    return render_template('Reports/report_c2.html',student=student_details,class_2=c_2_info,rows=rows)

@app.route('/student_dashboard/report_c3')
def report_c3():
    i = 3  # Assuming the class is 3

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch c_3_info from the database
    cursor.execute("SELECT * FROM class_3 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    c_3_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in class 3
        cursor.execute(
            f"SELECT c_3_sub_{j}_name, c_3_sub_{j}_marks_obtained, c_3_sub_{j}_total_marks, c_3_sub_{j}_percentage, c_3_sub_{j}_grade FROM class_3 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_c3.html template and pass the student and class 3 information
    return render_template('Reports/report_c3.html',student=student_details,class_3=c_3_info,rows=rows)

@app.route('/student_dashboard/report_c4')
def report_c4():
    i = 4  # Assuming the class is 4

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch c_4_info from the database
    cursor.execute("SELECT * FROM class_4 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    c_4_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in class 4
        cursor.execute(
            f"SELECT c_4_sub_{j}_name, c_4_sub_{j}_marks_obtained, c_4_sub_{j}_total_marks, c_4_sub_{j}_percentage, c_4_sub_{j}_grade FROM class_4 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_c4.html template and pass the student and class 4 information
    return render_template('Reports/report_c4.html',student=student_details,class_4=c_4_info,rows=rows)

@app.route('/student_dashboard/report_c5')
def report_c5():
    i = 5  # Assuming the class is 5

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch c_5_info from the database
    cursor.execute("SELECT * FROM class_5 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    c_5_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in class 5
        cursor.execute(
            f"SELECT c_5_sub_{j}_name, c_5_sub_{j}_marks_obtained, c_5_sub_{j}_total_marks, c_5_sub_{j}_percentage, c_5_sub_{j}_grade FROM class_5 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_c5.html template and pass the student and class 5 information
    return render_template('Reports/report_c5.html',student=student_details,class_5=c_5_info,rows=rows)

@app.route('/student_dashboard/report_c6')
def report_c6():
    i = 6  # Assuming the class is 6

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch c_6_info from the database
    cursor.execute("SELECT * FROM class_6 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    c_6_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in class 6
        cursor.execute(
            f"SELECT c_6_sub_{j}_name, c_6_sub_{j}_marks_obtained, c_6_sub_{j}_total_marks, c_6_sub_{j}_percentage, c_6_sub_{j}_grade FROM class_6 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_c6.html template and pass the student and class 6 information
    return render_template('Reports/report_c6.html',student=student_details,class_6=c_6_info,rows=rows)

@app.route('/student_dashboard/report_c7')
def report_c7():
    i = 7  # Assuming the class is 7

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch c_7_info from the database
    cursor.execute("SELECT * FROM class_7 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    c_7_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in class 7
        cursor.execute(
            f"SELECT c_7_sub_{j}_name, c_7_sub_{j}_marks_obtained, c_7_sub_{j}_total_marks, c_7_sub_{j}_percentage, c_7_sub_{j}_grade FROM class_7 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_c7.html template and pass the student and class 7 information
    return render_template('Reports/report_c7.html',student=student_details,class_7=c_7_info,rows=rows)

@app.route('/student_dashboard/report_c8')
def report_c8():
    i = 8  # Assuming the class is 8

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch c_8_info from the database
    cursor.execute("SELECT * FROM class_8 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    c_8_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in class 8
        cursor.execute(
            f"SELECT c_8_sub_{j}_name, c_8_sub_{j}_marks_obtained, c_8_sub_{j}_total_marks, c_8_sub_{j}_percentage, c_8_sub_{j}_grade FROM class_8 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_c8.html template and pass the student and class 8 information
    return render_template('Reports/report_c8.html',student=student_details,class_8=c_8_info,rows=rows)

@app.route('/student_dashboard/report_c9')
def report_c9():
    i = 9  # Assuming the class is 9

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch c_9_info from the database
    cursor.execute("SELECT * FROM class_9 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    c_9_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in class 9
        cursor.execute(
            f"SELECT c_9_sub_{j}_name, c_9_sub_{j}_marks_obtained, c_9_sub_{j}_total_marks, c_9_sub_{j}_percentage, c_9_sub_{j}_grade FROM class_9 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_c9.html template and pass the student and class 9 information
    return render_template('Reports/report_c9.html',student=student_details,class_9=c_9_info,rows=rows)

@app.route('/student_dashboard/report_c10')
def report_c10():
    i = 10  # Assuming the class is 10

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch c_10_info from the database
    cursor.execute("SELECT * FROM class_10 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    c_10_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in class 10
        cursor.execute(
            f"SELECT c_10_sub_{j}_name, c_10_sub_{j}_marks_obtained, c_10_sub_{j}_total_marks, c_10_sub_{j}_percentage, c_10_sub_{j}_grade FROM class_10 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_c10.html template and pass the student and class 10 information
    return render_template('Reports/report_c10.html',student=student_details,class_10=c_10_info,rows=rows)


@app.route('/student_dashboard/report_c11')
def report_c11():
    i = 11  # Assuming the class is 11

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch c_11_info from the database
    cursor.execute("SELECT * FROM class_11 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    c_11_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in class 11
        cursor.execute(
            f"SELECT c_11_sub_{j}_name, c_11_sub_{j}_marks_obtained, c_11_sub_{j}_total_marks, c_11_sub_{j}_percentage, c_11_sub_{j}_grade FROM class_11 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_c11.html template and pass the student and class 11 information
    return render_template('Reports/report_c11.html',student=student_details,class_11=c_11_info,rows=rows)


@app.route('/student_dashboard/report_c12')
def report_c12():
    i = 12  # Assuming the class is 12

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch c_11_info from the database
    cursor.execute("SELECT * FROM class_12 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    c_12_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in class 11
        cursor.execute(
            f"SELECT c_12_sub_{j}_name, c_12_sub_{j}_marks_obtained, c_12_sub_{j}_total_marks, c_12_sub_{j}_percentage, c_12_sub_{j}_grade FROM class_12 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_c11.html template and pass the student and class 11 information
    return render_template('Reports/report_c12.html',student=student_details,class_12=c_12_info,rows=rows)

@app.route('/student_dashboard/report_ug_sem_1')
def report_ug_sem_1():
    i = 1  # Assuming the sem is 1

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch ug_sem_1_info from the database
    cursor.execute("SELECT * FROM ug_sem_1 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    ug_sem_1_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in ug_sem 1
        cursor.execute(
            f"SELECT ug_sem_1_sub_{j}_name, ug_sem_1_sub_{j}_marks_obtained, ug_sem_1_sub_{j}_total_marks, ug_sem_1_sub_{j}_percentage, ug_sem_1_sub_{j}_grade FROM ug_sem_1 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_ug_sem_1.html template and pass the student and ug_sem 1 information
    return render_template('Reports/report_ug_sem_1.html',student=student_details,ug_sem_1=ug_sem_1_info,rows=rows)



@app.route('/student_dashboard/report_pg_sem_1')
def report_pg_sem_1():
    i = 1  # Assuming the sem is 1

    # Fetch student_info from the database
    cursor.execute("SELECT * FROM student_info WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    student_details = cursor.fetchone()

    # Fetch pg_sem_1_info from the database
    cursor.execute("SELECT * FROM pg_sem_1 WHERE aadhaar_no = ?",(session['aadhaar_no'],))
    pg_sem_1_info = cursor.fetchone()

    # Initialize an empty list to store subject-wise details
    rows = []

    # Fetch subject-wise details from the database
    for j in range(1,6):  # Assuming there are 5 subjects in pg_sem 1
        cursor.execute(
            f"SELECT pg_sem_1_sub_{j}_name, pg_sem_1_sub_{j}_marks_obtained, pg_sem_1_sub_{j}_total_marks, pg_sem_1_sub_{j}_percentage, pg_sem_1_sub_{j}_grade FROM pg_sem_1 WHERE aadhaar_no = ?",
            (session['aadhaar_no'],))
        subject_data = cursor.fetchone()
        rows.append(subject_data)

    # Render the report_pg_sem_1.html template and pass the student and pg_sem 1 information
    return render_template('Reports/report_pg_sem_1.html',student=student_details,pg_sem_1=pg_sem_1_info,rows=rows)



if __name__ == '__main__':
    app.run()

