import { QueryEngineFactory, type QueryEngine } from '@comunica/query-sparql';

export class ConfigPathQueryEngineFactory {
  private readonly factory: QueryEngineFactory;
  private readonly configPath: string;

  public constructor(args: IConfigPathQueryEngineFactoryArgs) {
    this.factory = new QueryEngineFactory();
    this.configPath = args.configPath;
  }

  public async create(): Promise<QueryEngine> {
    return this.factory.create({ configPath: this.configPath });
  }
}

export interface IConfigPathQueryEngineFactoryArgs {
  configPath: string;
}
