import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='ApiToolbox',
    version='0.0.1',
    author='zromer@fredhutch.org',
    description='Provides basic tools for quickly implementing RESTful APIs in Flask',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sciscogenetics/ApiToolbox',
    packages=setuptools.find_packages(),
    install_requires=["aws_xray_sdk==2.4.0",
                        "boto3==1.9.93",
                        "Flask==1.0.2",
                        "flask-RESTful==0.3.6",
                        "marshmallow==2.19.2",
                        "moto==1.3.7",
                        "pytest>=3.8.0",
                        "pytest-cov>=2.7.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
