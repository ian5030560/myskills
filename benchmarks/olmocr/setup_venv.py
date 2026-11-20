#!/usr/bin/env python3
"""Create the isolated venv that holds the official olmOCR-Bench scorer.

The scorer needs Python 3.11+ and pulls in heavy dependencies (about 660 MB), so it lives
in its own venv under this folder instead of the repo's. Usage:

    python setup_venv.py --python <path to a Python 3.11+ interpreter>
"""

import argparse
import shutil
import subprocess
import sys

from bench_common import MIN_PYTHON, SCORER_REQUIREMENTS, VENV, die, venv_python


def _python_version(python: str) -> tuple:
    try:
        out = subprocess.run(
            [python, "-c", "import sys; print(sys.version_info[0], sys.version_info[1])"],
            capture_output=True, text=True, check=True,
        ).stdout.split()
    except (OSError, subprocess.CalledProcessError) as exc:
        die(f"Cannot run {python}: {exc}")
    return int(out[0]), int(out[1])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--python", required=True,
                        help="Python 3.11+ interpreter used to create the venv")
    parser.add_argument("--recreate", action="store_true", help="delete an existing venv first")
    args = parser.parse_args()

    version = _python_version(args.python)
    if version < MIN_PYTHON:
        die(f"{args.python} is Python {version[0]}.{version[1]}; the olmOCR scorer needs "
            f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer. Pass a newer interpreter with --python.")

    if VENV.exists() and args.recreate:
        shutil.rmtree(VENV)
    if not venv_python().exists():
        print(f"creating venv: {VENV}")
        subprocess.run([args.python, "-m", "venv", str(VENV)], check=True)

    print(f"installing: {' '.join(SCORER_REQUIREMENTS)}")
    result = subprocess.run([str(venv_python()), "-m", "pip", "install", *SCORER_REQUIREMENTS],
                            check=False)
    if result.returncode != 0:
        die("pip install failed. On Windows a long venv path can hit MAX_PATH; keep this repo "
            "close to the drive root or enable long paths.")
    print(f"venv: {VENV}")


if __name__ == "__main__":
    sys.exit(main())
