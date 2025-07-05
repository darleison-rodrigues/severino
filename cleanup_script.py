import shutil, os

# Directories to remove
dirs_to_remove = [
    '.pytest_cache',
    '.venv',
    'logs',
    'data/cache',
    'data/sessions',
    'src/severino.egg-info'
]

for d in dirs_to_remove:
    full_path = os.path.join('C:/Users/darle/Documents/GitHub/severino', d)
    if os.path.exists(full_path):
        shutil.rmtree(full_path, ignore_errors=True)
        print(f"Removed directory: {full_path}")

# Remove __pycache__ directories
for root, dirs, files in os.walk('C:/Users/darle/Documents/GitHub/severino'):
    if '__pycache__' in dirs:
        shutil.rmtree(os.path.join(root, '__pycache__'), ignore_errors=True)
        print(f"Removed __pycache__ in: {root}")

# Remove specific files
files_to_remove = [
    'C:/Users/darle/Documents/GitHub/severino/create_dirs.py',
    'C:/Users/darle/Documents/GitHub/severino/create_dev_docs_dir.py'
]

for f in files_to_remove:
    if os.path.exists(f):
        os.remove(f)
        print(f"Removed file: {f}")
