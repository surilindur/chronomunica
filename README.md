<p align="center">
    <img alt="logo" src="https://raw.githubusercontent.com/surilindur/chronomunica/main/images/logo.svg" width="250">
</p>

<p align="center">
    <img alt="ci" src="https://github.com/surilindur/chronomunica/actions/workflows/ci.yml/badge.svg">
    <img alt="black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
</p>

Chronomunica is an experimental Python tool to measure query execution using [Comunica](https://github.com/comunica/comunica). The tool uses a combination of a proxy server and subprocess calls to execute queries using specific query engine configurations and queries. Please note that Chronomunica is not intended for actual use, and should be treated with caution. If you want to actually run benchmarks, look into using [jbr.js](https://github.com/rubensworks/jbr.js).

Currently, the tool will output:

* **Requested URLS** using a proxy HTTP server between the query engine and the actual server, including **request count** and **unique URL count**.
* **Query results** captured from the CLI output of the query engine, including **result count**, **unique result count**, **result hash** and **result arrival times** in nanoseconds for use in calculating, for example, the [diefficiency metrics](https://link.springer.com/chapter/10.1007/978-3-319-68204-4_1).
* **Unrecognised engine CLI output** and the times of their capture, to help capture debug prints and other output that is not recognised as query results but could be useful for examining together with the results.
* **Start and end times** and the total time taken in seconds, to help spot when a query execution takes unnecessarily long even with a timeout.
* **Errors** from the query engine stderr or when another error occurs, to help inspect issues later.

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
