
from google.cloud import translate
from onlineservices.Translate import Translate
from flask import jsonify
import time
class Translator():

    def __init__(self, jsonObject):
        #print("OK")
        
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
            target_language=tracktext.get("target_language")


            t8=time.time()      
        

            translatedText=translateObject.getTranslatedText(target_language, text)
            t7=time.time()


            print("Translator Took: " +str(t7-t8))
            tractTextTranslatedObject['id']=tracktext.get("id")
            tractTextTranslatedObject['sentence']=translatedText
            translations.append(tractTextTranslatedObject)

        output["translations"]=translations
        return output

    	

       





