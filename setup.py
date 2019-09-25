from setuptools import setup

requirements = ["python>=3.6"]

setup(name='fairways',
      version='0.8',
      description='Toolset to organize batch tasks',
      url='https://gitlab.com/danwin/fairways_py#egg=fairways',
      author='Dmitry Zimoglyadov',
      author_email='dmitry.zimoglyadov@gmail.com',
      license='MIT',
      packages=['fairways'],
      zip_safe=False)