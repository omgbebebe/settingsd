# -*- coding: utf-8 -*-


import os
import re
import shutil

from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared

import settingsd.tools as tools
import settingsd.tools.editors


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
	def setRawConfigPath(self, config_path) :
		self.setConfigValue("RTORRENT_CONFIG", config_path)

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, out_signature="s")
	def rawConfigPath(self) :
		config_path_list = self.configValue("RTORRENT_CONFIG")
		return ( config_path_list[0] if len(config_path_list) > 0 else "" )

	###

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, in_signature="s")
	def setRawConfig(self, config_file_data) :
		config_path_list = self.configValue("RTORRENT_CONFIG")
		if len(config_path_list) > 0 and len(config_path_list[0]) > 0 :
			config_file = open(config_path_list[0], "w")
			config_file.write(config_file_data)
			try :
				config_file.close()
			except : pass

	@service.functionMethod(DAEMON_METHODS_NAMESPACE, out_signature="s")
	def rawConfig(self) :
		config_path_list = self.configValue("RTORRENT_CONFIG")
		if len(config_path_list) > 0 and len(config_path_list[0]) > 0 :
			config_file = open(config_path_list[0])
			config_file_data = config_file.read()
			try :
				config_file.close()
			except : pass
			return config_file_data
		return ""


	### Private ###

	def setConfigValue(self, variable_name, values_list) :
		rtorrentd_editor = tools.editors.PlainEditor(spaces_list = [])
		rtorrentd_editor.open(config.value(SERVICE_NAME, "rtorrentd_conf"), config.value(SERVICE_NAME, "rtorrentd_conf_sample"))
		rtorrentd_editor.setValue(variable_name, values_list)
		rtorrentd_editor.save()
		rtorrentd_editor.close()

	def configValue(self, variable_name) :
		rtorrentd_editor = tools.editors.PlainEditor(spaces_list = [])
		rtorrentd_editor.open(config.value(SERVICE_NAME, "rtorrentd_conf"))
		values_list = rtorrentd_editor.value(variable_name)
		rtorrentd_editor.close()
		return values_list


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
			(SERVICE_NAME, "rtorrentd_conf", "/etc/sysconfig/rtorrent", str),

			(SERVICE_NAME, "rtorrentd_conf_sample", os.path.join(const.FUNCTIONS_DATA_DIR, SERVICE_NAME, "rtorrent"), str)
		]

