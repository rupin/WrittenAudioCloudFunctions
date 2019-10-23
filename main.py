from utilities.UtilityFunctions import GenerateSingleAudio, CombineFiles
#from utilities.UtilityFunctions import  CombineFilesWithFFMPEG
from flask import jsonify

def main(request):
	jsonObject=request.get_json()
	return GenerateSingleAudio(jsonObject)


def combineAudioFiles(request):
	jsonObject=request.get_json()
	return CombineFiles(jsonObject)

# def FFMPEGCombiner(request):
# 	jsonObject=request.get_json()
# 	return CombineFilesWithFFMPEG(jsonObject)




# if __name__ == "__main__":
# 	from flask import Flask, request
# 	app = Flask(__name__)

# 	@app.route('/', methods=['POST'])
# 	def index():
# 	    return main(request)

# 	@app.route('/combine', methods=['POST'])
# 	def combine():
# 	    return combineAudioFiles(request)
# 	app.run('127.0.0.1', 8080, debug=True)