# -*- coding: utf-8 -*-

import os
import ConfigParser

import const
import config


#####
ConfigDictObject = {
	"service" : {
		"name" : (const.DEFAULT_CONFIG_SERVICE_NAME, str, None),
		"path" : (const.DEFAULT_CONFIG_SERVICE_PATH, str, None),
		"bus_type" : (const.DEFAULT_CONFIG_SERVICE_BUS_TYPE, str, const.CONFIG_VALID_SERVICE_BUS_TYPES_LIST)
	}
}


#####
class ValidatorError(Exception) :
	pass

class ValueError(Exception) :
	pass


##### Public #####
def setValue(section, option, value, validator = None, valid_values_list = None) :
	global ConfigDictObject

	if not ConfigDictObject.has_key(section) :
		ConfigDictObject[section] = {}

	if ConfigDictObject[section].has_key(option) :
		validator = ConfigDictObject[section][option][1]
		valid_values_list = ConfigDictObject[section][option][2]

	if valid_values_list != None and not value in valid_values_list :
		raise ValueError("Option \"%s::%s = %s\" not in list %s" % (section, option, value, valid_values_list))
	if validator != None :
		try :
			value = validator(value)
		except Exception, err1 :
			raise ValidatorError("Incorrect option \"%s::%s = %s\" by validator \"%s\": %s" % (
				section, option, value, validator.__name__, str(err1) ))

	ConfigDictObject[section][option] = (value, validator, valid_values_list)

def value(section, option) :
	return ConfigDictObject[section][option][0]

def validator(section, option) :
	return ConfigDictObject[section][option][1]

def validValues(section, option) :
	return ConfigDictObject[section][option][2]

def loadConfigFiles() :
	for config_files_list_item in os.listdir(const.CONFIGS_DIR) :
		if not config_files_list_item.endswith(const.CONFIG_FILE_POSTFIX) :
			continue

		config_parser = ConfigParser.ConfigParser()
		config_parser.read(os.path.join(const.CONFIGS_DIR, config_files_list_item))

		for section in config_parser.sections() :
			for option in config_parser.options(section):
				setValue(section, option, config_parser.get(section, option))

	print ConfigDictObject

