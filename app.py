from flask import Flask, render_template, request, redirect, url_for
import pyodbc
from werkzeug.security import generate_password_hash,check_password_hash

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
# cursor.execute("SELECT * FROM student_auth")
# columns = [column[0] for column in cursor.description]
# print(columns)

app = Flask(__name__)

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

@app.route('/admin_register')
def admin_register():
    return render_template('Admin/admin_register.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('Admin/admin_dashboard.html')

@app.route('/admin_manage')
def admin_manage():
    return render_template('Admin/admin_manage.html')

@app.route('/admin_profile')
def admin_profile():
    return render_template('Admin/admin_profile.html')


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
    return render_template('Institute/institute_profile.html')

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
    return render_template('Student/student_dashboard.html')

@app.route('/student_manage')
def student_manage():
    return render_template('Student/student_manage.html')

@app.route('/student_profile')
def student_profile():
    return render_template('Student/student_profile.html')

# Routes for student
############################################\

###########################################
# Routes for student form

@app.route('/form_student_info')
def form_student_info():
    return render_template('Student/student_info_forms/form_student_info.html')

@app.route('/form_parents_info')
def form_parents_info():
    return render_template('Student/student_info_forms/form_parents_info.html')

@app.route('/form_address')
def form_address():
    return render_template('Student/student_info_forms/form_address.html')


# student education details
@app.route('/form_c_1')
def form_c_1():
    return render_template('Student/student_info_forms/form_c_1.html')

@app.route('/form_c_2')
def form_c_2():
    return render_template('Student/student_info_forms/form_c_2.html')

@app.route('/form_c_3')
def form_c_3():
    return render_template('Student/student_info_forms/form_c_3.html')

@app.route('/form_c_4')
def form_c_4():
    return render_template('Student/student_info_forms/form_c_4.html')

@app.route('/form_c_5')
def form_c_5():
    return render_template('Student/student_info_forms/form_c_5.html')

@app.route('/form_c_6')
def form_c_6():
    return render_template('Student/student_info_forms/form_c_6.html')

@app.route('/form_c_7')
def form_c_7():
    return render_template('Student/student_info_forms/form_c_7.html')

@app.route('/form_c_8')
def form_c_8():
    return render_template('Student/student_info_forms/form_c_8.html')

@app.route('/form_c_9')
def form_c_9():
    return render_template('Student/student_info_forms/form_c_9.html')

@app.route('/form_c_10')
def form_c_10():
    return render_template('Student/student_info_forms/form_c_10.html')

@app.route('/form_c_11')
def form_c_11():
    return render_template('Student/student_info_forms/form_c_11.html')

@app.route('/form_c_12')
def form_c_12():
    return render_template('Student/student_info_forms/form_c_12.html')

@app.route('/form_ug_details')
def form_ug_details():
    return render_template('Student/student_info_forms/form_ug_details.html')

@app.route('/form_pg_details')
def form_pg_details():
    return render_template('Student/student_info_forms/form_pg_details.html')

# Routes for student form
############################################


if __name__ == '__main__':
    app.run()

