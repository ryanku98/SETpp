import os
import csv
import pandas as pd
from app.roster import roster_file, course_id_i, instructor_email_i

# qs = ['The labs helped me understand the lecture material.', 'The labs taught me new skills.', 'The labs taught me to think creatively.', 'I would be able to repeat the labswithout help.', 'The lab instructor was supportive.', 'The lab instructor was approachable.', 'The lab instructor was able to answer my questions.', 'The lab instructor helped me reach a clear understanding of key concepts.', 'The lab instructor fostered a mutually respectful learning environment.', 'The amount of lab equipmentwas sufficient.', 'The available space was sufficient for the lab activities.', 'If lab equipment or setups were not functioning properly, adequate support was available to rectify the situation.'

results_file = 'documents/results.csv'
questions_file = 'documents/survey_questions.txt'

# class ResultsTable():

def initResultsTable():
    if not os.path.exists(results_file):
        with open(results_file, 'w', newline='') as f_results, open(questions_file, 'r') as f_questions:
            headers = f_questions.readlines()
            # put instructor email in first column
            headers.insert(0, 'Instructor Email')
            # put course ID in second column
            headers.insert(1, 'Class Nbr')
            csv_results = csv.writer(f_results, delimiter=',')
            csv_results.writerow(headers)
            print('Headers loaded')
        
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
