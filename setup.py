import os
from setuptools import setup, find_packages

base_dependencies = ['beautifulsoup4', 'pandas']
dev_dependencies = ['pandas-profiling',
                    'pytest'
                    'requests',
                    'seaborn',
                    'tqdm']
setup(
    name='properties_scrapper',    
    install_requires=base_dependencies,
    extras_require={
        'dev': dev_dependencies
    },
    description='',
    packages=find_packages(where='src'),
    package_dir={"": "src"}
)