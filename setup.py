from setuptools import setup

setup(
    name='azure-cli-dev',
    version="0.1",
    description='Microsoft Azure Command-Line Tools Core Module',
    long_description="test",
    license='MIT',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    url='https://github.com/bquantump/azclidev',
    zip_safe=False,
    classifiers=["Programming Language :: Python :: 3"],
    packages=['clidev'],
    install_requires=['pytest', 'virtualenv'],
    include_package_data=True,
    entry_points={
        'console_scripts': ['clidev=clidev.clidev:main']
    }
)
