from setuptools import setup, find_packages

requirements = ["python>=3.3"]

setup(name='fairways',
      version='0.9.7',
      description='Toolset to organize tasks',
      url='https://gitlab.com/danwin/fairways_py#egg=fairways',
      author='Dmitry Zimoglyadov',
      author_email='dmitry.zimoglyadov@gmail.com',
      license='Apache 2.0',
      packages=find_packages(),
      install_requires=[
            'cached-property>=1.5.1',
            'colorlog>=4.0.2',
            'python-dateutil>=2.8.0',
            'python-dotenv>=0.10.3',
            'requests>=2.22.0',
      ],
      zip_safe=False)