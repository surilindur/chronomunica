import { readFileSync } from 'node:fs';
import { basename } from 'node:path';
import { QueryEngineFactory } from '@comunica/query-sparql';
import type { QueryStringContext, BindingsStream, Bindings, IQueryEngine } from '@comunica/types';
import type { IBindingsHash } from './bindingshash';
import type { IMeasurementSerializer } from './measurementserializer';
import type { IRequestCounter } from './requestcounter';

export class MeasurementRunner {
  private readonly bindingsHash: IBindingsHash;
  private readonly requestCounter: IRequestCounter;
  private readonly measurementSerializer: IMeasurementSerializer;
  private readonly queryEngineFactory: QueryEngineFactory;

  public constructor(args: IMeasurementRunnerArgs) {
    this.bindingsHash = args.bindingsHash;
    this.requestCounter = args.requestCounter;
    this.measurementSerializer = args.measurementSerializer;
    this.queryEngineFactory = new QueryEngineFactory();
  }

  public async run(config: string, query: string, context?: string): Promise<void> {
    const queryId = basename(query).split('.')[0];
    const configId = basename(config).split('.')[0];
    const queryString = readFileSync(query, { encoding: 'utf-8' });
    const contextFromFile = context ? JSON.parse(readFileSync(context, { encoding: 'utf-8' })) : {};
    const queryStringContext = <QueryStringContext>{
      ...contextFromFile,
      fetch: this.requestCounter.getFetch(),
      lenient: true,
    };
    let output: Record<string, any> = {};
    try {
      output = await this.execute(queryString, config, queryStringContext);
    } catch (error: unknown) {
      output = { error: String(error) };
    }
    output = { query: queryId, config: configId, ...output };
    await this.measurementSerializer.serialize(output);
  }

  private async execute(
    queryString: string,
    engineConfig: string,
    context: QueryStringContext,
  ): Promise<Record<string, any>> {
    return new Promise((resolve, reject) => {
      this.queryEngineFactory.create({
        configPath: engineConfig,
        mainModulePath: process.cwd(),
      }).then((queryEngine: IQueryEngine) => {
        queryEngine.queryBindings(queryString, context).then((bindingsStream: BindingsStream) => {
          const startTime = Date.now();
          const intervals: number[] = [];
          let previousTime = startTime;
          let currentTime = startTime;
          let resultCount = 0;
          bindingsStream
            .on('data', (bindings: Bindings) => {
              this.bindingsHash.add(bindings);
              resultCount++;
              // Register the passed interval
              currentTime = Date.now();
              intervals.push(currentTime - previousTime);
              previousTime = currentTime;
            })
            .on('error', reject)
            .on('end', () => resolve({
              duration: Date.now() - startTime,
              results: {
                intervals,
                count: resultCount,
                hash: this.bindingsHash.digest(),
              },
              requests: {
                count: this.requestCounter.getCount(),
                links: this.requestCounter.getLinks(),
              },
            }));
        }).catch(reject);
      }).catch(reject);
    });
  }
}

export interface IMeasurementRunner {
  run: (config: string, query: string, context?: string) => Promise<void>;
}

export interface IMeasurementRunnerArgs {
  bindingsHash: IBindingsHash;
  requestCounter: IRequestCounter;
  measurementSerializer: IMeasurementSerializer;
}
