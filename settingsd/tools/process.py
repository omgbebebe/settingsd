# -*- coding: utf-8 -*-

import subprocess

from .. import logger


##### Exceptions #####
class SubprocessFailure(Exception) :
	pass


##### Public methods #####
def execProcess(proc_args, fatal_flag = True) :
	logger.debug("{submod}: Executing child process \"%s\"" % (proc_args))

	proc = subprocess.Popen(proc_args, shell=True, bufsize=1024, close_fds=True,
		stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		env={ "LC_ALL" : "C" })
	(proc_stdout, proc_stderr) = proc.communicate()

	if proc.returncode != 0 :
		error_text = "Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
			proc_args, proc_stdout.strip(), proc_stderr.strip(), proc.returncode )
		if fatal_flag :
			raise SubprocessFailure(error_text)
		logger.error("{submod}: "+error_text)

	logger.debug("{submod}: Child process \"%s\" finished, return_code=%d" % (proc_args, proc.returncode))

	return (proc_stdout, proc_stderr, proc.returncode)

