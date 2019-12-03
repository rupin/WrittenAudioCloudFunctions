from pydub import AudioSegment
from google.cloud import storage
import requests
from io import BytesIO,StringIO
import os
import io
import tempfile
import time
from mutagen.mp3 import MP3
import math

import json

class AudioCombiner():
	
	def __init__(self, bucket_name):
		self.audiocontainer=AudioSegment.empty()
		self.musiccontainer=None
		self.lastTiming=0
		self.lastDuration=0
		self.silentDurationStarttime=0
		self.storage_client=storage.Client()
		self.bucket_name=bucket_name
		self.bucket = self.storage_client.get_bucket(self.bucket_name)		
		self.AudioMarkers=[]
		self.track_duration=None



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
		audioMarker={}
		audioMarker["start"]=round(starttime*1000,3)
		audioMarker["end"]=round(audioMarker["start"]+duration*1000,3)
		audioMarker["type"]="A"
		

		#Calculate the Empty Duration
		emptyduration=starttime-(self.lastTiming+self.lastDuration)
		emptyduration=round(emptyduration,3) * 1000
		# the blank track starts at this time.
		
		#Create the Blank Track
		ta=time.time()
		blankTrack=AudioSegment.silent(duration=emptyduration,frame_rate=frameRate)
		tb=time.time()


		print("Creating a Blank file Took: " +str(tb-ta))

		silentMarker={}
		#We wish to add music only if the silent duration is greater than 
		#3 seconds/3000 milliseconds


	
		blankTrackStartTime=round((self.lastTiming+self.lastDuration)*1000,3)
		silentMarker["start"]=blankTrackStartTime

		silentMarker["end"]=round(blankTrackStartTime+emptyduration,3)
		silentMarker["duration"]=round(emptyduration,3)
		silentMarker["type"]="S"
		self.AudioMarkers.append(silentMarker)

		
		self.AudioMarkers.append(audioMarker)

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



	def createOverlayMusic(self,music_file_path, attenuation=25):
		fadeDuration=1500
		tmpdir=tempfile.gettempdir() # prints the current temporary directory
		tempFilePath=tmpdir+"/"+music_file_path
		#print(tempFilePath)	
		blob = self.bucket.blob(music_file_path)
		ta=time.time()

		blob.download_to_filename(tempFilePath)

		tb=time.time()
		print("Downloading Music Overlay File Took: " +str(tb-ta))


		ta=time.time()


		self.musiccontainer=AudioSegment.from_file(tempFilePath, format="mp3")


		musicfileDuration=self.musiccontainer.duration_seconds
		if(self.track_duration>musicfileDuration):
			factor=math.ceil(self.track_duration/musicfileDuration)
			self.musiccontainer=self.musiccontainer*factor #duplicate the music file
			self.musiccontainer=(self.musiccontainer[0:self.track_duration*1000]) # trim any excess
			musicfileDuration=self.musiccontainer.duration_seconds
		
		modifiedMusicRef=None
		
		lastEndTime=0
		for audioMark in self.AudioMarkers:
			print(audioMark)
			marktype=audioMark['type']
			markStart=lastEndTime
			markEnd=audioMark['end']
			duration=audioMark.get('duration',0)
			# initialSegment=musicFileRef[markStart:markStart+transition]
			# middleSegment=musicFileRef[markStart+transition:markEnd-transition]
			# finalSegment=musicFileRef[markEnd-transition:markEnd]
			segment=self.musiccontainer[markStart:markEnd]
			if(marktype=='S'):#needs the total duration greater than 2000
				#initialSegment=initialSegment*
				#pass
				#segment=self.musiccontainer[markStart:markEnd]
				if(duration>4000):
					segment=segment.fade_in(fadeDuration).fade_out(fadeDuration)
				else:
					# If the duration of the silence
					# is less than 4000 milliseconds, just keep the music volume low
					# it is as good as assuming the spoke audio is running
					# This makes small transitions sound less jarring
					segment=segment-attenuation
			    
			elif(marktype=='A'):
				
				segment=segment-attenuation
			     
			if(modifiedMusicRef is None):
				modifiedMusicRef=segment
			else:
				modifiedMusicRef=modifiedMusicRef+segment

			lastEndTime=markEnd

		#modifiedMusicRef=modifiedMusicRef

		#segment=self.musiccontainer[endTime]

		self.musiccontainer=modifiedMusicRef
			
			

	def getAudioDuration(self):
		self.track_duration=self.audiocontainer.duration_seconds
		return self.track_duration

	def combineMusicWithTrack(self):
		ta=time.time()
		self.audiocontainer=self.audiocontainer.overlay(self.musiccontainer) 
		tb=time.time()
		print("Combining Music with Audio took: " +str(tb-ta))


	def saveFile(self, filename):
		
		extension='.mp3'

		filename_with_extension=filename+extension
		f = io.BytesIO()
		self.audiocontainer.export(f, format="mp3")
		track_audio = MP3(f)


		if(self.track_duration is None):
			duration=track_audio.info.length
		else:
			duration=self.track_duration

		f.seek(0)
			 
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

		

