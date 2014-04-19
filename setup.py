import os
import sys
from setuptools import setup, find_packages

version = '0.1.0'

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


setup(name='android-resource-remover',
      version=version,
      description=('Android resource remover'),
      long_description='\n\n'.join((read('README.md'), read('CHANGELOG'))),
      classifiers=[
          'License :: OSI Approved :: BSD License',
          'Intended Audience :: Developers',
          'Programming Language :: Python'],
      author='Keepsafe',
      author_email='support@getkeepsafe.com',
      url='https://github.com/KeepSafe/android-resource-remover/',
      license='Apache',
      py_modules=['android_clean_app'],
      namespace_packages=[],
      install_requires = ['lxml >= 3.3.3'],
      entry_points={
          'console_scripts': [
              'android-resource-remover = android_clean_app:main']
      },
      include_package_data = False)
