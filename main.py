from utilities.UtilityFunctions import GenerateSingleAudio, CombineFiles
from flask import jsonify

def main(request):
	jsonObject=request.get_json()
	return GenerateSingleAudio(jsonObject)


def combineAudioFiles(request):
	jsonObject=request.get_json()
	data = subprocess.Popen(['ls', '-l', filename], stdout = subprocess.PIPE)

	output = data.communicate()
	return CombineFiles(jsonObject)

def ffmpegcombiner(request):
	import subprocess 
	import os 
	data = subprocess.Popen(['ffmpeg'])
	output = data.communicate()
	return output




if __name__ == "__main__":
	from flask import Flask, request
	app = Flask(__name__)

	@app.route('/', methods=['POST'])
	def index():
	    return main(request)

	@app.route('/combine', methods=['POST'])
	def combine():
	    return ffmpegcombiner(request)
	app.run('127.0.0.1', 8080, debug=True)