"""
CI smoke script: runs app-only compile and pytest from repo root.
"""
from pathlib import Path
import subprocess
import sys


def run(cmd, cwd=None):
    print("$", " ".join(cmd))
    res = subprocess.run(cmd, cwd=cwd, capture_output=False)
    if res.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(res.returncode)


if __name__ == '__main__':
    ROOT = Path(__file__).resolve().parents[1]
    run([sys.executable, str(ROOT / 'tools' / 'compile_app.py')], cwd=ROOT)
    run([sys.executable, '-m', 'pytest', '-q'], cwd=ROOT)