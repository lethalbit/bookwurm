# SPDX-License-Identifier: BSD-3-Clause
import json
import logging          as log
from argparse           import ArgumentParser, Namespace
from pathlib            import Path
from io                 import StringIO, SEEK_SET, SEEK_END

from rich               import print
from rich.panel         import Panel

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
			'--detailed-results', '-D',
			action = 'store_true',
			help   = 'Enable detailed results'
		)

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

	def _print_detailed_results(self, results: dict, query: str, limit: int, idx: Index):
		CONTEXT_DELTA = 128
		for hit in results['hits']:
			doc_id      = hit['id']
			doc_path    = Path(json.loads(hit['file']))
			doc_meta    = f'[red]{hit["type"].upper()}[/], [yellow]{hit["total_pages"]} pages[/]'
			doc_matches = hit['_matchesPosition']

			print(f' [green]*[/] [cyan]{hit["title"]}[/] ([magenta]{len(doc_matches.keys())} matches[/])')
			print(f'   [link=file://{doc_path}][blue]{doc_path.stem}[/][/] ({doc_meta})')

			for page, matches in doc_matches.items():
				d = idx.get_document(doc_id, {
					'fields': [ page ]
				})

				if page.startswith('pages.'):
					page_idx = page.split('.')[-1]
					p = d.pages[page_idx]
					ibuff = StringIO(p)
					obuff = StringIO()

					obuff.seek(0, SEEK_SET)
					obuff.write('[dim]')

					curr_pos = 0
					for match in matches:
						start_pos = match['start']
						end_pos   = match['start'] + match['length']
						curr_pos  = start_pos - CONTEXT_DELTA
						if curr_pos < 0:
							curr_pos = start_pos

						ibuff.seek(curr_pos, SEEK_SET)
						obuff.write(ibuff.read(start_pos - curr_pos))
						obuff.write('[/][bold magenta]')
						obuff.write(ibuff.read(match['length']))
						obuff.write('[/][dim]')
						obuff.write(ibuff.read(end_pos + CONTEXT_DELTA))
						curr_pos = end_pos + CONTEXT_DELTA


					obuff.write('[/]')
					res = obuff.getvalue()
					obuff.close()
					ibuff.close()


					print(Panel(
						res.encode('utf-8').decode('unicode_escape').strip(),
						title = f'Page [cyan]{page_idx}[/] [dim magenta]({len(matches)} matches)[/]'
					))





	def _print_simple_results(self, results: dict, query: str, limit: int):
		for hit in results['hits']:
			doc_path = Path(json.loads(hit['file']))
			doc_meta = f'[red]{hit["type"].upper()}[/], [yellow]{hit["total_pages"]} pages[/]'

			print(f' [green]*[/] [cyan]{hit["title"]}[/] ([magenta]{len(hit["_matchesPosition"].keys())} matches[/])')
			print(f'   [link=file://{doc_path}][blue]{doc_path.stem}[/][/] ({doc_meta})')

	def run(self, args: Namespace, config: dict) -> int:
		query: str = args.query
		limit: int = args.limit
		detailed: bool = args.detailed_results

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

		results = idx.search(query, {
			'showMatchesPosition': True,
			'attributesToRetrieve': [
				'id', 'title', 'type', 'author', 'keywords', 'file', 'total_pages'
			],
			'showMatchesPosition': True,
			'limit': limit,
		})

		total = results['estimatedTotalHits']

		limited = ''
		if total > limit:
			limited = f'Showing {limit} of '

		print(f'{limited}{total} results found in {results["processingTimeMs"]}ms')

		if detailed:
			self._print_detailed_results(results, query, limit, idx)
		else:
			self._print_simple_results(results, query, limit)

		return 0
