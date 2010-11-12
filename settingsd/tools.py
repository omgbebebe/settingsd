# -*- coding: utf-8 -*-


import subprocess

import logger


##### Exceptions #####
class SubprocessFailure(Exception) :
	pass


##### Public methods #####
def execProcess(proc_args) :
	logger.debug("{submod}: Executing child process \"%s\"" % (proc_args))
	proc = subprocess.Popen(proc_args, shell=True, bufsize=1024, close_fds=True,
		stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		env={ "LC_ALL" : "C" })
	(proc_stdout, proc_stderr) = proc.communicate()
	logger.debug("{submod}: Child process \"%s\" finished, return_code=%d" % (proc_args, proc.returncode))

	return (proc_stdout, proc_stderr, proc.returncode)

