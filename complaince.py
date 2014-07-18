# A python script to do compliance checks on cisco configuration files

import checks
import os
from os.path import expanduser
import argparse
import getpass
import sys

from iosdevice import IOSDevice

CONFIG_LOCATION = '/data/network/configs/'
FIX_DIR = expanduser('~/fixes/')

parser = argparse.ArgumentParser(description="Compliance driver for UOW")
parser.add_argument('--check', help='The specific compliance check to run (defaults to all)')
parser.add_argument('--host', help='The specific host to run check(s) against (defaults to all)')
parser.add_argument('--generateFix', action="store_true", help='generate fix configs to the given directory')
parser.add_argument('--andFix', action='store_true', help='Perform fixes')
parser.add_argument('--checks', action='store_true', help='Shows a list of the checks avaliable and exit')
parser.add_argument('--configdir', help='Sets the directory to load the configuration from.  Defaults to %s' % CONFIG_LOCATION)
parser.add_argument('--fixdir', help='Sets the directory to store the fix commands in.  Defaults to %s' % FIX_DIR)
args = parser.parse_args()

#Perform the fixups if the defaults were over-written
if args.fixdir:
	FIX_DIR = args.fixdir
if args.configdir:
	CONFIG_LOCATION = args.configdir

def performComplianceCheck(check, succeeded, failed, args):
	for device in devices:
		check_instance = check(device, "\n".join(device.parsed_switch_config.ioscfg))
		if check_instance.checkRequired():
			if check_instance.checkSucceeded():
				succeeded.append(device)
			else:
				failed.append(device)

				if not args.generateFix:
					continue
				
				#We have a failed device.  Check to see if we can remedy this now.
				fix_commands = check_instance.fixConfig()
				if fix_commands:
					# The compliance check has generated config that should fix the issue
					filename = device.filename.split("/")[-1]
					save_directory = FIX_DIR + check.__module__

					#Create the directory to store these compliance fixes in
					if not os.path.exists(save_directory):
						os.makedirs(save_directory)
					
					file = open(save_directory + "/%s" % filename, 'w')
					file.write("! %s\n" % device.getHostname())
					file.write(fix_commands)
					file.close()


if __name__ == '__main__':
	if args.checks:
		#print out a list of checks
		for check in checks.clsmembers:
			to_print = "\"%s\"" % check.title
			if check.description:
				to_print += " - " + check.description
			print to_print
		sys.exit(0)

	if args.andFix: #ToDo:  Write this
		raise NotImplementedError
	
	#Check to see if we should only load up a single device
	devices = [] #Devices to check
	if args.host:
		devices.append(IOSDevice(CONFIG_LOCATION + "/" + args.host))
	else:
		for filename in os.listdir("/data/network/configs"):
			filename = "/data/network/configs/" + filename
			try:
				device = IOSDevice(filename)
				devices.append(device)
			except:
				print "Could not load %s" % filename
				pass 

	#Build a list of checks that we should perform
	checks_to_perform = []
	if args.check:
		for check in checks.clsmembers:
			if check.title == args.check:
				checks_to_perform.append(check)
				break
	else:
		checks_to_perform = checks.clsmembers

	#Perform the checks
	for check in checks_to_perform:
		succeeded = []
		failed = []
		performComplianceCheck(check, succeeded, failed, args)
		print check.title + " ........(%s/%s)" % (len(succeeded), len(succeeded)+len(failed) )
		if len(failed) > 0:
			for item in failed:
				print "  * %s" % item.hostname

