from setuptools import setup, find_packages

setup(
    name='severino',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'click',
        'google-generativeai',
        'llama-cpp-python[cuda]', # Ensure CUDA toolkit is installed for this
        'python-dotenv',
        'psutil', # For resource monitoring
    ],
    entry_points={
        'console_scripts': [
            'severino=main:cli', # This makes 'severino' command available after pip install
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A CLI for ML monitoring assistance using Gemma and Gemini.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your-repo/severino', # Replace with your actual repo
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', # Or your chosen license
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Utilities',
    ],
    python_requires='>=3.9',
)
