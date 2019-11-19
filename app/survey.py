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
    c_id_i_roster = 1
    subject_i_roster = 2
    course_i_roster = 3
    prof_name_i_roster = 6
    prof_email_i_roster = 7
    s_id_i_roster = 8
    stud_email_i_roster = 9

    with open(csv_filepath, 'r', newline='') as f_roster:
        # skip header row
        next(f_roster)
        rows = csv.reader(f_roster, delimiter=',')
        prev_c_id = -1
        print(log_header('ROSTER UPLOADED - PARSING'))
        student_threads = list()
        for row in rows:
            # add sections, addSection() avoids repeats
            subject = row[subject_i_roster]
            course_num = row[course_i_roster]
            c_id = removeZeroes(row[c_id_i_roster])
            prof_name = row[prof_name_i_roster]
            prof_email = row[prof_email_i_roster]
            # only attempt to add a new section if moved onto new section
            if prev_c_id != c_id:
                addSection(subject, course_num, c_id, prof_name, prof_email)
                prev_c_id = c_id
            # make one student per row
            s_id = removeZeroes(row[s_id_i_roster])
            stud_email = row[stud_email_i_roster]
            t = Thread(target=addStudent, args=(current_app._get_current_object(), s_id, c_id, stud_email))
            student_threads.append(t)
            t.start()
        # make sure all adding threads finish before exiting (because emailing is called next and it might be called before all addStudent threads finish)
        for t in student_threads:
            t.join()
    os.remove(csv_filepath)
