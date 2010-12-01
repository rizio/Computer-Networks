#!/usr/bin/env python

"""
Blah

CS585 - Lab 3 - Maurizio Leo
"""
import time
import pexpect
import getpass, os

GWAGDY = '192.168.1.110'
GHELMY = '192.168.110.2'
MICKEY = '192.168.110.4'
SPOOF = '192.168.110.3'

BARCA = '192.168.1.121'
INTER = '192.168.121.2'
GENOA = '192.168.121.3'
ROMA = '192.168.121.4'

# FILENAME = 'testVideo.avi'
# TORRENT_FILENAME = 'testVideo.avi.torrent'

FILENAME = 'ubuntu.iso'
TORRENT_FILENAME = 'ubuntu.iso.torrent'


def ssh_command (user, host, password):
	"""
	SSH into 'host' with password 'password'.
	This method will handle logging in to a machine where keys have not been exchanged.
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
	This method starts iperf on the child.
	"""
	if(server == True):
		print 'Starting iperf server on: %s.' % srcMachine
		child.sendline('/bin/bash -c "iperf -s > iperf_log.txt"')
	else:
		print 'Starting iperf client on: %s, to %s.' % (srcMachine, dstMachine)
		child.sendline('/bin/bash -c "iperf -c %s -i 5 -t 320 > iperf_log.txt"' % dstMachine)

def start_opentracker (child, host):
	"""
	Start the OpenTracker BitTorrent tracker on 'host'.
	You must be a super user to call this method.
	"""
	print 'Starting OpenTracker on %s.' % host
	child.sendline('/bin/bash -c "./opentracker -i %s -P 6969 -p 6969"' % host)

def start_bittorrent (child, host, deletePreviousDownload=False):
	"""
	Start headless BitTornado to download / seed the torrent file.
	This method will remove the previously downloaded torrent file if deletePreviousDownload = True
	"""
	if deletePreviousDownload:
		child.sendline('rm %s' % FILENAME)

	print 'BitTornado downloading/seeding %s on %s.' % (TORRENT_FILENAME, host)
	child.sendline('btdownloadheadless %s' % TORRENT_FILENAME)
	

def become_su(child, password):
	"""
	Call this method to elevate the current user to superuser.
	"""
	print 'Becoming superuser.'
	child.sendline('sudo su -')
	i = child.expect([pexpect.TIMEOUT, '(.*?) password for (.*?):', 'root@(.*)'], timeout=5)
	if i == 0:
		print 'Error becoming superuser.'
		print child.before, child.after
		return None
	if i == 1:
		child.sendline(password)
		print 'Password entered.'
	if i == 2:
		print 'Password already entered.'
		return None

def main ():

	user = 'maurizio'
	password = getpass.getpass('Password: ')

	# TODO: Need to kill OpenTracker somehow
	# TODO: Login problems on first connect?

	# --
	# Start GWAGDY's iperf server
	# --
	print '[GWAGDY]: start iperf server'
	gwagdy = ssh_command (user, GWAGDY, password)
	start_iperf (gwagdy, GWAGDY)
	
	# Start BARCA's iperf server
	print '\n[BARCA]: Start iperf server'
	barca = ssh_command (user, BARCA, password)
	start_iperf (barca, BARCA)

	# --
	# Start GHELMY's OpenTracker
	# --
	print '\n[GHELMY]: start OpenTracker.'
	ghelmy = ssh_command(user, GHELMY,  password)
	become_su(ghelmy,  password)
	ghelmy.sendline('cd opentracker')
	start_opentracker(ghelmy, GHELMY)
	
	# Wait a sec before starting seeding
	time.sleep(2)
	
	# -- 
	# Start GHELMY's bittornado seeding
	# --
	print '\n[GHELMY]: start seeding torrent file.'
	ghelmy_torrent = ssh_command(user, GHELMY,  password)

	if ghelmy_torrent:
		start_bittorrent(ghelmy_torrent, GHELMY)
	else:
		print 'Could not connect to Ghelmy.'
	
	time.sleep(1)
	
	# --
	# Start SPOOF's bittornado dl/seed
	# --
	print '\n[SPOOF]: start downloading torrent.'
	spoof = ssh_command(user, SPOOF, password)

	if spoof:
		start_bittorrent(spoof, SPOOF)
	else:
		print 'Could not connect to Spoof.'

	# --
	# Start INTER's bittornado dl/seed
	# --
	print '\n[INTER]: start downloading torrent.'
	inter = ssh_command(user, INTER, password)

	if inter:
		start_bittorrent(inter, INTER)
	else:
		print 'Could not connect to InterMilan.'

	# --	
	# Start GENOA's bittornado dl/seed
	# --
	print '\n[GENOA]: start downloading torrent.'
	genoa = ssh_command(user, GENOA, password)

	if genoa:
		start_bittorrent(genoa, GENOA)
	else:
		print 'Could not connect to Genoa.'

	# --	
	# Start MICKEY'S iperf client
	# --
	print '\n[MICKEY]: start iperf client.'
	mickey = ssh_command(user, MICKEY, password)
	start_iperf (mickey, MICKEY, BARCA, False)
	
	# --	
	# Start ROMA's iperf client
	# --
	print '\n[ROMA]: start iperf client.'	
	roma = ssh_command(user, ROMA, password)
	start_iperf (roma, ROMA, GWAGDY, False)

	print('-------------------------------------------')
	raw_input("\n\nExperiment running.  Hit <Enter> to quit.\n")
	print('-------------------------------------------')
	
	# --
	# TEAR DOWN
	# --

	gwagdy.close()
	barca.close()
	ghelmy.close()
	ghelmy_torrent.close()
	spoof.close()
	inter.close()
	genoa.close()
	mickey.close()
	roma.close()
	
if __name__ == '__main__':
	print "Running BitTorrent setup."
	
	try:
		main()
	except Exception, e:
		print str(e)
		os._exit(1)