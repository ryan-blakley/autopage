%global srcname autopage

Name:           python-%{srcname}
Version:        0.4.1
Release:        1%{?dist}
Summary:        A Python library to provide automatic paging for console output
License:        ASL 2.0
URL:            https://pypi.python.org/pypi/autopage
Source0:        %{pypi_source}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

%global _description %{expand:
Autopage is a Python library to provide automatic paging for console output.}
%description %_description

%package -n python%{python3_pkgversion}-%{srcname}
Summary:        %{summary}

%description -n python%{python3_pkgversion}-%{srcname}

%prep
%autosetup -n %{srcname}-%{version}

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install --skip-build --root %{buildroot}

%files -n python%{python3_pkgversion}-%{srcname}
%{python3_sitelib}/*
%{_datadir}/licenses/python-%{srcname}

%changelog
* Fri Sep 24 2021 Ryan Blakley <rblakley@redhat.com> 0.4.1-1
- Fix building rpm for r7/8 and all of fedora.

* Mon Jul 12 2021 Zane Bitter <zaneb@fedoraproject.org> 0.4.0-1
- Update to v0.4.0

* Fri Jun 25 2021 Zane Bitter <zaneb@fedoraproject.org> 0.3.1-1
- Update to v0.3.1 for easier packaging

* Fri Jun 25 2021 Zane Bitter <zaneb@fedoraproject.org> 0.3.0-2
- Support building for EPEL

* Fri Jun 18 2021 Zane Bitter <zaneb@fedoraproject.org> 0.3.0-1
- Initial build
