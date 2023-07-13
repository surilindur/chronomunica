import type { QueryEngine } from '@comunica/query-sparql';
import type { QueryStringContext, BindingsStream, Bindings } from '@comunica/types';
import type { IBindingsHash } from '@solidlab/chronomunica-bindings-hash';
import type { IRequestCounter } from '@solidlab/chronomunica-request-counter';

export class QueryExecution implements IQueryExecution {
  private readonly queryString: string;
  private readonly queryContext: QueryStringContext;
  private readonly queryEngine: QueryEngine;
  private readonly fetchCounter: IRequestCounter;
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

  public async collect(): Promise<IQueryExecutionOutput> {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      let previousTime = startTime;
      let currentTime = startTime;
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
          .on('end', () => resolve({
            hash: this.bindingsHash.digest(),
            intervals: this.intervals,
            requests: this.fetchCounter.count,
            duration: Date.now() - startTime,
            results: this.results,
          }));
      }).catch(reject);
    });
  }
}

export interface IQueryExecution {
  collect: () => Promise<IQueryExecutionOutput>;
}

export interface IQueryExecutionArgs {
  query: string;
  context?: Record<string, any>;
  engine: QueryEngine;
  fetchCounter: IRequestCounter;
  bindingsHash: IBindingsHash;
}

export interface IQueryExecutionOutput {
  hash: string;
  requests: number;
  results: number;
  duration: number;
  intervals: number[];
  error?: any;
}
