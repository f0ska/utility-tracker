import os
import sys
import tempfile


APP_ID = "io.github.f0ska.utilitytracker"
APP_DIR_NAME = "utilitytracker"


def project_path(*parts):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *parts)


def user_data_dir():
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.join(
            os.path.expanduser("~"), ".local", "share"
        )
    return os.path.join(base, APP_DIR_NAME)


def user_state_dir():
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_STATE_HOME") or os.path.join(
            os.path.expanduser("~"), ".local", "state"
        )
    return os.path.join(base, APP_DIR_NAME)


def first_writable_path(filename, directories):
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=directory, delete=True):
                pass
            return os.path.join(directory, filename)
        except OSError:
            continue

    raise OSError(f"Could not create writable path for {filename}")


def database_path():
    legacy_path = project_path("utility_tracker.db")
    if os.path.exists(legacy_path):
        return legacy_path

    return first_writable_path(
        "utility_tracker.db",
        [user_data_dir(), os.path.dirname(legacy_path), os.path.join(tempfile.gettempdir(), APP_DIR_NAME)],
    )


def log_path():
    return first_writable_path(
        "app.log",
        [user_state_dir(), os.path.join(tempfile.gettempdir(), APP_DIR_NAME)],
    )


def icon_source_path():
    return project_path("icon.svg")


def linux_icon_dir():
    return os.path.join(
        os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share"),
        "icons",
        "hicolor",
        "scalable",
        "apps",
    )
