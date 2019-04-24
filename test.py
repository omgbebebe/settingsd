from unittest import TestCase, main
from pprint import pprint as pp
from dbus import SystemBus
import os, sys


SEPARATOR = "\n" + "-"*30 + "\n"

list_ = ["common_info", "date_time", "dnsmasq_config", "example",
 "local_groups", "local_users", "network", "nss_roles",
  "ntp_config", "package_updates", "rtorrentd_config", "ssl",
   "statistics", "system_services"]

class TestSettingsdMain():
        def __init__(self, *args, **kwargs):
                self.dbus = SystemBus()
                self.log_file = open("test_log.log", "w")

        def test_interactive(self):
                for module_name in list_:
                        #### auto 
                        print("Module name: %s\nWant to run all methods of this module automatically? (y/n)" % module_name)
                        auto = False
                        confirmaion = input()
                        if confirmaion == "y":
                                auto = True

                        remote_object = dbus.get_object("org.etersoft.settingsd", "/org/etersoft/settingsd/functions/{}".format(module_name))
                        remote_object.Introspect()
                        for method_name, args in remote_object.__dict__['_introspect_method_map'].items():
                                if method_name.rsplit(".", 1)[1] == "Introspect":
                                        continue
                                if auto:
                                        if args != "" and args !=" ":
                                                print("Test with arguments:", ".".join((method_name.rsplit(".", 3)[1:])), args)
                                                print( "\nProceed test? (y/n)")
                                                confirmaion = input()
                                                if confirmaion == "y":
                                                        print("Argument(%d) types: " % len(args), *args)
                                                        print("Enter arguments:\n")
                                                        in_args = input().split()
                                                        try:
                                                                print("Output: ", remote_object.__getattr__(method_name.rsplit(".", 1)[1])(*in_args), SEPARATOR)
                                                        except Exception as e:
                                                                print(SEPARATOR, str(e), SEPARATOR)
                                                else:
                                                        continue
                                        else:
                                                try:
                                                        print("Testing: ", ".".join((method_name.rsplit(".", 3)[1:])))
                                                        print("Output: ", remote_object.__getattr__(method_name.rsplit(".", 1)[1])(), SEPARATOR)
                                                except Exception as e:
                                                        print(SEPARATOR, str(e), SEPARATOR)
                                else:
                                        print("Testing: ", ".".join((method_name.rsplit(".", 3)[1:])), "\nProceed test? (y/n)")
                                        confirmaion = input()
                                        if confirmaion == "y":
                                                if args != "" and args != " ":
                                                        pass
                                                try:
                                                        print("Output: ", remote_object.__getattr__(method_name.rsplit(".", 1)[1])(), SEPARATOR)
                                                except Exception as e:
                                                        print(SEPARATOR, str(e), SEPARATOR)
                                        else:
                                                print("Skipped...." + SEPARATOR)

        def test_auto(self):
                for module_name in list_:
                        remote_object = dbus.get_object("org.etersoft.settingsd", "/org/etersoft/settingsd/functions/{}".format(module_name))
                        remote_object.Introspect()
                        for method_name, args in remote_object.__dict__['_introspect_method_map'].items():
                                if args != "" and args !=" ":
                                        print("Test with arguments:", ".".join((method_name.rsplit(".", 3)[1:])))
                                try:
                                        print("Testing: ", ".".join((method_name.rsplit(".", 3)[1:])))
                                        print("Output: ", remote_object.__getattr__(method_name.rsplit(".", 1)[1])(), SEPARATOR)
                                except Exception as e:
                                        print(SEPARATOR, str(e), SEPARATOR)
                                        self.log_file.write(SEPARATOR + str(e) + SEPARATOR)
                self.log_file.close()


if __name__ == "__main__":
        test_interface = TestSettingsdMain()
        if len(sys.argv) > 1:
                if sys.argv[1] == "-i" or sys.argv[1] == "--interactive":
                        test_interface.test_interactive()
                elif sys.argv[1] == '-h' or sys.argv[1] == "--help":
                        print("Usage:\
                        \n\tpython3 test.py [OPTION]\n \
                        \n\tOptions:\
                        \n\t-i, --interactive : Interactive mode (Default: auto mode with skip of argumented methods)\
                        \n\t-h, --help: Get help\
                        ")
                        exit(0)
        test_interface.test_auto()



