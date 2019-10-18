from onlineservices.TTS import TTS
def main():
	newTTSObject=TTS(TTS.SERVICE_PROVIDER_GOOGLE)
	audioStream=newTTSObject.getTTSAudio(sentence)
