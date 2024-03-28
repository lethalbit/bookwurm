# SPDX-License-Identifier: BSD-3-Clause
import logging          as log
from argparse           import ArgumentParser, Namespace
from pathlib            import Path
from concurrent.futures import ThreadPoolExecutor
from multiprocessing    import cpu_count
from hashlib            import blake2b
import json

from rich.progress      import (
	Progress, SpinnerColumn, BarColumn,
	TextColumn, TaskID
)

import fitz             as pymupdf
from meilisearch        import Client
from meilisearch.index  import Index
from meilisearch.errors import MeilisearchApiError

from .                  import BookwurmAction


class IndexAction(BookwurmAction):
	pretty_name = 'index'
	short_help  = 'preform file indexing'

	def __init__(self):
		pass

	def _collect_files(self, doc_dir: Path, pb: Progress, task: TaskID) -> list[Path]:
		dirs: list[Path] = list()
		files: list[Path] = list()

		dirs.append(doc_dir)
		while len(dirs) > 0:
			wd = dirs.pop()
			for d in wd.iterdir():
				if d.is_dir():
					dirs.append(d)
				elif d.is_file():
					files.append(d)
			pb.update(task, completed = len(files))

		return files

	def register_args(self, parser: ArgumentParser) -> None:
		parser.add_argument(
			'--jobs', '-j',
			type = int,
			default = cpu_count() // 4,
			help    = 'Number of parallel threads to run indexing on'
		)

		parser.add_argument(
			'directory',
			type = Path
		)

	def run(self, args: Namespace, config: dict) -> int:
		threads: int = args.jobs
		root: Path = args.directory

		if not root.exists():
			log.error(f'Directory \'{root}\' does not exist, aborting')
			return 1

		log.info(f'Indexing \'{root}\' with {threads} threads')

		pb = Progress(
			SpinnerColumn(),
			TextColumn('{task.description} [bold blue]{task.fields[name]: <50.50}', justify = 'left'),
			BarColumn(),
			TextColumn('{task.completed}/{task.total}'),
		)


		def _index_pdf(f: Path, doc_id: str, idx: Index, cli: Client, task: TaskID):
			pdf = pymupdf.Document(f.resolve())


			title = pdf.metadata.get('title')
			author = pdf.metadata.get('author')
			keywords = pdf.metadata.get('keywords')

			if title is None:
				title = ''

			if author is None:
				author = ''

			if keywords is None:
				keywords = ''

			title       = title.strip().replace('\\x00', '')
			author      = author.strip().replace('\\x00', '')
			keywords    = keywords.strip().split(' ')
			total_pages = pdf.page_count

			if title == '':
				title = f.name

			pb.update(task, total = total_pages)
			pb.start_task(task)

			pages = {}
			for page_number in range(0, total_pages):
				page = pdf.load_page(page_number)
				pages[page_number] = json.dumps(page.get_text())
				pb.advance(task)

			rec = {
				'id': doc_id,
				'type': 'pdf',
				'file': json.dumps(str(f.resolve())),
				'title': title,
				'author': author,
				'keywords': keywords,
				'total_pages': total_pages,
				'pages': pages,
			}

			pb.update(task, description = 'Writing to index')
			res = idx.add_documents([rec])
			t = meili.wait_for_task(res.task_uid, timeout_in_ms = 100_000, interval_in_ms = 500)
			if t.error is not None:
				log.error(f'Failed add to index: {t.error["message"]}')

		def _index_text(f: Path, doc_id: str, idx: Index, cli: Client, task: TaskID):
			pass

		def _index_csv(f: Path, doc_id: str, idx: Index, cli: Client, task: TaskID):
			pass



		def _index(elem: tuple[Path, Client, Index, TaskID]):
			f: Path = elem[0]
			meili: Client = elem[1]
			idx: Index = elem[2]
			root_task: TaskID = elem[3]

			h = blake2b(key = f.name.encode('utf-8')[:64])
			h.update(str(f.parent).encode('utf-8'))
			doc_id = h.hexdigest()[:64]

			try:
				idx.get_document(doc_id)
				log.debug(f'Already indexed \'{f}\', skipping')
				pb.advance(root_task)
				return
			except MeilisearchApiError as e:
				if e.code != 'document_not_found':
					raise e

			index_method = {
				'.pdf': _index_pdf,
				# '.html': _index_text,
				# '.txt': _index_text,
				# '.csv': _index_csv,
			}.get(f.suffix, None)

			if index_method is None:
				log.error(f'Unable to index file \'{f}\', skipping')
				return

			task = pb.add_task('Processing', name = str(f), start = False)
			try:
				index_method(f, doc_id, idx, meili, task)
				pb.advance(root_task)
			except Exception as e:
				log.error(f'Unable to index document \'{f}\': {e}')

			pb.remove_task(task)

		with pb:
			root_task = pb.add_task('Collecting from', name = str(root), start = False, total = None)
			files = self._collect_files(root, pb, root_task)
			pb.update(root_task, total = len(files), completed = 0, description = 'Indexing from')
			pb.start_task(root_task)

			meili = Client(
				f'{config["meilisearch"]["host"]}:{config["meilisearch"]["port"]}',
				f'{config["meilisearch"]["key"]}'
			)

			try:
				idx = meili.get_index('bookwurm')
			except MeilisearchApiError as e:
				if e.code == 'index_not_found':
					idx = self._make_meili_index(meili)

			with ThreadPoolExecutor(max_workers = threads) as pool:
				pool.map(_index, map(lambda f: (f, meili, idx, root_task), files))

		return 0

	def _make_meili_index(self, meili: Client) -> Index:
		res = meili.create_index('bookwurm', {
			"primaryKey": "id"
		})

		task = meili.wait_for_task(res.task_uid)
		if task.error is not None:
			log.error(f'Failed to create index: {task.error["message"]}')

		return meili.get_index('bookwurm')
