# -*- coding: utf-8 -*-


import os
import re
import shutil

from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import tools


##### Private constants #####
SERVICE_NAME = "rtorrentd_config"

DAEMON_METHODS_NAMESPACE = "rtorrent.daemon"


##### Private classes #####
class RTorrentd(service.FunctionObject) :

	### DBus methods ###

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, in_signature="s")
	def setUser(self, user_name) :
		self.setConfigValue("RTORRENTD_USER", user_name)

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, out_signature="s")
	def user(self) :
		user_name_list = self.configValue("RTORRENTD_USER")
		return ( user_name_list[0] if len(user_name_list) > 0 else "" )

	###

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, in_signature="s")
	def setDownloadsDir(self, downloads_dir_path) :
		self.setConfigValue("RTORRENTD_DOWNLOADS", downloads_dir_path)

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, out_signature="s")
	def downloadsDir(self) :
		downloads_dir_path_list = self.configValue("RTORRENTD_DOWNLOADS")
		return ( downloads_dir_path_list[0] if len(downloads_dir_path_list) > 0 else "" )

	###

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, in_signature="s") 
	def setSessionDir(self, session_dir_path) :
		self.setConfigValue("RTORRENTD_SESSION", session_dir_path)

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, out_signature="s")
	def sessionDir(self) :
		session_dir_path_list = self.configValue("RTORRENTD_SESSION")
		return ( session_dir_path_list[0] if len(session_dir_path_list) > 0 else "" )

	###

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, in_signature="s")
	def setTmpDir(self, tmp_dir_path) :
		self.setConfigValue("RTORRENTD_TMP", tmp_dir_path)

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, out_signature="s")
	def tmpDir(self) :
		tmp_dir_path_list = self.configValue("RTORRENTD_TMP")
		return ( tmp_dir_path_list[0] if len(tmp_dir_path_list) > 0 else "" )

	###

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, in_signature="s")
	def setSocketPath(self, socket_path) :
		self.setConfigValue("RTORRENTD_SOCKET", socket_path)

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, out_signature="s")
	def socketPath(self) :
		socket_path_list = self.configValue("RTORRENTD_SOCKET")
		return ( socket_path_list[0] if len(socket_path_list) > 0 else "" )

	###

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, in_signature="s")
	def setSocketUser(self, user_name) :
		socket_owner_list = self.configValue("RTORRENT_SOCKET_OWNER")
		socket_owner_list = ( socket_owner_list[0].split(":") if len(socket_owner_list) > 0 else ["", ""] )

		if len(socket_owner_list) != 2 :
			socket_owner_list = (user_name, "")
		else :
			socket_owner_list[0] = user_name
		self.setConfigValue("RTORRENT_SOCKET_OWNER", ":".join(socket_owner_list))

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, in_signature="s")
	def setSocketGroup(self, group_name) :
		socket_owner_list = self.configValue("RTORRENT_SOCKET_OWNER")
		socket_owner_list = ( socket_owner_list[0].split(":") if len(socket_owner_list) > 0 else ["", ""] )

		if len(socket_owner_list) != 2 :
			socket_owner_list = ("", group_name)
		else :
			socket_owner_list[1] = group_name
		self.setConfigValue("RTORRENT_SOCKET_OWNER", ":".join(socket_owner_list))

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, out_signature="s")
	def socketUser(self) :
		socket_owner_list = self.configValue("RTORRENT_SOCKET_OWNER")
		return ( socket_owner_list[0].split(":")[0] if len(socket_owner_list) > 0 else "" )

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, out_signature="s")
	def socketGroup(self) :
		socket_owner_list = self.configValue("RTORRENT_SOCKET_OWNER")
		socket_owner_list = ( socket_owner_list[0].split(":") if len(socket_owner_list) > 0 else ["", ""] )
		return ( socket_owner_list[1] if len(socket_owner_list) == 2 else "" )

	###

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, in_signature="i")
	def setSocketMode(self, socket_mode) :
		self.setConfigValue("RTORRENT_SOCKET_PERMISSIONS", int(socket_mode))

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, out_signature="i")
	def socketMode(self) :
		socket_mode_list = self.configValue("RTORRENT_SOCKET_PERMISSIONS")
		return ( int(socket_mode_list[0]) if len(socket_mode_list) > 0 else -1 )

	###

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, in_signature="s")
	def setConfigPath(self, config_path) :
		self.setConfigValue("RTORRENT_CONFIG", config_path)

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, out_signature="s")
	def configPath(self) :
		config_path_list = self.configValue("RTORRENT_CONFIG")
		return ( config_path_list[0] if len(config_path_list) > 0 else "" )


	### Private ###

	def setConfigValue(self, variable_name, values_list, replace_flag = True) :
		if not type(values_list).__name__ in ("list", "tuple") :
			values_list = [values_list]

		rtorrentd_config_file_path = config.value(SERVICE_NAME, "rtorrentd_config_file_path")

		###

		rtorrentd_config_file_path_sample = config.value(SERVICE_NAME, "rtorrentd_config_file_path_sample")
		if not os.access(rtorrentd_config_file_path, os.F_OK) :
			if os.access(rtorrentd_config_file_path_sample, os.F_OK) :
				shutil.copy2(rtorrentd_config_file_path_sample, rtorrentd_config_file_path)
			else :
				open(rtorrentd_config_file_path, "w").close()

		###

		rtorrentd_config_file = open(rtorrentd_config_file_path, "r+")
		rtorrentd_config_file_data = rtorrentd_config_file.read()

		variable_regexp = re.compile(r"(((\n|\A)%s=[^\n]*)+)" % (variable_name))
		variable = "\n".join([ "%s=\"%s\"" % (variable_name, values_list_item) for values_list_item in values_list ])
		if variable_regexp.search(rtorrentd_config_file_data) :
			if len(variable) != 0 :
				variable = ( "\n" if replace_flag else "\\1\n" )+variable
			rtorrentd_config_file_data = variable_regexp.sub(variable, rtorrentd_config_file_data)
		elif len(variable) != 0 :
			rtorrentd_config_file_data += ( "\n" if rtorrentd_config_file_data[-1] != "\n" else "" )+variable+"\n"

		rtorrentd_config_file.seek(0)
		rtorrentd_config_file.truncate()
		rtorrentd_config_file.write(rtorrentd_config_file_data)

		try :
			rtorrentd_config_file_data.close()
		except : pass

	def configValue(self, variable_name) :
		if os.access(config.value(SERVICE_NAME, "rtorrentd_config_file_path"), os.F_OK) :
			rtorrentd_config_file = open(config.value(SERVICE_NAME, "rtorrentd_config_file_path"), "r")
			rtorrentd_config_file_list = rtorrentd_config_file.read().split("\n")
			try :
				rtorrentd_config_file.close()
			except : pass

			variable_regexp = re.compile(r"^%s=[\"\']?([^\n\"\']*)" % (variable_name))
			variables_list = []
			for rtorrentd_config_file_list_item in rtorrentd_config_file_list :
				if len(rtorrentd_config_file_list_item) == 0 :
					continue
				variable_match = variable_regexp.match(rtorrentd_config_file_list_item)
				if variable_match != None :
					variables_list.append(variable_match.group(1))
			return variables_list
		return []


##### Public classes #####
class Service(service.Service) :

	### Public ###

	def initService(self) :
		shared.Functions.addSharedObject(SERVICE_NAME, RTorrentd(SERVICE_NAME, self))


	### Private ###

	@classmethod
	def serviceName(self) :
		return SERVICE_NAME

	@classmethod
	def options(self) :
		return [
			(SERVICE_NAME, "rtorrentd_config_file_path", "/etc/sysconfig/rtorrent", str),

			(SERVICE_NAME, "rtorrentd_config_file_path_sample", os.path.join(const.FUNCTIONS_DATA_DIR, SERVICE_NAME, "rtorrent"), str)
		]

