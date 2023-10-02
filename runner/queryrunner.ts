import { resolve as resolvePath } from 'node:path';
import { QueryEngineFactory } from '@comunica/query-sparql';
import type { QueryStringContext, BindingsStream, Bindings, IQueryEngine } from '@comunica/types';
import { BindingsHash, type IBindingsHash } from './bindingshash';
import { RequestCollector, type IRequestCollector } from './requestcollector';

export class QueryRunner implements IQueryRunner {
  private readonly bindingsHash: IBindingsHash;
  private readonly requestCollector: IRequestCollector;
  private readonly queryEngineFactory: QueryEngineFactory;
  private readonly queryString: string;
  private readonly queryStringContext: QueryStringContext;
  private readonly configPath: string;
  private readonly mainModulePath: string;

  public constructor(args: IQueryRunnerArgs) {
    this.bindingsHash = new BindingsHash({ algorithm: args.algorithm, encoding: args.encoding });
    this.requestCollector = new RequestCollector({ count: true, links: true });
    this.queryEngineFactory = new QueryEngineFactory();
    this.mainModulePath = resolvePath(args.workdir ?? process.cwd());
    this.configPath = resolvePath(args.config);
    this.queryString = args.query;
    this.queryStringContext = {
      sources: [ ...args.query.matchAll(/^(?!PREFIX).*<(.*)>/gmu) ].map(match => match[1]),
      ...args.context ? JSON.parse(args.context) : {},
      fetch: this.requestCollector.getFetch(),
      lenient: args.lenient,
    };
  }

  public async run(): Promise<IQueryExecution> {
    try {
      return await this.execute();
    } catch (error: unknown) {
      return { error: String(error) };
    }
  }

  private async execute(): Promise<IQueryExecutionSuccess> {
    return new Promise((resolve, reject) => {
      this.queryEngineFactory.create({
        configPath: this.configPath,
        mainModulePath: this.mainModulePath,
      }).then((queryEngine: IQueryEngine) => {
        queryEngine
          .queryBindings(this.queryString, this.queryStringContext)
          .then((bindingsStream: BindingsStream) => {
            const startTime = Date.now();
            const resultIntervals: number[] = [];
            let previousTime = startTime;
            let currentTime = startTime;
            let resultCount = 0;
            bindingsStream
              .on('data', (bindings: Bindings) => {
                // Register the passed interval
                currentTime = Date.now();
                resultIntervals.push(currentTime - previousTime);
                previousTime = currentTime;
                this.bindingsHash.add(bindings);
                resultCount++;
              })
              .on('error', reject)
              .on('end', () => resolve({
                duration: Date.now() - startTime,
                resultIntervals,
                resultCount,
                resultHash: this.bindingsHash.digest(),
                requestCount: this.requestCollector.getCount(),
                requestUrls: this.requestCollector.getLinks(),
              }));
          }).catch(reject);
      }).catch(reject);
    });
  }
}

export interface IQueryRunner {
  run: () => Promise<IQueryExecution>;
}

type IQueryExecution = IQueryExecutionFailure | IQueryExecutionSuccess;

export interface IQueryExecutionFailure {
  error: string;
}

export interface IQueryExecutionSuccess {
  duration: number;
  resultCount: number;
  resultHash: string;
  resultIntervals: number[];
  requestCount: number;
  requestUrls: string[];
}

export interface IQueryRunnerArgs {
  config: string;
  query: string;
  lenient: boolean;
  context?: string;
  workdir?: string;
  algorithm: string;
  encoding: string;
}
