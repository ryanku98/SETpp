import os
import csv
import pandas as pd
from app.roster import roster_file, course_id_i, instructor_email_i

questions_file = os.path.join('documents', 'survey_questions.txt')
results_file = os.path.join('documents', 'results.csv')
statistics_file = os.path.join('documents', 'statistics.csv')

# initialize results table if DNE
def initTable(filepath):
    # STANDARDIZE INIT
    if not os.path.exists(filepath):
        with open(filepath, 'w', newline='') as f_results:
            csv_results = csv.writer(f_results, delimiter=',')
            csv_results.writerow(getHeaders())
            print('Headers loaded')

# retrieve headers: instructor email + class nbr + questions
def getHeaders():
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
        initTable(results_file)
    # get instructor email using course number, insert into front of list
    submission.insert(0, searchInstructorEmail(submission[0]))
    with open(results_file, 'a', newline='') as f_results:
        csv_results = csv.writer(f_results, delimiter=',')
        csv_results.writerow(submission)
        print('New submission inserted')
    
# return results in sorted order
def getSortedResults():
    # reset statistics file
    if os.path.exists(statistics_file):
        os.remove(statistics_file)
    initTable(statistics_file)
    
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
        
# def andresfunction():
#     total = len(mc_qs)
# 
#     df = pd.read_csv(r'../documents/stats.csv')
#     # print(df)
# 
#     means = []
# 
#     for i in range(0, total):
#         means.append(df[mc_qs[i]].mean())
# 
#     for i in range(0, total):
#         print("Mean for \"" + mc_qs[i] + "\": " + str(means[i]))
