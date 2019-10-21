from utilities.UtilityFunctions import GenerateSingleAudio


def main(request):
	jsonObject=request.get_json()
	return GenerateSingleAudio(jsonObject)


def combineAudioFiles(request):
	jsonObject=request.get_json()




# if __name__ == "__main__":
#     from flask import Flask, request
#     app = Flask(__name__)

#     @app.route('/', methods=['POST'])
#     def index():
#         return main(request)

#     app.run('127.0.0.1', 8000, debug=True)