from pydub import AudioSegment
from google.cloud import storage
import requests
import io 
import os
import tempfile
import time


class AudioCombiner():
	
	def __init__(self, bucket_name):
		self.audiocontainer=AudioSegment.empty()
		self.lastTiming=0
		self.lastDuration=0
		self.silentDurationStarttime=0
		self.storage_client=storage.Client()
		self.bucket_name=bucket_name
		self.bucket = self.storage_client.get_bucket(self.bucket_name)



	def combiner(self,file_path, starttime, duration, frameRate):
		
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
		currentAudio=AudioSegment.from_file(tempFilePath, format="mp3")
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
		filename_with_extension=filename+".mp3"
		f = io.BytesIO()
		self.audiocontainer.export(f, format="mp3")		 
		blob = self.bucket.blob(filename_with_extension)
		#print(blob.__dict__)		
		blob.upload_from_file(f)
		return filename_with_extension