import { resolve } from 'node:path';
import { env } from 'node:process';
import { parseArgs } from 'node:util';
import { ComponentsManager } from 'componentsjs';
import type { MeasurementRunner } from './MeasurementRunner';

const defaultRunner = 'urn:chronomunica:runner#default';
const defaultConfig = resolve(__dirname, '..', 'config', 'default.json');
const defaultMainModulePath = resolve(__dirname);

export async function runApp(): Promise<void> {
  let { config, engine, query, context, runner, modules } = parseArgs({
    options: {
      config: { type: 'string', default: defaultConfig },
      engine: { type: 'string' },
      query: { type: 'string' },
      context: { type: 'string' },
      runner: { type: 'string', short: 'e', default: defaultRunner },
      modules: { type: 'string', short: 'm', default: defaultMainModulePath },
    },
  }).values;

  config = env.CHRONOMUNICA_CONFIG ?? config;
  engine = env.CHRONOMUNICA_ENGINE ?? engine;
  runner = env.CHRONOMUNICA_RUNNER ?? runner;
  modules = env.CHRONOMUNICA_MODULE_PATH ?? modules;
  query = env.CHRONOMUNICA_QUERY ?? query;
  context = env.CHRONOMUNICA_CONTEXT ?? context;

  const manager = await ComponentsManager.build({
    mainModulePath: modules!,
    typeChecking: false,
  });

  await manager.configRegistry.register(config!);
  const queryRunner = await manager.instantiate<MeasurementRunner>(runner!);
  await queryRunner.run(engine!, query!, context);
}

export function runAppStatic(): void {
  runApp().then().catch(error => {
    throw error;
  });
}
