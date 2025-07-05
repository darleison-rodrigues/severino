from setuptools import setup, find_packages

setup(
    name='severino',
    version='0.1.0',
    # Explicitly list top-level packages
    packages=['src', 'packages'],
    # Map where these packages are located
    package_dir={
        'src': 'src',
        'packages': 'packages'
    },
    include_package_data=True,
    install_requires=[
        'click',
        
        'llama-cpp-python[cuda]',
        'python-dotenv',
        'psutil',
        'rich',
    ],
    entry_points={
        'console_scripts': [
            'severino=src.main:cli', # Corrected entry point
        ],
    },
    author='Creator',
    author_email='your.email@example.com',
    description='A CLI for ML monitoring assistance using Gemma.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your-repo/severino',
    license='Severino Custom Non-Commercial License',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: Other/Proprietary License', # Custom Non-Commercial License
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Utilities',
    ],
    python_requires='>=3.9',
)