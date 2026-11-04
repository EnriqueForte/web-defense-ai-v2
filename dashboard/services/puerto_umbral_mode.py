"""Session-scoped source shared by Flask and its idle manual worker."""
import json
import os
from pathlib import Path

from dashboard.services.read_store import atomic_write_text, capture_file
from dashboard.services.structured_publication import _directory

ROOT = Path(__file__).resolve().parents[2]
MODES = {'corrected', 'vulnerable'}


def selection_path():
    value = os.getenv('PUERTO_UMBRAL_MODE_FILE')
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute() or not path.resolve().is_relative_to((ROOT / '.local-state' / 'launcher').resolve()):
        raise ValueError('invalid_source_selection_path')
    if path.name != 'source-mode.json':
        raise ValueError('invalid_source_selection_path')
    return _directory(path)


def selected_mode():
    path = selection_path()
    if path is None:
        mode = os.getenv('PUERTO_UMBRAL_MODE', 'vulnerable')
    else:
        captured = capture_file(path)
        if captured.status != 'available' or captured.size > 1024:
            raise ValueError('invalid_source_selection')
        value = json.loads(captured.text)
        if type(value) is not dict or set(value) != {'schema_version', 'mode'} or value['schema_version'] != 1:
            raise ValueError('invalid_source_selection')
        mode = value['mode']
    if not isinstance(mode, str) or mode not in MODES:
        raise ValueError('invalid_source_mode')
    return mode


def select_mode(mode):
    if not isinstance(mode, str) or mode not in MODES:
        raise ValueError('invalid_source_mode')
    path = selection_path()
    if path is None:
        raise ValueError('source_selection_unavailable')
    atomic_write_text(path, json.dumps({'schema_version': 1, 'mode': mode}))
