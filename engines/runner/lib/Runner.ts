import { resolve } from 'node:path';
import { env } from 'node:process';
import { parseArgs } from 'node:util';
import type { IQueryExecutionManager } from '@solidlab/chronomunica-query-executor';
import { ComponentsManager } from 'componentsjs';

const defaultExecutor = 'urn:chronomunica:executor#default';
const defaultMainModulePath = resolve(__dirname);
const defaultConfig = resolve(__dirname, '../config/config-default.json');

export async function runApp(): Promise<void> {
  let { config, executor, modules } = parseArgs({
    options: {
      config: { type: 'string', short: 'c', default: defaultConfig },
      executor: { type: 'string', short: 'e', default: defaultExecutor },
      modules: { type: 'string', short: 'm', default: defaultMainModulePath },
    },
  }).values;

  config = env.CHRONOMUNICA_CONFIG ?? config;
  executor = env.CHRONOMUNICA_EXECUTOR ?? executor;
  modules = env.CHRONOMUNICA_MODULE_PATH ?? modules;

  const manager = await ComponentsManager.build({
    mainModulePath: modules!,
    typeChecking: false,
  });

  await manager.configRegistry.register(config!);
  const queryExecutionManager: IQueryExecutionManager = await manager.instantiate(executor!);
  await queryExecutionManager.execute();
}

export function runAppStatic(): void {
  runApp().then().catch(error => {
    throw error;
  });
}
