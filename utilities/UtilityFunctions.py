from onlineservices.TTS import TTS
from google.cloud import storage
import json
from io import BytesIO
import time
from flask import jsonify

from mutagen.mp3 import MP3

from utilities.AudioCombiner import AudioCombiner
#from utilities.FFMPEGCombiner import FFMPEGCombiner


# def CombineFilesWithFFMPEG(jsonobject):
# 	trackID=jsonobject.get("id")
# 	bucket_name=jsonobject.get('bucket_name')
# 	trackTextArray=jsonobject.get("tracktexts")
# 	AC=FFMPEGCombiner(bucket_name)
# 	for trackText in trackTextArray:

# 		trackProcessed=trackText.get("processed")
# 		starttime=trackText.get('time_marker')
# 		frameRate=trackText.get('frameRate', 24000)

# 		if(trackProcessed):
# 			file_name=trackText.get('file_name')
# 			file_url=trackText.get('audio_file')
# 			duration=trackText.get('duration')			
			
# 		else:
# 			unconvertedTrackText=trackText.get("convertObject")
# 			fileInfo=GenerateSingleAudio(unconvertedTrackText, False)
# 			file_name=fileInfo.get("file_name")
# 			duration=fileInfo.get("duration")
# 		t8=time.time()
# 		AC.CacheFile(file_name, starttime, duration, frameRate)
# 		t7=time.time()
# 		print("Cacher Took: " +str(t7-t8))


# 	combinedFileName="track_"+trackID
# 	AC.generateCombinedFile(combinedFileName)
# 	AC.SaveOutputFileToBucket(combinedFileName)
# 	return 'abcd'


	


def CombineFiles(jsonobject):
	responseDict={}
	trackID=jsonobject.get("id")
	responseDict['id']=trackID
	bucket_name=jsonobject.get('bucket_name')
	trackTextArray=jsonobject.get("tracktexts")
	AC=AudioCombiner(bucket_name)
	processed_tracks=[]
	for trackText in trackTextArray:
		
		trackProcessed=trackText.get("processed")
		starttime=trackText.get('time_marker')
		frameRate=trackText.get('frameRate', 24000)

		if(trackProcessed):
			file_name=trackText.get('file_name')
			file_url=trackText.get('audio_file')
			duration=trackText.get('duration')			
			
		else:
			processed_track_dict={}
			unconvertedTrackText=trackText.get("convertObject")
			fileInfo=GenerateSingleAudio(unconvertedTrackText, False)
			
			file_name=fileInfo.get("file_name")
			duration=fileInfo.get("duration")


			processed_track_dict["id"]=unconvertedTrackText.get("object_id")
			processed_track_dict["file_name"]=file_name
			processed_track_dict["duration"]=duration
			processed_track_dict["file_url"]=fileInfo.get("file_url")
			processed_tracks.append(processed_track_dict)
			

		t8=time.time()
		AC.combiner(file_name, starttime, duration, frameRate)
		t7=time.time()
		print("Combiner Took: " +str(t7-t8))

		

	responseDict['processed_tracks']=processed_tracks



	combinedFileName=jsonobject.get("track_file_name")

	
	t9=time.time()
	combined_file_name_with_extension=AC.saveFile(combinedFileName)
	t10=time.time()
	print("Saving Combined File Took: " +str(t10-t9))
	responseDict['track_file_name']=combined_file_name_with_extension
	#responseDict['track_file_name']=saved_combined_file
	return jsonify(responseDict)


		






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
