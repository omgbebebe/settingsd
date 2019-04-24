from unittest import TestCase, main
from pprint import pprint as pp
from dbus import SystemBus

sep = "\n" + "-"*30 + "\n"

list_ = ["common_info", "date_time", "dnsmasq_config", "example",
 "local_groups", "local_users", "network", "nss_roles",
  "ntp_config", "package_updates", "rtorrentd_config", "ssl",
   "statistics", "system_services"]

class TestSettingsdMain():
        def __init__(self, *args, **kwargs):
                self.dbus = SystemBus()
                self.log_file = open("test_log.log", "w")

        def test_all(self):
                for module_name in list_:
                        remote_object = dbus.get_object("org.etersoft.settingsd", "/org/etersoft/settingsd/functions/{}".format(module_name))
                        remote_object.Introspect()
                        for method_name, args in remote_object.__dict__['_introspect_method_map'].items():
                                if args != "" and args !=" ":
                                        print("Test with arguments:", ".".join((method_name.rsplit(".", 3)[1:])))
                                try:
                                        print("Testing: ", ".".join((method_name.rsplit(".", 3)[1:])), "\nProceed test? (y/n)")
                                        confirmaion = input()
                                        if confirmaion == "y":
                                                print("Output: ", remote_object.__getattr__(method_name.rsplit(".", 1)[1])(), sep)
                                        else:
                                                print("Skipped...." + sep)
                                                continue
                                except Exception as e:
                                        print(sep, str(e), sep)
                                        self.log_file.write(sep + str(e) + sep)
                self.log_file.close()


dbus = SystemBus()


t = TestSettingsdMain()
t.test_all()



