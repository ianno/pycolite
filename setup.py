'''
Setup.py file adapted from
https://github.com/pypa/sampleproject
released under the MIT license

Author: Antonio Iannopollo
'''

from setuptools import setup, find_packages  # Always prefer setuptools over distutils
import os
import pycolite.util.util as util
from configparser import ConfigParser, NoSectionError, NoOptionError, ParsingError
import sys

here = os.path.abspath(os.path.dirname(__file__))


#load setup.cfg
setup_cfg = ConfigParser()

with open('setup.cfg') as filep:
    try:
        setup_cfg.readfp(filep)
    except ParsingError:
        print('error parsing setup.cfg')
        sys.exit(-1)

try:
    nuxmv_path = setup_cfg.get(util.TOOL_SECT, util.NUXMV_OPT)
except (NoSectionError, NoOptionError):
    print('Error loading nuxmv configuration info')
    #sys.exit(-1)

nuxmv_path = util.which(nuxmv_path)

if nuxmv_path is None:
    print('Error, nuxmv path is invalid')
    sys.exit(-1)

try:
    temp_dir_path = setup_cfg.get(util.PATH_SECT, util.TEMP_OPT)
except (NoSectionError, NoOptionError):
    print('Error loading temp dir configuration info')
    temp_dir_path = ''
    #sys.exit(-1)

temp_dir_path = os.path.abspath(temp_dir_path)
#make sure the directory exists
if not os.path.exists(temp_dir_path):
    print('creating %s' % temp_dir_path)
    os.makedirs(temp_dir_path)

#write internal config file
config_path = os.path.join(here, util.CONFIG_FILE_RELATIVE_PATH)

util.create_main_config_file(config_path, [util.TOOL_SECT,
                                           util.PATH_SECT],
                             {util.TOOL_SECT: (util.NUXMV_OPT, nuxmv_path),
                              util.PATH_SECT: (util.TEMP_OPT, temp_dir_path)
                             })

# Get the long description from the relevant file
with open(os.path.join(here, 'DESCRIPTION.md')) as f:
    long_description = f.read()

setup(
    name='pycolite',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.9.0.dev1',

    description='A library to manipulate contracts (for Contract Based Design) in python',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/ianno/pycolite',

    # Author details
    author='Antonio Iannopollo',
    author_email='antonio@berkeley.edu',

    # Choose your license
    license='GPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='system contract based design platform',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs']),

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['ply', 'py', 'pytest'],

    # List additional groups of dependencies here (e.g. development dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    extras_require = {
        'dev': ['check-manifest'],
        'test': ['pytest'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
    },
)
