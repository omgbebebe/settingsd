# -*- coding: utf-8 -*-


import sys
import os
import signal
import errno
import resource

import const
import logger


##### Private methods #####
def pidsListOfPythonProc(proc_name, without_options_list = [], uid = 0) :
	proc_name = os.path.basename(proc_name)

	proc_pids_list = []
	for proc_list_item in os.listdir("/proc") :
		try :
			proc_pid = int(proc_list_item)
		except :
			continue

		cmdline_file_path = os.path.join("/proc", proc_list_item, "cmdline")
		if os.stat(cmdline_file_path).st_uid != uid :
			continue

		cmdline_file = open(cmdline_file_path)
		cmdline_list = cmdline_file.read().split("\0")
		try :
			cmdline_file.close()
		except : pass

		if len(cmdline_list) >= 2 and os.path.basename(cmdline_list[1]) == proc_name :
			ignore_flag = False
			for without_options_list_item in without_options_list :
				if without_options_list_item in cmdline_list :
					ignore_flag = True
					break
			if not ignore_flag :
				proc_pids_list.append(proc_pid)
	return proc_pids_list

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
def startDaemon(function, work_dir_path = None, umask = None) :
	pid = os.fork()
	if pid > 0 :
		try :
			os.waitpid(pid, 0)
		except OSError :
			pass
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

			function()

def killDaemon() :
	pids_list = pidsListOfPythonProc(sys.argv[0], ["-k", "--kill"], os.getuid())
	if len(pids_list) != 0 :
		for pids_list_item in pids_list :
			os.kill(pids_list_item, signal.SIGTERM)
			logger.info("SIGTERM has been sended to %s process \"%s\" with pid \"%d\"" % (
				const.MY_NAME, os.path.basename(sys.argv[0]), pids_list_item ))
		return 0
	else :
		logger.error("Cannot determine a %s daemon process of \"%s\"" % (const.MY_NAME, os.path.basename(sys.argv[0])))
		return -1

def daemonStatus() :
	pids_list = pidsListOfPythonProc(sys.argv[0], ["-s", "--status"], os.getuid())
	if len(pids_list) != 0 :
		for pids_list_item in pids_list :
			logger.info("%s daemon has been founded with pid \"%d\"" % (const.MY_NAME, pids_list_item))
		return 0
	else :
		logger.error("Cannot determine a %s daemon process of \"%s\"" % (const.MY_NAME, os.path.basename(sys.argv[0])))
		return -1

