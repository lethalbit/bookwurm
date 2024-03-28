# SPDX-License-Identifier: BSD-3-Clause

from sys import version_info

# Bounce out if python is  too old
if version_info < (3, 10):
	raise RuntimeError('Python version 3.10 or newer is required to use bookwurm')

try:
	from importlib import metadata
	__version__ = metadata.version(__package__)
except ImportError:
	__version__ = 'unknown' # :nocov:

__all__ = ()
