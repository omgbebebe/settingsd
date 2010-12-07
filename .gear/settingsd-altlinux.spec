Name: settingsd
Version: 0.1
Release: alt10

Summary: Settingsd - extensible service to control the operating system via D-Bus

Group: System/Servers
License: GPL
URL: http://etersoft.ru

Packager: Devaev Maxim <mdevaev@etersoft.ru>

#Git: git.eter:/people/mdevaev/packages/settingsd.git
Source: %name-%version.tar

BuildArch: noarch

BuildRequires: python-dev

Requires: python-module-dbus, python-module-pyinotify, python-module-gudev
Requires: chkconfig, service, SysVinit, pm-utils, lsb-release
Requires: smartctl, ntpdate, hwclock

%description
Extensible service to control the operating system via D-Bus.


%prep
%setup

%build
%python_build

%install
%python_install
# FIXME: Hack to drop out buildroot
%__subst 's|%buildroot||g' %buildroot%python_sitelibdir/%name/const.py


%files
%_bindir/settingsd-server.py
%dir %_sysconfdir/%name/
%config(noreplace) %_sysconfdir/%name/*.conf
%_initddir/%name
%_sysconfdir/dbus-1/system.d/*.conf
%_datadir/%name/
%python_sitelibdir/%name/
%python_sitelibdir/*.egg-info


%changelog
* Tue Dec 07 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt10
- added validator for IPv4 address
- changed functionality level
- check for on-digit mask range
- closing file does not emmit exception
- fixed small bug in IPv4 address validator, added validator for IPv4 netmask validator, validator for hardware MAC address
- new parsers for ntp_config
- plugin for dnsmasq configuration
- some calls of execProcess in plugins no longer cause exceptions
- updated D-Bus policy

* Thu Nov 25 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt9
- added package requirement at hwclock

* Thu Nov 25 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt8
- added DBus policy for fmod_date_time, refactoring
- added module for date/time configuration
- current functionality level = 62
- fixed regexp for ntp servers, code for checks /etc/ntp.conf
- output version status at option -v
- refactoring

* Tue Nov 16 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt7
- added requirements for this verison

* Mon Nov 15 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt6
- added exception on process fail to fmod_system_services at first services loading
- added module for check SMART status
- added signal for disk changed to disks_smart
- additional version constants: functionality level and development status
- add simple SMART support checking
- add tools module with execProcess()
- aPI for determine settingsd version and functionality level
- dBus policy for fmod_disks_smart
- dynamic add and remove system services by inotify events on /etc/rc.d/init.d
- enable GObject threads
- fixed bug with getting dict of sharedObjects
- installation info and dynamic classifiers from settingsd/const.py
- merge branch 'master' of git.eter:/people/mdevaev/packages/settingsd
- moved raising SubprocessFailure to tools module
- new {submod} macros for logger
- refactoring all function modules for using tools
- removed unused modules
- systemServices in shared
- using constructor instead initService(), first run not emits signals

* Wed Nov 10 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt5
- changed return value type of meminfo API from float to int
- dBus policy for fmod_ntp_config
- fixed bug with access to object_path
- most verbosity server messages at loading and closing services
- nTP configuration module
- style fix
- using closed variables instead private in classes, fixed small bugs in logger
- validator for string list

* Tue Oct 26 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt4
- Fixed build errors

* Tue Oct 26 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt3
- Fixed init script including into package

* Mon Oct 25 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt2
- Fixed build errors
- Added startup init srcipt

* Mon Oct 25 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt1
- Initial build

