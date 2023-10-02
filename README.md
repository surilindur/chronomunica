<p align="center">
    <img alt="logo" src="./images/logo.svg" width="300">
</p>

Chronomunica is an experimental tool to measure query execution using [Comunica](https://github.com/comunica/comunica). The tool can instantiate `QueryEngine` instances, execute queries with them and output collected metrics. Please note that Chronomunica is not intended for actual use, and should be treated with caution. Thank you!

Currently, the tool will output:

* **Result count** and **hash** for validating the results. For the same set of results, the result count and hash should be identical. Individual results are not recorded, since the hash should be sufficient.
* **Result intervals** by checking the time between results arriving, for use in calculating, for example, the [diefficiency metrics](https://link.springer.com/chapter/10.1007/978-3-319-68204-4_1).
* **Network request count** and **requested URLs** using a proxy `fetch` function. This relies on all network requests within the engine using this proxy function that gets passed in the context. When using a link traversal engine of Comunica, the Solid Type Index actor has to have its inference option disabled.
* **Error** when an error happens, with the error itself serialized as a string for later use. When an error happens, the tool will skip further repetitions of a query.

## Usage


    TODO

## Docker

    TODO

## Issues

Please feel free to report any issues on the GitHub issue tracker, however do also note that this tool is not intendec for actual use and is more of an experiment in trying to get some timings out of Comunica without going over the top.
