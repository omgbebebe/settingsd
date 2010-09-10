# -*- coding: utf-8 -*-


import sys
import syslog
import getopt

from settingsd import const
from settingsd import validators
from settingsd import startup
#from settingsd import daemon # TODO


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
		"\t-k, --kill -- Kill daemon process" % (const.MY_NAME) )

def version() :
	print "%s version %s" % (const.MY_NAME, const.VERSION)


##### Main ######
if __name__ == "__main__" :
	log_level = None
	use_syslog_flag = None
	bus_type = None
	daemon_mode_flag = False

	try :
		(opts_list, args_list) = getopt.getopt(sys.argv[1:], "hdk", ( "help", "version",
			"log-level=", "use-syslog=", "bus-type=", "daemon", "kill" ))

		for (opts_list_item, args_list_item) in opts_list :
			if opts_list_item in ("-h", "--help") :
				help()

			elif opts_list_item in ("-v", "--version") :
				version()

			elif opts_list_item in ("--log-level") :
				try :
					log_level = validators.validRange(int(args_list_item), const.ALL_LOG_LEVELS_LIST)
				except Exception, err1 :
					print "Incorrect option \"%s\": %s" % (opts_list_item, str(err1))
					sys.exit(1)

			elif opts_list_item in ("--use-syslog") :
				try :
					use_syslog_flag = validators.validBool(args_list_item)
				except Exception, err1 :
					print "Incorrect option \"%s\": %s" % (opts_list_item, str(err1))

			elif opts_list_item in ("--bus-type") :
				try :
					bus_type = validators.validRange(args_list_item, const.ALL_BUS_TYPES_LIST)
				except Exception, err1 :
					print "Incorrect option \"%s\": %s" % (opts_list_item, str(err1))
					sys.exit(1)

			elif opts_list_item in ("-d", "--daemon") :
				daemon_mode_flag = True

			elif opts_list_item in ("-k", "--kill") :
				pass # TODO

			else :
				print "Unknown option \"%s\"" % (opts_list_item)
	except Exception, err1 :
		print "Bad command line options: %s" % (str(err1))

	#####

	startup_proc = startup.Startup(log_level, use_syslog_flag, bus_type, daemon_mode_flag)
	startup_proc.run()

