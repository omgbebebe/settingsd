# -*- coding: utf-8 -*-

import subprocess

from .. import logger


##### Exceptions #####
class SubprocessFailure(Exception) :
	pass


##### Public methods #####
def execProcess(args_list, input = None, fatal_flag = True) :
	logger.debug("{submod}: Executing child process \"%s\"" % (str(args_list)))

	proc = subprocess.Popen(args_list, shell=True, bufsize=1024, close_fds=True,
		stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		env={ "LC_ALL" : "C" })
	(proc_stdout, proc_stderr) = proc.communicate(input)

	if proc.returncode != 0 :
		error_text = "Error while execute \"%s\"\nStdout: %s\nStderr: %s\nReturn code: %d" % (
			str(args_list), proc_stdout.strip(), proc_stderr.strip(), proc.returncode )
		if fatal_flag :
			raise SubprocessFailure(error_text)
		logger.error("{submod}: "+error_text)

	logger.debug("{submod}: Child process \"%s\" finished, return_code=%d" % (str(args_list), proc.returncode))

	return (proc_stdout, proc_stderr, proc.returncode)

