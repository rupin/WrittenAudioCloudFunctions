from pydub import AudioSegment
from google.cloud import storage
import requests
import io 
import os
import tempfile
import time
import subprocess



class FFMPEGCombiner():
	
	def __init__(self, bucket_name):
		self.audiocontainer=AudioSegment.empty()
		self.lastTiming=0
		self.lastDuration=0
		self.silentDurationStarttime=0
		self.storage_client=storage.Client()
		self.bucket_name=bucket_name
		self.bucket = self.storage_client.get_bucket(self.bucket_name)
		self.blank_file_index=0 
		self.output_file_path=''
		self.file_list=[]

	def CacheFile(self,file_path, starttime, duration, frameRate):
		
		#fileStream=requests.get(file_path)
		#print(fileStream.__dict__)
		tmpdir=tempfile.gettempdir() # prints the current temporary directory
		tempFilePath=tmpdir+"/"+file_path
		#print(tempFilePath)	
		blob = self.bucket.blob(file_path)
		ta=time.time()

		blob.download_to_filename(tempFilePath)

		tb=time.time()
		print("Downloading File Took: " +str(tb-ta))

		
		
		emptyduration=starttime-(self.lastTiming+self.lastDuration)
		emptyduration=round(emptyduration,3) * 1000
		if(emptyduration>0):
	
			blankTrack=AudioSegment.silent(duration=emptyduration,frame_rate=frameRate)		
			blank_file_with_extension="blank_"+str(self.blank_file_index)+".mp3"
			blankFilePath=tmpdir+"/"+blank_file_with_extension
			blankTrack.export(blankFilePath, format="mp3")	
			self.file_list.append(blankFilePath)
			self.blank_file_index=self.blank_file_index+1
		
		self.file_list.append(tempFilePath)		
		silentDurationEndTime=self.silentDurationStarttime+emptyduration		
		self.lastTiming=starttime
		self.lastDuration=duration # dummy, but this has to be initialised by the duration of the current stream
		self.blank_file_index=self.blank_file_index+1
		

	

	def generateCombinedFile(self, filename):
		tmpdir=tempfile.gettempdir() # prints the current temporary directory

		txt_file_name=filename+".txt"
		txt_file_path=tmpdir+"/"+txt_file_name

		output_file_name=filename+".mp3"
		output_file_path=tmpdir+"/"+output_file_name
		self.output_file_path=output_file_path


		with open(txt_file_path,"w+") as txtfile:
			for input_file in self.file_list:			

				line="file '"+input_file+"'"
				txtfile.write(line)
				txtfile.write("\n")
			txtfile.close()

  		
		#file_string="|".join(self.file_list)
		args_list=[]
		args_list.append('ffmpeg')
		args_list.append('-safe')
		args_list.append('0')
		args_list.append('-f')
		args_list.append('concat')
		args_list.append("-i")
		args_list.append(txt_file_path)
		args_list.append("-c")
		args_list.append("copy")
		args_list.append(output_file_path)
		args_list.append("-y")		
			
		
		#Use ffmpeg for 
		subprocess.Popen(args_list,stderr=subprocess.STDOUT)

		
		#os.remove(txt_file_path)	

	def SaveOutputFileToBucket(self, filename):
		filename_with_extension=filename+".mp3"		 
		blob = self.bucket.blob(filename_with_extension)
		print(self.output_file_path)		
		blob.upload_from_filename(self.output_file_path)
		#os.remove(self.output_file_path)

				


