#Imports
import os as os
import numpy as np
import pandas as pd
import openai as ai
import csv as csv
import string as string
from collections import Counter as cntr

#Grab API Key
apiKeyFile = "OpenAIKey.txt"
if os.path.exists(apiKeyFile):
  with open(apiKeyFile, 'r') as file:
    apiKey = file.read().strip()
else:
  print("API key file not found")

#Assigning Key
ai.api_key = apiKey

#CSV Columns
choiceA = [] #1 for old, 0 for young
explanationA = [] #reasoning for choiceA
qualityA = [] #rating of old doctor
qualityB = [] #rating of young doctor
age = [] #age of respondent
isMale = [] #1 for male, 0 for non-male

#Read CSV File
csvFile = "AI_support_cleaned.csv" #Name of CSV File
if os.path.exists(csvFile):
  with open(csvFile, 'r') as file:
    iterator = csv.reader(file)
    next(iterator) #skip header
    for row in iterator:
      choiceA.append(row[3])
      explanationA.append(row[6])
      qualityA.append(row[4])
      qualityB.append(row[5])
      age.append(row[7])
      isMale.append(row[8])
else:
  print(f"CSV File '{csvFile}' not found.\n")

#Define OpenAI Function Call
def explainChoice(myPrompt, text):
  response = ai.Completion.create(
    model = "text-davinci-003",
    prompt = f'''{myPrompt} User Response: {text}''',
    temperature = 0,
    max_tokens = 60,
    top_p = 1.0,
    frequency_penalty = 0.0,
    presence_penalty = 0.0)
  answer = str(response['choices'][0]['text'])
  return answer

#Define function to locate most frequently used KEY words
def findKeywords(sentences, numWords):
  words = []
  for sentence in sentences:
    for word in sentence.lower().split():
        word = word.translate(str.maketrans('', '', string.punctuation))
        if len(word) >= 3:
          words.append(word)
    counter = cntr(words)
    return [word for word, count in counter.most_common(numWords)]

#Summarizes the user's response using NLP
aiExplanation = []
if os.path.exists("aiExplanations.csv"):
  with open("aiExplanations.csv", 'r') as file:
    iterator = csv.reader(file)
    next(iterator)
    for row in iterator:
      aiExplanation.append(row[0])
else:
  myPrompt = "The user has given a reasoning behind their preference of either an older or younger doctor. Summarize their response into one phrase. Do not use any special characters."
  for i in explanationA:
    aiExplanation.append(explainChoice(myPrompt, i))
  with open("aiExplanations.csv", "w", newline="") as file:
    iterator = csv.writer(file)
    for i in aiExplanation:
      iterator.writerow([i.strip()])

#Separates AI Explanations by preference of older or younger
explanationOld = []
explanationYoung = []
for i in range(len(aiExplanation)):
  if int(choiceA[i]) == 1:
    explanationOld.append(aiExplanation[i])
  else:
    explanationYoung.append(aiExplanation[i])

#Find most frequent terms
keywordsOld = findKeywords(explanationOld, 10)
keywordsYoung = findKeywords(explanationYoung, 10)
print("\n")
print("Most used words for preference of older.")
print(keywordsOld)
print("\n")
print("Most used words for preference of younger.")
print(keywordsYoung)
print("\n")

#Number of responses that prefer older doctor
sumA = 0.0
for i in choiceA:
  sumA += float(i)

#Number of responses that prefer experience for older doctor
sumExperience = 0
for i in range(len(aiExplanation)):
    if int(choiceA[i]) == 1 and "experience" in aiExplanation[i].lower():
      sumExperience += 1

#Proportion of respondents that prefer older doctor
print("The proportion of respondents that prefer the older doctor.")
print(sumA / float(len(choiceA)))
print("\n")

#Proportion of respondents that cite experience, given they chose the older doctor
print("The proportion of respondents that cite mainly experience, given they chose the older doctor.")
print(float(sumExperience) / sumA)
print("\n")

#Proportion of respondents that cite accuracy
sumAccuracy = 0
sumB = 0.0
for i in choiceA:
  if int(i) == 0:
    sumB += 1
for i in range(len(aiExplanation)):
  if int(choiceA[i]) == 0 and "accura" in aiExplanation[i].lower():
    sumAccuracy += 1
print("The proportion of respondents that cite mainly accuracy, given they chose the younger doctor.")
print(float(sumAccuracy) / sumB)
print("\n")

