# from werkzeug.security import generate_password_hash,check_password_hash
#
# password="123"
# print(password)
# hash = generate_password_hash(password)
# print(hash)
# cp = (check_password_hash(hash,password))
# print(cp)
#
# if cp == True:
#     print("Password is correct")
# else:
#     print("Password is incorrect")
#
#


import matplotlib.pyplot as plt
import numpy as np

marks_obtained = [['1300'], ['1300'], ['1300'], ['1300'], ['1300'], ['1300'], ['1300'], ['1300'], ['1300'], ['1400'], ['1200'], ['450']]
total_marks = [['1500'], ['1500'], ['1500'], ['1500'], ['1500'], ['1500'], ['1500'], ['1500'], ['1500'], ['1500'], ['1500'], ['500']]
percentage = [['95'], ['95'], ['95'], ['95'], ['95'], ['95'], ['95'], ['95'], ['95'], ['78'], ['80'], ['87']]
grade = [['A'], ['B'], ['C'], ['D'], ['E'], ['F'], ['D'], ['C'], ['A'], ['E'], ['D'], ['B']]
cgpa = [['9'], ['9'], ['9'], ['9'], ['9'], ['9'], ['9'], ['9'], ['9'], ['8'], ['8'], ['7.0']]

# Convert nested lists to flat lists
marks_obtained = [int(x[0]) for x in marks_obtained]
total_marks = [int(x[0]) for x in total_marks]
percentage = [float(x[0]) for x in percentage]
grade = [x[0] for x in grade]
cgpa = [float(x[0]) for x in cgpa]

class_labels = ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Class 7", "Class 8", "Class 9",
                "Class 10", "Class 11", "Class 12"]

# Plot the data into bar graphs using matplotlib

# Marks Obtained vs Total Marks
# Convert class labels to numpy array for easier positioning of bars
x = np.arange(len(class_labels))

# Width of each bar
bar_width = 0.35

# Create the figure and axes
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the bars
rects1 = ax.bar(x - bar_width/2, marks_obtained, bar_width, label='Marks Obtained')
rects2 = ax.bar(x + bar_width/2, total_marks, bar_width, label='Total Marks')

# Add labels, title, and legend
ax.set_xlabel('Classes')
ax.set_ylabel('Marks')
ax.set_title('Marks Obtained vs Total Marks')
ax.set_xticks(x)
ax.set_xticklabels(class_labels, rotation=45)
ax.legend()

# Show plot
plt.tight_layout()
plt.show()

# Percentage vs Classes
plt.figure(figsize=(10, 6))
plt.bar(class_labels, percentage, label="Percentage")
plt.xlabel('Classes')
plt.ylabel('Percentage')
plt.title('Percentage vs Classes')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

# Grade vs Classes
# Define a dictionary to map grades to numerical values
grade_mapping = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}

# Convert grades to numerical values using the dictionary
numerical_grades = [grade_mapping[grade] for grade in grade]

class_labels = ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6",
                "Class 7", "Class 8", "Class 9", "Class 10", "Class 11", "Class 12"]


# Plot the bar graph
plt.figure(figsize=(10, 6))
plt.bar(class_labels, numerical_grades, label="Grade")
plt.xlabel('Classes')
plt.ylabel('Grade')
plt.title('Grade vs Classes')
plt.xticks(rotation=45)
plt.yticks(range(6), ['F', 'E', 'D', 'C', 'B', 'A'])  # Set y-axis labels
plt.legend()
plt.tight_layout()
plt.show()


# CGPA vs Classes
plt.figure(figsize=(10, 6))
plt.bar(class_labels, cgpa, label="CGPA")
plt.xlabel('Classes')
plt.ylabel('CGPA')
plt.title('CGPA vs Classes')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()







