# Interlinked Platform for School Education, Higher Education, and Technical Education in India

## Description

Background: As of now, we don’t have master database regarding students at various levels, without which framing policies with regard to education and upliftment of student community is difficult. Provision of common platform in which the entire data base of school education, higher education and technical education are interlinked, which will help the government to identify the grey areas where actual concentration is needed. 

Further, the percentage of students entering various fields of education and percentage of student drop outs also can be identified and also State/District wise drop outs can be identified and thereby these places can be targeted for improvement. 

Summary: An integrated platform should be developed for the integration of School education, Higher education and technical education in India. 

This will help in: 
1. Better synchronization between the agencies controlling School education, Higher education and Technical education. 
2. Access to real time data for framing policies related to School education, Higher education and Technical education
3. Integration in all these three verticals Objective : 
To develop an Interlinked platform for School education, Higher education and Technical education in India

## Features

The list of the features of the platform, including those related to school education, higher education, and technical education.

## Installation

1. **Install Python 3.x**:

	- Visit the official Python website [https://www.python.org](https://www.python.org).
	- Navigate to the Downloads section and select the latest version of Python 3.x for your operating system (Windows, macOS, or Linux).
	- Download the installer and run it.
	- Follow the installation wizard's instructions, ensuring to select the option to add Python to your system PATH during installation.
	- Once the installation is complete, open a command prompt or terminal and type python --version to verify that Python is installed correctly.
 
       OR

    - Use existing virtual environment in the repository `/.venv` with Python 3.13.
	
       OR
	
    - create a new virtual environment and install all of these Python libraries by using `requirements.txt` in the repository:
     ```
     pip install -r requirements.txt
     ```
    - Alternatively, install each library manually using:
     ```
     pip install matplotlib flask pyodbc Werkzeug numpy mpld3 pandas seaborn
     ```

2. **Install MS Access**:
    - **Full Installation**:
     1. Navigate to the official Microsoft website: [https://www.microsoft.com](https://www.microsoft.com).
     2. Locate the Microsoft Access download page: [https://www.microsoft.com/en-us/microsoft-365/access](https://www.microsoft.com/en-us/microsoft-365/access).
     3. Click on the “Download” button to begin the download process.
     4. Once the download is complete, open the installation file and follow the on-screen instructions to install Microsoft Access on your computer.
       
    OR
   
    - **MS Access Redistributable (Driver Only)**:
     1. Go to the link for Microsoft Access Database Engine 2016 Redistributable: [https://www.microsoft.com/en-us/download/details.aspx?id=54920](https://www.microsoft.com/en-us/download/details.aspx?id=54920).
     2. Download the file by clicking the Download button and saving the file to your hard disk.
     3. Double-click the `AccessDatabaseEngine.exe` program file on your hard disk to start the setup program.
     4. Follow the instructions on the screen to complete the installation.


## Usage

Instructions on how to use the platform, including how to access the different education levels.

1. **Edit `app.py`**:
    - Open `app.py` in the repository with any IDE.
    - If you want to use the same database as MS Access, keep the path same in code lines `#13` to `#22`.
    - Else you can use your own database AS Access or any
    - Source: [https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-Microsoft-Access](https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-Microsoft-Access)
    - Example:
     ```python
     conn_str = (
         r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
         r'DBQ=C:\path\to\mydb.accdb;'
     )
     cnxn = pyodbc.connect(conn_str)
     crsr = cnxn.cursor()
     for table_info in crsr.tables(tableType='TABLE'):
         print(table_info.table_name)
     ```

2. **Run `app.py`**:
    - Run `app.py` in the repository from the command line or any IDE:
     ```
     python app.py
     ```

3. **Check Successful Run**:
    - When it is successfully running, you will see this message:
     ```
     %path-repo%\edu_tech\app.py
     * Serving Flask app 'app'
     * Debug mode: off
     WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
     * Running on http://127.0.0.1:5000
     ```

4. **Access Web Portal**:
    - After successfully running, go to the link [http://127.0.0.1:5000](http://127.0.0.1:5000) to access the web portal.

5. **Deployment**:
    - You can use any WSGI server to deploy this Python - Flask Application.

## Technologies Used

The list of the technologies used to build the platform.

Front End
1. HTML
2. CSS
3. JavaScript

Back End
1. Python
2. Flask
3. MS Access
4. NetApp/AWS/GCP

## Contributors

A list of the contributors to the project.

1. Mansi Choudhari
2. Saloni Rangari
3. Pratham Badge
4. Pratham Chopde
5. Atharva Paraskar

## License

GNU General Public License v3.0

## Contact

Contact information for the project.

<a href="https://t.me/sinister_virus">
    Telegram : @sinister_virus 
</a>
<br/>

<a href="mailto:sinister-virus@outlook.com">
    Email : sinister-virus@outlook.com
</a>
<br/>
