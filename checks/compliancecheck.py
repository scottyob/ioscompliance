class ComplianceCheck:

	title = "Unknown compliance check"
	description = None
	
	def __init__(self, ios_device, config):
		self.ios_device = ios_device
		self.config = config

	def checkRequired(self):
		"""
		Returns a boolean determining if the given device is required to be checked for compliance
		"""
		return False

	def checkSucceeded(self):
		"""
		Returns a boolean to determine if the compliance check checks out
		"""
		return True

	def fixConfig(self):
		"""
		If this script can automatically correct the compliance issue, this command is used to return the generated config to run on the device.
		"""
		return None

	def checkFixCommands(self):
		"""
		If this script can do a check to see if the fix block succeeded, place it here
		"""
		return None

	def checkFixResults(self, results):
		"""
		If this script can check to see if the fix block succeeded, the output of running the checks on the router is fed back into this function.  The function should return a boolean on the success value
		"""
		return True

