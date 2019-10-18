from onlineservices.TTS import TTS
def main(request):
	sentence="My Name is Rupin"
	newTTSObject=TTS('GOOG')
	audioStream=newTTSObject.convertTTSGoogle(sentence)
	print('Completed')