import os
import csv
import xlrd
# import pandas as pd
from app import db
from app.models import log_header, wipeDatabase, addSection, addStudent
from datetime import datetime
from dateutil.relativedelta import relativedelta
from werkzeug.utils import secure_filename

roster_filepath = os.path.join('documents', 'roster.csv')
s_id_i_roster = 8
c_id_i_roster = 1
prof_email_i_roster = 7
stud_email_i_roster = 9
subject_i_roster = 2
course_i_roster = 3
prof_name_i_roster = 6
# TODO: these should NOT be needed after database porting is done
results_file = os.path.join('documents', 'results.csv')
prof_email_i_results = 0
c_id_i_results = 1
# TODO: these should NOT be hardcoded - write function to determine if quesion is a FRQ (e.g. check if 'Free text response' is in the question)
# fr_ids = [6, 7, 13, 17, 21]

# return results in sorted order
# def getSortedResults():
#     # extract result entries and sort by course
#     with open(results_file, 'r', newline='') as f_results:
#         csv_results = csv.reader(f_results, delimiter=',')
#         # extract entries
#         entries = []
#         for row in csv_results:
#             entries.append(row)
#         # remove header row
#         entries.pop(0)
#         # sort by course (column index 1)
#         entries.sort(key=lambda entry: int(entry[1]))
#         return entries

# TODO: remove when unneeded
def removeZeroes(str):
    return str.lstrip('0').rstrip('.0')

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

    with open(csv_filepath, 'r', newline='') as f_roster:
        # skip header row
        next(f_roster)
        rows = csv.reader(f_roster, delimiter=',')
        prev_c_id = -1
        print(log_header('ROSTER UPLOADED - PARSING'))
        for row in rows:
            # add sections, addSection() avoids repeats
            subject = row[subject_i_roster]
            course_num = row[course_i_roster]
            c_id = row[c_id_i_roster].lstrip('0').rstrip('.0')
            prof_name = row[prof_name_i_roster]
            prof_email = row[prof_email_i_roster]
            # only attempt to add a new section if moved onto new section
            if prev_c_id != c_id:
                addSection(subject, course_num, c_id, prof_name, prof_email)
                prev_c_id = c_id
            # make one student per row
            s_id = row[s_id_i_roster].lstrip('0').rstrip('.0')
            stud_email = row[stud_email_i_roster]
            addStudent(s_id, c_id, stud_email)
    os.remove(csv_filepath)

# SECTION CLASS
# TODO: Evan creates a dataframe for parssing through these and sending the stats to the professors
# class Section:
#     def __init__(self, course_id, data):
#         self.course_id = course_id
#         self.mean_list = []
#         self.std_list = []
#         self.fr_list = []
#         self.data = data
#         self.course_id = course_id
#         self.formatted_stats = []
#         self.analyze_stats()
#
#     def analyze_stats(self):
#         """Uses Pandas to analyze statistics"""
#         question_i = 2
#         df = pd.DataFrame.from_records(self.data)
#         self.formatted_stats.append(self.course_id)
#         means = ''; stds = ''; frs = ''
#         headers = getResultsHeaders()   # cut off first two columns (intructor email & course id)
#         for i in range(question_i, len(self.data[0])):
#             if i in fr_ids:
#                 self.fr_list.append(df[i].values)
#                 frs += "- Answer for free response question \'{}\': {}\n".format(headers[i], df[i].values)
#             else:
#                 mean = pd.to_numeric(df[i]).mean()
#                 self.mean_list.append(mean)
#                 means += "- Mean for question \'{}\': {}\n".format(headers[i], mean)
#                 std = pd.to_numeric(df[i]).std()
#                 self.std_list.append(std)
#                 stds += "- Standard deviation for question \'{}\': {}\n".format(headers[i], std)
#
#         self.formatted_stats.append(means)
#         self.formatted_stats.append(stds)
#         self.formatted_stats.append(frs)

# data = [['eejohnson@scu.edu',83505,1,1,1,1,'asdf','asdf',1,1,1,1,1,'asdf',1,1,1,'asdf',2.5,2.5,2.5,'asdf'],
# ['eejohnson@scu.edu',83505,2,1,1,1,'asdf','asdf',1,1,1,1,1,'asdf',1,1,1,'asdf',2.5,2.5,2.5,'asdf']]
# sect = Section(83505,data)
# sect.get_section_stats()
# print(sect.fr_list)
