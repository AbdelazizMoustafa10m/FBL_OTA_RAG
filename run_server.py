import os
import subprocess

# Set the PORT environment variable explicitly
os.environ["PORT"] = "8080"

# Run the main.py script with the new PORT setting
subprocess.run(["python", "main.py"])
