# -*- coding: utf-8 -*-


import os
import ConfigParser

import const
import config
import validators


##### Public constants #####
APPLICATION_SECTION = const.MY_NAME
RUNTIME_SECTION = "runtime"

ALL_SECTIONS_LIST = (
	APPLICATION_SECTION,
	RUNTIME_SECTION
)


##### Private objects #####
ConfigDictObject = {
	APPLICATION_SECTION : {
		"service_name" : (const.DEFAULT_SERVICE_NAME, str),
		"service_path" : (const.DEFAULT_SERVICE_PATH, str),
		"bus_type" : (const.DEFAULT_BUS_TYPE, ( lambda arg : validators.validRange(arg, const.ALL_BUS_TYPES_LIST) )),
		"log_level" : (const.DEFAULT_LOG_LEVEL, ( lambda arg : validators.validRange(int(arg), const.ALL_LOG_LEVELS_LIST) )),
		"log_use_colors" :(const.DEFAULT_LOG_USE_COLORS_FLAG, validators.validBool)
	},
	RUNTIME_SECTION : {
		"bus_name" : (None, None),
		"use_syslog" : (False, None)
	}
}


##### Public methods #####
def setValue(section, option, value, validator = None) :
	global ConfigDictObject

	if not ConfigDictObject.has_key(section) :
		ConfigDictObject[section] = {}

	if ConfigDictObject[section].has_key(option) :
		validator = ConfigDictObject[section][option][1]

	if validator != None :
		try :
			value = validator(value)
		except Exception, err1 :
			raise validators.ValidatorError("Incorrect config option \"%s :: %s = %s\": %s" % (section, option, value, str(err1)))

	ConfigDictObject[section][option] = (value, validator)

def value(section, option) :
	return ConfigDictObject[section][option][0]

def validator(section, option) :
	return ConfigDictObject[section][option][1]

def loadConfigs(only_sections_list = (), exclude_sections_list = ()) :
	only_sections_list = list(only_sections_list)
	exclude_sections_list = list(exclude_sections_list)
	exclude_sections_list.append(RUNTIME_SECTION)

	for config_files_list_item in os.listdir(const.CONFIGS_DIR) :
		if not config_files_list_item.endswith(const.CONFIG_FILE_POSTFIX) :
			continue

		config_parser = ConfigParser.ConfigParser()
		config_parser.read(os.path.join(const.CONFIGS_DIR, config_files_list_item))

		for section in config_parser.sections() :
			if (len(only_sections_list) != 0 and not section in only_sections_list) or section in exclude_sections_list :
				continue

			for option in config_parser.options(section):
				setValue(section, option, config_parser.get(section, option))

