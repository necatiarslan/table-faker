from setuptools import setup, find_packages

with open("README.md") as file:
    description = file.read()

setup(
    name='tablefaker',
    version='1.0.0',
    description='A Python package for generating fake table data. Get data in pandas dataframe & pyarrow table or export to Csv, Json, Excel or Parquet',
    long_description = description,
    long_description_content_type = "text/markdown",
    author='Necati Arslan',
    author_email='necatia@gmail.com',
    packages=find_packages(),
    install_requires=[
        'faker',
        'pyyaml',
        'pandas',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries',
    ],
    project_urls={
        "Documentation": "https://github.com/necatiarslan/table-faker/README.md",
        "Source": "https://github.com/necatiarslan/table-faker",
    },
    entry_points={
        'console_scripts': [
            'tablefaker = tablefaker.cli:main',
        ],
    },
)