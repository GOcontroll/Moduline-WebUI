from pathlib import Path
from runpy import run_path

pkg_dir = Path(__file__).resolve().parent


def execute_script():
    script_pth = pkg_dir / "go-webui.py"
    run_path(str(script_pth), run_name="__main__")
