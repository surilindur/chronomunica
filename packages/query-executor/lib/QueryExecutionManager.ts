import { readFileSync, writeFileSync } from 'node:fs';
import { join, basename } from 'node:path';
import { QueryEngineFactory } from '@comunica/query-sparql';
import type { IBindingsHashFactory } from '@solidlab/chronomunica-bindings-hash';
import type { IRequestCounterFactory } from '@solidlab/chronomunica-request-counter';
import { QueryExecution } from './QueryExecution';

export class QueryExecutionManager implements IQueryExecutionManager {
  private readonly queryFiles: string[];
  private readonly queryContext: Record<string, any> | undefined;
  private readonly queryEngineConfigs: string[];
  private readonly resultSerializationPath: string;
  private readonly repeatExecution: number;

  private readonly bindingsHashFactory: IBindingsHashFactory;
  private readonly requestCounterFactory: IRequestCounterFactory;

  public constructor(args: IQueryExecutionManagerArgs) {
    this.bindingsHashFactory = args.bindingsHashFactory;
    this.requestCounterFactory = args.requestCounterFactory;
    this.repeatExecution = args.repeatExecution;
    this.resultSerializationPath = args.resultSerializationPath;
    this.queryEngineConfigs = args.queryEngineConfigs;
    this.queryContext = args.queryContext;
    this.queryFiles = args.queryFiles;
  }

  public async execute(): Promise<void> {
    for (const configPath of this.queryEngineConfigs) {
      for (const queryFile of this.queryFiles) {
        const results = await this.executeForConfigAndQuery(configPath, queryFile);
        const outputFilename = `${basename(configPath).split('.')[0]}-${basename(queryFile).split('.')[0]}.json`;
        const outputPath = join(this.resultSerializationPath, outputFilename);
        console.log(`Results: ${outputPath} (error: ${results.some(res => res.error !== undefined)})`);
        writeFileSync(outputPath, JSON.stringify(results, undefined, 2), { encoding: 'utf-8' });
      }
    }
  }

  private async executeForConfigAndQuery(
    configPath: string,
    queryFile: string,
  ): Promise<Record<string, any>[]> {
    const queryFileResults = [];
    const queryString = readFileSync(queryFile, { encoding: 'utf-8' });
    for (let repeat = 0; repeat < this.repeatExecution; repeat++) {
      const queryEngineFactory = new QueryEngineFactory();
      const queryEngine = await queryEngineFactory.create({ configPath });
      const execution = new QueryExecution({
        engine: queryEngine,
        bindingsHash: this.bindingsHashFactory.create(),
        fetchCounter: this.requestCounterFactory.create(),
        query: queryString,
        context: this.queryContext,
      });
      let output: Record<string, any> | undefined;
      let errorOccurred = false;
      try {
        console.log(`Execute: ${queryFile}`);
        output = await execution.collect();
      } catch (error: unknown) {
        errorOccurred = true;
        output = { error };
      }
      queryFileResults.push({
        query: queryFile,
        engine: configPath,
        ...output,
      });
      if (errorOccurred) {
        break;
      }
    }
    return queryFileResults;
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
  queryEngineConfigs: string[];
  queryContext?: Record<string, any>;
  queryFiles: string[];
}
