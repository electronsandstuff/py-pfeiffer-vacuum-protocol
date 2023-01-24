import setuptools

# Load my long description
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pfeiffer-vacuum-protocol',
    version='0.5',
    description=' Python interface to Pfeiffer vacuum gauges',
    author='Christopher M. Pierce',
    author_email='contact@chris-pierce.com',
    python_requires='>=3.5',
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[],
    license="GNU Lesser General Public License v3 (LGPLv3)",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
    ],
)
