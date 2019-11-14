import os
import csv
import xlrd
# import pandas as pd
from app import db
from app.models import Student, Section, Result
from datetime import datetime
from dateutil.relativedelta import relativedelta

roster_filepath = os.path.join('documents', 'roster.csv')
questions_file = os.path.join('documents', 'survey_questions.txt')
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
fr_ids = [6, 7, 13, 17, 21]

# initialize results table if DNE
# def initResultsTable():
#     if not os.path.exists(results_file):
#         with open(results_file, 'w', newline='') as f_results:
#             csv_results = csv.writer(f_results, delimiter=',')
#             csv_results.writerow(getResultsHeaders())
#             print('Headers loaded')

# Section.query.delete()
# Student.query.delete()
# Result.query.delete()
# db.session.add(Section(subject='COEN', course_num=' 123L', course_id=1234, prof_name='Ryan', prof_email='rku@scu.edu'))
# # s = Section.query.filter_by(course_id=1234).first()
# s = Section.query.first()
# # print(s)
# db.session.add(Result(section=s, response_data=[1, 2, 'a', 4]))
# # r = Result.query.first()
# # print(r)
# db.session.add(Student(section=s, s_id=1221784, email='rku@scu.edu'))
# print(Section.query.first())
# print(Student.query.first())
# print(Result.query.first())
# db.session.commit()

# return results in sorted order
def getSortedResults():
    # extract result entries and sort by course
    with open(results_file, 'r', newline='') as f_results:
        csv_results = csv.reader(f_results, delimiter=',')
        # extract entries
        entries = []
        for row in csv_results:
            entries.append(row)
        # remove header row
        entries.pop(0)
        # sort by course (column index 1)
        entries.sort(key=lambda entry: int(entry[1]))
        return entries

def clearSurveySession():
    """Deletes all files and database objects related to last survey session"""
    # TODO: remove file removal functions when database porting is complete
    if os.path.exists(roster_filepath):
        os.remove(roster_filepath)
    if os.path.exists(results_file):
        os.remove(results_file)
    Section.query.delete()
    Student.query.delete()
    Result.query.delete()
    Deadline.query.delete()
    Reminder.query.delete()
    db.session.commit()

# TODO: remove when unneeded
def removeZeroes(str):
    return str.lstrip('0').rstrip('.0')

def convertToCSV(filename):
    """Converts uploaded roster to CSV if Excel file, otherwise simply renames"""
    if not os.path.exists(filename):
        print('File ' + filename + ' not found.')
        return
    ext = filename[filename.rindex('.'):]
    # if uploaded file is Excel file
    if ext == '.xlsx' or ext == 'xls':
        # open excel file
        wb = xlrd.open_workbook(filename)
        sheet = wb.sheet_by_index(0)
        # create CSV file
        with open(roster_filepath, 'w', newline='') as f_roster:
            csv_roster = csv.writer(f_roster, delimiter=',')
            for row_num in range(sheet.nrows):
                csv_roster.writerow(sheet.row_values(row_num))
        # remove after converting
        os.remove(filename)
    # if uploaded file is CSV
    elif ext == '.csv':
        # rename to proper roster filename
        os.rename(filename, roster_filepath)

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
