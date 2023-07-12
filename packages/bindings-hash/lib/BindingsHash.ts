import { createHash, type Hash, type BinaryToTextEncoding } from 'node:crypto';
import type * as RDF from '@rdfjs/types';

export class BindingsHash implements IBindingsHash {
  private readonly algorithm: string;
  private readonly encoding: BinaryToTextEncoding;

  private readonly bindings: RDF.Bindings[];

  public constructor(args: IBindingsHashArgs) {
    this.algorithm = args.algorithm;
    this.encoding = args.encoding;
    this.bindings = [];
  }

  public digest(): string {
    const hash: Hash = createHash(this.algorithm, { defaultEncoding: 'utf-8' });
    const sortedValues = this.bindings
      .map(bindings => [ ...bindings.values() ].map(value => value.value).join(':'))
      .sort((first, second) => first.localeCompare(second));
    for (const value of sortedValues) {
      hash.push(value);
    }
    return hash.digest(this.encoding);
  }

  public add(bindings: RDF.Bindings): void {
    this.bindings.push(bindings);
  }
}

export interface IBindingsHash {
  digest: () => string;
  add: (bindings: RDF.Bindings) => void;
}

export interface IBindingsHashArgs {
  algorithm: string;
  encoding: BinaryToTextEncoding;
}
