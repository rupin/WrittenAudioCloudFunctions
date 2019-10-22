from onlineservices.TTS import TTS
from google.cloud import storage
import json
from io import BytesIO
import time
from flask import jsonify

from mutagen.mp3 import MP3

from utilities.AudioCombiner import AudioCombiner

def CombineFiles(jsonobject):
	trackID=jsonobject.get("id")
	bucket_name=jsonobject.get('bucket_name')
	trackTextArray=jsonobject.get("tracktexts")
	AC=AudioCombiner(bucket_name)
	for trackText in trackTextArray:

		trackProcessed=trackText.get("processed")
		starttime=trackText.get('time_marker')
		frameRate=trackText.get('frameRate', 24000)

		if(trackProcessed):
			file_name=trackText.get('file_name')
			file_url=trackText.get('audio_file')
			duration=trackText.get('duration')			
			
		else:
			unconvertedTrackText=trackText.get("convertObject")
			fileInfo=GenerateSingleAudio(unconvertedTrackText, False)
			file_name=fileInfo.get("file_name")
			duration=fileInfo.get("duration")
		t8=time.time()
		AC.combiner(file_name, starttime, duration, frameRate)
		t7=time.time()
		print("Combiner Took: " +str(t7-t8))


	combinedFileName="track_"+trackID
	t9=time.time()
	AC.saveFile(combinedFileName)
	t10=time.time()
	print("Saving Combined File Took: " +str(t10-t9))
	return "abcd"


		






def GenerateSingleAudio(jsonobject, returnJson=True):	
	
	newTTSObject=TTS()
	t0=time.time()
	audioStream=newTTSObject.convertTTSGoogle(jsonobject)
	t1=time.time()
	print("TTS Took: " +str(t1-t0))
	newTTSObject=None

	filename=jsonobject.get('filename')
	filename_with_extension=filename+".mp3"


	# Instantiates a client
	t2=time.time()
	storage_client = storage.Client()
	bucket_name=jsonobject.get('bucket_name')
	bucket = storage_client.get_bucket(bucket_name) 
	blob = bucket.blob(filename_with_extension)
	blob.upload_from_string(audioStream)
	t3=time.time()
	print("Storage Took: " +str(t3-t2))

	storage_client=None
	bucket=None
	blob=None

	output={}	

	output['file_url']='https://storage.cloud.google.com/'+bucket_name+'/'+filename_with_extension
	output['file_name']=filename_with_extension
	t4=time.time()
	#current_audio=AudioSegment.from_mp3(BytesIO(audioStream))	
	#output['duration']=current_audio.duration_seconds
	audio = MP3(BytesIO(audioStream))
	output['duration']=audio.info.length
	t5=time.time()
	print("Track Duration Took Calculation: " +str(t5-t4))
	#jsonreturnvalue=json.dumps(output)
	if(returnJson):
		return jsonify(output)
	else:
		return output