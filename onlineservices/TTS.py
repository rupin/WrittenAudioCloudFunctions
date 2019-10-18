
from google.cloud import texttospeech


class TTS():
	
	def convertTTSGoogle(self, configuration):

		sentence = configuration.get('sentence')		
		language_code=configuration.get('language_code')
		engine_name=configuration.get('engine_name')


		# Instantiates a client
		client = texttospeech.TextToSpeechClient()

		# Set the text input to be synthesized
		synthesis_input = texttospeech.types.SynthesisInput(text=sentence)

		# Build the voice request, select the language code ("en-US") and the ssml
		# voice gender ("neutral")
		voice = texttospeech.types.VoiceSelectionParams(
		    language_code=language_code,
		    ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE,
		    name=engine_name)

		# Select the type of audio file you want returned
		audio_config = texttospeech.types.AudioConfig(
		    audio_encoding=texttospeech.enums.AudioEncoding.MP3, # this gets a MP3 file
		    effects_profile_id=["large-home-entertainment-class-device"],)

		# Perform the text-to-speech request on the text input with the selected
		# voice parameters and audio file type
		response = client.synthesize_speech(synthesis_input, voice, audio_config)
		return response.audio_content