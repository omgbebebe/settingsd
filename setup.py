#!/usr/bimin/env python
# -*- coding: utf-8 -*-


import sys
import os

from distutils.core import setup
from distutils.command.install import install
from distutils import log

from settingsd import const


##### Private constants #####
packages_list = ["settingsd", "settingsd/tools", "settingsd/validators"]
scripts_list = ["settingsd-server.py"]
install_requires = ['file_read_backwards']

#####
data_files_list = [
	("/etc/dbus-1/system.d", ["configs/dbus/org.etersoft.settingsd.conf"]),
	("/etc/rc.d/init.d", ["init/settingsd"])
]
for maps_list_item in ( ("share/settingsd/plugins/functions", "plugins/functions"),
	("share/settingsd/plugins/actions", "plugins/actions"),
	("share/settingsd/plugins/customs", "plugins/customs"),
	("share/settingsd/data/functions", "data/functions"),
	("share/settingsd/data/actions", "data/actions"),
	("share/settingsd/data/customs", "data/customs"),
	("/etc/settingsd", "configs/settingsd") ) :

	data_files_list.append(( maps_list_item[0], [ os.path.join(maps_list_item[1], item)
		for item in os.listdir(maps_list_item[1]) if not item in (".gitignore",) ] ))


#####
classifiers_list = [ # http://pypi.python.org/pypi?:action=list_classifiers
	"Development Status :: 4 - Beta",
	"Environment :: Console",
	"Environment :: No Input/Output (Daemon)",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Operating System :: POSIX",
	"Programming Language :: Python",
	"Topic :: System",
	"Topic :: Utilities",
	{
		"alpha" : "Development Status :: 3 - Alpha",
		"beta" : "Development Status :: 4 - Beta",
		"stable" : "Development Status :: 5 - Production/Stable"
	}[const.VERSION_STATUS]
]


##### Private classes #####
class SettingsdInstall(install) :

	### Public ###

	def run(self) :
		install.run(self)
		self.postInstallHooks()


	### Private ###

	def postInstallHooks(self) :
		# FIXME: This is dirty hack. In normal realization, this code must be moved to build stage

		log.info("running post-install hooks")

		const_py_file = open(os.path.join(self.install_libbase, "settingsd/const.py"), "r+")
		const_py_file_data = const_py_file.read()

		for replaces_list_item in ( ("\"plugins/functions\"", "\"%s\"" % (os.path.join(self.install_data, "share/settingsd/plugins/functions"))),
			("\"plugins/actions\"", "\"%s\"" % (os.path.join(self.install_data, "share/settingsd/plugins/actions"))),
			("\"plugins/customs\"", "\"%s\"" % (os.path.join(self.install_data, "share/settingsd/plugins/customs"))),
			("\"plugins/functions\"", "\"%s\"" % (os.path.join(self.install_data, "share/settingsd/plugins/functions"))),
			("\"data/functions\"", "\"%s\"" % (os.path.join(self.install_data, "share/settingsd/data/functions"))),
			("\"data/actions\"", "\"%s\"" % (os.path.join(self.install_data, "share/settingsd/data/actions"))),
			("\"data/customs\"", "\"%s\"" % (os.path.join(self.install_data, "share/settingsd/data/customs"))),
			("\"configs/settingsd\"", "\"%s\"" % (os.path.join(( self.root if self.root != None else "/" ), "etc/settingsd"))) ) :
				const_py_file_data = const_py_file_data.replace(replaces_list_item[0], replaces_list_item[1])

		const_py_file.truncate()
		const_py_file.seek(0)
		const_py_file.write(const_py_file_data)

		try :
			const_py_file.close()
		except : pass


##### Main #####
setup(
	name = const.MY_NAME,
	version = const.VERSION,
	url = "http://etersoft.ru/", # FIXME: Add project url
	license = "GPL",

	author = "Devaev Maxim",
	author_email = "mdevaev@etersoft.ru",
	maintainer = "Devaev Maxim",
	maintainer_email = "mdevaev@etersoft.ru",

	description = "Settingsd - extensible service to control the operating system",

	packages = packages_list,
	scripts = scripts_list,
	data_files = data_files_list,
	requires = [
		"file_read_backwards"
	],

	cmdclass = { "install" : SettingsdInstall },

	classifiers = classifiers_list
)

