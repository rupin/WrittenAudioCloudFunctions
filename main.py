from onlineservices.TTS import TTS
from google.cloud import storage






def main(request):
	sentence="Let us Learn How to Design a PCB using Easy E D A"
	newTTSObject=TTS()
	audioStream=newTTSObject.convertTTSGoogle(sentence)
	# Instantiates a client
	storage_client = storage.Client()
	bucket = storage_client.get_bucket('written-audio-files') 
	blob = bucket.blob('animals-1.wav')
	blob.upload_from_string(audioStream)

	#print('Completed')

#main('abc')