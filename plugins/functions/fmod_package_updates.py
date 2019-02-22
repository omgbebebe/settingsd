import os
import errno
import re
from datetime import datetime
from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd.tools.process import execProcess


INTERFACE_NAME = "packageUpdates"
SERVICE_NAME = "package_updates"
APT_EXECUTABLE = "/usr/bin/apt"
APT_COMMANDS = (
	'install', 'upgrade', 'update', 'remove', 'purge', 'dist-upgrade', 'search',
	'autoremove', 'dselect-upgrade', 'check', 'clean', 'autoclean', 'source',
	'download', 'changelog', 'build-dep', 'full-upgrade', 'show', 'list',
	'edit-sources'
)
PACKAGE_REGEX = re.compile(r'^(\S+)/\S+')

MULTIPLE_SPACES_REGEX = re.compile(r'\s{2,}')

HISTORY_BLOCK_SIZE = 2 ** 16 # bytes


class PackageUpdates(service.FunctionObject) :
	@service.functionMethod(INTERFACE_NAME, in_signature="", out_signature="as")
	def get_available_updates(self):
		execProcess([APT_EXECUTABLE, 'update'])
		raw_output, = execProcess([APT_EXECUTABLE, 'list', '--upgradable'])[:1]
		return self._extract_upgradable_packages(raw_output.decode('utf-8'))

	@service.functionMethod(INTERFACE_NAME, in_signature="", out_signature="i")
	def get_last_update_date(self):
		with open('/var/log/apt/history.log', 'r') as apt_history_file:
			apt_history_file.seek(0, os.SEEK_END)
			file_size = apt_history_file.tell()
			full_block_count = file_size // HISTORY_BLOCK_SIZE
			block = 0
			while True:
				offset = 0 if block >= full_block_count else file_size - HISTORY_BLOCK_SIZE * (block + 1)
				result = self._try_extract_upgrade_date(apt_history_file, offset, file_size)
				if result:
					return result.timestamp()

				if block < full_block_count:
					block += 1
				else:
					return 0
	
	@service.functionMethod(INTERFACE_NAME, in_signature="", out_signature="")
	def install_updates(self):
		execProcess([APT_EXECUTABLE, 'upgrade', '-y'], shell=True, inherit_env=True)

	def _extract_upgradable_packages(self, apt_output):
		lines = apt_output.split('\n')
		matches = [PACKAGE_REGEX.match(line) for line in lines]
		return [m[1] for m in matches if m]

	def _parse_apt_block(self, block):
		fields = {}
		for line in block.split('\n'):
			parts = line.split(':', 1)
			if len(parts) != 2:
				continue
			fields[parts[0].strip()] = parts[1].strip()
		return fields

	def _parse_apt_operations(self, blocks):
		operations = []
		for block in blocks:
			fields = self._parse_apt_block(block)
			if all(key in fields for key in ('Start-Date', 'Commandline', 'End-Date')):
				operations.append({
					'startDate': self._parse_date(fields['Start-Date']),
					'command': self._parse_command(fields['Commandline'])
				})
		return operations

	def _parse_command(self, commandline):
		words = [w for w in commandline.split(' ') if len(w) and not w.startswith('-')]
		for word in words:
			if word in APT_COMMANDS:
				return word

	def _parse_date(self, date_str):
		date_str = MULTIPLE_SPACES_REGEX.sub(' ', date_str)
		return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

	def _read_apt_blocks(self, apt_history_file, offset, block_size):
		apt_history_file.seek(offset, os.SEEK_SET)
		data = apt_history_file.read(block_size)
		return data.split('\n\n')

	def _try_extract_upgrade_date(self, apt_history_file, offset, file_size):
		limit = max(file_size - offset, HISTORY_BLOCK_SIZE * 2) + 1
		for block_size in range(HISTORY_BLOCK_SIZE * 2, limit, HISTORY_BLOCK_SIZE):
			apt_operation_blocks = self._read_apt_blocks(apt_history_file, offset, block_size)
			apt_operations = self._parse_apt_operations(apt_operation_blocks)
			if len(apt_operations):
				break

		for operation in apt_operations[::-1]:
			if operation['command'] == 'upgrade':
				return operation['startDate']


class Service(service.Service) :
	def initService(self):
		shared.Functions.addSharedObject(SERVICE_NAME, PackageUpdates(SERVICE_NAME, self))

	@classmethod
	def serviceName(self):
		return SERVICE_NAME
