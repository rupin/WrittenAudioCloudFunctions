from onlineservices.TTS import TTS
def main():
	sentence="My Name is Rupin"
	newTTSObject=TTS(TTS.SERVICE_PROVIDER_GOOGLE)
	audioStream=newTTSObject.getTTSAudio(sentence)
	exit()
