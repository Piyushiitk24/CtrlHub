from cx_Freeze import setup, Executable
import sys

build_exe_options = {
    "packages": [
        "fastapi", "uvicorn", "serial", "numpy", "scipy", "control",
        "tkinter", "asyncio", "json", "logging", "threading"
    ],
    "include_files": [
        ("local_agent/models/", "models/"),
        ("local_agent/hardware/", "hardware/"),
        ("local_agent/simulations/", "simulations/"),
        ("local_agent/controllers/", "controllers/")
    ],
    "excludes": ["matplotlib", "pandas"]  # Exclude heavy packages not needed
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="CtrlHub Control Systems Agent",
    version="1.0.0",
    description="Local hardware interface and simulation engine for CtrlHub",
    author="CtrlHub Education",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "local_agent/main.py", 
            base=base, 
            target_name="CtrlHubAgent.exe" if sys.platform == "win32" else "CtrlHubAgent",
            icon=None  # Add icon path if available
        )
    ]
)
