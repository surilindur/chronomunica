import { executeAndSerializeMultipleSync } from '../lib';

const configsPath = process.argv.at(process.argv.indexOf('--configs') + 1);
const queriesPath = process.argv.at(process.argv.indexOf('--queries') + 1);
const outputPath = process.argv.at(process.argv.indexOf('--results') + 1);
const repeatCount = Number.parseInt(process.argv.at(process.argv.indexOf('--repeat') + 1) ?? '1', 10);

if (configsPath && queriesPath && outputPath) {
  executeAndSerializeMultipleSync(configsPath, queriesPath, outputPath, repeatCount);
} else {
  // eslint-disable-next-line no-console
  console.log('Missing config, query or output path');
}
