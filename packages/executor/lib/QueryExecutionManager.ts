import { readFileSync } from 'node:fs';
import { QueryEngineFactory } from '@comunica/query-sparql';
import type { IBindingsHashFactory } from '@solidlab/chronomunica-bindings-hash';
import type { IRequestCounterFactory } from '@solidlab/chronomunica-request-counter';
import { QueryExecution } from './QueryExecution';

export class QueryExecutionManager implements IQueryExecutionManager {
  private readonly queryFiles: string[];
  private readonly queryContext: Record<string, any> | undefined;
  private readonly queryEngineConfig: string;

  private readonly queryEngineFactory: QueryEngineFactory;
  private readonly bindingsHashFactory: IBindingsHashFactory;
  private readonly requestCounterFactory: IRequestCounterFactory;

  public constructor(args: IQueryExecutionManagerArgs) {
    this.queryEngineConfig = args.queryEngineConfig;
    this.queryEngineFactory = new QueryEngineFactory();
    this.bindingsHashFactory = args.bindingsHashFactory;
    this.requestCounterFactory = args.requestCounterFactory;
    this.queryContext = args.queryContext;
    this.queryFiles = args.queryFiles;
  }

  public async execute(): Promise<void> {
    for (const queryFile of this.queryFiles) {
      const execution = new QueryExecution({
        engine: await this.queryEngineFactory.create({ configPath: this.queryEngineConfig }),
        bindingsHash: this.bindingsHashFactory.create(),
        fetchCounter: this.requestCounterFactory.create(),
        query: readFileSync(queryFile, { encoding: 'utf-8' }),
        context: this.queryContext,
      });
      let executionError: unknown | undefined;
      try {
        await execution.collect();
      } catch (error: unknown) {
        executionError = error;
      }
      const output = execution.metrics(executionError);
      // eslint-disable-next-line no-console
      console.log(queryFile, JSON.stringify(output));
    }
  }
}

export interface IQueryExecutionManager {
  execute: () => Promise<void>;
}

export interface IQueryExecutionManagerArgs {
  bindingsHashFactory: IBindingsHashFactory;
  requestCounterFactory: IRequestCounterFactory;
  queryEngineConfig: string;
  queryContext?: Record<string, any>;
  queryFiles: string[];
}
