# bookwurm

bookwurm is a super simple document index and search interface. It was built for my needs and my needs alone, but everyone is more than welcome to use it if they so see fit.


bookwurm is backed by a [meilisearch] instance for the actual maintaining and searching of the index, the instance doesn't need to stay up, it only needs to be alive when bookwurm is trying to search the index or populate the index.

## Installing

TODO

## Usage

To index a directory:

```
$ python -m bookwurm index [-j NUM_THREADS] </path/to/directory>
```

To search index:

```
$ python -m bookwum search [-l RESULT_LIMIT] <query>
```
s
## License

bookwurm licensed under the [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) and can be found in [LICENSE.software](https://github.com/lethalbit/bookwurm/tree/main/LICENSE.software).


[meilisearch]: https://github.com/meilisearch/meilisearch
