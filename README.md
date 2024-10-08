[![Actions Status](https://github.com/bytewax/bytewax-rerun/workflows/CI/badge.svg)](https://github.com/bytewax/bytewax-rerun/actions)
[![PyPI](https://img.shields.io/pypi/v/bytewax-rerun.svg?style=flat-square)](https://pypi.org/project/bytewax-rerun/)
[![Bytewax User Guide](https://img.shields.io/badge/user-guide-brightgreen?style=flat-square)](https://docs.bytewax.io/projects/bytewax-rerun/en/stable/)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/6073079/195393689-7334098b-a8cd-4aaa-8791-e4556c25713e.png" width="350">
  <source media="(prefers-color-scheme: light)" srcset="https://user-images.githubusercontent.com/6073079/194626697-425ade3d-3d72-4b4c-928e-47bad174a376.png" width="350">
  <img alt="Bytewax">
</picture>

## Bytewax Rerun

Modules to make rerun integration easy.

This modules offers a single `Sink`: `RerunSink`.
This makes it easy to log messages to `Rerun` from bytewax, properly handling multiple workers.
You can instantiate as many sinks as you need, and you have to pass a `RerunMessage` to them:

```python
op.output("rerun-time-sink", messages_stream, RerunSink("app_id", "recording_id"))
```

`RerunMessage` is a helper class that defines an entity that can be logged into `Rerun` with
all the properties needed:

```python
message = RerunMessage(
    entity_path=f"metrics/{name}",
    entity=rr.Scalar(value),
    timeline="metrics",
    time=seconds_since_start,
)
```

The sink supports all `Rerun`'s operating modes: `spawn`, `connect`, `save` and `serve`.
So you can use the sink to record metrics to a file for each worker, and later use the `Rerun` viewer
to replay all the recordings togheter.

The sink also offers a `RerunSink.rerun_log` decorator. If you decorate any of your functions with this, `Bytewax` will log the moment the function was called, and how long it took to run the function into a separate timeline in `Rerun`. The metrics are divided by worker, so you can see when each one is activated and for how long. You can optionally log the arguments used in each function, so you can see your items flowing through the dataflow.

## Setting up the project for development

### Install `just`

We use [`just`](https://just.systems/man/en/) as a command runner for
actions / recipes related to developing Bytewax. Please follow [the
installation
instructions](https://github.com/casey/just?tab=readme-ov-file#installation).
There's probably a package for your OS already.

### Install `pyenv` and Python 3.12

I suggest using [`pyenv`](https://github.com/pyenv/pyenv)
to manage python versions.
[the installation instructions](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation).

You can also use your OS's package manager to get access to different
Python versions.

Ensure that you have Python 3.12 installed and available as a "global
shim" so that it can be run anywhere. The following will make plain
`python` run your OS-wide interpreter, but will make 3.12 available
via `python3.12`.

```console
$ pyenv global system 3.12
```

## Install `uv`

We use [`uv`](https://github.com/astral-sh/uv) as a virtual
environment creator, package installer, and dependency pin-er. There
are [a few different ways to install
it](https://github.com/astral-sh/uv?tab=readme-ov-file#getting-started),
but I recommend installing it through either
[`brew`](https://brew.sh/) on macOS or
[`pipx`](https://pipx.pypa.io/stable/).

## Install `just`

We use [`just`](https://just.systems/man/en/) as a command runner for
actions / recipes related to developing Bytewax. Please follow [the
installation
instructions](https://github.com/casey/just?tab=readme-ov-file#installation).
There's probably a package for your OS already.

## Development

We have a `just` recipe that will:

1. Set up a venv in `venvs/dev/`.

2. Install all dependencies into it in a reproducible way.

Start by adding any dependencies that are needed into [pyproject.toml](pyproject.toml) or into
[requirements/dev.in](requirements/dev.in) if they are needed for development.

Next, generate the pinned set of dependencies with

```console
> just venv-compile-all
```

## Create and activate a virtual environment

Once you have compiled your dependencies, run the following:

```console
> just get-started
```

Activate your development environment and run the development task:

```console
> . venvs/dev/bin/activate
> just develop
```

## License

`bytewax-rerun` is commercially licensed with
publicly available source code. You are welcome to prototype using
this module for free, but any use on business data requires a paid
license. See https://modules.bytewax.io/ for a license. Please see the
full details in [LICENSE](./LICENSE.md).
