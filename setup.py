from setuptools import setup, find_packages
import os

setup(
    name='graph_analyzer',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        # List your project's dependencies here, for example:
        # 'numpy>=1.18.0',
    ],
    entry_points={
        'console_scripts': [
            'graph_analyzer=graph_analyzer.main:main',  # Allows running `graph_analyzer`
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A command-line tool for parsing graphs and processing IR files.',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://gitee.com/tajh/graph_analyzer.git',  # Replace with the correct URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
