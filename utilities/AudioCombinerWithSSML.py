from pydub import AudioSegment
from google.cloud import storage
import requests
from io import BytesIO
import os
import io
import tempfile
import time
from mutagen.mp3 import MP3

from onlineservices.TTS import TTS


class AudioCombinerWithSSML():
	
	def __init__(self, bucket_name):
		self.SSMLString=""
		self.lastTiming=0
		self.lastDuration=0
		self.silentDurationStarttime=0
		self.storage_client=storage.Client()
		self.bucket_name=bucket_name
		self.bucket = self.storage_client.get_bucket(self.bucket_name)


	def startSSMLString(self):
		self.SSMLString="<speak><seq>"
		self.SSMLString=self.SSMLString+"<media xml:id='startnode' begin='0s'><speak>A</speak></media>"


	def getSSMLString(self):
		return self.SSMLString


	def SSMLStringCombiner(self, text, starttime):

		
		SSMLNode="<media begin='startnode.end+"+str(starttime)+"s'>"
		SSMLNode=SSMLNode+"<speak>"
		SSMLNode=SSMLNode+text
		SSMLNode=SSMLNode+"</speak></media>"
		
		self.SSMLString=self.SSMLString+SSMLNode


	def endSSMLString(self):
		self.SSMLString=self.SSMLString+"</seq></speak>"

	
		

		



	