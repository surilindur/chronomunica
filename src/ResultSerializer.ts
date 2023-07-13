import { writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

export class ResultSerializer implements IResultSerializer {
  private readonly path: string;

  public constructor(args: IResultSerializerArgs) {
    this.path = args.path;
  }

  public async serialize(results: Record<string, any>): Promise<void> {
    const serializeFilename = `${results.configId}-${results.queryId}-${Date.now()}.json`;
    const serializationPath = resolve(this.path, serializeFilename);
    writeFileSync(serializationPath, JSON.stringify(results, undefined, 2));
  }
}

export interface IResultSerializer {
  serialize: (results: Record<string, any>) => Promise<void>;
}

export interface IResultSerializerArgs {
  path: string;
}
