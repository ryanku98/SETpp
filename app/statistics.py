import os
import csv
import pandas as pd

# qs = ['The labs helped me understand the lecture material.', 'The labs taught me new skills.', 'The labs taught me to think creatively.', 'I would be able to repeat the labswithout help.', 'The lab instructor was supportive.', 'The lab instructor was approachable.', 'The lab instructor was able to answer my questions.', 'The lab instructor helped me reach a clear understanding of key concepts.', 'The lab instructor fostered a mutually respectful learning environment.', 'The amount of lab equipmentwas sufficient.', 'The available space was sufficient for the lab activities.', 'If lab equipment or setups were not functioning properly, adequate support was available to rectify the situation.'

statistics_file = 'documents/results.csv'
questions_file = 'documents/survey_questions.txt'

def initResultsTable():
    if not os.path.exists(statistics_file):
        with open(statistics_file, 'w') as f_statistics, open(questions_file, 'r') as f_questions:
            csvfile = csv.writer(f_statistics, delimiter=',')
            headers = f_questions.readlines()
            # put course ID in first column
            headers.insert(0, 'Class Nbr')
            # put instructor email in second column
            headers.insert(1, 'Instructor Email')
            csvfile.writerow(headers)
        print('Headers loaded')
        
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
