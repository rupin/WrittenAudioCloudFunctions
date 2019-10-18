from onlineservices.TTS import TTS
from google.cloud import storage
from pydub import AudioSegment
import json
from io import BytesIO





def main(request):
	bucket_name="written-audio-files"
	#sentence="Let us Learn How to Design a PCB using Easy E D A"
	print(request)
	jsonobject=request.get_json()
	newTTSObject=TTS()
	audioStream=newTTSObject.convertTTSGoogle(jsonobject)
	filename=jsonobject.get('filename')
	filename_with_extension=filename+".mp3"


	# Instantiates a client
	storage_client = storage.Client()
	bucket = storage_client.get_bucket(bucket_name) 
	blob = bucket.blob(filename_with_extension)
	blob.upload_from_string(audioStream)
	output={}
	output['file_url']='https://storage.cloud.google.com/'+bucket_name+'/'+filename_with_extension
	current_audio=AudioSegment.from_mp3(BytesIO(audioStream))	
	output['duration']=current_audio.duration_seconds
	jsonreturnvalue=json.dumps(output)
	return jsonreturnvalue


# if __name__ == "__main__":
#     from flask import Flask, request
#     app = Flask(__name__)

#     @app.route('/', methods=['POST'])
#     def index():
#         return main(request)

#     app.run('127.0.0.1', 8000, debug=True)