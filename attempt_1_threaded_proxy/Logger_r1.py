'''
This class implements a simple Logger which logs to a file
'''

class Logger():
	def __init__(self, fileName, alreadyOpen = False):	
		try:
			if alreadyOpen == False:
				self.fileHandle = open(fileName, "a")
			elif alreadyOpen == True:
				self.fileHandle = fileName
		except IOError:
			self.fileHandle = None

	def write(self, string):
		self.fileHandle.write(str(string))
	def close(self):
		self.fileHandle.close()