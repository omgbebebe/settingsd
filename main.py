import sys
import os
import dbus
import dbus.service
import dbus.glib
import gobject

from settingsd import const
from settingsd import config


if __name__ == "__main__" :
	config.loadConfigFiles()

	if config.value("service", "bus_type") == const.CONFIG_SERVICE_BUS_TYPE_SYSTEM :
		bus = dbus.SystemBus()
	else :
		bus = dbus.SessionBus()
	bus_name = dbus.service.BusName(config.value("service", "name"), bus = bus)
	config.setValue("runtime", "bus_name", bus_name)

	sys.path.append(const.PLUGINS_DIR)
	services_list = []
	for module_name in [ item[:-3] for item in os.listdir(const.PLUGINS_DIR) if item.endswith(".py") ] :
		services_list.append(__import__(module_name, globals(), locals(), [""]).Service())
		services_list[-1].initService()

	main_loop = gobject.MainLoop()
	print >> sys.stderr, "Initialized"
	try :
		main_loop.run()
	except KeyboardInterrupt :
		for services_list_item in services_list :
			services_list_item.closeService()
		main_loop.quit()
	print >> sys.stderr, "\nClosed"

