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


class SearchAction(BookwurmAction):
	pretty_name = 'serach'
	short_help  = 'preform index search'

	def __init__(self):
		pass



	def register_args(self, parser: ArgumentParser) -> None:
		parser.add_argument(
			'--limit', '-l',
			type    = int,
			default = 20,
			help    = 'Result limit'
		)

		parser.add_argument(
			'query',
			type = str
		)

	def run(self, args: Namespace, config: dict) -> int:
		query: str = args.query
		limit: int = args.limit

		console = Console()
		print = console.print

		print(f'Searching for: \'{query}\'')

		meili = Client(
			f'{config["meilisearch"]["host"]}:{config["meilisearch"]["port"]}',
			f'{config["meilisearch"]["key"]}'
		)

		try:
			idx = meili.get_index('bookwurm')
		except MeilisearchApiError as e:
			log.error(f'Unable to query bookwurm index: {e.message}')
			return 1

		res = idx.search(query, {
			'showMatchesPosition': True,
			'attributesToRetrieve': [
				'title', 'type', 'author', 'keywords', 'file', 'total_pages'
			],
			'showMatchesPosition': True,
			'limit': limit
		})

		total = res["estimatedTotalHits"]
		limited = ''
		if total > limit:
			limited = f'Showing {limit} of '

		print(f'{limited}{total} results found in {res["processingTimeMs"]}ms')

		for hit in res['hits']:
			print(f' [green]*[/] [cyan]{hit["title"]}[/] ([magenta]{len(hit["_matchesPosition"].keys())} matches[/])')

			doc_path = Path(json.loads(hit['file']))
			doc_meta = f'[red]{hit["type"].upper()}[/], [yellow]{hit["total_pages"]} pages[/]'

			print(f'   [link=file://{doc_path}][blue]{doc_path.stem}[/][/] ({doc_meta})')

		return 0
