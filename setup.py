from setuptools import setup

requirements = ["python>=3.6"]

setup(name='fairways',
      version='0.2',
      description='Generator for digital vouchers',
      url='https://gitlab.com/danwin/fairways_py',
      author='Dmitry Zimoglyadov',
      author_email='dmitry.zimoglyadov@gmail.com',
      license='MIT',
      packages=['fairways'],
      zip_safe=False)