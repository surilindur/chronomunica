import { readFileSync, writeFileSync } from 'node:fs';
import { join, basename } from 'node:path';
import { QueryEngineFactory } from '@comunica/query-sparql';
import type { IBindingsHashFactory } from '@solidlab/chronomunica-bindings-hash';
import type { IRequestCounterFactory } from '@solidlab/chronomunica-request-counter';
import { QueryExecution } from './QueryExecution';

export class QueryExecutionManager implements IQueryExecutionManager {
  private readonly queryFiles: string[];
  private readonly queryContext: Record<string, any> | undefined;
  private readonly queryEngineConfig: string;
  private readonly resultSerializationPath: string;
  private readonly repeatExecution: number;

  private readonly queryEngineFactory: QueryEngineFactory;
  private readonly bindingsHashFactory: IBindingsHashFactory;
  private readonly requestCounterFactory: IRequestCounterFactory;

  public constructor(args: IQueryExecutionManagerArgs) {
    this.bindingsHashFactory = args.bindingsHashFactory;
    this.requestCounterFactory = args.requestCounterFactory;
    this.repeatExecution = args.repeatExecution;
    this.resultSerializationPath = args.resultSerializationPath;
    this.queryEngineFactory = new QueryEngineFactory();
    this.queryEngineConfig = args.queryEngineConfig;
    this.queryContext = args.queryContext;
    this.queryFiles = args.queryFiles;
  }

  public async execute(): Promise<void> {
    for (const queryFile of this.queryFiles) {
      const queryFileResults = [];
      let errorOccurred = false;
      for (let repeat = 0; repeat < this.repeatExecution; repeat++) {
        const execution = new QueryExecution({
          engine: await this.queryEngineFactory.create({ configPath: this.queryEngineConfig }),
          bindingsHash: this.bindingsHashFactory.create(),
          fetchCounter: this.requestCounterFactory.create(),
          query: readFileSync(queryFile, { encoding: 'utf-8' }),
          context: this.queryContext,
        });
        let executionError: string | undefined;
        try {
          console.log(`Execute: ${queryFile}`);
          await execution.collect();
        } catch (error: unknown) {
          errorOccurred = true;
          executionError = String(error);
        }
        const output = execution.metrics(executionError);
        queryFileResults.push({
          query: queryFile,
          engine: this.queryEngineConfig,
          ...output,
        });
        if (errorOccurred) {
          break;
        }
      }
      const outputPath = join(this.resultSerializationPath, `${basename(queryFile).split('.')[0]}.json`);
      console.log(`Results: ${outputPath} (error: ${errorOccurred})`);
      writeFileSync(outputPath, JSON.stringify(queryFileResults, undefined, 2), { encoding: 'utf-8' });
    }
  }
}

export interface IQueryExecutionManager {
  execute: () => Promise<void>;
}

export interface IQueryExecutionManagerArgs {
  bindingsHashFactory: IBindingsHashFactory;
  requestCounterFactory: IRequestCounterFactory;
  resultSerializationPath: string;
  repeatExecution: number;
  queryEngineConfig: string;
  queryContext?: Record<string, any>;
  queryFiles: string[];
}
