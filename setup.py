#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause

from typing                 import Callable, TypeAlias, Type
from setuptools             import setup, find_packages
from pathlib                import Path

ScmVersion: TypeAlias = Type['setuptools_scm.version.ScmVersion']

REPO_ROOT   = Path(__file__).parent
README_FILE = (REPO_ROOT / 'README.md')


def vcs_ver() -> dict[str, str | Callable[[ScmVersion], str]]:
	def scheme(version: ScmVersion) -> str:
		if version.tag and not version.distance:
			return version.format_with('')
		else:
			return version.format_choice('+{node}', '+{node}.dirty')
	return {
		'relative_to': __file__,
		'version_scheme': 'guess-next-dev',
		'local_scheme': scheme
	}

setup(
	name = 'bookwurm',
	use_scm_version  = vcs_ver(),
	author           = 'Aki \'lethalbit\' Van Ness',
	author_email     = 'nya@catgirl.link',
	description      = 'Ingest documents into meilisearch',
	license          = 'BSD-3-Clause',
	python_requires  = '~=3.10',
	zip_safe         = True,
	url              = 'https://github.com/lethalbit/bookwurm',

	long_description = README_FILE.read_text(),
	long_description_content_type = 'text/markdown',

	setup_requires = [
		'wheel',
		'setuptools',
		'setuptools_scm'
	],

	install_requires = [
		'Jinja2',
		'arrow',
		'rich',
		'meilisearch',
		'PyMuPDF',
	],

	packages = find_packages(
		where = '.',
		exclude = (
			'tests', 'tests.*', 'examples', 'examples.*'
		)
	),

	package_data = { },

	extras_require = {

	},

	entry_points = {
		'console_scripts': [
			'bookwurm = bookwurm.cli:main',
		]
	},

	classifiers = [
		'Development Status :: 4 - Beta',

		'Environment :: Console',
	],

	project_urls = {
		'Documentation': 'https://github.com/lethalbit/bookwurm',
		'Source Code'  : 'https://github.com/lethalbit/bookwurm',
		'Bug Tracker'  : 'https://github.com/lethalbit/bookwurm/issues',
	}
)
