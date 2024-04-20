import os
import pyodbc
import pandas as pd
import numpy as np

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


# for i in cursor.tables(tableType='TABLE'):
#     print(i.table_name)
#
#
# for i in cursor.tables(tableType='VIEW'):
#     print(i.table_name)

# for i in cursor.columns(table='admin_auth'):
#     print(i.column_name)

# for i in cursor.columns(table='class_12'):
#     print(i.column_name)

aadhaar_no = "902728786228"

class_1_12_average_marks = []

query = f"SELECT c_1_sub_1_marks_obtained, c_1_sub_2_marks_obtained, c_1_sub_3_marks_obtained, c_1_sub_4_marks_obtained, c_1_sub_5_marks_obtained    FROM class_1 WHERE aadhaar_no = '{aadhaar_no}'"
cursor.execute(query)
data = cursor.fetchall()
data = np.array(data)
data = pd.DataFrame(data)
data.columns = ['Subject 1', 'Subject 2', 'Subject 3', 'Subject 4', 'Subject 5']
c_1_average_marks = data.mean(axis=1)
print(c_1_average_marks)
class_1_12_average_marks.append(c_1_average_marks)
#
# query = f"SELECT c_12_sub_1_marks_obtained, c_12_sub_2_marks_obtained, c_12_sub_3_marks_obtained, c_12_sub_4_marks_obtained, c_12_sub_5_marks_obtained    FROM class_12 WHERE aadhaar_no = '{aadhaar_no}'"
# cursor.execute(query)
# data = cursor.fetchall()
# data = np.array(data)
# data = pd.DataFrame(data)
# data.columns = ['Subject 1', 'Subject 2', 'Subject 3', 'Subject 4', 'Subject 5']
# c_12_average_marks = int(data.mean(axis=1).iloc[0])
# print(c_12_average_marks)
# class_1_12_average_marks.append(c_12_average_marks)
#
# print(class_1_12_average_marks)


