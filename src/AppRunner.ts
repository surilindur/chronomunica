import { env } from 'node:process';
import { parseArgs } from 'node:util';
import { MeasurementRunner, type IMeasurementRunner } from './MeasurementRunner';
import { BindingsHash, MeasurementSerializer, RequestCounter } from '.';

export async function runApp(): Promise<void> {
  let { engine, query, context, results, hash, digest } = parseArgs({
    options: {
      engine: { type: 'string' },
      query: { type: 'string' },
      context: { type: 'string' },
      results: { type: 'string' },
      hash: { type: 'string', default: 'sha256' },
      digest: { type: 'string', default: 'hex' },
    },
  }).values;

  engine = env.CHRONOMUNICA_ENGINE ?? engine;
  query = env.CHRONOMUNICA_QUERY ?? query;
  context = env.CHRONOMUNICA_CONTEXT ?? context;
  results = env.CHRONOMUNICA_RESULTS ?? results;
  hash = env.CHRONOMUNICA_HASH ?? hash;
  digest = env.CHRONOMUNICA_DIGEST ?? digest;

  if (!engine || !query || !results) {
    throw new Error('Missing engine config, query file path or results path');
  }

  const measurementRunner: IMeasurementRunner = new MeasurementRunner({
    bindingsHash: new BindingsHash({ algorithm: hash, encoding: digest }),
    measurementSerializer: new MeasurementSerializer({ path: results }),
    requestCounter: new RequestCounter(),
  });

  await measurementRunner.run(engine, query, context);
}

export function runAppStatic(): void {
  runApp().then().catch(error => {
    throw error;
  });
}
