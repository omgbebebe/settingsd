import sys
import os
import dbus
import dbus.service
import dbus.glib
import gobject

import settingsd.config


if __name__ == "__main__" :
	# future config init here

	bus_name = dbus.service.BusName(settingsd.config.GlobalConfig["service_name"], bus = dbus.SessionBus())

	main_parent_class = type("MainParent", (object,), {})
	setattr(main_parent_class, "busName", lambda self : bus_name)
	main_parent = main_parent_class()

	sys.path.append("plugins")
	services_list = []
	for module_name in [ item[:-3] for item in os.listdir("plugins") if item.endswith(".py") ] :
		services_list.append(__import__(module_name, globals(), locals(), [""]).Service(main_parent))
		services_list[-1].initService()
		print "Initialized \"%s\"" % (module_name)

	main_loop = gobject.MainLoop()
	try :
		main_loop.run()
	except KeyboardInterrupt :
		for services_list_item in services_list :
			services_list_item.closeService()
			print "Closed \"%s\"" % (module_name)
		main_loop.quit()

