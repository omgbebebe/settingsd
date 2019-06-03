#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import shutil

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
	("/etc/rc.d/init.d", ["init/settingsd"]), ('/lib/systemd/system', ['settingsd.service'])
]
for maps_list_item in ( ("share/settingsd/plugins/functions", "plugins/functions"),
	("share/settingsd/plugins/actions", "plugins/actions"),
	("share/settingsd/plugins/customs", "plugins/customs"),
	("share/settingsd/data/functions", "data/functions"),
	("share/settingsd/data/actions", "data/actions"),
	("share/settingsd/data/customs", "data/customs"),
	("/etc/settingsd", "configs/settingsd") ) :

	data_files_list.append(( maps_list_item[0], [ os.path.join(maps_list_item[1], item) for item
		in os.listdir(maps_list_item[1]) if os.path.isfile(maps_list_item[1] + '/'+ item) and item not in (".gitignore", "__pycache__") ] ))


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
		self.preInstallHook()
		install.run(self)
		self.postInstallHooks()


	### Private ###

	def preInstallHook(self):
		log.info("running pre-install hooks")

		for data_item in data_files_list:
			if not os.path.exists(self.install_data + "/" + data_item[0]):
					os.makedirs(self.install_data + "/" + data_item[0])

	def postInstallHooks(self) :
		# FIXME: This is dirty hack. In normal realization, this code must be moved to build stage

		log.info("running post-install hooks")

		const_py_file = open(os.path.join(self.install_libbase, "settingsd/const.py"), "r+")
		const_py_file_data = const_py_file.read()

		for replaces_list_item in (
			("\"plugins/functions\"", "\"%s\"" % "/usr/share/settingsd/plugins/functions"),
			("\"plugins/actions\"", "\"%s\"" % "/usr/share/settingsd/plugins/actions"),
			("\"plugins/customs\"", "\"%s\"" % "/usr/share/settingsd/plugins/customs"),
			("\"plugins/functions\"", "\"%s\"" % "/usr/share/settingsd/plugins/functions"),
			("\"data/functions\"", "\"%s\"" % "/usr/share/settingsd/data/functions"),
			("\"data/actions\"", "\"%s\"" % "/usr/share/settingsd/data/actions"),
			("\"data/customs\"", "\"%s\"" % "/usr/share/settingsd/data/customs"),
			("\"configs/settingsd\"", "\"%s\"" % "/etc/settingsd") ) :
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
	url = "https://github.com/Etersoft/settingsd",
	license = "LGPL 2.1 or later",

	author = "Devaev Maxim",
	author_email = "mdevaev@etersoft.ru",
	maintainer = "Vitaly Lipatov",
	maintainer_email = "lav@etersoft.ru",

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

