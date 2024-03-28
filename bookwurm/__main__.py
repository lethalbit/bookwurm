#!/usr/bin/env python
# SPDX-License-Identifier: BSD-3-Clause
import sys
from pathlib import Path

try:
	from bookwurm.cli import main
except ImportError:
	bookwurm_path = Path(sys.argv[0]).resolve()

	if (bookwurm_path.parent / 'bookwurm').is_dir():
		sys.path.insert(0, str(bookwurm_path.parent))

	from bookwurm.cli import main

sys.exit(main())
