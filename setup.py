from cx_Freeze import setup, Executable
import sys

build_exe_options = {
    "packages": ["fastapi", "uvicorn", "serial", "numpy", "scipy", "control"],
    "include_files": [
        ("models/", "models/"),
        ("templates/", "templates/")
    ]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="VirtualLab Control Systems Agent",
    version="1.0",
    description="Local hardware interface for VirtualLab",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, 
                           target_name="VirtualLabAgent.exe")]
)
