import { writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

export class MeasurementSerializer implements IMeasurementSerializer {
  private readonly outputPath: string;

  public constructor(args: IMeasurementSerializerArgs) {
    this.outputPath = args.outputPath;
  }

  public async serialize(results: Record<string, any>): Promise<void> {
    const serializeFilename = `${results.configId}-${results.queryId}-${Date.now()}.json`;
    const serializationPath = resolve(this.outputPath, serializeFilename);
    writeFileSync(serializationPath, JSON.stringify(results, undefined, 2));
  }
}

export interface IMeasurementSerializer {
  serialize: (results: Record<string, any>) => Promise<void>;
}

export interface IMeasurementSerializerArgs {
  outputPath: string;
}
