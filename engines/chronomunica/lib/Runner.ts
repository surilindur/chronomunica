import { resolve } from 'node:path';
import { parseArgs } from 'node:util';
import type { IQueryExecutionManager } from '@solidlab/chronomunica-executor';
import { ComponentsManager } from 'componentsjs';

const defaultExecutionManagerUri = 'urn:chronomunica:executor#default';

export async function runApp(): Promise<void> {
  const { config, executor } = parseArgs({
    options: {
      config: { type: 'string', short: 'c' },
      executor: { type: 'string', short: 'e' },
    },
  }).values;

  if (!config) {
    throw new Error('No configuration file path provided');
  }

  const manager = await ComponentsManager.build({
    mainModulePath: resolve(__dirname, '..', '..', '..'),
    typeChecking: false,
  });

  await manager.configRegistry.register(config);

  const queryExecutionManager = await manager.instantiate<IQueryExecutionManager>(
    executor ?? defaultExecutionManagerUri,
  );

  await queryExecutionManager.execute();
}

export function runAppStatic(): void {
  runApp().then(() => process.exit()).catch(error => {
    throw error;
  });
}
