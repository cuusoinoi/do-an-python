import subprocess
import sys


def main() -> None:
    init = subprocess.run([sys.executable, "-m", "scripts.init_db"])
    if init.returncode != 0:
        sys.exit(init.returncode)
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--reload"], check=True)


if __name__ == "__main__":
    main()
