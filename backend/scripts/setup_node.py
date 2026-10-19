"""
Automated user-space Node.js portable setup.
Downloads official Node.js LTS zip, extracts to %LOCALAPPDATA%\\Programs\\nodejs,
and runs npm install in frontend.
"""

import os
import sys
import urllib.request
import zipfile
import shutil
import subprocess

def setup_node():
    target_dir = os.path.expandvars(r"%LOCALAPPDATA%\Programs\nodejs")
    node_exe = os.path.join(target_dir, "node.exe")
    npm_cmd = os.path.join(target_dir, "npm.cmd")

    if not os.path.exists(node_exe):
        print(f"[INFO] Node.js not found at {target_dir}. Downloading official portable Node.js v20 LTS...")
        os.makedirs(target_dir, exist_ok=True)
        url = "https://nodejs.org/dist/v20.18.0/node-v20.18.0-win-x64.zip"
        zip_path = os.path.expandvars(r"%TEMP%\node-v20.18.0-win-x64.zip")

        print(f"[INFO] Downloading from {url}...")
        urllib.request.urlretrieve(url, zip_path)
        print(f"[INFO] Download complete ({os.path.getsize(zip_path)} bytes). Extracting...")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            temp_extract = os.path.expandvars(r"%TEMP%\node_extract")
            os.makedirs(temp_extract, exist_ok=True)
            zip_ref.extractall(temp_extract)
            extracted_sub = os.path.join(temp_extract, "node-v20.18.0-win-x64")
            for item in os.listdir(extracted_sub):
                src = os.path.join(extracted_sub, item)
                dst = os.path.join(target_dir, item)
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            shutil.rmtree(temp_extract, ignore_errors=True)
        os.remove(zip_path)
        print(f"[SUCCESS] Node.js extracted to {target_dir}")
    else:
        print(f"[INFO] Node.js already exists at {target_dir}")

    # Verify node version
    res = subprocess.run([node_exe, "--version"], capture_output=True, text=True)
    print(f"[INFO] Node version: {res.stdout.strip()}")

    # Run npm install in frontend
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
    print(f"[INFO] Running npm install in {frontend_dir}...")

    # Set PATH so npm finds node.exe
    env = os.environ.copy()
    env["PATH"] = f"{target_dir};" + env.get("PATH", "")

    npm_install = subprocess.run(
        [npm_cmd, "install"],
        cwd=frontend_dir,
        env=env,
        capture_output=True,
        text=True
    )
    print(npm_install.stdout)
    if npm_install.returncode != 0:
        print("[ERROR]", npm_install.stderr)
        return False

    print("[SUCCESS] Frontend packages installed successfully!")
    return True

if __name__ == "__main__":
    setup_node()
