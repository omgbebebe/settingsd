#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import syslog
import getopt

from settingsd import const
from settingsd import validators
from settingsd import application
from settingsd import daemon


##### Private methods #####
def help() :
	print ( "Usage: %s [options]\n"
		"Options:\n"
		"\t-h, --help -- Print this text\n"
		"\t-v, --version -- Print version and license info\n"
		"\t--log-level=<0|1|2> -- Log level, replace value from config\n"
		"\t--use-syslog=<yes|no> -- Force enable or disable useage of syslog\n"
		"\t--bus-type=<system|session> -- Use system or session bus, replace value from config\n"
		"\t-d, --daemon -- Run application as daemon, by default using interactive mode\n"
		"\t-s, --status -- Check status of daemon\n"
		"\t-k, --kill -- Kill daemon process" % (const.MY_NAME) )

def version() :
	print "%s version %s-%s, functionality_level=%d" % (const.MY_NAME, const.VERSION, const.VERSION_STATUS, const.FUNCTIONALITY_LEVEL)


##### Main #####
if __name__ == "__main__" :
	log_level = None
	use_syslog_flag = None
	bus_type = None
	daemon_mode_flag = False

	try :
		(opts_list, args_list) = getopt.getopt(sys.argv[1:], "hdsk", ( "help", "version",
			"log-level=", "use-syslog=", "bus-type=", "daemon", "status", "kill" ))

		for (opts_list_item, args_list_item) in opts_list :
			if opts_list_item in ("-h", "--help") :
				help()
				sys.exit(0)

			elif opts_list_item in ("-v", "--version") :
				version()
				sys.exit(0)

			elif opts_list_item in ("--log-level",) :
				try :
					log_level = validators.common.validRange(int(args_list_item), const.ALL_LOG_LEVELS_LIST)
				except Exception, err1 :
					print "Incorrect option \"%s\": %s" % (opts_list_item, str(err1))
					sys.exit(1)

			elif opts_list_item in ("--use-syslog",) :
				try :
					use_syslog_flag = validators.common.validBool(args_list_item)
				except Exception, err1 :
					print "Incorrect option \"%s\": %s" % (opts_list_item, str(err1))
					sys.exit(1)

			elif opts_list_item in ("--bus-type",) :
				try :
					bus_type = validators.common.validRange(args_list_item, const.ALL_BUS_TYPES_LIST)
				except Exception, err1 :
					print "Incorrect option \"%s\": %s" % (opts_list_item, str(err1))
					sys.exit(1)

			elif opts_list_item in ("-d", "--daemon") :
				daemon_mode_flag = True

			elif opts_list_item in ("-s", "--status") :
				try :
					sys.exit(abs(daemon.daemonStatus()))
				except Exception, err1 :
					print "Daemon status error: %s" % (str(err1))
					sys.exit(1)

			elif opts_list_item in ("-k", "--kill") :
				try :
					sys.exit(abs(daemon.killDaemon()))
				except Exception, err1 :
					print "Daemon kill error: %s" % (str(err1))
					sys.exit(1)

			else :
				print "Unknown option \"%s\"" % (opts_list_item)
	except Exception, err1 :
		print "Bad command line options: %s" % (str(err1))

	#####

	application.Application(log_level, use_syslog_flag, bus_type, daemon_mode_flag).run()

