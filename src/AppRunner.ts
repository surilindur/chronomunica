import { resolve } from 'node:path';
import { env } from 'node:process';
import { parseArgs } from 'node:util';
import { MeasurementRunner, type IMeasurementRunner } from './MeasurementRunner';
import { BindingsHash, MeasurementSerializer, RequestCounter } from '.';

const defaultConfig = resolve(__dirname, '..', 'config', 'default.json');

export async function runApp(): Promise<void> {
  let { engine, query, context } = parseArgs({
    options: {
      engine: { type: 'string' },
      query: { type: 'string' },
      context: { type: 'string' },
    },
  }).values;

  engine = env.CHRONOMUNICA_ENGINE ?? engine;
  query = env.CHRONOMUNICA_QUERY ?? query;
  context = env.CHRONOMUNICA_CONTEXT ?? context;

  if (!engine || !query) {
    throw new Error('Missing engine config or query file path');
  }

  const measurementRunner: IMeasurementRunner = new MeasurementRunner({
    bindingsHash: new BindingsHash({ algorithm: 'sha256', encoding: 'hex' }),
    measurementSerializer: new MeasurementSerializer({ outputPath: '/results' }),
    requestCounter: new RequestCounter(),
  });

  await measurementRunner.run(engine, query, context);
}

export function runAppStatic(): void {
  runApp().then().catch(error => {
    throw error;
  });
}
