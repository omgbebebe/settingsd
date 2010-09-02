import os
import ConfigParser

import const
import config


ConfigDictObject = {
	"service" : {
		"name" : const.DEFAULT_CONFIG_SERVICE_NAME,
		"path" : const.DEFAULT_CONFIG_SERVICE_PATH,
		"bus_type" : (const.DEFAULT_CONFIG_SERVICE_BUS_TYPE, const.CONFIG_VALID_SERVICE_BUS_TYPES_LIST)
	}
}


class ValueError(Exception) :
	pass


def setValue(section, option, value) :
	global ConfigDictObject

	if not ConfigDictObject.has_key(section) :
		ConfigDictObject[section] = {}

	if ConfigDictObject[section].has_key(option) and ConfigDictObject[section][option].__class__.__name__ == "tuple" :
		if not value in ConfigDictObject[section][option][1] :
			raise ValueError("Argument of \"%s :: %s\" \"%s\" not in list %s" % (
				section, option, value, str(ConfigDictObject[section][option][1] )))
		ConfigDictObject[section][option] = (value, ConfigDictObject[section][option][1])
	else :
		ConfigDictObject[section][option] = value

def value(section, option) :
	if ConfigDictObject[section][option].__class__.__name__ == "tuple" :
		return ConfigDictObject[section][option][0]
	return ConfigDictObject[section][option]

def validValues(section, option) :
	if ConfigDictObject[section][option].__class__.__name__ == "tuple" :
		return ConfigDictObject[section][option][1]
	return None


def loadConfigFiles() :
	for config_files_list_item in os.listdir(const.CONFIGS_DIR) :
		if not config_files_list_item.endswith(const.CONFIG_FILE_POSTFIX) :
			continue

		config_parser = ConfigParser.ConfigParser()
		config_parser.read(os.path.join(const.CONFIGS_DIR, config_files_list_item))

		for section in config_parser.sections() :
			for option in config_parser.options(section):
				setValue(section, option, config_parser.get(section, option))

