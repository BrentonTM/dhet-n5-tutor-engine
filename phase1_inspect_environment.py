# Install required Python packages for the environment inspection script.
# This script executes the requested pip install command.

import subprocess
import sys

PACKAGES = [
    "pydantic",
    "fastapi",
    "uvicorn",
    "pandas",
    "apscheduler",
    "pyyaml",
]

subprocess.check_call([sys.executable, "-m", "pip", "install", *PACKAGES])
