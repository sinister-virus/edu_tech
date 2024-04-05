from flask import Flask, render_template, request, redirect, url_for
import pyodbc

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
            return render_template('login.html', error="Invalid role.")

        # SQL Injection Vulnerability - Use parameterized queries
        cursor.execute(f"SELECT * FROM {table} WHERE aadhaar_no = ? AND password = ?", (username, password))
        result = cursor.fetchone()

        if result:
            return redirect(url_for(f'{role}_dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password.")

    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register_tnc.html')

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

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('Admin/admin_dashboard.html')


# Routes for admin
############################################


###########################################
# Routes for institute

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
@app.route('/student_dashboard')
def student_dashboard():
    return render_template('Student/student_dashboard.html')

@app.route('/student_manage')
def student_manage():
    return render_template('Student/student_dashboard.html')

@app.route('/student_profile')
def student_profile():
    return render_template('Student/student_dashboard.html')

# Routes for student
############################################\

###########################################
# Routes for register
@app.route('/register_student')
def register_student():
    return render_template('Authentication/register_student.html')

@app.route('/register_admin')
def register_admin():
    return render_template('Authentication/register_admin.html')

@app.route('/register_institute')
def register_institute():
    return render_template('Authentication/register_institute.html')

# Routes for register
############################################


if __name__ == '__main__':
    app.run()