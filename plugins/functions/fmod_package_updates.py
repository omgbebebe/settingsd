import re
from datetime import datetime
from settingsd import service
from settingsd import shared
from settingsd.tools.process import execProcess
from file_read_backwards import FileReadBackwards


INTERFACE_NAME = "packageUpdates"
SERVICE_NAME = "package_updates"
APT_EXECUTABLE = "/usr/bin/apt"
APT_COMMANDS = (
	'install', 'upgrade', 'update', 'remove', 'purge', 'dist-upgrade', 'search',
	'autoremove', 'dselect-upgrade', 'check', 'clean', 'autoclean', 'source',
	'download', 'changelog', 'build-dep', 'full-upgrade', 'show', 'list',
	'edit-sources'
)
PACKAGE_REGEX = re.compile(r'^(\S+)/\S+\s(\S+)')

MULTIPLE_SPACES_REGEX = re.compile(r'\s{2,}')


class PackageUpdates(service.FunctionObject) :
	@service.functionMethod(INTERFACE_NAME, in_signature="", out_signature="aas")
	def get_available_updates(self):
		execProcess([APT_EXECUTABLE, 'update'])
		raw_output, = execProcess([APT_EXECUTABLE, 'list', '--upgradable'])[:1]
		return self._extract_upgradable_packages(raw_output.decode('utf-8'))

	@service.functionMethod(INTERFACE_NAME, in_signature="", out_signature="i")
	def get_last_update_date(self):
		with FileReadBackwards('/var/log/apt/history.log') as apt_history_file:
			for block in self._read_apt_blocks(apt_history_file):
				result = self._try_extract_upgrade_date(block)
				if result:
					return result.timestamp()
		return 0
	
	@service.functionMethod(INTERFACE_NAME, in_signature="", out_signature="")
	def install_updates(self):
		execProcess([APT_EXECUTABLE, 'upgrade', '-y'], shell=True, inherit_env=True)

	def _extract_upgradable_packages(self, apt_output):
		lines = apt_output.split('\n')
		matches = [PACKAGE_REGEX.match(line) for line in lines]
		return [[m[1], m[2]] for m in matches if m]

	def _parse_apt_block(self, block):
		fields = {}
		for line in block.split('\n'):
			parts = line.split(':', 1)
			if len(parts) != 2:
				continue
			fields[parts[0].strip()] = parts[1].strip()
		return fields

	def _parse_apt_operation(self, block):
		fields = self._parse_apt_block(block)
		if all(key in fields for key in ('Start-Date', 'Commandline', 'End-Date')):
			return {
				'startDate': self._parse_date(fields['Start-Date']),
				'command': self._parse_command(fields['Commandline'])
			}
		else:
			raise ValueError('Non-full apt operation block: ' + block)

	def _parse_command(self, commandline):
		words = [w for w in commandline.split(' ') if len(w) and not w.startswith('-')]
		for word in words:
			if word in APT_COMMANDS:
				return word

	def _parse_date(self, date_str):
		date_str = MULTIPLE_SPACES_REGEX.sub(' ', date_str)
		return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

	def _read_apt_blocks(self, apt_history_file):
		block = []
		for line in apt_history_file:
			if line == '':
				if len(block):
					yield '\n'.join(block[::-1])
				block = []
				continue
			
			block.append(line)

	def _try_extract_upgrade_date(self, block):
		operation = self._parse_apt_operation(block)

		if operation['command'] == 'upgrade' or operation['command'] == 'dist-upgrade':
			return operation['startDate']

		return None


class Service(service.Service) :
	def initService(self):
		shared.Functions.addSharedObject(SERVICE_NAME, PackageUpdates(SERVICE_NAME, self))

	@classmethod
	def serviceName(self):
		return SERVICE_NAME
