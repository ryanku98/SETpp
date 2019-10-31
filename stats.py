import csv
import pandas as pd

df = pd.read_csv(r'stats.csv')
print(df)

mean1 = df['The labs helped me understand the lecture material.'].mean()
print("Mean for \"The labs helped me understand the lecture material.\": " + str(mean))

mean2 = df['The labs taught me new skills.'].mean()

mean3 = df['The labs taught me to think creatively.'].mean()

mean4 = df['I would be able to repeat the labswithout help.'].mean()

#What was your favorite aspect of the lab?Free text response

#What about the lab would you like to see improved?Free text response

#The lab instructor was supportive. (An answer of 3 is neutral)

#The lab instructor was approachable. (An answer of 3 is neutral)

#The lab instructor was able to answer my questions. (An answer of 3 is neutral)

#The lab instructor helped me reach a clear understanding of key concepts. (An answer of 3 is neutral)

#The lab instructor fostered a mutually respectful learning environment. (An answer of 3 is neutral)

#What, if anything, could the lab instructor do to improve the experience?Free text response

#The amount of lab equipmentwas sufficient. (An answer of 3 is neutral)

#The available space was sufficient for the lab activities. (An answer of 3 is neutral)

#If lab equipment or setups were not functioning properly, adequate support was available to rectify the situation. (An answer of 3 is neutral)

#What, if anything, could improve lab space and equipment?Free text response
