from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in isoft_customer_portal/__init__.py
from isoft_customer_portal import __version__ as version

setup(
	name="isoft_customer_portal",
	version=version,
	description="Isoft Customer Portal",
	author="Abbass  Chokor",
	author_email="abbasschokor225@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
