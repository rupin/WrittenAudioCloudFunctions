from pydub import AudioSegment
from google.cloud import storage
import requests
from io import BytesIO,StringIO
import os
import io
import tempfile
import time
from mutagen.mp3 import MP3


import json

class AudioCombiner():
	
	def __init__(self, bucket_name):
		self.audiocontainer=AudioSegment.empty()
		self.lastTiming=0
		self.lastDuration=0
		self.silentDurationStarttime=0
		self.storage_client=storage.Client()
		self.bucket_name=bucket_name
		self.bucket = self.storage_client.get_bucket(self.bucket_name)



	def combiner(self,file_path, starttime, duration, frameRate, file_format='mp3'):
		
		#fileStream=requests.get(file_path)
		#print(fileStream.__dict__)
		tmpdir=tempfile.gettempdir() # prints the current temporary directory
		tempFilePath=tmpdir+"/"+file_path
		#print(tempFilePath)	
		blob = self.bucket.blob(file_path)
		ta=time.time()

		blob.download_to_filename(tempFilePath)

		tb=time.time()
		print("Downloading File Took: " +str(tb-ta))


		ta=time.time()
		currentAudio=AudioSegment.from_file(tempFilePath, format=file_format)
		tb=time.time()
		print("Load AudioSegment: " +str(tb-ta))
		emptyduration=starttime-(self.lastTiming+self.lastDuration)
		emptyduration=round(emptyduration,3) * 1000
		ta=time.time()
		blankTrack=AudioSegment.silent(duration=emptyduration,frame_rate=frameRate)
		tb=time.time()
		print("Creating a Blank file Took: " +str(tb-ta))
		silentDurationEndTime=self.silentDurationStarttime+emptyduration

		ta=time.time()

		if(self.audiocontainer is None):
			self.audiocontainer=blankTrack+currentAudio
		else:
			self.audiocontainer=self.audiocontainer+blankTrack+currentAudio
		tb=time.time()

		print("Appending Took: " +str(tb-ta))
		self.lastTiming=starttime
		self.lastDuration=duration # dummy, but this has to be initialised by the duration of the current stream
		os.remove(tempFilePath)

	def saveFile(self, filename):
		
		extension='.mp3'

		filename_with_extension=filename+extension
		f = io.BytesIO()
		self.audiocontainer.export(f, format="mp3")
		track_audio = MP3(f)
		duration=track_audio.info.length	 
		blob = self.bucket.blob(filename_with_extension)
		#print(blob.__dict__)		
		blob.upload_from_file(f)
		return filename_with_extension, duration

	def saveJSONResponse(self, filename, responseDict):
		
		extension='.json'

		filename_with_extension=filename+extension
		f = io.BytesIO()
		jsonData = json.dumps(responseDict)
		binaryData = jsonData.encode()
		f.write(binaryData)
		f.seek(0) # This was important to get the reading position to the first byte	
			 
		blob = self.bucket.blob(filename_with_extension)	
		
		blob.upload_from_file(f)

		return filename_with_extension



	def deleteJSON(self,filename):
		extension='.json'
		filename_with_extension=filename+extension
			 
		blob = self.bucket.blob(filename_with_extension)	
		if(blob.exists()):
			blob.delete()
			print("Stale JSON Response Deleted")

		

