import os
import csv
import xlrd
# import pandas as pd
from app import db
from app.models import Student, Section, Result
from datetime import datetime
from dateutil.relativedelta import relativedelta

roster_file = os.path.join('documents', 'roster.csv')
roster_filepath = os.path.join('documents', 'roster.csv')
questions_file = os.path.join('documents', 'survey_questions.txt')
results_file = os.path.join('documents', 'results.csv')
s_id_i_roster = 8
c_id_i_roster = 1
prof_email_i_roster = 7
stud_email_i_roster = 9
subject_i_roster = 2
course_i_roster = 3
prof_name_i_roster = 6
prof_email_i_results = 0
c_id_i_results = 1
fr_ids = [6, 7, 13, 17, 21]

# initialize results table if DNE
# def initResultsTable():
#     if not os.path.exists(results_file):
#         with open(results_file, 'w', newline='') as f_results:
#             csv_results = csv.writer(f_results, delimiter=',')
#             csv_results.writerow(getResultsHeaders())
#             print('Headers loaded')

# retrieve headers: instructor email + class nbr + questions
def getResultsHeaders():
    with open(questions_file, 'r') as f_questions:
        headers = f_questions.readlines()
    # put instructor email in first column
    headers.insert(0, 'Instructor Email')
    # put course ID in second column
    headers.insert(1, 'Class Nbr')
    # strip trailing newline character that shows up for unknown reason
    for i, header in enumerate(headers):
        headers[i] = header.rstrip('\n')
    return headers

# enters new submission into results table
def submitResult(course_id, submission):
    data = submission   # submission should be list of answers to questions

Section.query.delete()
Result.query.delete()
db.session.add(Section(subject='COEN', course_num=' 123L', course_id=1234, prof_name='Ryan', prof_email='rku@scu.edu'))
s = Section.query.filter_by(course_id=1234).first()
print(s)
# db.session.add(Result(section=s, response_data=[1, 2, 'a', 4]))
# r = Result.query.first()
# print(r)
db.session.commit()

# enters new submission into results table
# def submitResult(course_id, submission):
#     # init table if DNE
#     if not os.path.exists(results_file):
#         initResultsTable()
#     # get instructor email using course number, insert into front of list
#     submission.insert(0, searchInstructorEmail(submission[0]))
#     with open(results_file, 'a', newline='') as f_results:
#         csv_results = csv.writer(f_results, delimiter=',')
#         csv_results.writerow(submission)
#         print('New submission inserted')

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

def searchInstructorEmail(course_id):
    with open(roster_file, 'r', newline='') as f_roster:
        csv_roster = csv.reader(f_roster, delimiter=',')
        for row in csv_roster:
            # if course number matches, return instructor email
            if removeZeroes(row[c_id_i_roster]) == str(course_id):
                return row[prof_email_i_roster]
        print('ERROR: Instructor email not found.')
        return 'ERROR'

# delete all files and database objects related to last survey session
def clearSurveySession():
    if os.path.exists(roster_file):
        os.remove(roster_file)
    if os.path.exists(results_file):
        os.remove(results_file)
    Student.query.delete()
    Section.query.delete()
    Result.query.delete()
    db.session.commit()

# Runs through roster, checks if student of matching student ID and course ID exists
def studentExists(s_id, c_id):
    students = Student.query.all()
    for student in students:
        if s_id == student.s_id and c_id == student.c_id:
            print('Student found')
            return True
    return False

    # with open(roster_file, 'r', newline='') as f_roster:
    #     # skip header row
    #     next(f_roster)
    #     csv_roster = csv.reader(f_roster, delimiter=',')
    #     for row in csv_roster:
    #         # print(row[s_id_i_roster].lstrip('0') + ' <-> ' + str(s_id) + ' | ' + row[c_id_i_roster].lstrip('0').rstrip('.0') + ' <-> ' + str(c_id))
    #         if removeZeroes(row[s_id_i_roster]) == str(s_id) and removeZeroes(row[c_id_i_roster]) == str(c_id):
    #             print('Student found')
    #             return True
    # print('Student not found')
    # return False

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
        with open(roster_file, 'w', newline='') as f_roster:
            csv_roster = csv.writer(f_roster, delimiter=',')
            for row_num in range(sheet.nrows):
                csv_roster.writerow(sheet.row_values(row_num))
        # remove after converting
        os.remove(filename)
    # if uploaded file is CSV
    elif ext == '.csv':
        # rename to proper roster filename
        os.rename(filename, roster_file)

def is_valid_datetime(dt1, dt2):
    """Returns True if dt1 is strictly after dt2 - False otherwise"""
    # at least one attribute of delta is positive iff dt1 is in fact after dt2 (non-positive attributes are 0)
    # all attributes of delta are 0 iff dt1 is identical to dt2
    # at least one attribute of delta is negative iff dt1 is before dt2 (non-negative attributes are 0)
    delta = relativedelta(dt1, dt2)
    # test for negativity in attributes:
    # first assume invalid
    # if hit positive value, set flag to True but continue to end
    # if hit negative value, return False immediately and unconditionally
    # if/when reached end, return flag (if all 0s, flag remains False)
    validity = False
    delta_attributes = [delta.years, delta.months, delta.weeks, delta.days, delta.hours, delta.minutes, delta.seconds, delta.microseconds]
    for attribute in delta_attributes:
        # if positive
        if attribute > 0:
            validity = True
        # if negative
        elif attribute < 0:
            return False
    return validity

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
