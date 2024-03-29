from onlineservices.TTS import TTS
from google.cloud import storage
import json
from io import BytesIO, StringIO
import time
from flask import jsonify

from mutagen.mp3 import MP3

from utilities.AudioCombiner import AudioCombiner
from utilities.AudioCombinerWithSSML import AudioCombinerWithSSML
from utilities.Translator import Translator


from pydub import AudioSegment

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

def CombineUsingSSML(jsonobject):

	responseDict={}
	trackID=jsonobject.get("id")
	responseDict['id']=trackID
	bucket_name=jsonobject.get('bucket_name')
	trackTextArray=jsonobject.get("tracktexts")
	combinedFileName=jsonobject.get("track_file_name")
	AC=AudioCombinerWithSSML(bucket_name)
	AC.startSSMLString()
	#processed_tracks=[]
	for trackText in trackTextArray:	
		objectToBeConverted=trackText.get("convertObject")
		starttime=trackText.get('time_marker')
		sentence=objectToBeConverted.get("sentence")
			
		AC.SSMLStringCombiner(sentence,starttime)
		#fileInfo=GenerateSingleAudio(unconvertedTrackText, False)
	
	AC.endSSMLString()

	
	dataDict={}
	dataDict["filename"]=combinedFileName
	dataDict["bucket_name"]=bucket_name
	dataDict["object_id"]=trackID
	dataDict["engine_name"]=jsonobject.get('engine_name')
	dataDict["language_code"]=jsonobject.get("language_code")
	dataDict['sentence']=AC.getSSMLString()
	dataDict['is_ssml']=True
	convertedFileInfo=GenerateSingleAudio(dataDict, True)
	
	return convertedFileInfo	
			

		

		





	


def CombineFiles(jsonobject):
	responseDict={}
	trackID=jsonobject.get("id")
	responseDict['id']=trackID
	bucket_name=jsonobject.get('bucket_name')
	trackTextArray=jsonobject.get("tracktexts")
	musicFilePath=jsonobject.get("music_file_path", None)
	AC=AudioCombiner(bucket_name)
	response_json_file_name=str(trackID)

	# It is likely the execution of this code goes above 30 seconds. 
	# The django front end will time out by then, but function execution does not stop. 
	
	# The last Function call would have saved a JSON of the response.
	# Let us delete that. 

	AC.deleteJSON(response_json_file_name)

	

	processed_tracks=[]
	for trackText in trackTextArray:
		
		trackProcessed=trackText.get("processed")
		starttime=trackText.get('time_marker')
		frameRate=trackText.get('frameRate', 24000)
		file_type=trackText.get('file_type', 'mp3')

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
		AC.combiner(file_name, starttime, duration, frameRate,file_type)
		t7=time.time()
		print("Combiner Took: " +str(t7-t8))

	combinedAudioDuration=AC.getAudioDuration()
	#print(combinedAudioDuration)
	if(musicFilePath is not None):
		AC.createOverlayMusic(musicFilePath)
		AC.combineMusicWithTrack()

	responseDict['processed_tracks']=processed_tracks



	combinedFileName=jsonobject.get("track_file_name")

	
	t9=time.time()
	combined_file_name_with_extension, duration=AC.saveFile(combinedFileName)
	t10=time.time()
	print("Saving Combined File Took: " +str(t10-t9))
	responseDict['track_file_name']=combined_file_name_with_extension
	responseDict['duration']=combinedAudioDuration

	# It is likely the execution of this code goes above 30 seconds. 
	# The django front end will time out, but Google function execution does not stop. 
	# we have to save the JSON response on the Cloud storage, and access 
	# it back from the front end once the request on the front end returns
	# a 503 Timeout Error.
	# The Code always overwrites the file, so the results are of the most recent file
	# We also delete the file at the start of the Function call. 

	
	
	savedJSONFileName=AC.saveJSONResponse(response_json_file_name,responseDict)
	#print(savedJSONFileName)
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
	file_type=jsonobject.get('file_type', 'mp3')
	extension='.wav'
	if(file_type=='mp3'):
		extension='.mp3'
	filename_with_extension=filename+extension


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
	output['duration']=0
	t4=time.time()
	if(file_type=='wav'):
		current_audio=AudioSegment.from_wav(BytesIO(audioStream))	
		output['duration']=current_audio.duration_seconds
	if(file_type=='mp3'):
		audio = MP3(BytesIO(audioStream))
		output['duration']=audio.info.length
	t5=time.time()
	print("Track Duration Took Calculation: " +str(t5-t4))
	#jsonreturnvalue=json.dumps(output)
	if(returnJson):
		return jsonify(output)
	else:
		return output

def Translate(jsonobject):
	output={}
	TranslatorObject=Translator(jsonobject)
	translatedDict=TranslatorObject.processTranslation()
	return jsonify(translatedDict)
