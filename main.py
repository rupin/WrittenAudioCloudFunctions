from onlineservices.TTS import TTS
from google.cloud import storage
import json
from io import BytesIO
import time
from flask import jsonify

from mutagen.mp3 import MP3





def main(request):
	
	#sentence="Let us Learn How to Design a PCB using Easy E D A"
	#print(request)
	jsonobject=request.get_json()
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
	bucket_name="written-audio-files"
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
	t4=time.time()
	#current_audio=AudioSegment.from_mp3(BytesIO(audioStream))	
	#output['duration']=current_audio.duration_seconds
	audio = MP3(BytesIO(audioStream))
	output['duration']=audio.info.length
	t5=time.time()
	print("Track Duration Took Calculation: " +str(t5-t4))
	#jsonreturnvalue=json.dumps(output)
	return jsonify(output)


# if __name__ == "__main__":
#     from flask import Flask, request
#     app = Flask(__name__)

#     @app.route('/', methods=['POST'])
#     def index():
#         return main(request)

#     app.run('127.0.0.1', 8000, debug=True)