Name: settingsd
Version: 0.1
Release: alt1
Summary: Settingsd - extensible service to control the operating system
Group: System
License: GPL
URL: http://etersoft.ru
#Git: git.eter:/people/mdevaev/packages/settingsd.git
Packager: Devaev Maxim <mdevaev@etersoft.ru>

Source: %name-%version.tar
BuildArch: noarch
BuildRequires: rpm-build-compat

Requires: python-module-dbus
Requires: chkconfig, service, SysVinit, pm-utils
Requires: lsb-release
%description
%summary


%prep
%setup


%build
%python_build


%install
%python_install


%files
%_bindir/settingsd-server.py
%dir %_sysconfdir/%name
%config(noreplace) %_sysconfdir/%name/*.conf
%_sysconfdir/dbus-1/system.d/*.conf
%_datadir/%name
%python_sitelibdir/%name
%python_sitelibdir/*.egg-info


%changelog
* Mon Oct 25 2010 Devaev Maxim <mdevaev@etersoft.ru> 0.1-alt1

