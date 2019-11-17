
from google.cloud import translate
from onlineservices.Translate import Translate
from flask import jsonify

class Translator():

    def __init__(self, jsonObject):
        #print("OK")
        self.sourceLanguage=jsonObject.get("source_language_code")
        self.targetLanguage=jsonObject.get("target_language_code")
        self.jsonObject=jsonObject

    def processTranslation(self):

        tracktexts=self.jsonObject.get("tracktexts",[])
        
        #print(tracktexts)
        output={}
        translateObject=Translate()
        translations=[]
        for tracktext in tracktexts:
            tractTextTranslatedObject={}
            text=tracktext.get("sentence")
            translatedText=translateObject.getTranslatedText(self.sourceLanguage, self.targetLanguage, text)
            tractTextTranslatedObject['id']=tracktext.get("id")
            tractTextTranslatedObject['sentence']=translatedText
            translations.append(tractTextTranslatedObject)

        output["translations"]=translations
        return output

    	

       





