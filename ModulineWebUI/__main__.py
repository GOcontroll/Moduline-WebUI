from os import chdir
from pathlib import Path
from runpy import run_path

pkg_dir = Path(__file__).resolve().parent


# shim function to allow auto generated script to run the actual main script
def execute_script():
    script_pth = pkg_dir / "go_webui.py"
    # fix the working directory so the file paths are correct
    chdir(pkg_dir.parent)
    run_path(str(script_pth), run_name="__main__")
