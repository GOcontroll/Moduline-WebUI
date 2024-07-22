from os import chdir
from pathlib import Path
from runpy import run_path

pkg_dir = Path(__file__).resolve().parent


def execute_script():
    script_pth = pkg_dir / "go-webui.py"
    chdir(pkg_dir.parent)
    run_path(str(script_pth), run_name="__main__")
