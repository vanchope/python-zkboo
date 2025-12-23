import time

def check_time(func, msg='', repetitions = 1000):
	time1 = time.time()
	for i in range(repetitions):
		func(i)
	time2 = time.time()
	print('"%s" - done %d repetitions in %f sec.' % (msg, repetitions, (time2-time1) ) )

class RunTimeMeasure:
	def __init__(self):
		self.time_start = None
		self.time_stop = None
		self.restart()

	def restart(self):
		self.time_start = time.time()

	def stop(self):  # returns time in sec.
		self.time_stop = time.time()
		return self.time_stop - self.time_start

	def debug_check_time(self, text):
		print('|DEBUG TIME| {} = {} sec.'.format(text, self.stop()))


global_time1 = RunTimeMeasure()