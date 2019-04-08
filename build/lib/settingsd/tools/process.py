# -*- coding: utf-8 -*-

import subprocess
from os import environ

from .. import const
from .. import config
from .. import logger


##### Exceptions #####
class SubprocessFailure(Exception) :
	pass


##### Public methods #####
def execProcess(proc_args_list, proc_input = None, fatal_flag = True,
	confidential_input_flag = False, inherit_env=False, shell=False) :
	if shell and not isinstance(proc_args_list, str):
		proc_args_list = ' '.join(proc_args_list)
	logger.debug("{submod}: Executing child process \"%s\"" % (str(proc_args_list)))

	env = { "LC_ALL" : "C" }
	if inherit_env:
		env = { **environ, **env }

	proc = subprocess.Popen(proc_args_list, bufsize=1024, close_fds=True,
		stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		env=env, shell=shell)
	(proc_stdout, proc_stderr) = proc.communicate(proc_input)

	if proc.returncode != 0 :
		if proc_input == None :
			proc_input = ""
		elif confidential_input_flag and config.value(config.APPLICATION_SECTION, "log_level") != const.LOG_LEVEL_DEBUG :
			proc_input = "<CONFIDENTIAL>"
		error_text = "Error while execute \"%s\"\nStdout: %s\nStderr: %s\nStdin: %s\nReturn code: %d" % (
			str(proc_args_list), proc_stdout.strip(), proc_stderr.strip(), proc_input, proc.returncode )
		if fatal_flag :
			logger.error("{submod}: "+error_text)
			raise SubprocessFailure(error_text)

	logger.debug("{submod}: Child process \"%s\" finished, return_code=%d" % (str(proc_args_list), proc.returncode))

	return (proc_stdout, proc_stderr, proc.returncode)
