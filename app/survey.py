import os
import csv
import xlrd
import pandas as pd

headers = ["Instructor Email","Class Nbr","The labs helped me understand the lecture material. (An answer of 3 is neutral)",
"The labs taught me new skills. (An answer of 3 is neutral)","The labs taught me to think creatively. (An answer of 3 is neutral)","I would be able to repeat the labs without help. (An answer of 3 is neutral)","What was your favorite aspect of the lab? (Free text response)","What about the lab would you like to see improved? (Free text response)","The lab instructor was supportive. (An answer of 3 is neutral)","The lab instructor was approachable. (An answer of 3 is neutral)","The lab instructor was able to answer my questions. (An answer of 3 is neutral)","The lab instructor helped me reach a clear understanding of key concepts. (An answer of 3 is neutral)","The lab instructor fostered a mutually respectful learning environment. (An answer of 3 is neutral)","What, if anything, could the lab instructor do to improve the experience? (Free text response)","The amount of lab equipment was sufficient. (An answer of 3 is neutral)","The available space was sufficient for the lab activities. (An answer of 3 is neutral)","If lab equipment or setups were not functioning properly, adequate support was available to rectify the situation. (An answer of 3 is neutral)","What, if anything, could improve lab space and equipment? (Free text response)","On average, the approximate number of hours completing a lab was (5 choices: <2 2 2.5 3 >3)","How many hours did you spend preparing for the lab? (5 choices: <2 2 2.5 3 >3)","How many hours did you spend writing lab reports outside the designated lab period? (5 choices: <2 2 2.5 3 >3)","What feedback would you give the lecture section instructor (not the lab TA) about the labs? (Free text response)"]

questions_file = os.path.join('documents', 'survey_questions.txt')
roster_file = os.path.join('documents', 'roster.csv')
results_file = os.path.join('documents', 'results.csv')
s_id_i_roster = 8
c_id_i_roster = 1
prof_email_i_roster = 7
stud_email_i_roster = 9
prof_email_i_results = 0
c_id_i_results = 1

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
            if removeZeroes(row[c_id_i_roster]) == str(course_id):
                return row[prof_email_i_roster]
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
        # skip header row
        next(f_roster)
        csv_roster = csv.reader(f_roster, delimiter=',')
        for row in csv_roster:
            # print(row[s_id_i_roster].lstrip('0') + ' <-> ' + str(s_id) + ' | ' + row[c_id_i_roster].lstrip('0').rstrip('.0') + ' <-> ' + str(c_id))
            if removeZeroes(row[s_id_i_roster]) == str(s_id) and removeZeroes(row[c_id_i_roster]) == str(c_id):
                print('Student found')
                return True
    print('Student not found')
    return False

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

# SECTION CLASS
# TODO: Evan creates a dataframe for parssing through these and sending the stats to the professors
class Section:
    def __init__(self, course_id, data):
        self.prof_email = "a1morales@scu.edu"
        self.mean_list = []
        self.std_list = []
        self.fr_list = []
        self.data = data

    def get_section_stats(self):
        """WLL BE CALLED ON INDIVIDUAL SECTIONS"""

        # add first row to self.data
        self.data.insert(0, headers)

        df = pd.DataFrame.from_records(self.data)

        course_i = 1
        question_i = 2
        fr_ids = [6, 7, 13, 17, 21]

        course = section_data[course_i]

        for i in range(question_i, len(section_data)):
            if (i in fr_ids):
                self.fr_list.append(section_data[i])
            else:
                self.mean_list.append(df[section_data[i]].mean())
                self.std_list.append(df[section_data[i]].std())

        return self
