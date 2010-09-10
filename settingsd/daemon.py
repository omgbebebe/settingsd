# -*- coding: utf-8 -*-


import os
import signal
import errno
import resource

import logger


##### Private methods #####
def pidOfPythonProc(proc_name, uid = 0) :
	for proc_list_item in os.listdir("/proc") :
		try :
			proc_pid = int(proc_list_item)
		except :
			continue

		cmdline_file_path = os.path.join("/proc", proc_list_item, "cmdline")
		if os.stat(cmdline_file_path).st_mode != uid :
			continue

		cmdline_file = open(cmdline_file_path)
		cmdline_list = cmdline_file.read().split("\0")

		if len(cmdline_list) >= 2 and os.path.basename(cmdline_list[1]) == proc_name :
			cmdline_file.close()
			return proc_pid

		cmdline_file.close()
	return None

def maxFd() :
	max_fd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
	if max_fd == resource.RLIM_INFINITY :
		max_fd = 1024

	try :
		max_fd = os.sysconf("SC_OPEN_MAX")
	except ValueError :
		pass

	if max_fd < 0 :
		max_fd = 1024

	return max_fd

def closeFd(fd, retries_count = 5) :
	for count in xrange(retries_count) :
		try :
			os.close(fd)
		except OSError, err1 :
			if err1.errno != errno.EBADF :
				continue
		break


##### Public methods #####
def startDaemon(init_function, close_function, work_dir_path = None, umask = None) :
	pid = os.fork()
	if pid > 0 :
		try :
			os.waitpid(pid, 0)
		except OSError :
			pass
		os._exit(0)
	elif pid == 0 :
		logger.verbose("First fork() to %d as session lead" % (os.getpid()))

		os.setsid()
		pid = os.fork()
		if pid > 0 :
			os._exit(0)
		elif pid == 0 :
			logger.verbose("Second fork() to %d as main process" % (os.getpid()))

			if work_dir_path != None :
				os.chdir(work_dir_path)
				logger.verbose("New working directory: %s" % (work_dir_path))
			if umask != None :
				os.umask(umask)
				logger.verbose("Accapted new umask: %.3o" % (umask))

			for fd in xrange(maxFd()) :
				closeFd(fd)
			null_fd = os.open("/dev/null", os.O_RDWR)
			for fd in (0, 1, 2) :
				os.dup2(null_fd, fd)

			try :
				init_function()
			except (SystemExit, KeyboardInterrupt) :
				close_function()
			except :
				try :
					close_function()
				except :
					pass
				os._exit(1) # FIXME
		else :
			os._exit(1) # FIXME
	else :
		os._exit(1) # FIXME

def killDaemon() :
	pid = pidOfPythonProc("main.py", os.getuid()) # FIXME
	if pid != None :
		os.kill(pid, signal.SIGTERM)
	else :
		logger.error("Cannot determine a daemon process of \"%s\"" % ("main.py")) # FIXME

