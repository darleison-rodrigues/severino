import subprocess
import hashlib
import os
from typing import Dict, List, Optional

def get_git_status(repo_path: str) -> Dict[str, List[str]]:
    """
    Gets the status of the Git repository.
    Returns a dictionary with lists of modified, untracked, and staged files.
    """
    status = {
        "modified": [],
        "untracked": [],
        "staged": []
    }
    try:
        # Check for modified and untracked files
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith(' M') or line.startswith('MM'):
                status["modified"].append(line[3:])
            elif line.startswith('??'):
                status["untracked"].append(line[3:])
            elif line.startswith('A ') or line.startswith('M '): # Staged changes
                status["staged"].append(line[3:])

        return status
    except subprocess.CalledProcessError as e:
        print(f"Error getting git status: {e}")
        return status
    except FileNotFoundError:
        print("Git command not found. Please ensure Git is installed and in your PATH.")
        return status

def generate_file_checksum(file_path: str, hash_algorithm: str = "sha256") -> Optional[str]:
    """
    Generates a checksum for a given file.
    """
    if not os.path.exists(file_path):
        return None

    hasher = hashlib.new(hash_algorithm)
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error generating checksum for {file_path}: {e}")
        return None

# Example Usage
if __name__ == "__main__":
    # Create dummy files for testing
    if not os.path.exists("temp_repo"):
        os.makedirs("temp_repo")
    
    with open("temp_repo/file1.txt", "w") as f:
        f.write("This is file 1.")
    with open("temp_repo/file2.txt", "w") as f:
        f.write("This is file 2.")

    # Initialize a dummy git repo
    subprocess.run(["git", "init"], cwd="temp_repo", capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd="temp_repo", capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd="temp_repo", capture_output=True, text=True)

    print("\n--- Initial Git Status ---")
    status = get_git_status("temp_repo")
    print(status)

    # Modify a file
    with open("temp_repo/file1.txt", "a") as f:
        f.write("\nModified content.")
    
    # Create an untracked file
    with open("temp_repo/new_file.txt", "w") as f:
        f.write("This is a new file.")

    print("\n--- Git Status After Changes ---")
    status = get_git_status("temp_repo")
    print(status)

    print("\n--- Checksums ---")
    checksum1 = generate_file_checksum("temp_repo/file1.txt")
    checksum2 = generate_file_checksum("temp_repo/file2.txt")
    print(f"Checksum for file1.txt: {checksum1}")
    print(f"Checksum for file2.txt: {checksum2}")

    # Clean up dummy repo
    subprocess.run(["rmdir", "/s", "/q", "temp_repo"], shell=True, capture_output=True, text=True)
    print("\nCleaned up temp_repo.")
