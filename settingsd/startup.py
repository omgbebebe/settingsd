# -*- coding: utf-8 -*-

import sys
import os
import signal
import syslog

import const
import config
import logger
import application
import daemon


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
			raise

		if self._bus_type != None :
			config.setValue(config.APPLICATION_SECTION, "bus_type", self._bus_type)

		if self._log_level != None :
			config.setValue(config.APPLICATION_SECTION, "log_level", self._log_level)

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
			raise

		try :
			signal.signal(signal.SIGTERM, self.quit)
			signal.signal(signal.SIGQUIT, self.quit)
		except :
			logger.error("signal() error")
			logger.attachException()

		try :
			self._app.runLoop()
		except (SystemExit, KeyboardInterrupt) :
			self.quit()
		except :
			logger.error("Runtime error, trying to close services")
			logger.attachException()
			self.quit()
			raise

	def runDaemon(self) :
		work_dir_path = ( "/" if os.getuid() == 0 else None )
		umask = ( 077 if os.getuid() == 0 else None )
		daemon.startDaemon(self.runInteractive, work_dir_path, umask)


	### Handlers ###

	def quit(self, signum = None, frame = None) :
		if signum != None :
			logger.info("Recieved signal %d, closing..." % (signum))

		self._app.closeServices()
		self._app.quitLoop()
		logger.info("Closed")

