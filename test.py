import subprocess as sbp
from unittest import TestCase, main
import xml.etree.ElementTree as ET
from pprint import pprint as pp

list_ = ["common_info", "date_time", "dnsmasq_config", "example",
 "local_groups", "local_users", "machine", "network", "nss_roles",
  "ntp_config", "package_updates", "rtorrentd_config", "ssl",
   "statistics", "system_services"]
cmd = "dbus-send --system --type=method_call --print-reply \
        --dest=org.etersoft.settingsd /org/etersoft/settingsd/functions/{func_name}\
             org.etersoft.settingsd.functions.{funcName}.{interface}.{method} {args}"

class TestSettingsdMain(TestCase):
        def test_common_info(self):
                res = sbp.run(cmd.format(func_name="common_info", funcName="commonInfo", interface="lsbRelease", method="version", args=""), stdout=sbp.PIPE)
                res = res.stdout.decode('utf-8')
                print(res)
    



if __name__ == '__main__':
    main()



