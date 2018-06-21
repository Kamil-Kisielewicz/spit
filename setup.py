#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function
#
# Standard imports
#
import glob, os
import pdb
#from distutils.extension import Extension
#
# setuptools' sdist command ignores MANIFEST.in
#
#from distutils.command.sdist import sdist as DistutilsSdist
from setuptools import setup
#
# DESI support code.
#
#from desiutil.setup import DesiTest, DesiVersion, get_version

# Check dependencies
#if sys.argv[1] != 'egg_info':
#    from pypit import archeck
#    archeck.version_check()

#
# Begin setup
#
setup_keywords = dict()
#
# THESE SETTINGS NEED TO BE CHANGED FOR EVERY PRODUCT.
#
setup_keywords['name'] = 'spit'
setup_keywords['description'] = 'SPectral Image Typing'
setup_keywords['author'] = 'PYPIT Collaboration'
setup_keywords['author_email'] = 'pypit@ucolick.org'
setup_keywords['license'] = 'BSD'
setup_keywords['url'] = 'https://github.com/PYPIT/spit'
#
# END OF SETTINGS THAT NEED TO BE CHANGED.
#
setup_keywords['version'] = '0.1.dev0' #get_version(setup_keywords['name'])
#
# Use README.rst as long_description.
#
setup_keywords['long_description'] = ''
if os.path.exists('README.md'):
    with open('README.md') as readme:
        setup_keywords['long_description'] = readme.read()
#
# Set other keywords for the setup function.  These are automated, & should
# be left alone unless you are an expert.
#
# Treat everything in bin/ except *.rst as a script to be installed.
#
if os.path.isdir('bin'):
    setup_keywords['scripts'] = [fname for fname in glob.glob(os.path.join('bin', '*'))
        if not os.path.basename(fname).endswith('.rst')]
setup_keywords['provides'] = [setup_keywords['name']]
setup_keywords['requires'] = ['Python (>2.7.0)']
# setup_keywords['install_requires'] = ['Python (>2.7.0)']
setup_keywords['zip_safe'] = False
#setup_keywords['use_2to3'] = False
setup_keywords['packages'] = ['spit'] #find_packages('pypit')
#setup_keywords['package_dir'] = {'':''}
#setup_keywords['cmdclass'] = {'version': DesiVersion, 'test': DesiTest, 'sdist': DistutilsSdist}
#setup_keywords['test_suite']='{name}.tests.{name}_test_suite.{name}_test_suite'.format(**setup_keywords)
#setup_keywords['setup_requires']=['pytest-runner']
setup_keywords['tests_require']=['pytest']

#setup_keywords['cmdclass']={'build_ext': build_ext}

# Autogenerate command-line scripts.
#
# setup_keywords['entry_points'] = {'console_scripts':['desiInstall = desiutil.install.main:main']}

#
# Add internal data directories.
#

data_files = []

# walk through the data directory, adding all files
data_generator = os.walk('spit/data')
for path, directories, files in data_generator:
    for f in files:
        data_path = '/'.join(path.split('/')[1:])
        data_files.append(data_path + '/' + f)
# add pipeline and spectrograph settings
#settings = glob.glob('auto_type/settings/settings.*')
#settings = ['/'.join(path.split('/')[1:]) for path in settings]
#data_files.extend(settings)
setup_keywords['package_data'] = {'spit': data_files,
                                  '': ['*.rst', '*.txt']}
setup_keywords['include_package_data'] = True

#
# Run setup command.
#
setup(**setup_keywords)

