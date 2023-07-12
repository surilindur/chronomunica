import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { basename, join } from 'node:path';
import { QueryEngineFactory } from '@comunica/query-sparql';
import type { IQueryEngine, BindingsStream, Bindings } from '@comunica/types';
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

export async function executeAndMeasure(configPath: string, queryPath: string): Promise<IQueryResult> {
  // Read the query from the file
  const queryString: string = readFileSync(queryPath, { encoding: 'utf-8' });

  // Create the fetch counter, bindings hasher and intervals array
  const bindingsHash: BindingsHash = new BindingsHash();
  const fetchCounter: IFetchCounter = createFetchCounter();
  const intervals: number[] = [];
  let results = 0;

  // Create the factory and the engine
  const factory: QueryEngineFactory = new QueryEngineFactory();
  const engine: IQueryEngine = await factory.create({ configPath, logLevel: 'error' });

  // Query start time and current time
  const queryStartTime = Date.now();
  let previousTime = queryStartTime;
  let currentTime = queryStartTime;

  // Execute the query and measure the results
  const bindingsStream: BindingsStream = await engine.queryBindings(queryString, <any>{ fetch: fetchCounter.fetch });

  // Output the results, whether errored out or not
  const generateOutput = (error?: any): IQueryResult => ({
    hash: bindingsHash.digest('hex'),
    config: basename(configPath),
    query: basename(queryPath),
    intervals,
    requests: fetchCounter.count,
    results,
    error,
  });

  return new Promise((resolve, reject) => {
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
  });
}

export async function executeAndSerialize(configPath: string, queryPath: string, outputPath: string): Promise<void> {
  const measurement: IQueryResult = await executeAndMeasure(configPath, queryPath);
  // eslint-disable-next-line no-console
  console.log(`Serialize: ${outputPath}`);
  writeFileSync(outputPath, JSON.stringify(measurement, undefined, 2));
}

export async function executeAndSerializeMultiple(configs: string, queries: string, output: string): Promise<void> {
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
      const outputFilePath = join(output, `${config.name.split('.')[0]}-${query.name.split('.')[0]}.json`);
      await executeAndSerialize(configPath, queryPath, outputFilePath);
    }
  }
}

export function executeAndSerializeMultipleSync(configs: string, queries: string, output: string): void {
  // eslint-disable-next-line no-console
  console.log(`Configs: ${configs}`);
  // eslint-disable-next-line no-console
  console.log(`Queries: ${queries}`);
  // eslint-disable-next-line no-console
  console.log(`Results: ${output}`);
  // eslint-disable-next-line no-console
  console.log('Executing...');
  // eslint-disable-next-line no-console
  executeAndSerializeMultiple(configs, queries, output).then(() => console.log('Finished')).catch(console.log);
}
