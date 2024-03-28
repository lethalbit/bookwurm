# bookwurm

> [!CAUTION]
> This is a very young, and very unstable project that was built for personal use.
> The index schema is not stable, nor how things are indexed, or anything else,
> if you **really** wan't to use this, do so with caution.

bookwurm is a super simple document index and search interface. It was built for my needs and my needs alone, but everyone is more than welcome to use it if they so see fit.


bookwurm is backed by a [meilisearch] instance for the actual maintaining and searching of the index, the instance doesn't need to stay up, it only needs to be alive when bookwurm is trying to search the index or populate the index.

## Installing

To install, you can just use [pipx] to do most of the heavy lifting.

```
$ pipx install git+https://github.com/lethalbit/bookwurm
```

Once that's done, make sure you have a local [meilisearch] somewhere, we just need the authorization key, host and port to dump in the bookwurm config.


The fastest way to get a bookwurm config is to just run bookwurm once, it'll then dump the default config to `$HOME/.config/bookwurm/config.json`. So, you can just run `bookwurm stats`, it'll fail, but that's fine, we have a config file now.


Next, open the configuration file, and make sure the `host`, `port`, and `key` in the `meilisearch` section are set correctly, it should look something like this:

```json
{
    "index_directories": [],
    "meilisearch": {
        "host": "http://127.0.0.1",
        "port": "7700",
        "key": "jVvpzuSrbgpLREZTmql-Rn8SpLwW7fLs0DwC8W8jMVs",
        "exec": "$HOME/.cache/bookwurm/meilisearch",
        "db_dir": "$HOME/.local/share/bookwurm/data.ms",
        "dump_dir": "$HOME/.local/share/bookwurm/dumps"
    }
}
```

You can safely ignore the last three options, they're not implemented yet.


## Usage

Prior to usage, make sure the configured [meilisearch] instance is running somewhere, you can shut it down when you're done with bookwurm.

To index a directory (this will take a loooong time):

```
$ python -m bookwurm index [-j NUM_THREADS] </path/to/directory>
```

To search index:

```
$ python -m bookwum search [-l RESULT_LIMIT] <query>
```

## License

bookwurm licensed under the [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) and can be found in [LICENSE.software](https://github.com/lethalbit/bookwurm/tree/main/LICENSE.software).


[meilisearch]: https://github.com/meilisearch/meilisearch
