
from google.cloud import translate_v2 as translate
import re

class Translate():

	def __init__(self):
		patternsList=[]
		for i in range(33, 48):
			patternsList.append("&#"+str(i)+";")
		for i in range(58, 65):
			patternsList.append("&#"+str(i)+";")
		for i in range(91, 97):
			patternsList.append("&#"+str(i)+";")
		for i in range(123, 127):
			patternsList.append("&#"+str(i)+";")
		
		self.patterns="|".join(patternsList)
		
	def sanitise(self,text):
		text=re.sub(self.patterns, "", text)
		return text
	
	def getTranslatedText(self,target, sentence):    	


		translate_client = translate.Client()


		# Text can also be a sequence of strings, in which case this method
		# will return a sequence of results for each text.
		result = translate_client.translate(sentence,target_language=target)
		translation=self.sanitise(result['translatedText'])
		return translation

	




