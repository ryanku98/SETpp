import csv
import pandas as pd

qs = ['The labs helped me understand the lecture material.', 'The labs taught me new skills.', 'The labs taught me to think creatively.', 'I would be able to repeat the labswithout help.', 'The lab instructor was supportive.', 'The lab instructor was approachable.', 'The lab instructor was able to answer my questions.', 'The lab instructor helped me reach a clear understanding of key concepts.', 'The lab instructor fostered a mutually respectful learning environment.', 'The amount of lab equipmentwas sufficient.', 'The available space was sufficient for the lab activities.', 'If lab equipment or setups were not functioning properly, adequate support was available to rectify the situation.'

df = pd.read_csv(r'stats.csv')
# print(df)

means = []

c = 0
for (q in qs):
    means[c]= df[qs[c]].mean()
    c = c + 1
    
    
for (mean in means):
    print("Mean for " + qs[1] + " : " + str(mean1))

mean4 = df[].mean()



# FREE RESPONSE QUESTIONS

#What was your favorite aspect of the lab?Free text response
#What about the lab would you like to see improved?Free text response
#What, if anything, could the lab instructor do to improve the experience?Free text response
#What, if anything, could improve lab space and equipment?Free text response
