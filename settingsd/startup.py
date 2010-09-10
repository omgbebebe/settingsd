# -*- coding: utf-8 -*-

import sys
import signal
import syslog

import const
import config
import logger
import application
#import daemon # TODO


##### Public classes #####
class Startup(object) :
	def __init__(self, log_level, use_syslog_flag, bus_type, daemon_mode_flag) :
		object.__init__(self)

		#####

		self._log_level = log_level
		self._use_syslog_flag = use_syslog_flag
		self._bus_type = bus_type
		self._daemon_mode_flag = daemon_mode_flag

		#####

		self._app = application.Application()


	### Public ###

	def run(self) :
		self.prepare()
		if self._daemon_mode_flag :
			self.runDaemon()
		else :
			self.runInteractive()


	### Private ###

	def prepare(self) :
		if self._use_syslog_flag == None :
			if self._daemon_mode_flag :
				syslog.openlog(const.MY_NAME, syslog.LOG_PID, syslog.LOG_DAEMON)
				config.setValue(config.RUNTIME_SECTION, "use_syslog", True)
		else :
			syslog.openlog(const.MY_NAME, syslog.LOG_PID, ( syslog.LOG_DAEMON if self._daemon_mode_flag else syslog.LOG_USER ))
			config.setValue(config.RUNTIME_SECTION, "use_syslog", True)

		try :
			self._app.loadApplicationConfigs()
		except :
			logger.error("Initialization error")
			logger.attachException()
			sys.exit(1)

		if self._bus_type != None :
			config.setValue(config.APPLICATION_SECTION, "bus_type", self._bus_type)

		if self._log_level != None :
			config.setValue(config.APPLICATION_SECTION, "log_level", self._log_level)

	###

	def runInteractive(self) :
		try :
			self._app.loadModules()
			self._app.loadServicesConfigs()
			self._app.initBus()
			self._app.initServices()
			logger.info("Initialized")
		except :
			logger.error("Initialization error")
			logger.attachException()
			sys.exit(1)

		try :
			self._app.runLoop()
		except (SystemExit, KeyboardInterrupt) :
			try :
				self._app.closeServices()
			except :
				logger.error("Critical error on services closing, abort all processes and go boom")
			self._app.quitLoop()
			logger.info("Closed")
		except :
			logger.error("Runtime error, trying to close services")
			logger.attachException()
			try :
				self._app.closeServices()
			except :
				logger.error("Critical error on services closing, abort all processes and go boom")
			self._app.quitLoop()
			logger.error("Closed")
			sys.exit(1)

	def runDaemon(self) :
		print "TODO" # TODO

