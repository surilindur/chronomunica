<p align="center">
    <img alt="logo" src="./images/logo.svg" width="300">
</p>

Chronomunica is an experimental Python tool to measure query execution using [Comunica](https://github.com/comunica/comunica). The tool uses a combination of a proxy server and subprocess calls to execute queries using specific query engine configurations and queries. Please note that Chronomunica is not intended for actual use, and should be treated with caution. Thank you!

Currently, the tool will output:

* **Result count** and **hash** for validating the results. For the same set of results, the result count and hash should be identical. Individual results are not recorded, since the hash should be sufficient.
* **Result intervals** by checking the time between results arriving, for use in calculating, for example, the [diefficiency metrics](https://link.springer.com/chapter/10.1007/978-3-319-68204-4_1).
* **Requested URLs** using a proxy HTTP server between the query engine and the actual server. This may not work for all configurations, but for simple RDF data servers such as the [Community Solid Server](https://github.com/CommunitySolidServer/CommunitySolidServer) it seems to function.
* **Error** when an error happens, with the error itself serialized as a string for later use. When an error happens, the tool will skip further repetitions of a query.

## Usage

    TODO

## Docker

There is a Dockerfile provided, which can be built:

    $ docker build --network host --tag chronomunica:dev .

The file can then be used to run the utility:

    $ docker run --network host chronomunica:dev --help

The Docker image used for the query engine can then be based on this one.

## Issues

Please feel free to report any issues on the GitHub issue tracker, however do also note that this tool is not intendec for actual use and is more of an experiment in trying to get some timings out of Comunica without going over the top.
