"""
CI smoke script: runs app-only compile and pytest.
"""
import subprocess
import sys

def run(cmd):
    print("$", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=False)
    if res.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(res.returncode)

if __name__ == '__main__':
    run([sys.executable, 'tools/compile_app.py'])
    run([sys.executable, '-m', 'pytest', '-q'])
