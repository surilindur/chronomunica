import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { basename, join } from 'node:path';
import { QueryEngineFactory } from '@comunica/query-sparql';
import type { IQueryEngine, QueryStringContext, BindingsStream, Bindings } from '@comunica/types';
import { BindingsHash } from './BindingsHash';
import { createFetchCounter, type IFetchCounter } from './FetchCounter';

export interface IQueryResult {
  hash: string;
  requests: number;
  results: number;
  query: string;
  config: string;
  intervals: number[];
  error?: any;
}

export interface IQueryParameters {
  configPath: string;
  queryPath: string;
  resultPath: string;
  repeat: number;
}

export function executeAndMeasure(args: IQueryParameters): Promise<IQueryResult> {
  return new Promise((resolve, reject) => {
    // Read the query from the file
    const queryString: string = readFileSync(args.queryPath, { encoding: 'utf-8' });

    // Create the fetch counter, bindings hasher and intervals array
    const bindingsHash: BindingsHash = new BindingsHash();
    const fetchCounter: IFetchCounter = createFetchCounter();
    const intervals: number[] = [];
    let results = 0;

    // Create the factory and the engine
    const factory: QueryEngineFactory = new QueryEngineFactory();

    // Query start time and current time
    const queryStartTime = Date.now();
    let previousTime = queryStartTime;
    let currentTime = queryStartTime;

    // Execute the query and measure the results
    const queryStringContext: QueryStringContext = <QueryStringContext>{ fetch: fetchCounter.fetch };

    // Output the results, whether errored out or not
    const generateOutput = (error?: any): IQueryResult => ({
      hash: bindingsHash.digest('hex'),
      config: basename(args.configPath),
      query: basename(args.queryPath),
      intervals,
      requests: fetchCounter.count,
      results,
      error,
    });

    factory.create({ configPath: args.configPath, logLevel: 'error' }).then((engine: IQueryEngine) => {
      engine.queryBindings(queryString, queryStringContext).then((bindingsStream: BindingsStream) => {
        bindingsStream
          .on('data', (bindings: Bindings) => {
            // Include new result in hash
            bindingsHash.add(bindings);
            // Increment result counter
            results++;
            // Register the passed interval
            currentTime = Date.now();
            intervals.push(currentTime - previousTime);
            previousTime = currentTime;
          })
          .on('error', reason => resolve(generateOutput(reason)))
          .on('end', () => resolve(generateOutput()));
      }).catch(reject);
    }).catch(reject);
  });
}

export async function executeAndMeasureRepeat(args: IQueryParameters): Promise<IQueryResult[]> {
  const results: IQueryResult[] = [];
  for (let i = 0; i < args.repeat; i++) {
    results.push(await executeAndMeasure(args));
  }
  return results;
}

export async function executeAndSerializeMultiple(
  configs: string,
  queries: string,
  output: string,
  repeat: number,
): Promise<void> {
  for (const config of readdirSync(configs, { withFileTypes: true, recursive: false })) {
    if (!config.isFile()) {
      continue;
    }
    for (const query of readdirSync(queries, { withFileTypes: true, recursive: false })) {
      if (!query.isFile()) {
        continue;
      }
      const configPath = join(config.path, config.name);
      const queryPath = join(query.path, query.name);
      const resultPath = join(output, `${config.name.split('.')[0]}-${query.name.split('.')[0]}.json`);
      const results = await executeAndMeasureRepeat({
        configPath,
        queryPath,
        resultPath,
        repeat,
      });
      // eslint-disable-next-line no-console
      console.log(`Serialize: ${resultPath}`, results);
      writeFileSync(resultPath, JSON.stringify(results, undefined, 2));
    }
  }
}

export function executeAndSerializeMultipleSync(
  configs: string,
  queries: string,
  output: string,
  repeat: number,
): void {
  // eslint-disable-next-line no-console
  console.log(`Configs: ${configs}`);
  // eslint-disable-next-line no-console
  console.log(`Queries: ${queries}`);
  // eslint-disable-next-line no-console
  console.log(`Results: ${output}`);
  // eslint-disable-next-line no-console
  console.log(`Repeat: ${repeat}`);
  // eslint-disable-next-line no-console
  executeAndSerializeMultiple(configs, queries, output, repeat).then(() => console.log('Finished')).catch(console.log);
}
