import os
from openpyxl import Workbook, load_workbook


def save_marks_to_excel(roll_no, name, course, subject, internal, marks):

    file_name = f"{course}inter marks.xlsx"

    # Create file if not exists
    if not os.path.exists(file_name):

        workbook = Workbook()
        sheet = workbook.active

        sheet.title = "Internal Marks"

        sheet.append([
            "Roll No",
            "Name",
            "Course",
            "Subject",
            "Internal",
            "Marks"
        ])

        workbook.save(file_name)


    # Open existing file
    workbook = load_workbook(file_name)

    sheet = workbook.active


    # Add new student row
    sheet.append([
        roll_no,
        name,
        course,
        subject,
        internal,
        marks
    ])


    workbook.save(file_name)