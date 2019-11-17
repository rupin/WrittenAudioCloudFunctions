
from google.cloud import translate_v2 as translate

class Translate():

    def getTranslatedText(self,source, target, sentence):    	

        
        translate_client = translate.Client()
        

        # Text can also be a sequence of strings, in which case this method
        # will return a sequence of results for each text.
        result = translate_client.translate(sentence, source_language=source, target_language=target)

        return result['translatedText']



