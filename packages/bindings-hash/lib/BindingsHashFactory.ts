import { BindingsHash, type IBindingsHash } from './BindingsHash';

export class BindingsHashFactory implements IBindingsHashFactory {
  private readonly algorithm: string;
  private readonly encoding: string;

  public constructor(args: IBindingsHashFactoryArgs) {
    this.algorithm = args.algorithm;
    this.encoding = args.encoding;
  }

  public create(): IBindingsHash {
    return new BindingsHash({
      algorithm: this.algorithm,
      encoding: this.encoding,
    });
  }
}

export interface IBindingsHashFactory {
  create: () => IBindingsHash;
}

export interface IBindingsHashFactoryArgs {
  algorithm: string;
  encoding: string;
}
