
from google.cloud import translate_v2 as translate

class Translate():

    def getTranslatedText(self,target, sentence):    	

        
        translate_client = translate.Client()
        

        # Text can also be a sequence of strings, in which case this method
        # will return a sequence of results for each text.
        result = translate_client.translate(sentence,target_language=target)

        return result['translatedText']



