from typing import Dict, List
from pathlib import Path
from json import loads
from sys import argv


def check_result_consistency(results: Path) -> None:
    expected_hash: Dict[str, str] = {}
    expected_count: Dict[str, int] = {}
    received_count: Dict[str, List[int]] = {}
    print(f"Checking consistency in {results}")
    for result_path in results.iterdir():
        with open(result_path, "r") as result_file:
            data = loads(result_file.read())
        if data["engine_timeout_reached"] == True:
            continue
        config: str = data["engine_config"]
        query: str = data["engine_query"]
        result_hash: str = data["result_hash"]
        result_count: int = data["result_count"]
        if query not in expected_hash:
            expected_hash[query] = result_hash
            expected_count[query] = result_count
        elif expected_hash[query] != result_hash:
            print(f"Different results for <{query}>:")
            print(f"\tconfig: {config}")
            print(f"\tresults: {result_count} / {expected_count[query]}")
        if query not in received_count:
            received_count[query] = [result_count]
        else:
            received_count[query].append(result_count)

    for query, received_results in received_count.items():
        query_id: str = query.split("/")[-1].replace(".sparql", "")
        print(f"Result counts for {query_id}:", received_results)


if __name__ == "__main__":
    result_path: Path = Path(argv[1]).resolve()
    check_result_consistency(result_path)
