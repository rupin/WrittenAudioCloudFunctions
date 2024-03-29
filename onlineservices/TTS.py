
from google.cloud import texttospeech


class TTS():
	
	def convertTTSGoogle(self, configuration):

		sentence = configuration.get('sentence')
		#print(sentence)		
		language_code=configuration.get('language_code')
		engine_name=configuration.get('engine_name')
		ssml=configuration.get('is_ssml', False)
		audio_speed=configuration.get('audio_speed', 1)
		audio_pitch=configuration.get('audio_pitch', 1)
		file_type=configuration.get('file_type', 'mp3')
		#print(engine_name)
		#print(ssml)
		# Instantiates a client
		client = texttospeech.TextToSpeechClient()

		if(not ssml):

			# Set the text input to be synthesized
			print("Not SSML")
			synthesis_input = texttospeech.types.SynthesisInput(text=sentence)
		else:
			print("Is SSML")
			synthesis_input = texttospeech.types.SynthesisInput(ssml=sentence)

		# Build the voice request, select the language code ("en-US") and the ssml
		# voice gender ("neutral")
		voice = texttospeech.types.VoiceSelectionParams(
		    language_code=language_code,
		    name=engine_name)

		# Select the type of audio file you want returned
		encoding=texttospeech.enums.AudioEncoding.LINEAR16 # this gets a WAV file
		if(file_type=='mp3'):
			encoding=texttospeech.enums.AudioEncoding.MP3 # this gets a MP3 file

		audio_config = texttospeech.types.AudioConfig(
		    audio_encoding=encoding, 
		    effects_profile_id=["large-home-entertainment-class-device"],
		    speaking_rate=audio_speed,
		    pitch=audio_pitch
		    )

		# Perform the text-to-speech request on the text input with the selected
		# voice parameters and audio file type
		response = client.synthesize_speech(synthesis_input, voice, audio_config)
		return response.audio_content