import { resolve } from 'node:path';
import { parseArgs } from 'node:util';
import type { IQueryExecutionManager } from '@solidlab/chronomunica-query-executor';
import { ComponentsManager } from 'componentsjs';

const defaultExecutor = 'urn:chronomunica:executor#default';
const defaultMainModulePath = resolve(__dirname);
const defaultConfig = resolve(__dirname, '../config/config-default.json');

export async function runApp(): Promise<void> {
  const { config, executor, mainModulePath } = parseArgs({
    options: {
      config: { type: 'string', short: 'c', default: defaultConfig },
      executor: { type: 'string', short: 'e', default: defaultExecutor },
      mainModulePath: { type: 'string', short: 'm', default: defaultMainModulePath },
    },
  }).values;

  const manager = await ComponentsManager.build({
    mainModulePath: mainModulePath!,
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
