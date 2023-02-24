#Imports
import os as os
import numpy as np
import pandas as pd
import openai as ai
import csv as csv

#Grab API Key
apiKeyFile = "OpenAIKey.txt"

if os.path.exists(apiKeyFile):
    with open(apiKeyFile, 'r') as file:
        apiKey = file.read().strip()

else:
  print("API key file not found")

ai.api_key = apiKey

#Global Inputs
csvFile = "AIShortened.csv" #Name of CSV File
promptOlder = "A user was asked a whether or not they'd prefer to be assisted by an old doctor or a young one. Both doctors would be assisted by medical AI. They preferred an older doctor. Can you shorten their explanation by listing a few key attributes? Limit your response to one phrase."
promptYounger = "A user was asked a whether or not they'd prefer to be assisted by an old doctor or a young one. Both doctors would be assisted by medical AI. They preferred an younger doctor. Can you shorten their explanation by listing a few key attributes? Limit your response to one phrase."

#Global Variables
doctorAge = []
doctorAgeReason = []
preferOld = []
preferOldReason = []
simpleOld = []
preferYoung = []
preferYoungReason = []
simpleYoung = []

#Call OpenAI API: Modify Request Above
def explainChoice(myPrompt, text):
  response = ai.Completion.create(
    model="text-davinci-002",
    prompt=
    f'''{myPrompt} User Explanation: {text}''',
    temperature=0,
    max_tokens=60,
    top_p=1.0,
    frequency_penalty=0.5,
    presence_penalty=0.0)
  answer = str(response['choices'][0]['text'])
  return answer

if os.path.exists(csvFile):
  with open(csvFile, 'r') as file:
    iterator = csv.reader(file)
    next(iterator) #skip header
    for row in iterator:
      doctorAge.append(row[3])
      doctorAgeReason.append(row[6])
else:
  print(f"CSV File '{csvFile}' not found.\n")

#for i in doctorAgeReason:
#  if(doctorAge[doctorAgeReason.index(i)] == '1'): #prefers older doctor
#    preferOld.append(doctorAge.index(i))
#    preferOldReason.append(i)
#    simpleOld.append(explainChoice(promptOlder, i))
#  else: #prefers younger doctor
#    preferYoung.append(doctorAge.index(i))
#    preferYoungReason.append(i)
#    #simpleYoung.append(explainChoice(doctorAgeReason[doctorAge.index(i)]))

if len(doctorAge) > 0:
  #plan:
    #convert our .csv file into a matrix of only useful values
    #should be able to generate new vectors that separate valuable characteristics, makes comparisons simpler
    #can use R to make more statistical conclusions on the association between variables
else: 
  print("Was unable to populate from .csv file.\n")

#print(simpleOld)
#print(simpleYoung)