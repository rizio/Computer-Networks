#!/usr/bin/env python

"""
Blah

CS585 - Lab 3 - Maurizio Leo
"""
import time
import pexpect
import getpass, os

def ssh_command (user, host, password):
	"""
	"""
	ssh_newkey = 'Are you sure you want to continue connecting'
	child = pexpect.spawn('ssh -l %s %s'%(user, host))
	i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
	if i == 0: # Timeout
		print 'ERROR!'
		print 'SSH could not login. Here is what SSH said:'
		print child.before, child.after
		return None
	if i == 1: # SSH does not have the public key. Just accept it.
		child.sendline ('yes')
		child.expect ('password: ')
		i = child.expect([pexpect.TIMEOUT, 'password: '])
		if i == 0: # Timeout
			print 'ERROR!'
			print 'SSH could not login. Here is what SSH said:'
			print child.before, child.after
			return None		  
	child.sendline(password)
	print 'Login to %s successful.' % host
	return child

def start_iperf (child, srcMachine, dstMachine=None, server=True):
	"""
	"""
	if(server == True):
		print 'Starting iperf server on: %s.' % srcMachine
		child.sendline('/bin/bash -c "iperf -s > iperf_log.txt"')
	else:
		print 'Starting iperf client on: %s, to %s.' % (srcMachine, dstMachine)
		child.sendline('/bin/bash -c "iperf -c %s -i 5 > iperf_log.txt"' % dstMachine) #-t 120

def main ():
	GWAGDY = '192.168.1.110'
	GHELMY = '192.168.110.2'
	MICKEY = '192.168.110.4'
	SPOOF = '192.168.110.3'

	BARCA = '192.168.1.121'
	INTER = '192.168.121.2'
	GENOA = '192.168.121.3'
	ROMA = '192.168.121.4'

	user = 'maurizio'
	password = getpass.getpass('Password: ')

	# Start GWAGDY's iperf server
	print 'Setup Gwagdy with iperf server.'
	gwagdy = ssh_command (user, GWAGDY, password)
	start_iperf (gwagdy, GWAGDY)
	
	# Start BARCA's iperf server
	print '\nSetup Barca with iperf server.'
	barca = ssh_command (user, BARCA, password)
	start_iperf (barca, BARCA)

	# Start GHELMY's OpenTracker
	#print '\nSetup GHELMY with OpenTracker.'
	
	
	# Start GHELMY's bittornado dl/seed
	
	# Start SPOOF's bittornado dl/seed
	
	# Start INTER's bittornado dl/seed
	
	# Start GENOA's bittornado dl/seed
	
	# Start MICKEY'S iperf client
	#print 'Setup MICKEY with iperf client.'
	
	# Start ROMA's iperf client
	print '\nSetup Roma with iperf client.'	
	roma = ssh_command(user, ROMA, password)
	start_iperf (roma, ROMA, GWAGDY, False)

	raw_input("\n\nExperiment running.  Hit <Enter> to quit.\n")
	
	# TEAR DOWN
	gwagdy.close()
	barca.close()
	# ghelmy.close()
	# spoof.close()
	# inter.close()
	# genoa.close()
	# mickey.close()
	# roma.close()
	
if __name__ == '__main__':
	print "Running BitTorrent setup."
	
	try:
		main()
	except Exception, e:
		print str(e)
		os._exit(1)