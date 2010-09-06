# -*- coding: utf-8 -*-


import sys

import const
import config


#####
def message(log_level, message) :
	text_log_levels_list = [
		"%s [ Info ]:" % (const.MY_NAME), # const.LOG_LEVEL_INFO == 0
		"%s [ Details ]:" % (const.MY_NAME), # const.LOG_LEVEL_VERBOSE == 1
		"%s [ Debug ]:" % (const.MY_NAME) # # const.LOG_LEVEL_DEBUG == 2
	]
	if log_level <= config.value("service", "log_level") :
		print >> sys.stderr, text_log_levels_list[log_level], message

