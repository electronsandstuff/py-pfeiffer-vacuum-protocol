# pfeiffer_vacuum_protocol - Python interface to Pfeiffer vacuum gauges
# Copyright (C) 2020 Christopher M. Pierce (contact@chris-pierce.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import setuptools

# Load my long description
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name='pfeiffer-vacuum-protocol',
        version='0.3',
        description=' Python interface to Pfeiffer vacuum gauges',
        author='Christopher M. Pierce',
        author_email='contact@chris-pierce.com',
        python_requires='>=3.5',
        packages=setuptools.find_packages(),
        long_description=long_description,
        long_description_content_type="text/markdown",
        install_requires = [],
        license = "GNU Lesser General Public License v3 (LGPLv3)",
        classifiers = [
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
            "Development Status :: 4 - Beta",
            "Operating System :: OS Independent",
        ],
    )
