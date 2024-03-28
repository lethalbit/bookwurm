# SPDX-License-Identifier: BSD-3-Clause
import logging          as log
from argparse           import ArgumentParser, Namespace
from pathlib            import Path
import json

from rich.console       import Console

from meilisearch        import Client
from meilisearch.index  import Index
from meilisearch.errors import MeilisearchApiError

from .                  import BookwurmAction


class StatsAction(BookwurmAction):
	pretty_name = 'stats'
	short_help  = 'get index stats'

	def __init__(self):
		pass


	def register_args(self, parser: ArgumentParser) -> None:
		pass

	def run(self, args: Namespace, config: dict) -> int:
		console = Console()
		print = console.print


		meili = Client(
			f'{config["meilisearch"]["host"]}:{config["meilisearch"]["port"]}',
			f'{config["meilisearch"]["key"]}'
		)

		try:
			idx = meili.get_index('bookwurm')
		except MeilisearchApiError as e:
			log.error(f'Unable to query bookwurm index: {e.message}')
			return 1

		stats = idx.get_stats()

		print('[cyan]bookwurm index stats:[/]')
		print(f' * Number of Documents: {stats.number_of_documents}')

		return 0
