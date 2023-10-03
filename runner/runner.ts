import yargs from 'yargs/yargs';
import { QueryRunner } from './queryrunner';

export async function runApp(): Promise<void> {
  const args = await yargs(process.argv.slice(2)).options({
    config: {
      type: 'string',
      demand: true,
      description: 'The Components.js configuration file to instantiate a query engine from',
    },
    query: {
      type: 'string',
      demand: true,
      description: 'The SPARQL query to execute, passed as a string',
    },
    context: {
      type: 'string',
      description: 'Optional query context, passed as a serialized JSON object',
    },
    lenient: {
      type: 'boolean',
      default: true,
      description: 'Whether the engine should be run in lenient mode',
    },
    workdir: {
      type: 'string',
      description: 'The working directory to execute the runner in',
    },
    algorithm: {
      type: 'string',
      default: 'md5',
      description: 'The hash algorithm to use on query results',
    },
    encoding: {
      type: 'string',
      default: 'hex',
      description: 'The encoding to use for result hash digest',
    },
  }).parse();

  const runner = new QueryRunner(args);
  const result = await runner.run();
  console.log(JSON.stringify(result));
}

export function runAppStatic(): void {
  runApp().then().catch(error => {
    throw error;
  });
}

process.on('uncaughtExceptionMonitor', (err, origin) => {
  console.error(`Uncaught error from ${origin}: ${err.message}`);
});

runAppStatic();
