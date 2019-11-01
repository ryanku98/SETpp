import csv
import pandas as pd

# mc_qs = ['The labs helped me understand the lecture material.', 'The labs taught me new skills.', 'The labs taught me to think creatively.', 'I would be able to repeat the labswithout help.', 'The lab instructor was supportive.', 'The lab instructor was approachable.', 'The lab instructor was able to answer my questions.', 'The lab instructor helped me reach a clear understanding of key concepts.', 'The lab instructor fostered a mutually respectful learning environment.', 'The amount of lab equipmentwas sufficient.', 'The available space was sufficient for the lab activities.', 'If lab equipment or setups were not functioning properly, adequate support was available to rectify the situation.']

# instead scrape questions from the first row of the csv file
mc_qs = ["The labs helped me understand the lecture material.", "The labs taught me new skills.", "The labs taught me to think creatively."]

total = len(mc_qs)

df = pd.read_csv(r'../documents/stats.csv')
# print(df)

means = []

for i in range(0, total):
    means.append(df[mc_qs[i]].mean())

for i in range(0, total):
    print("Mean for \"" + mc_qs[i] + "\": " + str(means[i]))




# FREE RESPONSE QUESTIONS

#What was your favorite aspect of the lab?Free text response
#What about the lab would you like to see improved?Free text response
#What, if anything, could the lab instructor do to improve the experience?Free text response
#What, if anything, could improve lab space and equipment?Free text response
