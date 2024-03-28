# SPDX-License-Identifier: BSD-3-Clause
import json
import logging          as log
from argparse           import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace

from rich               import traceback
from rich.logging       import RichHandler

from .                  import paths
from .actions.index     import IndexAction
from .actions.search    import SearchAction
from .actions.stats     import StatsAction

__all__ = (
	'main',
)

BOOKWURM_CONFIG_DEFAULT = {
	'index_directories': [],
	'meilisearch': {
		'host'    : 'http://127.0.0.1',
		'port'    : '7700',
		'key'     : '',
		# The following params are not used yet, once we can
		# spin up our own melisearch instance when we need to
		# then they will be
		'exec'    : str(paths.BOOKWURM_CACHE / 'meilisearch'),
		'db_dir'  : str(paths.BOOKWURM_DATA  / 'data.ms'),
		'dump_dir': str(paths.BOOKWURM_DATA  / 'dumps'),
	}
}


def setup_logging(args: Namespace = None) -> None:
	'''
	Initialize logging subscriber

	Set up the built-in rich based logging subscriber, and force it
	to be the one at runtime in case there is already one set up.

	Parameters
	----------
	args : argparse.Namespace
		Any command line arguments passed.

	'''

	level = log.INFO
	if args is not None and args.verbose:
		level = log.DEBUG

	log.basicConfig(
		force    = True,
		format   = '%(message)s',
		datefmt  = '[%X]',
		level    = level,
		handlers = [
			RichHandler(rich_tracebacks = True, show_path = False)
		]
	)

def init_dirs() -> None:

	dirs = (
		paths.BOOKWURM_CACHE,
		paths.BOOKWURM_CONFIG,
		paths.BOOKWURM_DATA
	)

	for d in dirs:
		if not d.exists():
			d.mkdir(parents = True, exist_ok = True)

ACTIONS = (
	{ 'name': 'index',  'instance': IndexAction()  },
	{ 'name': 'search', 'instance': SearchAction() },
	{ 'name': 'stats',  'instance': StatsAction()  },
)

def main() -> int:
	traceback.install()
	setup_logging()
	init_dirs()

	parser = ArgumentParser(
		formatter_class = ArgumentDefaultsHelpFormatter,
		description     = 'Ingest documents',
		prog            = 'bookwurm'
	)

	core_options = parser.add_argument_group('Core Options')

	core_options.add_argument(
		'--verbose', '-v',
		action = 'store_true',
		help   = 'Enable verbose output'
	)

	action_parser = parser.add_subparsers(
		dest = 'action',
		required = True
	)

	if len(ACTIONS) > 0:
		for act in ACTIONS:
			action = act['instance']
			p = action_parser.add_parser(
					act['name'],
					help = action.short_help,
				)
			action.register_args(p)

	args = parser.parse_args()

	setup_logging(args)

	if not paths.BOOKWURM_CONFIG_FILE.exists():
		log.warning('bookwurm configuration file does not exist, creating default')
		with paths.BOOKWURM_CONFIG_FILE.open('w') as f:
			json.dump(BOOKWURM_CONFIG_DEFAULT, f, indent = 4)
		config = BOOKWURM_CONFIG_DEFAULT
	else:
		with paths.BOOKWURM_CONFIG_FILE.open('r') as f:
			config = json.load(f)

	if config['meilisearch']['key'] == '':
		log.error('You need to specify a milisearch key in the bookwurm config file')
		log.info(f'Config file is located at {paths.BOOKWURM_CONFIG_FILE}')
		return 1

	try:
		act = list(filter(lambda a: a['name'] == args.action, ACTIONS))[0]
		return act['instance'].run(args, config)
	except KeyboardInterrupt:
		log.info('bye!')
