# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path
from os      import environ


def _get_xdg_dir(name: str, default: Path) -> Path:
	if name in environ:
		return Path(environ[name])
	return default

HOME_DIR   = _get_xdg_dir('XDG_HOME',        Path.home()                )
CACHE_DIR  = _get_xdg_dir('XDG_CACHE_HOME',  (HOME_DIR / '.cache')      )
DATA_DIR   = _get_xdg_dir('XDG_DATA_HOME',   (HOME_DIR / '.local/share'))
CONFIG_DIR = _get_xdg_dir('XDG_CONFIG_HOME', (HOME_DIR / '.config')     )

del _get_xdg_dir

BOOKWURM_CACHE  = (CACHE_DIR  / 'bookwurm')
BOOKWURM_DATA   = (DATA_DIR   / 'bookwurm')
BOOKWURM_CONFIG = (CONFIG_DIR / 'bookwurm')


BOOKWURM_CONFIG_FILE = (BOOKWURM_CONFIG / 'config.json')
