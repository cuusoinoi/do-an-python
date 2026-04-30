import subprocess
import sys


def main() -> None:
    subprocess.run([sys.executable, "-m", "scripts.init_db"], check=True)
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--reload"], check=True)


if __name__ == "__main__":
    main()
