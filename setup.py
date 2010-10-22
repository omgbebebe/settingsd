# -*- coding: utf-8 -*-


import sys
import os

from distutils.core import setup
from distutils.command.install import install
from distutils import log


##### Private constants #####
packages_list = ["settingsd"]
scripts_list = ["settingsd-server.py"]

data_files_list = [
	("/etc/dbus-1/system.d", ["configs/dbus/org.etersoft.settingsd.conf"])
]
for maps_list_item in ( ("share/settingsd/functions", "plugins/functions"),
	("share/settingsd/actions", "plugins/actions"),
	("share/settingsd/customs", "plugins/customs"),
	("/etc/settingsd", "configs/settingsd") ) :

	data_files_list.append(( maps_list_item[0], [ os.path.join(maps_list_item[1], item)
		for item in os.listdir(maps_list_item[1]) if not item in (".gitignore",) ] ))


##### Private classes #####
class SettingsdInstall(install) :

	### Public ###

	def run(self) :
		install.run(self)
		self.postInstallHooks()


	### Private ###

	def postInstallHooks(self) :
		log.info("running post-install hooks")

		const_py_file = open(os.path.join(self.install_libbase, "settingsd/const.py"), "r+")
		const_py_file_data = const_py_file.read()

		for replaces_list_item in ( ("\"plugins/functions\"", "\"%s\"" % (os.path.join(self.install_data, "share/settingsd/functions"))),
			("\"plugins/actions\"", "\"%s\"" % (os.path.join(self.install_data, "share/settingsd/actions"))),
			("\"plugins/customs\"", "\"%s\"" % (os.path.join(self.install_data, "share/settingsd/customs"))),
			("\"configs/settingsd\"", "\"%s\"" % (( self.root if self.root != None else "/" )+"etc/settingsd")) ) :
				const_py_file_data = const_py_file_data.replace(replaces_list_item[0], replaces_list_item[1])

		const_py_file.truncate()
		const_py_file.write(const_py_file_data)

		try :
			const_py_file.close()
		except : pass


##### Main #####
setup(
	name = "settingsd",
	version = "0.1",
	url = "http://etersoft.ru/", # FIXME
	license = "GPL",

	author = "Devaev Maxim",
	author_email = "mdevaev@etersoft.ru",
	maintainer = "Devaev Maxim",
	maintainer_email = "mdevaev@etersoft.ru",

	description = "Settingsd - extensible service to control the operating system",

	packages = packages_list,
	scripts = scripts_list,
	data_files = data_files_list,

	cmdclass = { "install" : SettingsdInstall },

	classifiers = [ # http://pypi.python.org/pypi?:action=list_classifiers
		"Development Status :: 4 - Beta",
		"Environment :: Console",
		"Environment :: No Input/Output (Daemon)",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Operating System :: POSIX",
		"Programming Language :: Python",
		"Topic :: System",
		"Topic :: Utilities"
	]
)

