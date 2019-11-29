import os
import csv
import xlrd
from flask import current_app
from app import db
from app.models import log_header, addSection, addStudent
from werkzeug.utils import secure_filename
from threading import Thread

def removeZeroes(str):
    """Strip extra characters in SCU's roster template cells"""
    try:
        # strips leading zeroes and trailing decimals (i.e. .0)
        # float casting needed first in case str is a string-type decimal (i.e. '1.0') - casting directly to int would fail
        return int(float(str))
    except:
        # needed for headers, etc. when passed-in value is not a string-type number
        return str

def parse_roster(form_roster_data):
    """Use uploaded roster to create corresponding database objects - expects a wtforms.fields.FileField object (i.e. form.<uploaded_file>.data)"""
    # save file locally
    filename = secure_filename(form_roster_data.filename)
    form_roster_data.save(filename)
    csv_filepath = os.path.join('documents', filename)

    ext = filename[filename.rindex('.'):]
    # if Excel file, convert to CSV and remove Excel version
    if ext == '.xlsx' or ext == '.xls':
        wb = xlrd.open_workbook(filename)
        sheet = wb.sheet_by_index(0)
        # convert
        with open(csv_filepath, 'w', newline='') as f_roster:
            csv_roster = csv.writer(f_roster, delimiter=',')
            for row_num in range(sheet.nrows):
                csv_roster.writerow(sheet.row_values(row_num))
        # remove Excel file
        os.remove(filename)
    # if already CSV file, simply move file
    elif ext == '.csv':
        os.rename(filename, csv_filepath)

    # indices as expected by the given SCU roster template
    C_ID_I = 1
    SUBJECT_I = 2
    COURSE_I = 3
    PROF_NAME_I = 6
    PROF_EMAIL_I = 7
    S_ID_I = 8
    STUDENT_EMAIL_I = 9
    section_count = 0
    student_count = 0

    with open(csv_filepath, 'r', newline='') as f_roster:
        # skip header row
        next(f_roster)
        rows = csv.reader(f_roster, delimiter=',')
        prev_c_id = -1
        print(log_header('ROSTER UPLOADED - PARSING'))
        student_threads = list()
        for row in rows:
            # add sections, addSection() avoids repeats
            subject = row[SUBJECT_I]
            course_num = row[COURSE_I]
            c_id = removeZeroes(row[C_ID_I])
            prof_name = row[PROF_NAME_I]
            prof_email = row[PROF_EMAIL_I]
            # only attempt to add a new section if moved onto new section
            if prev_c_id != c_id:
                addSection(subject, course_num, c_id, prof_name, prof_email)
                section_count += 1
                prev_c_id = c_id
            # make one student per row
            s_id = removeZeroes(row[S_ID_I])
            stud_email = row[STUDENT_EMAIL_I]
            t = Thread(target=addStudent, args=(current_app._get_current_object(), s_id, c_id, stud_email))
            student_threads.append(t)
            t.start()
        # make sure all adding threads finish before exiting (because emailing is called next and it might be called before all addStudent threads finish)
        for t in student_threads:
            t.join()
            student_count += 1
    os.remove(csv_filepath)
    print('ADDED {} SECTIONS AND {} STUDENTS'.format(section_count, student_count))
