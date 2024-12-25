import os
from pathlib import Path


def find_project_root(current_dir=None):
    if current_dir is None:
        current_dir = os.getcwd()

    while True:
        # Check if the current directory contains a known project file or directory (e.g., setup.py, .git, etc.)
        if any(os.path.exists(os.path.join(current_dir, marker)) for marker in
               ['setup.py', '.git']):
            return Path(current_dir)

        # Move up one level in the directory hierarchy
        parent_dir = os.path.dirname(current_dir)

        # If we've reached the root directory, stop searching
        if parent_dir == current_dir:
            raise FileNotFoundError("Project root not found")

        current_dir = parent_dir
