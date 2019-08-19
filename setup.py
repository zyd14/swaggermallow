import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='swaggermallow',
    version='0.0.1',
    author='zromer@fredhutch.org',
    description='Provides basic tools for converting Marshmallow Schemas to flask-restplus Models so they can be used in flask-restplus decorators for generating Swagger documentation.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/zyd14/swaggermallow',
    packages=setuptools.find_packages(),
    install_requires=[
                    "aniso8601==7.0.0",
                    "atomicwrites==1.3.0",
                    "attrs==19.1.0",
                    "Click==7.0",
                    "coverage==4.5.4",
                    "Flask==1.0.2",
                    "Flask-RESTful==0.3.6",
                    "flask-restful-swagger==0.20.1",
                    "flask-restplus==0.13.0",
                    "importlib-metadata==0.19",
                    "itsdangerous==1.1.0",
                    "Jinja2==2.10.1",
                    "jsonschema==3.0.2",
                    "MarkupSafe==1.1.1",
                    "marshmallow==2.19.2",
                    "more-itertools==7.2.0",
                    "pluggy==0.12.0",
                    "py==1.8.0"
                    "pyrsistent==0.15.4",
                    "pytest==3.8.2",
                    "pytest-cov>=2.7.1",
                    "pytz==2019.2",
                    "six==1.12.0",
                    "Werkzeug==0.15.5",
                    "zipp==0.5.2"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
