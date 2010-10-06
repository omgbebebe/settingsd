# -*- coding: utf-8 -*-


import sys
import traceback
import syslog

import const
import config


##### Public constants #####
ERROR_MESSAGE = (0, syslog.LOG_ERR, const.LOG_LEVEL_INFO)
WARNING_MESSAGE = (1, syslog.LOG_WARNING, const.LOG_LEVEL_INFO)
NOTICE_MESSAGE = (2, syslog.LOG_NOTICE, const.LOG_LEVEL_INFO)
INFO_MESSAGE = (3, syslog.LOG_INFO, const.LOG_LEVEL_INFO)
VERBOSE_MESSAGE = (4, syslog.LOG_INFO, const.LOG_LEVEL_VERBOSE)
DEBUG_MESSAGE = (5, syslog.LOG_INFO, const.LOG_LEVEL_DEBUG) # syslog.LOG_DEBUG

ALL_MESSAGES_LIST = (
	ERROR_MESSAGE,
	INFO_MESSAGE,
	NOTICE_MESSAGE,
	WARNING_MESSAGE,
	VERBOSE_MESSAGE,
	DEBUG_MESSAGE
)


##### Exceptions #####
class UnknownMessageType(Exception) :
	pass


##### Private methods #####
def log(message_type, message) :
	if not message_type in ALL_MESSAGES_LIST :
		raise UnknownMessageType("Message type \"%d\" not in list %s" % (message_type, ALL_MESSAGES_LIST))

	if message_type[2] <= config.value(config.APPLICATION_SECTION, "log_level") :
		use_colors_flag = sys.stderr.isatty() and config.value(config.APPLICATION_SECTION, "log_use_colors")
		message_type_texts_list = (
			( "\033[31m Error \033[0m" if use_colors_flag else " Error " ),
			( "\033[33mWarning\033[0m" if use_colors_flag else "Warning" ),
			( "\033[32mNotice \033[0m" if use_colors_flag else "Notice " ),
			( "\033[32m Info  \033[0m" if use_colors_flag else " Info  " ),
			( "\033[36mDetails\033[0m" if use_colors_flag else "Details" ),
			" Debug "
		)

		for message_list_item in message.split("\n") :
			message_list_item = "[ %s ]: %s" % (message_type_texts_list[message_type[0]], message_list_item)
			print >> sys.stderr, message_list_item
			if config.value(config.RUNTIME_SECTION, "use_syslog") :
				syslog.syslog(message_type[1], message_list_item)


##### Public methods #####
def error(message) :
	log(ERROR_MESSAGE, message)

def info(message) :
	log(INFO_MESSAGE, message)

def notice(message) :
	log(NOTICE_MESSAGE, message)

def warning(message) :
	log(WARNING_MESSAGE, message)

def verbose(message) :
	log(VERBOSE_MESSAGE, message)

def debug(message) :
	log(DEBUG_MESSAGE, message)

def attachException(message_type = ERROR_MESSAGE) :
	for line in traceback.format_exc().splitlines() :
		log(message_type, line)

