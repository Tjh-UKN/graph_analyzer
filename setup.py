from setuptools import setup, find_packages

setup(
    name='graph_parser_tool',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        # List your project's dependencies here, for example:
        # 'numpy>=1.18.0',
    ],
    entry_points={
        'console_scripts': [
            'graph_parser=graph_parser:main',  # Allows running `graph_parser`
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A command-line tool for parsing graphs and processing IR files.',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/your-repo/graph-parser',  # Replace with the correct URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
