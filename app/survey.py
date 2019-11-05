import os
import csv
import pandas as pd

questions_file = os.path.join('documents', 'survey_questions.txt')
roster_file = os.path.join('documents', 'roster.csv')
results_file = os.path.join('documents', 'results.csv')
# statistics_file = os.path.join('documents', 'statistics.csv')
# List of headers of roster file
# roster_headers = ['Term', 'Class Nbr', 'Subject', 'Catalog', 'Title', 'Section', 'Instructor', 'Instructor Email', 'Student ID', 'Student', 'Email', 'Tot Enrl', 'Unit Taken', 'Grade', 'Campus', 'Location', 'Add Dt', 'Drop Dt', 'Comb Sect', 'Career', 'Component', 'Session', 'Class Type', 'Grade Base']
student_id_i = 8
course_id_i = 1
prof_email_i = 7
student_email_i = 9


# initialize results table if DNE
def initResultsTable():
    if not os.path.exists(results_file):
        with open(results_file, 'w', newline='') as f_results:
            csv_results = csv.writer(f_results, delimiter=',')
            csv_results.writerow(getResultsHeaders())
            print('Headers loaded')


# retrieve headers: instructor email + class nbr + questions
def getResultsHeaders():
    with open(questions_file, 'r') as f_questions:
        headers = f_questions.readlines()
        # put instructor email in first column
        headers.insert(0, 'Instructor Email')
        # put course ID in second column
        headers.insert(1, 'Class Nbr')
        return headers


# enters new submission into results table
def submitResult(submission):
    # init table if DNE
    if not os.path.exists(results_file):
        initResultsTable()
    # get instructor email using course number, insert into front of list
    submission.insert(0, searchInstructorEmail(submission[0]))
    with open(results_file, 'a', newline='') as f_results:
        csv_results = csv.writer(f_results, delimiter=',')
        csv_results.writerow(submission)
        print('New submission inserted')


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
            if row[course_id_i] == str(course_id):
                return row[instructor_email_i]
        print('ERROR: Instructor email not found.')
        return 'ERROR'


# delete all files related to last survey session
def clearSurveySession():
    if os.path.exists(roster_file):
        os.remove(roster_file)
    if os.path.exists(results_file):
        os.remove(results_file)


# Runs through roster, checks if student of matching student ID and course ID exists
def studentExists(s_id, c_id):
    with open(roster_file, 'r', newline='') as f_roster:
        csv_roster = csv.reader(f_roster, delimiter=',')
        for row in csv_roster:
            if row[student_id_i] == str(s_id) and row[course_id_i] == str(c_id):
                print('Student found')
                return True
    print('Student not found')
    return False


def send_section_emails():
    # iterate through sorted results
    # analyze_data() for each new Section
    # email that dataframe here


def analyze_data(data):
    '''WLL BE CALLED ON INDIVIDUAL SECTIONS'''
    section_data = pd.DataFrame.from_records(data)
    means = []; stds = []; frs = [] # means, standard deviations, free responses

    # for question in section_data:
    #    means.append(question.mean)

    for i in range(0, len(section_data)):
        

#    for i in range(0, total):
#        means.append(df[mc_qs[i]].mean())

    for i in range(0, total):
        print("Mean for \"" + mc_qs[i] + "\": " + str(means[i]))

class Section:
    __init__(self, course_id):
        self.prof_email
        self.mean_list = []
        self.std_list = []
        self.fr_list = []
