#import nltk
#nltk.download('stopwords')
from rake_nltk import Rake  
import pandas as pd  

df = pd.read_csv(r'AIShortened.csv')

df1 = df.loc[df['CONDITION'] == 1]  
explanation = df1['Explanation'].tolist() 

print(explanation)

r = Rake(min_length=2) 

r.extract_keywords_from_sentences(explanation) 

print(r.get_ranked_phrases_with_scores())