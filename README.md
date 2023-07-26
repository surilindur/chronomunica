<p align="center">
    <img alt="logo" src="./images/logo.svg" width="300">
</p>

Chronomunica is an experimental tool to measure query execution using [Comunica](https://github.com/comunica/comunica). The tool can instantiate `QueryEngine` instances, execute queries with them and output collected metrics. Please note that Chronomunica is not intended for actual use, and should be treated with caution. Thank you!

Currently, the tool will output:

* **Engine configuration** and **query** that were used for the execution.
* **Result count** and **hash** for validating the results. For the same set of results, the result count and hash should be identical.
* **Result intervals** by checking the time between results arriving, for use in calculating, for example, the [diefficiency metrics](https://link.springer.com/chapter/10.1007/978-3-319-68204-4_1).
* **Network request count** and **requested URLs** using a proxy `fetch` function. This relies on all network requests within the engine using this proxy function that gets passed in the context. When using a link traversal engine of Comunica, the Solid Type Index actor has to have its inference option disabled.
* **Error** when an error happens, with the error itself serialized as a string for later use. When an error happens, the tool will skip further repetitions of a query.

## Usage

The tool has not been published anywhere, but can be run locally. After cloning, install the dependencies:

    $ yarn install --immutable

The tool can then be executed:

    $ yarn chronomunica --engine .../config-default.json --query .../example-query.rq --output .../results.json

The following parameters are available:

| Environment variable   | Command line | Required | Description                                        |
|:-----------------------|:-------------|:--------:|:---------------------------------------------------|
| `CHRONOMUNICA_ENGINE`  | `--engine`   | ✓       | Path to query engine config to instantiate from    |
| `CHRONOMUNICA_QUERY`   | `--query`    | ✓       | Path to the file containing a SPARQL query to run  |
| `CHRONOMUNICA_OUTPUT`  | `--output`   | ✓       | Path to a file to serialize results into           |
| `CHRONOMUNICA_CONTEXT` | `--context`  |          | Path to a JSON file containing a query context     |
| `CHRONOMUNICA_HASH`    | `--hash`     |          | Hash function to use for results, default `sha256` |
| `CHRONOMUNICA_DIGEST`  | `--digest`   |          | Encoding to use for hash digest, default `hex`     |

The environment variable, when provided, will override command line arguments.

## Docker

There is a Dockerfile provided for building an image for local use. For example, to build the image for a non-existent tag:

    $ docker build --network host --tag solidlab/chronomunica:dev .

The image can then be used to run Chronomunica somewhere locally:

    $ docker run --init --network host solidlab/chronomunica:dev

The purpose of the Dockerfile is to be of use when running local experiments.

## Issues

Please feel free to report any issues on the GitHub issue tracker, however do also note that this tool is not intendec for actual use and is more of an experiment in trying to get some timings out of Comunica without going over the top.
