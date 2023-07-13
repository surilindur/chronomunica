import { readFileSync } from 'node:fs';
import { basename } from 'node:path';
import { QueryEngineFactory } from '@comunica/query-sparql';
import type { QueryStringContext, BindingsStream, Bindings } from '@comunica/types';
import type { IBindingsHash } from './BindingsHash';
import type { IRequestCounter } from './RequestCounter';
import type { IResultSerializer } from './ResultSerializer';

export class QueryRunner {
  private readonly bindingsHash: IBindingsHash;
  private readonly requestCounter: IRequestCounter;
  private readonly resultSerializer: IResultSerializer;

  public constructor(args: IQueryRunnerArgs) {
    this.bindingsHash = args.bindingsHash;
    this.requestCounter = args.requestCounter;
    this.resultSerializer = args.resultSerializer;
  }

  public async run(config: string, query: string, context?: string): Promise<void> {
    const queryId = basename(query).split('.')[0];
    const configId = basename(config).split('.')[0];
    const queryString = readFileSync(query, { encoding: 'utf-8' });
    const contextFromFile = context ? JSON.parse(readFileSync(context, { encoding: 'utf-8' })) : {};
    const queryStringContext = <QueryStringContext>{
      ...contextFromFile,
      fetch: this.requestCounter.fetch,
    };
    let output: Record<string, any> = {};
    try {
      output = await this.execute(queryString, config, queryStringContext);
    } catch (error: unknown) {
      output = { error };
    }
    output = { query: queryId, config: configId, ...output };
    await this.resultSerializer.serialize(output);
  }

  private async execute(
    queryString: string,
    engineConfig: string,
    context: QueryStringContext,
  ): Promise<Record<string, any>> {
    const queryEngineFactory = new QueryEngineFactory();
    const queryEngine = await queryEngineFactory.create({ configPath: engineConfig });
    return new Promise((resolve, reject) => {
      queryEngine.queryBindings(queryString, context).then((bindingsStream: BindingsStream) => {
        const startTime = Date.now();
        const intervals: number[] = [];
        let previousTime = startTime;
        let currentTime = startTime;
        let resultCount = 0;
        bindingsStream.on('data', (bindings: Bindings) => {
          this.bindingsHash.add(bindings);
          resultCount++;
          // Register the passed interval
          currentTime = Date.now();
          intervals.push(currentTime - previousTime);
          previousTime = currentTime;
        }).on('error', reject).on('end', () => resolve({
          hash: this.bindingsHash.digest(),
          intervals,
          requests: this.requestCounter.count,
          duration: Date.now() - startTime,
          results: resultCount,
        }));
      }).catch(reject);
    });
  }
}

export interface IQueryRunner {
  run: (config: string, query: string, context?: string) => Promise<void>;
}

export interface IQueryRunnerArgs {
  bindingsHash: IBindingsHash;
  requestCounter: IRequestCounter;
  resultSerializer: IResultSerializer;
}
