"""py2app build config for producing a double-clickable .app bundle.

Run from this directory, because the paths below are relative to it:
`cd packaging && ../.venv/bin/python setup.py py2app`. The bundle appears in packaging/dist/.
PyInstaller is the fallback (see README) if py2app proves incompatible with PySide6.
"""

from setuptools import setup

APP = ["../src/rsync_sync_gui/__main__.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "packages": ["PySide6"],
    "iconfile": "AppIcon.icns",
    "plist": {
        "CFBundleName": "Rsync Sync GUI",
        "CFBundleDisplayName": "Rsync Sync GUI",
        "CFBundleIdentifier": "com.local.rsyncsyncgui",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1.0.0",
        "LSMinimumSystemVersion": "12.0",
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
