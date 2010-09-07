# -*- coding: utf-8 -*-


import sys

import const
import config


#####
ERROR_MESSAGE = 0
INFO_MESSAGE = 1
VERBOSE_MESSAGE = 2
DEBUG_MESSAGE = 3

ALL_MESSAGES_LIST = (
	ERROR_MESSAGE,
	INFO_MESSAGE,
	VERBOSE_MESSAGE,
	DEBUG_MESSAGE
)


#####
class UnknownMessageType(Exception) :
	pass


#####
def message(message_type, message) :
	if message_type in (ERROR_MESSAGE, INFO_MESSAGE) :
		log_level = const.LOG_LEVEL_INFO
	elif message_type == VERBOSE_MESSAGE :
		log_level = const.LOG_LEVEL_VERBOSE
	elif message_type == DEBUG_MESSAGE :
		log_level = const.LOG_LEVEL_DEBUG
	else :
		raise UnknownMessageType("Message type \"%d\" not in list %s" % (message_type, ALL_MESSAGES_LIST))

	if log_level <= config.value(const.MY_NAME, "log_level") :
		text_log_levels_list = (
			"%s [ Info ]:" % (const.MY_NAME),
			"%s [ Details ]:" % (const.MY_NAME), 
			"%s [ Debug ]:" % (const.MY_NAME)
		)

		print >> sys.stderr, text_log_levels_list[log_level], message

