import { writeFileSync } from 'node:fs';

export class MeasurementSerializer implements IMeasurementSerializer {
  private readonly path: string;

  public constructor(args: IMeasurementSerializerArgs) {
    this.path = args.path;
  }

  public async serialize(results: Record<string, any>): Promise<void> {
    writeFileSync(this.path, JSON.stringify(results, undefined, 2));
  }
}

export interface IMeasurementSerializer {
  serialize: (results: Record<string, any>) => Promise<void>;
}

export interface IMeasurementSerializerArgs {
  path: string;
}