#Finds quality difference between doctors
qualDiff = []
for i in range(len(qualityA)):
  qualDiff.append(float(qualityA[i]) - float(qualityB[i]))

#Finds the quality difference for those who want older doctor, separated by experience reasoning
sumExpOldQuality = 0
countExpOld = 0
sumNoExpOldQuality = 0
countNoExpOld = 0
for i in range(len(aiExplanation)):
  if int(choiceA[i]) == 1 and "experience" in aiExplanation[i].lower():
    sumExpOldQuality += qualDiff[i]
    countExpOld += 1
  elif int(choiceA[i]) == 1:
    sumNoExpOldQuality += qualDiff[i]
    countNoExpOld += 1

#Prints the quality difference for those who prefer old because of experience
print("This is the estimated quality difference for those who want an older doctor because of experience. (6 to -6)")
print(float(sumExpOldQuality) / float(countExpOld))
print("\n")

#Prints quality difference for those who prefer old NOT because of experience
print("This is the estimated quality difference for those who want an older doctor NOT because of experience. (6 to -6)")
print(float(sumNoExpOldQuality) / float(countNoExpOld))
print("\n")

#Finds the quality difference for those who prefer young, separated by accuracy
sumKeyYoungQuality = 0
countKeyYoung = 0
sumNoKeyYoungQuality = 0
countNoKeyYoung = 0
for i in range(len(aiExplanation)):
  if int(choiceA[i]) == 0 and "accura" in aiExplanation[i].lower():
    sumKeyYoungQuality += qualDiff[i]
    countKeyYoung += 1
  elif int(choiceA[i]) == 0:
    sumNoKeyYoungQuality += qualDiff[i]
    countNoKeyYoung += 1

#Prints the quality difference for those who prefer young because of accuracy
print("This is the estimated quality difference for those who want a younger doctor because of accuracy. (6 to -6)")
if countKeyYoung > 0:
  print(float(sumKeyYoungQuality) / float(countKeyYoung))
else:
  print("0.0")
print("\n")

#Prints quality difference for those who prefer old NOT because of accuracy
print("This is the estimated quality difference for those who want a younger doctor NOT because of accuracy. (6 to -6)")
print(float(sumNoKeyYoungQuality) / float(countNoKeyYoung))
print("\n")

#Separates original explanation category by choiceA and keywords
originalExplanationExperience = []
originalExplanationAccuracy = []
for i in range(len(aiExplanation)):
  if int(choiceA[i]) == 1 and "experience" in aiExplanation[i].lower():
    originalExplanationExperience.append(explanationA[i])
  elif int(choiceA[i]) == 0 and "accura" in aiExplanation[i].lower():
    originalExplanationAccuracy.append(explanationA[i])

#Uses keywords to determine if there are any linked reasonings with them
secondaryExperience = []
secondaryAccuracy = []
newExpPrompt = "The user has stated that they prefer an older doctor because of the reason of experience. Give me another reason. Limit your response to one phrase. Do not use any special characters."
newAccPrompt = "The user has stated that they prefer a younger doctor because of the reason of accuracy. Give me another reason. Limit your response to one phrase. Do not use any special characters."
for i in range(len(originalExplanationExperience)):
  secondaryExperience.append(explainChoice(newExpPrompt, originalExplanationExperience[i]))
for i in range(len(originalExplanationAccuracy)):
  secondaryAccuracy.append(explainChoice(newAccPrompt, originalExplanationAccuracy[i]))

#Prints the secondary reasons, only considering those who consider experience or accuracy
print("Of the respondents who prefer an older doctor for their experience, the following lists their most common secondary reasonings.")
print(findKeywords(secondaryExperience, 10))
print("\n")
print("Of the respondents who prefer a younger doctor for their accuracy, the following lists their most common secondary reasonings.")
print(findKeywords(secondaryAccuracy, 10))
print("\n")


#NOTES ON RESULTS
  #Respondents overwhelmingly preferred older doctor, but we knew that
  #Respondents who prefer the old doctor, overwhelmingly chose experience as their number one benefit
  #Respondents who prefer the young doctor, mostly chose accuracy, but only a minority of the time
    #More diversified reasonings, which I suppose could imply that there is less likely to be a significant reason to choose younger
    #OR that there are many good reasons to choose younger, and the AI couldn't capture all that information because we limited it to one quality per response
  #Accuracy in a younger doctor doesn't seem to have any effect on what respondents rate each doctor.
    #Implies that there is no definitive reason behind picking a younger doctor, and your reason doesn't impact your rating of each doctorcle