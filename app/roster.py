import os
import csv
import xlrd
import re
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

def isValidEmail(email):
    """Returns true if email is a correctly formatted SCU email"""
    # help from https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    regex = '^\w+([\.-]?\w+)*@scu.edu+$'
    if re.search(regex, email):
        return True
    return False

def isID(val):
    """Returns true if val is a valid ID"""
    if isinstance(val, int) and val > 0:
        return True
    return False

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

    # expected headers:
    C_ID_S = 'Class Nbr'
    SUBJECT_S = 'Subject'
    COURSE_S = 'Catalog'
    PROF_NAME_S = 'Instructor'
    PROF_EMAIL_S = 'Instructor Email'
    S_ID_S = 'Student ID'
    STUDENT_EMAIL_S = 'Student Email'

    # counters
    section_count = 0
    student_count = 0

    with open(csv_filepath, 'r', newline='') as f_roster:
        # skip header row
        # next(f_roster)
        rows = csv.reader(f_roster, delimiter=',')
        header_row = next(rows)
        # ensure important columns have correct headers
        if not (header_row[0][C_ID_I].lower() == C_ID_S.lower() and \
                header_row[0][SUBJECT_I].lower() == SUBJECT_S.lower() and \
                header_row[0][COURSE_I].lower() == COURSE_S.lower() and \
                header_row[0][PROF_NAME_I].lower() == PROF_NAME_S.lower() and \
                header_row[0][PROF_EMAIL_I].lower() == PROF_EMAIL_S.lower() and \
                header_row[0][S_ID_I].lower() == S_ID_S.lower() and \
                header_row[0][STUDENT_EMAIL_I].lower() == SUBJECT_S.lower()):
            # remove and return false (therefore exiting early) if roster does not have expected headers
            os.remove(csv_filepath)
            return False

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
            # only attempt to add a new section if moved onto new valid section ID with properly formatted SCU email
            if prev_c_id != c_id and isValidEmail(prof_email) and isID(c_id):
                addSection(subject, course_num, c_id, prof_name, prof_email)
                section_count += 1
                prev_c_id = c_id
            # make one student per row
            s_id = removeZeroes(row[S_ID_I])
            stud_email = row[STUDENT_EMAIL_I]
            if isValidEmail(stud_email) and isID(s_id) and prev_c_id == c_id:
                # only add student if has correctly formatted SCU email
                # prev_c_id only matches c_id if section with c_id was created - if not, don't add student because his/her section DNE in DB
                t = Thread(target=addStudent, args=(current_app._get_current_object(), s_id, c_id, stud_email))
                student_threads.append(t)
                t.start()
        # make sure all adding threads finish before exiting (because emailing is called next and it might be called before all addStudent threads finish)
        for t in student_threads:
            t.join()
            student_count += 1
    os.remove(csv_filepath)
    print('ADDED {} SECTIONS AND {} STUDENTS'.format(section_count, student_count))
    return True
