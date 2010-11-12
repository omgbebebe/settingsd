# -*- coding: utf-8 -*-


import sys
import traceback
import syslog
import inspect
import time

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


ALL_MESSAGES_TEXTS_LIST = (
	(" Error ", "\033[31m Error \033[0m"),
	("Warning", "\033[33mWarning\033[0m"),
	("Notice ", "\033[32mNotice \033[0m"),
	(" Info  ", "\033[32m Info  \033[0m"),
	("Details", "\033[36mDetails\033[0m"),
	(" Debug ", " Debug ")
)


MODULE_CALLER_NAME_TAG = "{mod}"
SUBMODULE_CALLER_NAME_TAG = "{submod}"
CURRENT_TIME_TAG = "{time}"

ALL_TAGS_LIST = (
	MODULE_CALLER_NAME_TAG,
	SUBMODULE_CALLER_NAME_TAG,
	CURRENT_TIME_TAG
)


##### Exceptions #####
class UnknownMessageType(Exception) :
	pass


##### Private methods #####
def log(message_type, message) :
	if not message_type in ALL_MESSAGES_LIST :
		raise UnknownMessageType("Message type \"%s\" not in list %s" % (str(message_type), ALL_MESSAGES_LIST))

	if message_type[2] <= config.value(config.APPLICATION_SECTION, "log_level") :
		for all_tags_list_item in ALL_TAGS_LIST :
			if all_tags_list_item == MODULE_CALLER_NAME_TAG :
				try :
					message = message.replace(MODULE_CALLER_NAME_TAG,
						inspect.getmodule(inspect.currentframe().f_back.f_back).__name__)
				except : pass
			elif all_tags_list_item == SUBMODULE_CALLER_NAME_TAG :
				try :
					message = message.replace(SUBMODULE_CALLER_NAME_TAG,
						inspect.getmodule(inspect.currentframe().f_back.f_back.f_back).__name__)
				except : pass
			elif all_tags_list_item == CURRENT_TIME_TAG :
				message = message.replace(CURRENT_TIME_TAG, time.ctime())

		colored_index = int(sys.stderr.isatty() and config.value(config.APPLICATION_SECTION, "log_use_colors"))
		for message_list_item in message.split("\n") :
			print >> sys.stderr, "[ %s ] %s" % (ALL_MESSAGES_TEXTS_LIST[message_type[0]][colored_index], message_list_item)
			if config.value(config.RUNTIME_SECTION, "use_syslog") :
				syslog.syslog(message_type[1], "[ %s ] %s" % (ALL_MESSAGES_TEXTS_LIST[message_type[0]][0], message_list_item))


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

###

def attachException(message_type = ERROR_MESSAGE) :
	for line in traceback.format_exc().splitlines() :
		log(message_type, line)

