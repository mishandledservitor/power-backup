"""py2app build config for producing a double-clickable .app bundle.

Run from the repo root: `python packaging/setup.py py2app`
Falls back to PyInstaller (see README) if py2app proves incompatible with PySide6.
"""

from setuptools import setup

APP = ["../src/rsync_sync_gui/__main__.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "packages": ["PySide6"],
    "plist": {
        "CFBundleName": "Rsync Sync GUI",
        "CFBundleDisplayName": "Rsync Sync GUI",
        "CFBundleIdentifier": "com.local.rsyncsyncgui",
        "CFBundleShortVersionString": "0.1.0",
        "LSMinimumSystemVersion": "12.0",
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
