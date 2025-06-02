%undefine _debugsource_packages
%define module pendulum
%define oname pendulum
%bcond_without test

Name:		python-pendulum
Version:	3.1.0
Release:	1
Summary:	Python datetimes made easy
URL:		https://pypi.org/project/pendulum/
License:	MIT
Group:		Development/Python
Source0:	https://github.com/python-pendulum/pendulum/archive/%{version}/%{oname}-%{version}.tar.gz
Source1:	pendulum-3.1.0-vendor.tar.xz

BuildSystem:	python
BuildRequires:  cargo
BuildRequires:  rust-packaging
BuildRequires:	python
BuildRequires:	pkgconfig(python3)
BuildRequires:	python%{pyver}dist(maturin)
BuildRequires:	python%{pyver}dist(cython)
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(python-dateutil) >= 2.6
BuildRequires:	python%{pyver}dist(tzdata) >= 2020.1
%if %{with test}
BuildRequires:	python%{pyver}dist(freezegun)
BuildRequires:	python%{pyver}dist(mypy)
BuildRequires:	python%{pyver}dist(ruff)
BuildRequires:	python%{pyver}dist(poetry)
BuildRequires:	python%{pyver}dist(pre-commit)
BuildRequires:	python%{pyver}dist(pytest)
BuildRequires:	python%{pyver}dist(pytest-cov)
BuildRequires:	python%{pyver}dist(pytz) >= 2022.1
BuildRequires:	python%{pyver}dist(six)
BuildRequires:	python%{pyver}dist(time-machine) >= 2.16
BuildRequires:	python%{pyver}dist(typing-extensions)
BuildRequires:	patchelf
%endif

%description
Python datetimes made easy

%prep
%autosetup -n %{module}-%{version} -p1 -a1

# Remove pytest-benchmark dependency. We don't care about it in RPM builds.
sed -i '/@pytest.mark.benchmark/d' $(find tests -type f -name '*.py')

# move extracted vendor archive into the rust/ subdir
mv vendor/ rust/
%cargo_prep -v rust/vendor

cat >>rust/.cargo/config <<EOF
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"

EOF

%build
export CFLAGS="%{optflags}"
export CARGO_HOME=$PWD/rust/.cargo
%py_build

cd rust
%cargo_license_summary
%{cargo_license} > ../LICENSES.dependencies

%install
%py_install

%if %{with test}
%check
export CI=true
export PYTHONPATH="%{buildroot}%{python_sitearch}:${PWD}"
%{__python} -m pytest -v -rs --import-mode=importlib tests/

%endif

%files
%{python3_sitearch}/%{module}
%{python3_sitearch}/%{module}-%{version}.dist-info
%license LICENSE
%license LICENSES.dependencies
%doc README.rst
