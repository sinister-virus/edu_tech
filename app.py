import matplotlib
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pyodbc
from werkzeug.security import generate_password_hash,check_password_hash
import matplotlib.pyplot as plt
import numpy as np
import mpld3


#database connection
conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\ROG\PycharmProjects\edu_tech\edutech_db.accdb;')
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# for i in cursor.tables(tableType='VIEW'):
#     print(i.table_name)
#
# for i in cursor.tables(tableType='TABLE'):
#     print(i.table_name)
#
# cursor.execute("SELECT * FROM class_10")
# columns = [column[0] for column in cursor.description]
# print(columns)

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

@app.route('/student_dashboard')
def student_dashboard():
    pie_charts_html = []
    j=1
    for i in range(1, 6):
        # Execute the SQL query
        cursor.execute(f"SELECT c_{j}_sub_{i}_name, c_{j}_sub_{i}_marks_obtained, c_{j}_sub_{i}_total_marks FROM class_{j} WHERE aadhaar_no = ?", (session['aadhaar_no'],))

        # Fetch the data
        data = cursor.fetchone()

        # Plot the pie chart
        labels = [data[0] + ' obtained marks', data[0] + ' total marks']
        sizes = [data[1], str(int(data[2])-int(data[1]))]
        fig,ax = plt.subplots(figsize=(5,5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(data[0] + ' Marks Distribution')

        # Convert the plot to HTML
        pie_chart_html = mpld3.fig_to_html(fig)
        pie_charts_html.append(pie_chart_html)

    matplotlib.pyplot.close()

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Student/student_dashboard.html', pie_charts=pie_charts_html)

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

            # Update c_1_info in the database
            cursor.execute("""
                UPDATE class_1
                SET c_1_sub_1_name = ?, c_1_sub_1_marks_obtained = ?, c_1_sub_1_total_marks = ?, c_1_sub_2_name = ?, c_1_sub_2_marks_obtained = ?, c_1_sub_2_total_marks = ?, c_1_sub_3_name = ?, c_1_sub_3_marks_obtained = ?, c_1_sub_3_total_marks = ?, c_1_sub_4_name = ?, c_1_sub_4_marks_obtained = ?, c_1_sub_4_total_marks = ?, c_1_sub_5_name = ?, c_1_sub_5_marks_obtained = ?, c_1_sub_5_total_marks = ?, c_1_sub_6_name = ?, c_1_sub_6_marks_obtained = ?, c_1_sub_6_total_marks = ?, c_1_sub_7_name = ?, c_1_sub_7_marks_obtained = ?, c_1_sub_7_total_marks = ?, c_1_sub_8_name = ?, c_1_sub_8_marks_obtained = ?, c_1_sub_8_total_marks = ?, c_1_sub_9_name = ?, c_1_sub_9_marks_obtained = ?, c_1_sub_9_total_marks = ?, c_1_sub_10_name = ?, c_1_sub_10_marks_obtained = ?, c_1_sub_10_total_marks = ?, c_1_sub_11_name = ?, c_1_sub_11_marks_obtained = ?, c_1_sub_11_total_marks = ?, c_1_sub_12_name = ?, c_1_sub_12_marks_obtained = ?, c_1_sub_12_total_marks = ?, c_1_sub_13_name = ?, c_1_sub_13_marks_obtained = ?, c_1_sub_13_total_marks = ?, c_1_sub_14_name = ?, c_1_sub_14_marks_obtained = ?, c_1_sub_14_total_marks = ?, c_1_sub_15_name = ?, c_1_sub_15_marks_obtained = ?, c_1_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_1_sub_1_name, c_1_sub_1_marks_obtained, c_1_sub_1_total_marks, c_1_sub_2_name, c_1_sub_2_marks_obtained, c_1_sub_2_total_marks, c_1_sub_3_name, c_1_sub_3_marks_obtained, c_1_sub_3_total_marks, c_1_sub_4_name, c_1_sub_4_marks_obtained, c_1_sub_4_total_marks, c_1_sub_5_name, c_1_sub_5_marks_obtained, c_1_sub_5_total_marks, c_1_sub_6_name, c_1_sub_6_marks_obtained, c_1_sub_6_total_marks, c_1_sub_7_name, c_1_sub_7_marks_obtained, c_1_sub_7_total_marks, c_1_sub_8_name, c_1_sub_8_marks_obtained, c_1_sub_8_total_marks, c_1_sub_9_name, c_1_sub_9_marks_obtained, c_1_sub_9_total_marks, c_1_sub_10_name, c_1_sub_10_marks_obtained, c_1_sub_10_total_marks, c_1_sub_11_name, c_1_sub_11_marks_obtained, c_1_sub_11_total_marks, c_1_sub_12_name, c_1_sub_12_marks_obtained, c_1_sub_12_total_marks, c_1_sub_13_name, c_1_sub_13_marks_obtained, c_1_sub_13_total_marks, c_1_sub_14_name, c_1_sub_14_marks_obtained, c_1_sub_14_total_marks, c_1_sub_15_name, c_1_sub_15_marks_obtained, c_1_sub_15_total_marks, aadhaar_no))

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

            # Update c_2_info in the database
            cursor.execute("""
                UPDATE class_2
                SET c_2_sub_1_name = ?, c_2_sub_1_marks_obtained = ?, c_2_sub_1_total_marks = ?, c_2_sub_2_name = ?, c_2_sub_2_marks_obtained = ?, c_2_sub_2_total_marks = ?, c_2_sub_3_name = ?, c_2_sub_3_marks_obtained = ?, c_2_sub_3_total_marks = ?, c_2_sub_4_name = ?, c_2_sub_4_marks_obtained = ?, c_2_sub_4_total_marks = ?, c_2_sub_5_name = ?, c_2_sub_5_marks_obtained = ?, c_2_sub_5_total_marks = ?, c_2_sub_6_name = ?, c_2_sub_6_marks_obtained = ?, c_2_sub_6_total_marks = ?, c_2_sub_7_name = ?, c_2_sub_7_marks_obtained = ?, c_2_sub_7_total_marks = ?, c_2_sub_8_name = ?, c_2_sub_8_marks_obtained = ?, c_2_sub_8_total_marks = ?, c_2_sub_9_name = ?, c_2_sub_9_marks_obtained = ?, c_2_sub_9_total_marks = ?, c_2_sub_10_name = ?, c_2_sub_10_marks_obtained = ?, c_2_sub_10_total_marks = ?, c_2_sub_11_name = ?, c_2_sub_11_marks_obtained = ?, c_2_sub_11_total_marks = ?, c_2_sub_12_name = ?, c_2_sub_12_marks_obtained = ?, c_2_sub_12_total_marks = ?, c_2_sub_13_name = ?, c_2_sub_13_marks_obtained = ?, c_2_sub_13_total_marks = ?, c_2_sub_14_name = ?, c_2_sub_14_marks_obtained = ?, c_2_sub_14_total_marks = ?, c_2_sub_15_name = ?, c_2_sub_15_marks_obtained = ?, c_2_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_2_sub_1_name, c_2_sub_1_marks_obtained, c_2_sub_1_total_marks, c_2_sub_2_name, c_2_sub_2_marks_obtained, c_2_sub_2_total_marks, c_2_sub_3_name, c_2_sub_3_marks_obtained, c_2_sub_3_total_marks, c_2_sub_4_name, c_2_sub_4_marks_obtained, c_2_sub_4_total_marks, c_2_sub_5_name, c_2_sub_5_marks_obtained, c_2_sub_5_total_marks, c_2_sub_6_name, c_2_sub_6_marks_obtained, c_2_sub_6_total_marks, c_2_sub_7_name, c_2_sub_7_marks_obtained, c_2_sub_7_total_marks, c_2_sub_8_name, c_2_sub_8_marks_obtained, c_2_sub_8_total_marks, c_2_sub_9_name, c_2_sub_9_marks_obtained, c_2_sub_9_total_marks, c_2_sub_10_name, c_2_sub_10_marks_obtained, c_2_sub_10_total_marks, c_2_sub_11_name, c_2_sub_11_marks_obtained, c_2_sub_11_total_marks, c_2_sub_12_name, c_2_sub_12_marks_obtained, c_2_sub_12_total_marks, c_2_sub_13_name, c_2_sub_13_marks_obtained, c_2_sub_13_total_marks, c_2_sub_14_name, c_2_sub_14_marks_obtained, c_2_sub_14_total_marks, c_2_sub_15_name, c_2_sub_15_marks_obtained, c_2_sub_15_total_marks, aadhaar_no))

            # Commit changes
            conn.commit()

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
                SET c_3_sub_1_name = ?, c_3_sub_1_marks_obtained = ?, c_3_sub_1_total_marks = ?, c_3_sub_2_name = ?, c_3_sub_2_marks_obtained = ?, c_3_sub_2_total_marks = ?, c_3_sub_3_name = ?, c_3_sub_3_marks_obtained = ?, c_3_sub_3_total_marks = ?, c_3_sub_4_name = ?, c_3_sub_4_marks_obtained = ?, c_3_sub_4_total_marks = ?, c_3_sub_5_name = ?, c_3_sub_5_marks_obtained = ?, c_3_sub_5_total_marks = ?, c_3_sub_6_name = ?, c_3_sub_6_marks_obtained = ?, c_3_sub_6_total_marks = ?, c_3_sub_7_name = ?, c_3_sub_7_marks_obtained = ?, c_3_sub_7_total_marks = ?, c_3_sub_8_name = ?, c_3_sub_8_marks_obtained = ?, c_3_sub_8_total_marks = ?, c_3_sub_9_name = ?, c_3_sub_9_marks_obtained = ?, c_3_sub_9_total_marks = ?, c_3_sub_10_name = ?, c_3_sub_10_marks_obtained = ?, c_3_sub_10_total_marks = ?, c_3_sub_11_name = ?, c_3_sub_11_marks_obtained = ?, c_3_sub_11_total_marks = ?, c_3_sub_12_name = ?, c_3_sub_12_marks_obtained = ?, c_3_sub_12_total_marks = ?, c_3_sub_13_name = ?, c_3_sub_13_marks_obtained = ?, c_3_sub_13_total_marks = ?, c_3_sub_14_name = ?, c_3_sub_14_marks_obtained = ?, c_3_sub_14_total_marks = ?, c_3_sub_15_name = ?, c_3_sub_15_marks_obtained = ?, c_3_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_3_sub_1_name, c_3_sub_1_marks_obtained, c_3_sub_1_total_marks, c_3_sub_2_name, c_3_sub_2_marks_obtained, c_3_sub_2_total_marks, c_3_sub_3_name, c_3_sub_3_marks_obtained, c_3_sub_3_total_marks, c_3_sub_4_name, c_3_sub_4_marks_obtained, c_3_sub_4_total_marks, c_3_sub_5_name, c_3_sub_5_marks_obtained, c_3_sub_5_total_marks, c_3_sub_6_name, c_3_sub_6_marks_obtained, c_3_sub_6_total_marks, c_3_sub_7_name, c_3_sub_7_marks_obtained, c_3_sub_7_total_marks, c_3_sub_8_name, c_3_sub_8_marks_obtained, c_3_sub_8_total_marks, c_3_sub_9_name, c_3_sub_9_marks_obtained, c_3_sub_9_total_marks, c_3_sub_10_name, c_3_sub_10_marks_obtained, c_3_sub_10_total_marks, c_3_sub_11_name, c_3_sub_11_marks_obtained, c_3_sub_11_total_marks, c_3_sub_12_name, c_3_sub_12_marks_obtained, c_3_sub_12_total_marks, c_3_sub_13_name, c_3_sub_13_marks_obtained, c_3_sub_13_total_marks, c_3_sub_14_name, c_3_sub_14_marks_obtained, c_3_sub_14_total_marks, c_3_sub_15_name, c_3_sub_15_marks_obtained, c_3_sub_15_total_marks, aadhaar_no))

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
                SET c_4_sub_1_name = ?, c_4_sub_1_marks_obtained = ?, c_4_sub_1_total_marks = ?, c_4_sub_2_name = ?, c_4_sub_2_marks_obtained = ?, c_4_sub_2_total_marks = ?, c_4_sub_3_name = ?, c_4_sub_3_marks_obtained = ?, c_4_sub_3_total_marks = ?, c_4_sub_4_name = ?, c_4_sub_4_marks_obtained = ?, c_4_sub_4_total_marks = ?, c_4_sub_5_name = ?, c_4_sub_5_marks_obtained = ?, c_4_sub_5_total_marks = ?, c_4_sub_6_name = ?, c_4_sub_6_marks_obtained = ?, c_4_sub_6_total_marks = ?, c_4_sub_7_name = ?, c_4_sub_7_marks_obtained = ?, c_4_sub_7_total_marks = ?, c_4_sub_8_name = ?, c_4_sub_8_marks_obtained = ?, c_4_sub_8_total_marks = ?, c_4_sub_9_name = ?, c_4_sub_9_marks_obtained = ?, c_4_sub_9_total_marks = ?, c_4_sub_10_name = ?, c_4_sub_10_marks_obtained = ?, c_4_sub_10_total_marks = ?, c_4_sub_11_name = ?, c_4_sub_11_marks_obtained = ?, c_4_sub_11_total_marks = ?, c_4_sub_12_name = ?, c_4_sub_12_marks_obtained = ?, c_4_sub_12_total_marks = ?, c_4_sub_13_name = ?, c_4_sub_13_marks_obtained = ?, c_4_sub_13_total_marks = ?, c_4_sub_14_name = ?, c_4_sub_14_marks_obtained = ?, c_4_sub_14_total_marks = ?, c_4_sub_15_name = ?, c_4_sub_15_marks_obtained = ?, c_4_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_4_sub_1_name, c_4_sub_1_marks_obtained, c_4_sub_1_total_marks, c_4_sub_2_name, c_4_sub_2_marks_obtained, c_4_sub_2_total_marks, c_4_sub_3_name, c_4_sub_3_marks_obtained, c_4_sub_3_total_marks, c_4_sub_4_name, c_4_sub_4_marks_obtained, c_4_sub_4_total_marks, c_4_sub_5_name, c_4_sub_5_marks_obtained, c_4_sub_5_total_marks, c_4_sub_6_name, c_4_sub_6_marks_obtained, c_4_sub_6_total_marks, c_4_sub_7_name, c_4_sub_7_marks_obtained, c_4_sub_7_total_marks, c_4_sub_8_name, c_4_sub_8_marks_obtained, c_4_sub_8_total_marks, c_4_sub_9_name, c_4_sub_9_marks_obtained, c_4_sub_9_total_marks, c_4_sub_10_name, c_4_sub_10_marks_obtained, c_4_sub_10_total_marks, c_4_sub_11_name, c_4_sub_11_marks_obtained, c_4_sub_11_total_marks, c_4_sub_12_name, c_4_sub_12_marks_obtained, c_4_sub_12_total_marks, c_4_sub_13_name, c_4_sub_13_marks_obtained, c_4_sub_13_total_marks, c_4_sub_14_name, c_4_sub_14_marks_obtained, c_4_sub_14_total_marks, c_4_sub_15_name, c_4_sub_15_marks_obtained, c_4_sub_15_total_marks, aadhaar_no))

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
                SET c_5_sub_1_name = ?, c_5_sub_1_marks_obtained = ?, c_5_sub_1_total_marks = ?, c_5_sub_2_name = ?, c_5_sub_2_marks_obtained = ?, c_5_sub_2_total_marks = ?, c_5_sub_3_name = ?, c_5_sub_3_marks_obtained = ?, c_5_sub_3_total_marks = ?, c_5_sub_4_name = ?, c_5_sub_4_marks_obtained = ?, c_5_sub_4_total_marks = ?, c_5_sub_5_name = ?, c_5_sub_5_marks_obtained = ?, c_5_sub_5_total_marks = ?, c_5_sub_6_name = ?, c_5_sub_6_marks_obtained = ?, c_5_sub_6_total_marks = ?, c_5_sub_7_name = ?, c_5_sub_7_marks_obtained = ?, c_5_sub_7_total_marks = ?, c_5_sub_8_name = ?, c_5_sub_8_marks_obtained = ?, c_5_sub_8_total_marks = ?, c_5_sub_9_name = ?, c_5_sub_9_marks_obtained = ?, c_5_sub_9_total_marks = ?, c_5_sub_10_name = ?, c_5_sub_10_marks_obtained = ?, c_5_sub_10_total_marks = ?, c_5_sub_11_name = ?, c_5_sub_11_marks_obtained = ?, c_5_sub_11_total_marks = ?, c_5_sub_12_name = ?, c_5_sub_12_marks_obtained = ?, c_5_sub_12_total_marks = ?, c_5_sub_13_name = ?, c_5_sub_13_marks_obtained = ?, c_5_sub_13_total_marks = ?, c_5_sub_14_name = ?, c_5_sub_14_marks_obtained = ?, c_5_sub_14_total_marks = ?, c_5_sub_15_name = ?, c_5_sub_15_marks_obtained = ?, c_5_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_5_sub_1_name, c_5_sub_1_marks_obtained, c_5_sub_1_total_marks, c_5_sub_2_name, c_5_sub_2_marks_obtained, c_5_sub_2_total_marks, c_5_sub_3_name, c_5_sub_3_marks_obtained, c_5_sub_3_total_marks, c_5_sub_4_name, c_5_sub_4_marks_obtained, c_5_sub_4_total_marks, c_5_sub_5_name, c_5_sub_5_marks_obtained, c_5_sub_5_total_marks, c_5_sub_6_name, c_5_sub_6_marks_obtained, c_5_sub_6_total_marks, c_5_sub_7_name, c_5_sub_7_marks_obtained, c_5_sub_7_total_marks, c_5_sub_8_name, c_5_sub_8_marks_obtained, c_5_sub_8_total_marks, c_5_sub_9_name, c_5_sub_9_marks_obtained, c_5_sub_9_total_marks, c_5_sub_10_name, c_5_sub_10_marks_obtained, c_5_sub_10_total_marks, c_5_sub_11_name, c_5_sub_11_marks_obtained, c_5_sub_11_total_marks, c_5_sub_12_name, c_5_sub_12_marks_obtained, c_5_sub_12_total_marks, c_5_sub_13_name, c_5_sub_13_marks_obtained, c_5_sub_13_total_marks, c_5_sub_14_name, c_5_sub_14_marks_obtained, c_5_sub_14_total_marks, c_5_sub_15_name, c_5_sub_15_marks_obtained, c_5_sub_15_total_marks, aadhaar_no))

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
                SET c_6_sub_1_name = ?, c_6_sub_1_marks_obtained = ?, c_6_sub_1_total_marks = ?, c_6_sub_2_name = ?, c_6_sub_2_marks_obtained = ?, c_6_sub_2_total_marks = ?, c_6_sub_3_name = ?, c_6_sub_3_marks_obtained = ?, c_6_sub_3_total_marks = ?, c_6_sub_4_name = ?, c_6_sub_4_marks_obtained = ?, c_6_sub_4_total_marks = ?, c_6_sub_5_name = ?, c_6_sub_5_marks_obtained = ?, c_6_sub_5_total_marks = ?, c_6_sub_6_name = ?, c_6_sub_6_marks_obtained = ?, c_6_sub_6_total_marks = ?, c_6_sub_7_name = ?, c_6_sub_7_marks_obtained = ?, c_6_sub_7_total_marks = ?, c_6_sub_8_name = ?, c_6_sub_8_marks_obtained = ?, c_6_sub_8_total_marks = ?, c_6_sub_9_name = ?, c_6_sub_9_marks_obtained = ?, c_6_sub_9_total_marks = ?, c_6_sub_10_name = ?, c_6_sub_10_marks_obtained = ?, c_6_sub_10_total_marks = ?, c_6_sub_11_name = ?, c_6_sub_11_marks_obtained = ?, c_6_sub_11_total_marks = ?, c_6_sub_12_name = ?, c_6_sub_12_marks_obtained = ?, c_6_sub_12_total_marks = ?, c_6_sub_13_name = ?, c_6_sub_13_marks_obtained = ?, c_6_sub_13_total_marks = ?, c_6_sub_14_name = ?, c_6_sub_14_marks_obtained = ?, c_6_sub_14_total_marks = ?, c_6_sub_15_name = ?, c_6_sub_15_marks_obtained = ?, c_6_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_6_sub_1_name, c_6_sub_1_marks_obtained, c_6_sub_1_total_marks, c_6_sub_2_name, c_6_sub_2_marks_obtained, c_6_sub_2_total_marks, c_6_sub_3_name, c_6_sub_3_marks_obtained, c_6_sub_3_total_marks, c_6_sub_4_name, c_6_sub_4_marks_obtained, c_6_sub_4_total_marks, c_6_sub_5_name, c_6_sub_5_marks_obtained, c_6_sub_5_total_marks, c_6_sub_6_name, c_6_sub_6_marks_obtained, c_6_sub_6_total_marks, c_6_sub_7_name, c_6_sub_7_marks_obtained, c_6_sub_7_total_marks, c_6_sub_8_name, c_6_sub_8_marks_obtained, c_6_sub_8_total_marks, c_6_sub_9_name, c_6_sub_9_marks_obtained, c_6_sub_9_total_marks, c_6_sub_10_name, c_6_sub_10_marks_obtained, c_6_sub_10_total_marks, c_6_sub_11_name, c_6_sub_11_marks_obtained, c_6_sub_11_total_marks, c_6_sub_12_name, c_6_sub_12_marks_obtained, c_6_sub_12_total_marks, c_6_sub_13_name, c_6_sub_13_marks_obtained, c_6_sub_13_total_marks, c_6_sub_14_name, c_6_sub_14_marks_obtained, c_6_sub_14_total_marks, c_6_sub_15_name, c_6_sub_15_marks_obtained, c_6_sub_15_total_marks, aadhaar_no))

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
                SET c_7_sub_1_name = ?, c_7_sub_1_marks_obtained = ?, c_7_sub_1_total_marks = ?, c_7_sub_2_name = ?, c_7_sub_2_marks_obtained = ?, c_7_sub_2_total_marks = ?, c_7_sub_3_name = ?, c_7_sub_3_marks_obtained = ?, c_7_sub_3_total_marks = ?, c_7_sub_4_name = ?, c_7_sub_4_marks_obtained = ?, c_7_sub_4_total_marks = ?, c_7_sub_5_name = ?, c_7_sub_5_marks_obtained = ?, c_7_sub_5_total_marks = ?, c_7_sub_6_name = ?, c_7_sub_6_marks_obtained = ?, c_7_sub_6_total_marks = ?, c_7_sub_7_name = ?, c_7_sub_7_marks_obtained = ?, c_7_sub_7_total_marks = ?, c_7_sub_8_name = ?, c_7_sub_8_marks_obtained = ?, c_7_sub_8_total_marks = ?, c_7_sub_9_name = ?, c_7_sub_9_marks_obtained = ?, c_7_sub_9_total_marks = ?, c_7_sub_10_name = ?, c_7_sub_10_marks_obtained = ?, c_7_sub_10_total_marks = ?, c_7_sub_11_name = ?, c_7_sub_11_marks_obtained = ?, c_7_sub_11_total_marks = ?, c_7_sub_12_name = ?, c_7_sub_12_marks_obtained = ?, c_7_sub_12_total_marks = ?, c_7_sub_13_name = ?, c_7_sub_13_marks_obtained = ?, c_7_sub_13_total_marks = ?, c_7_sub_14_name = ?, c_7_sub_14_marks_obtained = ?, c_7_sub_14_total_marks = ?, c_7_sub_15_name = ?, c_7_sub_15_marks_obtained = ?, c_7_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_7_sub_1_name, c_7_sub_1_marks_obtained, c_7_sub_1_total_marks, c_7_sub_2_name, c_7_sub_2_marks_obtained, c_7_sub_2_total_marks, c_7_sub_3_name, c_7_sub_3_marks_obtained, c_7_sub_3_total_marks, c_7_sub_4_name, c_7_sub_4_marks_obtained, c_7_sub_4_total_marks, c_7_sub_5_name, c_7_sub_5_marks_obtained, c_7_sub_5_total_marks, c_7_sub_6_name, c_7_sub_6_marks_obtained, c_7_sub_6_total_marks, c_7_sub_7_name, c_7_sub_7_marks_obtained, c_7_sub_7_total_marks, c_7_sub_8_name, c_7_sub_8_marks_obtained, c_7_sub_8_total_marks, c_7_sub_9_name, c_7_sub_9_marks_obtained, c_7_sub_9_total_marks, c_7_sub_10_name, c_7_sub_10_marks_obtained, c_7_sub_10_total_marks, c_7_sub_11_name, c_7_sub_11_marks_obtained, c_7_sub_11_total_marks, c_7_sub_12_name, c_7_sub_12_marks_obtained, c_7_sub_12_total_marks, c_7_sub_13_name, c_7_sub_13_marks_obtained, c_7_sub_13_total_marks, c_7_sub_14_name, c_7_sub_14_marks_obtained, c_7_sub_14_total_marks, c_7_sub_15_name, c_7_sub_15_marks_obtained, c_7_sub_15_total_marks, aadhaar_no))

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
                SET c_8_sub_1_name = ?, c_8_sub_1_marks_obtained = ?, c_8_sub_1_total_marks = ?, c_8_sub_2_name = ?, c_8_sub_2_marks_obtained = ?, c_8_sub_2_total_marks = ?, c_8_sub_3_name = ?, c_8_sub_3_marks_obtained = ?, c_8_sub_3_total_marks = ?, c_8_sub_4_name = ?, c_8_sub_4_marks_obtained = ?, c_8_sub_4_total_marks = ?, c_8_sub_5_name = ?, c_8_sub_5_marks_obtained = ?, c_8_sub_5_total_marks = ?, c_8_sub_6_name = ?, c_8_sub_6_marks_obtained = ?, c_8_sub_6_total_marks = ?, c_8_sub_7_name = ?, c_8_sub_7_marks_obtained = ?, c_8_sub_7_total_marks = ?, c_8_sub_8_name = ?, c_8_sub_8_marks_obtained = ?, c_8_sub_8_total_marks = ?, c_8_sub_9_name = ?, c_8_sub_9_marks_obtained = ?, c_8_sub_9_total_marks = ?, c_8_sub_10_name = ?, c_8_sub_10_marks_obtained = ?, c_8_sub_10_total_marks = ?, c_8_sub_11_name = ?, c_8_sub_11_marks_obtained = ?, c_8_sub_11_total_marks = ?, c_8_sub_12_name = ?, c_8_sub_12_marks_obtained = ?, c_8_sub_12_total_marks = ?, c_8_sub_13_name = ?, c_8_sub_13_marks_obtained = ?, c_8_sub_13_total_marks = ?, c_8_sub_14_name = ?, c_8_sub_14_marks_obtained = ?, c_8_sub_14_total_marks = ?, c_8_sub_15_name = ?, c_8_sub_15_marks_obtained = ?, c_8_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_8_sub_1_name, c_8_sub_1_marks_obtained, c_8_sub_1_total_marks, c_8_sub_2_name, c_8_sub_2_marks_obtained, c_8_sub_2_total_marks, c_8_sub_3_name, c_8_sub_3_marks_obtained, c_8_sub_3_total_marks, c_8_sub_4_name, c_8_sub_4_marks_obtained, c_8_sub_4_total_marks, c_8_sub_5_name, c_8_sub_5_marks_obtained, c_8_sub_5_total_marks, c_8_sub_6_name, c_8_sub_6_marks_obtained, c_8_sub_6_total_marks, c_8_sub_7_name, c_8_sub_7_marks_obtained, c_8_sub_7_total_marks, c_8_sub_8_name, c_8_sub_8_marks_obtained, c_8_sub_8_total_marks, c_8_sub_9_name, c_8_sub_9_marks_obtained, c_8_sub_9_total_marks, c_8_sub_10_name, c_8_sub_10_marks_obtained, c_8_sub_10_total_marks, c_8_sub_11_name, c_8_sub_11_marks_obtained, c_8_sub_11_total_marks, c_8_sub_12_name, c_8_sub_12_marks_obtained, c_8_sub_12_total_marks, c_8_sub_13_name, c_8_sub_13_marks_obtained, c_8_sub_13_total_marks, c_8_sub_14_name, c_8_sub_14_marks_obtained, c_8_sub_14_total_marks, c_8_sub_15_name, c_8_sub_15_marks_obtained, c_8_sub_15_total_marks, aadhaar_no))

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
                SET c_9_sub_1_name = ?, c_9_sub_1_marks_obtained = ?, c_9_sub_1_total_marks = ?, c_9_sub_2_name = ?, c_9_sub_2_marks_obtained = ?, c_9_sub_2_total_marks = ?, c_9_sub_3_name = ?, c_9_sub_3_marks_obtained = ?, c_9_sub_3_total_marks = ?, c_9_sub_4_name = ?, c_9_sub_4_marks_obtained = ?, c_9_sub_4_total_marks = ?, c_9_sub_5_name = ?, c_9_sub_5_marks_obtained = ?, c_9_sub_5_total_marks = ?, c_9_sub_6_name = ?, c_9_sub_6_marks_obtained = ?, c_9_sub_6_total_marks = ?, c_9_sub_7_name = ?, c_9_sub_7_marks_obtained = ?, c_9_sub_7_total_marks = ?, c_9_sub_8_name = ?, c_9_sub_8_marks_obtained = ?, c_9_sub_8_total_marks = ?, c_9_sub_9_name = ?, c_9_sub_9_marks_obtained = ?, c_9_sub_9_total_marks = ?, c_9_sub_10_name = ?, c_9_sub_10_marks_obtained = ?, c_9_sub_10_total_marks = ?, c_9_sub_11_name = ?, c_9_sub_11_marks_obtained = ?, c_9_sub_11_total_marks = ?, c_9_sub_12_name = ?, c_9_sub_12_marks_obtained = ?, c_9_sub_12_total_marks = ?, c_9_sub_13_name = ?, c_9_sub_13_marks_obtained = ?, c_9_sub_13_total_marks = ?, c_9_sub_14_name = ?, c_9_sub_14_marks_obtained = ?, c_9_sub_14_total_marks = ?, c_9_sub_15_name = ?, c_9_sub_15_marks_obtained = ?, c_9_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_9_sub_1_name, c_9_sub_1_marks_obtained, c_9_sub_1_total_marks, c_9_sub_2_name, c_9_sub_2_marks_obtained, c_9_sub_2_total_marks, c_9_sub_3_name, c_9_sub_3_marks_obtained, c_9_sub_3_total_marks, c_9_sub_4_name, c_9_sub_4_marks_obtained, c_9_sub_4_total_marks, c_9_sub_5_name, c_9_sub_5_marks_obtained, c_9_sub_5_total_marks, c_9_sub_6_name, c_9_sub_6_marks_obtained, c_9_sub_6_total_marks, c_9_sub_7_name, c_9_sub_7_marks_obtained, c_9_sub_7_total_marks, c_9_sub_8_name, c_9_sub_8_marks_obtained, c_9_sub_8_total_marks, c_9_sub_9_name, c_9_sub_9_marks_obtained, c_9_sub_9_total_marks, c_9_sub_10_name, c_9_sub_10_marks_obtained, c_9_sub_10_total_marks, c_9_sub_11_name, c_9_sub_11_marks_obtained, c_9_sub_11_total_marks, c_9_sub_12_name, c_9_sub_12_marks_obtained, c_9_sub_12_total_marks, c_9_sub_13_name, c_9_sub_13_marks_obtained, c_9_sub_13_total_marks, c_9_sub_14_name, c_9_sub_14_marks_obtained, c_9_sub_14_total_marks, c_9_sub_15_name, c_9_sub_15_marks_obtained, c_9_sub_15_total_marks, aadhaar_no))

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
                SET c_10_sub_1_name = ?, c_10_sub_1_marks_obtained = ?, c_10_sub_1_total_marks = ?, c_10_sub_2_name = ?, c_10_sub_2_marks_obtained = ?, c_10_sub_2_total_marks = ?, c_10_sub_3_name = ?, c_10_sub_3_marks_obtained = ?, c_10_sub_3_total_marks = ?, c_10_sub_4_name = ?, c_10_sub_4_marks_obtained = ?, c_10_sub_4_total_marks = ?, c_10_sub_5_name = ?, c_10_sub_5_marks_obtained = ?, c_10_sub_5_total_marks = ?, c_10_sub_6_name = ?, c_10_sub_6_marks_obtained = ?, c_10_sub_6_total_marks = ?, c_10_sub_7_name = ?, c_10_sub_7_marks_obtained = ?, c_10_sub_7_total_marks = ?, c_10_sub_8_name = ?, c_10_sub_8_marks_obtained = ?, c_10_sub_8_total_marks = ?, c_10_sub_9_name = ?, c_10_sub_9_marks_obtained = ?, c_10_sub_9_total_marks = ?, c_10_sub_10_name = ?, c_10_sub_10_marks_obtained = ?, c_10_sub_10_total_marks = ?, c_10_sub_11_name = ?, c_10_sub_11_marks_obtained = ?, c_10_sub_11_total_marks = ?, c_10_sub_12_name = ?, c_10_sub_12_marks_obtained = ?, c_10_sub_12_total_marks = ?, c_10_sub_13_name = ?, c_10_sub_13_marks_obtained = ?, c_10_sub_13_total_marks = ?, c_10_sub_14_name = ?, c_10_sub_14_marks_obtained = ?, c_10_sub_14_total_marks = ?, c_10_sub_15_name = ?, c_10_sub_15_marks_obtained = ?, c_10_sub_15_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_10_sub_1_name, c_10_sub_1_marks_obtained, c_10_sub_1_total_marks, c_10_sub_2_name, c_10_sub_2_marks_obtained, c_10_sub_2_total_marks, c_10_sub_3_name, c_10_sub_3_marks_obtained, c_10_sub_3_total_marks, c_10_sub_4_name, c_10_sub_4_marks_obtained, c_10_sub_4_total_marks, c_10_sub_5_name, c_10_sub_5_marks_obtained, c_10_sub_5_total_marks, c_10_sub_6_name, c_10_sub_6_marks_obtained, c_10_sub_6_total_marks, c_10_sub_7_name, c_10_sub_7_marks_obtained, c_10_sub_7_total_marks, c_10_sub_8_name, c_10_sub_8_marks_obtained, c_10_sub_8_total_marks, c_10_sub_9_name, c_10_sub_9_marks_obtained, c_10_sub_9_total_marks, c_10_sub_10_name, c_10_sub_10_marks_obtained, c_10_sub_10_total_marks, c_10_sub_11_name, c_10_sub_11_marks_obtained, c_10_sub_11_total_marks, c_10_sub_12_name, c_10_sub_12_marks_obtained, c_10_sub_12_total_marks, c_10_sub_13_name, c_10_sub_13_marks_obtained, c_10_sub_13_total_marks, c_10_sub_14_name, c_10_sub_14_marks_obtained, c_10_sub_14_total_marks, c_10_sub_15_name, c_10_sub_15_marks_obtained, c_10_sub_15_total_marks, aadhaar_no))

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
                SET c_11_sub_1_name = ?, c_11_sub_1_marks_obtained = ?, c_11_sub_1_total_marks = ?, c_11_sub_2_name = ?, c_11_sub_2_marks_obtained = ?, c_11_sub_2_total_marks = ?, c_11_sub_3_name = ?, c_11_sub_3_marks_obtained = ?, c_11_sub_3_total_marks = ?, c_11_sub_4_name = ?, c_11_sub_4_marks_obtained = ?, c_11_sub_4_total_marks = ?, c_11_sub_5_name = ?, c_11_sub_5_marks_obtained = ?, c_11_sub_5_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_11_sub_1_name, c_11_sub_1_marks_obtained, c_11_sub_1_total_marks, c_11_sub_2_name, c_11_sub_2_marks_obtained, c_11_sub_2_total_marks, c_11_sub_3_name, c_11_sub_3_marks_obtained, c_11_sub_3_total_marks, c_11_sub_4_name, c_11_sub_4_marks_obtained, c_11_sub_4_total_marks, c_11_sub_5_name, c_11_sub_5_marks_obtained, c_11_sub_5_total_marks, aadhaar_no))

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
                SET c_12_sub_1_name = ?, c_12_sub_1_marks_obtained = ?, c_12_sub_1_total_marks = ?, c_12_sub_2_name = ?, c_12_sub_2_marks_obtained = ?, c_12_sub_2_total_marks = ?, c_12_sub_3_name = ?, c_12_sub_3_marks_obtained = ?, c_12_sub_3_total_marks = ?, c_12_sub_4_name = ?, c_12_sub_4_marks_obtained = ?, c_12_sub_4_total_marks = ?, c_12_sub_5_name = ?, c_12_sub_5_marks_obtained = ?, c_12_sub_5_total_marks = ?
                WHERE aadhaar_no = ?
            """, (c_12_sub_1_name, c_12_sub_1_marks_obtained, c_12_sub_1_total_marks, c_12_sub_2_name, c_12_sub_2_marks_obtained, c_12_sub_2_total_marks, c_12_sub_3_name, c_12_sub_3_marks_obtained, c_12_sub_3_total_marks, c_12_sub_4_name, c_12_sub_4_marks_obtained, c_12_sub_4_total_marks, c_12_sub_5_name, c_12_sub_5_marks_obtained, c_12_sub_5_total_marks, aadhaar_no))

            # Commit changes
            conn.commit()

            # Redirect to the next form
            return redirect(url_for('form_c_12'))  # replace 'next_form' with the actual name of the next form

        else:
            # Fetch c_12_info from the database
            cursor.execute("SELECT * FROM class_12 WHERE aadhaar_no = ?", (session['aadhaar_no'],))
            c_12_info = cursor.fetchone()

            # Pass the c_12_info to the template
            return render_template('Student/student_info_forms/form_c_12.html', class_12=c_12_info)
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return str(e), 500


@app.route('/form_ug_details')
def form_ug_details():

    return render_template('Student/student_info_forms/form_ug_details.html')

@app.route('/form_pg_details')
def form_pg_details():
    return render_template('Student/student_info_forms/form_pg_details.html')

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

        # Plot the pie chart
        labels = [data[0] + ' obtained marks', data[0] + ' total marks']
        sizes = [data[1], str(int(data[2])-int(data[1]))]
        fig,ax = plt.subplots(figsize=(5,5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(data[0] + ' Marks Distribution')

        # Convert the plot to HTML
        pie_chart_html = mpld3.fig_to_html(fig)
        pie_charts_html.append(pie_chart_html)

    matplotlib.pyplot.close()

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

        # Plot the pie chart
        labels = [data[0] + ' obtained marks', data[0] + ' total marks']
        sizes = [data[1], str(int(data[2])-int(data[1]))]
        fig,ax = plt.subplots(figsize=(5,5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(data[0] + ' Marks Distribution')

        # Convert the plot to HTML
        pie_chart_html = mpld3.fig_to_html(fig)
        pie_charts_html.append(pie_chart_html)

    matplotlib.pyplot.close()

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

        # Plot the pie chart
        labels = [data[0] + ' obtained marks', data[0] + ' total marks']
        sizes = [data[1], str(int(data[2])-int(data[1]))]
        fig,ax = plt.subplots(figsize=(5,5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(data[0] + ' Marks Distribution')

        # Convert the plot to HTML
        pie_chart_html = mpld3.fig_to_html(fig)
        pie_charts_html.append(pie_chart_html)

    matplotlib.pyplot.close()

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

        # Plot the pie chart
        labels = [data[0] + ' obtained marks', data[0] + ' total marks']
        sizes = [data[1], str(int(data[2])-int(data[1]))]
        fig,ax = plt.subplots(figsize=(5,5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(data[0] + ' Marks Distribution')

        # Convert the plot to HTML
        pie_chart_html = mpld3.fig_to_html(fig)
        pie_charts_html.append(pie_chart_html)

    matplotlib.pyplot.close()

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

        # Plot the pie chart
        labels = [data[0] + ' obtained marks', data[0] + ' total marks']
        sizes = [data[1], str(int(data[2])-int(data[1]))]
        fig,ax = plt.subplots(figsize=(5,5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(data[0] + ' Marks Distribution')

        # Convert the plot to HTML
        pie_chart_html = mpld3.fig_to_html(fig)
        pie_charts_html.append(pie_chart_html)

    matplotlib.pyplot.close()

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

        # Plot the pie chart
        labels = [data[0] + ' obtained marks', data[0] + ' total marks']
        sizes = [data[1], str(int(data[2])-int(data[1]))]
        fig,ax = plt.subplots(figsize=(5,5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(data[0] + ' Marks Distribution')

        # Convert the plot to HTML
        pie_chart_html = mpld3.fig_to_html(fig)
        pie_charts_html.append(pie_chart_html)

    matplotlib.pyplot.close()

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

        # Plot the pie chart
        labels = [data[0] + ' obtained marks', data[0] + ' total marks']
        sizes = [data[1], str(int(data[2])-int(data[1]))]
        fig,ax = plt.subplots(figsize=(5,5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(data[0] + ' Marks Distribution')

        # Convert the plot to HTML
        pie_chart_html = mpld3.fig_to_html(fig)
        pie_charts_html.append(pie_chart_html)

    matplotlib.pyplot.close()

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

        # Plot the pie chart
        labels = [data[0] + ' obtained marks', data[0] + ' total marks']
        sizes = [data[1], str(int(data[2])-int(data[1]))]
        fig,ax = plt.subplots(figsize=(5,5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(data[0] + ' Marks Distribution')

        # Convert the plot to HTML
        pie_chart_html = mpld3.fig_to_html(fig)
        pie_charts_html.append(pie_chart_html)

    matplotlib.pyplot.close()

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

        # Plot the pie chart
        labels = [data[0] + ' obtained marks', data[0] + ' total marks']
        sizes = [data[1], str(int(data[2])-int(data[1]))]
        fig,ax = plt.subplots(figsize=(5,5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(data[0] + ' Marks Distribution')

        # Convert the plot to HTML
        pie_chart_html = mpld3.fig_to_html(fig)
        pie_charts_html.append(pie_chart_html)

    matplotlib.pyplot.close()

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

        # If data is None, replace it with a default value
        if data is None:
            data = ('No Data', 0, 0)

        # Plot the pie chart
        labels = [data[0] + ' obtained marks', data[0] + ' total marks']
        sizes = [data[1], str(int(data[2])-int(data[1]))]
        fig,ax = plt.subplots(figsize=(5,5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(data[0] + ' Marks Distribution')

        # Convert the plot to HTML
        pie_chart_html = mpld3.fig_to_html(fig)
        pie_charts_html.append(pie_chart_html)

    matplotlib.pyplot.close()

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

        # Plot the pie chart
        labels = [data[0] + ' obtained marks', data[0] + ' total marks']
        sizes = [data[1], str(int(data[2])-int(data[1]))]
        fig,ax = plt.subplots(figsize=(5,5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(data[0] + ' Marks Distribution')

        # Convert the plot to HTML
        pie_chart_html = mpld3.fig_to_html(fig)
        pie_charts_html.append(pie_chart_html)

    matplotlib.pyplot.close()

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

        # Plot the pie chart
        labels = [data[0] + ' obtained marks', data[0] + ' total marks']
        sizes = [data[1], str(int(data[2])-int(data[1]))]
        fig,ax = plt.subplots(figsize=(5,5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(data[0] + ' Marks Distribution')

        # Convert the plot to HTML
        pie_chart_html = mpld3.fig_to_html(fig)
        pie_charts_html.append(pie_chart_html)

    matplotlib.pyplot.close()

    # Render the student_dashboard.html template and pass the pie chart HTML
    return render_template('Academic Performance/gc12.html', pie_charts=pie_charts_html)

if __name__ == '__main__':
    app.run()

