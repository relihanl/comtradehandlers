from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

setup(name='comtradehandlers',
      version='0.1.0',
      description='Support for IEEE COMTRADE readers and writers',
      long_description=long_description,
      url='',
      author='Liam Relihan',
      author_email='liam.relihan@resourcekraft.com',
      license='MIT',
      packages=['comtradehandlers'],
      package_dir={ 'comtradehandlers': 'src',
                    'examples':'examples'},
      keywords=['COMTRADE', 'smartgrid', 'oscilloscope','power quality','power']
      )
