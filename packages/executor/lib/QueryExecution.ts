import type { IQueryEngine, QueryStringContext, BindingsStream, Bindings } from '@comunica/types';
import type { IBindingsHash } from '@solidlab/chronomunica-bindings-hash';
import type { IFetchCounter } from '@solidlab/chronomunica-fetch-counter';

export class QueryExecution implements IQueryExecution {
  private readonly queryString: string;
  private readonly queryContext: QueryStringContext;
  private readonly queryEngine: IQueryEngine;
  private readonly fetchCounter: IFetchCounter;
  private readonly bindingsHash: IBindingsHash;

  private results: number;
  private readonly intervals: number[];

  public constructor(args: IQueryExecutionArgs) {
    this.queryString = args.query;
    this.queryEngine = args.engine;
    this.fetchCounter = args.fetchCounter;
    this.bindingsHash = args.bindingsHash;
    this.queryContext = <QueryStringContext>{
      ...args.context,
      fetch: this.fetchCounter.fetch,
    };
    this.results = 0;
    this.intervals = [];
  }

  public async collect(): Promise<void> {
    return new Promise((resolve, reject) => {
      let previousTime = Date.now();
      let currentTime = previousTime;
      this.queryEngine.queryBindings(this.queryString, this.queryContext).then((bindingsStream: BindingsStream) => {
        bindingsStream
          .on('data', (bindings: Bindings) => {
            // Include new result in hash
            this.bindingsHash.add(bindings);
            // Increment result counter
            this.results++;
            // Register the passed interval
            currentTime = Date.now();
            this.intervals.push(currentTime - previousTime);
            previousTime = currentTime;
          })
          .on('error', reject)
          .on('end', resolve);
      }).catch(reject);
    });
  }

  public metrics(error?: any): IQueryExecutionOutput {
    return {
      hash: this.bindingsHash.digest(),
      intervals: this.intervals,
      requests: this.fetchCounter.count,
      results: this.results,
      error,
    };
  }
}

export interface IQueryExecution {
  collect: () => Promise<void>;
}

export interface IQueryExecutionArgs {
  query: string;
  context?: Record<string, any>;
  engine: IQueryEngine;
  fetchCounter: IFetchCounter;
  bindingsHash: IBindingsHash;
}

export interface IQueryExecutionOutput {
  hash: string;
  requests: number;
  results: number;
  intervals: number[];
  error?: any;
}
