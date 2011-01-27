# -*- coding: utf-8 -*-


import os
import re
import shutil


##### Exceptions #####
class NotAssociated(Exception) :
	pass

class AlreadyAssociated(Exception) :
	pass


##### Public classes #####
class PlainEditor(object) :
	def __init__(self, delimiter = "=", spaces_list = ["\\s"], quotes_list= ["\"", "\'"], comments_list = ["#"]) :
		object.__init__(self)

		#####

		self.__delimiter = delimiter
		self.__spaces_list = list(spaces_list)
		self.__quotes_list = list(quotes_list)
		self.__comments_list = list(comments_list)

		#####

		self.__config_file_path = None
		self.__config_file_data_list = None

		###

		spaces = ( "[%s]*" % ("".join(self.__spaces_list)) if len(self.__spaces_list) > 0 else "" )
		comments = "".join(self.__comments_list)

		self.__comments_regexp = re.compile(r"%s(?<!\\)[%s]%s" % (spaces, comments, spaces))
		self.__variable_regexp = re.compile(r"%s%s%s" % (spaces, self.__delimiter, spaces))


	### Public ###

	def open(self, config_file_path, sample_config_file_path = None) :
		if self.__config_file_path != None :
			raise AlreadyAssociated("This parser already associated with config \"%s\"" % self.__config_file_path)

		if not os.access(config_file_path, os.F_OK) :
			if sample_config_file_path != None and os.access(sample_config_file_path, os.F_OK) :
				shutil.copy2(sample_config_file_path, config_file_path)
			else :
				open(config_file_path, "w").close()

		config_file = open(config_file_path, "r")
		self.__config_file_data_list = config_file.read().split("\n")
		self.__config_file_path = config_file_path
		try :
			config_file.close()
		except : pass

	def save(self) :
		if self.__config_file_path == None :
			raise NotAssociated("This parser is not associated with config")

		config_file = open(self.__config_file_path, "w")
		config_file.write("\n".join(self.__config_file_data_list))
		try :
			config_file.close()
		except : pass

	def close(self) :
		if self.__config_file_path == None :
			raise NotAssociated("This parser is not associated with config")

		self.__config_file_data_list = None
		self.__config_file_path = None

	###

	def setValue(self, variable_name, values_list) :
		if self.__config_file_path == None :
			raise NotAssociated("This parser is not associated with config")

		if not type(values_list).__name__ in ("list", "tuple") :
			values_list = [values_list]

		last_variable_index = len(self.__config_file_data_list) - 1
		count = 0
		while count < len(self.__config_file_data_list) :
			variable = self.__comments_regexp.split(self.__config_file_data_list[count].strip(), 1)[0]
			variable_parts_list = self.__variable_regexp.split(variable, 1)

			if variable_parts_list[0] == variable_name :
				self.__config_file_data_list.pop(count)
				last_variable_index = count
			else :
				count += 1

		space = ( " " if len(self.__spaces_list) > 0 else "" )
		quote = ( self.__quotes_list[0] if len(self.__quotes_list) > 0 else "" )

		for count in xrange(len(values_list)) :
			variable = variable_name + space + self.__delimiter + space + quote + str(values_list[count]) + quote
			self.__config_file_data_list.insert(last_variable_index + count, variable)

	def value(self, variable_name) :
		if self.__config_file_path == None :
			raise NotAssociated("This parser is not associated with config")

		values_list = []
		for config_file_data_list_item in self.__config_file_data_list :
			variable = self.__comments_regexp.split(config_file_data_list_item.strip(), 1)[0]
			variable_parts_list = self.__variable_regexp.split(variable, 1)

			if variable_parts_list[0] == variable_name :
				if len(variable_parts_list) > 1 :
					value = variable_parts_list[1]
					for quotes_list_item in self.__quotes_list :
						if len(value) > 2 and value[0] == value[-1] == quotes_list_item :
							value = value[1:-1]
					values_list.append(value)
				else :
					values_list.append("")

		return values_list

