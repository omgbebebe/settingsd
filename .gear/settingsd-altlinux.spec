Name: settingsd
Version: 0.1
Release: alt3

Summary: Settingsd - extensible service to control the operating system via D-Bus

Group: System/Servers
License: GPL
URL: http://etersoft.ru

Packager: Devaev Maxim <mdevaev@etersoft.ru>

#Git: git.eter:/people/mdevaev/packages/settingsd.git
Source: %name-%version.tar

BuildArch: noarch

BuildRequires: python-dev

Requires: python-module-dbus
Requires: chkconfig, service, SysVinit, pm-utils
Requires: lsb-release

%description
Extensible service to control the operating system via D-Bus.

%prep
%setup

%build
%python_build

%install
%python_install
# FIXME: hack to drop out buildroot
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
* Tue Oct 26 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt3
- Fixed init script including into package

* Mon Oct 25 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt2
- Fixed build errors
- Added startup init srcipt

* Mon Oct 25 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt1
- Initial build

