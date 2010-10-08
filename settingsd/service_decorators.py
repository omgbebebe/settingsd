# -*- coding: utf-8 -*-


import dbus
import dbus.service
import dbus.glib

import const
import config
import dbus_tools
import logger


##### Private decorators #####
def tracer(function, statics_list=[0]) :
	def wrapper(self, *args_list, **kwargs_dict) :
		if config.value(config.APPLICATION_SECTION, "log_level") == const.LOG_LEVEL_DEBUG :
			logger.debug("%s%s %s::%s" % ( "    "*statics_list[0],
				str((function.__dict__.has_key("_dbus_is_method") and "Called method") or
					(function.__dict__.has_key("_dbus_is_signal") and "Emited signal")),
				self._object_path, dbus_tools.joinMethod(function._dbus_interface, function.__name__) ))

			statics_list[0] += 1
			try :
				return_value = function(self, *args_list, **kwargs_dict)
			except :
				logger.attachException()
				raise
			finally :
				statics_list[0] -= 1

			logger.debug("%s... executed as %s::%s(%s, %s) --> %s" % ( "    "*statics_list[0],
				self.__class__.__name__, function.__name__, str(args_list), str(kwargs_dict),  str(return_value) ))

			return return_value
		else :
			try :
				return function(self, *args_list, **kwargs_dict)
			except :
				logger.attachException()
				raise

	wrapper.__name__ = function.__name__
	wrapper.__dict__ = function.__dict__
	wrapper.__doc__ = function.__doc__

	return wrapper


##### Public decorators #####
def customMethod(interface_name, **kwargs_dict) :
	def decorator(function) :
		return tracer(dbus.service.method(interface_name, **kwargs_dict)(function))
	return decorator

def functionMethod(interface_name, **kwargs_dict) :
	def decorator(function) :
		return customMethod(dbus_tools.joinMethod(config.value(config.APPLICATION_SECTION, "service_name"),
			"functions", interface_name), **kwargs_dict)(function)
	return decorator

def actionMethod(interface_name, **kwargs_dict) :
	def decorator(function) :
		return customMethod(dbus_tools.joinMethod(config.value(config.APPLICATION_SECTION, "service_name"),
			"actions", interface_name), **kwargs_dict)(function)
	return decorator

###

def customSignal(interface_name) :
	def decorator(function) :
		return tracer(dbus.service.signal(interface_name)(function))
	return decorator

def functionSignal(interface_name) :
	def decorator(function) :
		return customSignal(dbus_tools.joinMethod(config.value(config.APPLICATION_SECTION, "service_name"),
			 "functions", interface_name))(function)
	return decorator

def actionSignal(interface_name) :
	def decorator(function) :
		return customSignal(dbus_tools.joinMethod(config.value(config.APPLICATION_SECTION, "service_name"),
			"actions", interface_name))(function)
	return decorator

