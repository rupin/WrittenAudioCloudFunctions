from pydub import AudioSegment
from google.cloud import storage
import requests
import io 
import os
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
		f = io.BytesIO()		
		blob = self.bucket.blob(file_path)
		blob.download_to_filename(file_path)		
		currentAudio=AudioSegment.from_file(file_path, format="mp3")
		emptyduration=starttime-(self.lastTiming+self.lastDuration)
		emptyduration=round(emptyduration,3) * 1000
		blankTrack=AudioSegment.silent(duration=emptyduration,frame_rate=frameRate)
		silentDurationEndTime=self.silentDurationStarttime+emptyduration

		if(self.audiocontainer is None):
			self.audiocontainer=blankTrack+currentAudio
		else:
			self.audiocontainer=self.audiocontainer+blankTrack+currentAudio

		self.lastTiming=starttime
		self.lastDuration=duration # dummy, but this has to be initialised by the duration of the current stream
		os.remove(file_path)

	def saveFile(self, filename):
		filename_with_extension=filename+".mp3"
		f = io.BytesIO()
		self.audiocontainer.export(f, format="mp3")		 
		blob = self.bucket.blob(filename_with_extension)		
		blob.upload_from_file(f)