from setuptools import setup, find_packages

requirements = ["python>=3.6"]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='fairways',
    use_scm_version={
        'version_scheme': 'python-simplified-semver',
        'local_scheme': 'no-local-version',
    },
    setup_requires=['setuptools_scm'],
    #   version='0.9.10',
    description='Toolset to organize tasks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitlab.com/danwin/fairways_py#egg=fairways',
    author='Dmitry Zimoglyadov',
    author_email='dmitry.zimoglyadov@gmail.com',
    license='Apache 2.0 / MIT',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'cached-property>=1.5.1',
        'colorlog>=4.0.2',
        'python-dateutil>=2.8.0',
        'python-dotenv>=0.10.3',
        'requests>=2.22.0',
    ],
    zip_safe=False)