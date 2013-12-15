'''
This class implements a simple Logger which logs to a file
'''

class Logger():
	def __init__(self, fileName):	
		try:
			self.fileHandle = open(fileName, "a")
		except IOError:
			self.fileHandle = None

	def write(self, string):
		self.fileHandle.write(str(string))
	def close(self):
		self.fileHandle.close()