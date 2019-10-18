
from google.cloud import texttospeech


class TTS():
	
	def convertTTSGoogle(self, engtext):
		#print(engtext)

		#return

		# Instantiates a client
		client = texttospeech.TextToSpeechClient()

		# Set the text input to be synthesized
		synthesis_input = texttospeech.types.SynthesisInput(text=engtext)

		# Build the voice request, select the language code ("en-US") and the ssml
		# voice gender ("neutral")
		voice = texttospeech.types.VoiceSelectionParams(
		    language_code='en-IN',
		    ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE,
		    name= "en-IN-Wavenet-A")

		# Select the type of audio file you want returned
		audio_config = texttospeech.types.AudioConfig(
		    audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16, # this gets a WAV file
		    effects_profile_id=["large-home-entertainment-class-device"],)

		# Perform the text-to-speech request on the text input with the selected
		# voice parameters and audio file type
		response = client.synthesize_speech(synthesis_input, voice, audio_config)
		return response.audio_content