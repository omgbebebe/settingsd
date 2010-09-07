# -*- coding: utf-8 -*-


import sys
import traceback

import const
import config


##### Public constants #####
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


##### Exceptions #####
class UnknownMessageType(Exception) :
	pass


##### Public methods #####
def message(message_type, message) :
	if message_type in (ERROR_MESSAGE, INFO_MESSAGE) :
		message_level = const.LOG_LEVEL_INFO
	elif message_type == VERBOSE_MESSAGE :
		message_level = const.LOG_LEVEL_VERBOSE
	elif message_type == DEBUG_MESSAGE :
		message_level = const.LOG_LEVEL_DEBUG
	else :
		raise UnknownMessageType("Message type \"%d\" not in list %s" % (message_type, ALL_MESSAGES_LIST))

	if message_level <= config.value(const.MY_NAME, "log_level") :
		message_level_prefixes_list = (
			"%s [ Error ]:" % (const.MY_NAME),
			"%s [ Info ]:" % (const.MY_NAME),
			"%s [ Details ]:" % (const.MY_NAME),
			"%s [ Debug ]:" % (const.MY_NAME)
		)
		print >> sys.stderr, message_level_prefixes_list[message_type], message

def attachException() :
	for line in traceback.format_exc().splitlines() :
		message(ERROR_MESSAGE, line)

