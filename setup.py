from setuptools import setup, find_packages

requirements = ["python>=3.6"]

setup(name='fairways',
      version='0.9.6',
      description='Toolset to organize tasks',
      url='https://gitlab.com/danwin/fairways_py#egg=fairways',
      author='Dmitry Zimoglyadov',
      author_email='dmitry.zimoglyadov@gmail.com',
      license='Apache 2.0',
      packages=find_packages(),
      zip_safe=False)