from setuptools import setup, find_packages

with open("README.md") as file:
    description = file.read()

setup(
    name='tablefaker',
    version='1.8.0',
    description='A Python package to generate fake tabular data. Get data in pandas dataframe or export to Parquet, DeltaLake, Csv, Json, Excel or Sql',
    long_description = description,
    long_description_content_type = "text/markdown",
    author='Necati Arslan',
    author_email='necatia@gmail.com',
    keywords='faker, fake data, tabular data, data generation, pandas, parquet, csv, json, excel, sqllite, delta lake',
    packages=find_packages(),
    python_requires=">=3.9",
    license='Apache License 2.0',
    url="https://github.com/necatiarslan/table-faker",
    install_requires=[
        'faker',
        'pyyaml',
        'pandas',
        'openpyxl',
        'fastparquet',
        'psutil'
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
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Operating System :: OS Independent',
    ],
    project_urls={
        "Documentation": "https://github.com/necatiarslan/table-faker/blob/main/README.md",
        "Source": "https://github.com/necatiarslan/table-faker",
    },
    entry_points={
        'console_scripts': [
            'tablefaker = tablefaker.cli:main',
        ],
    },
)