import { createHash, type Hash, type BinaryToTextEncoding } from 'node:crypto';
import type * as RDF from '@rdfjs/types';

export class BindingsHash implements IBindingsHash {
  private readonly algorithm: string;
  private readonly encoding: string;

  private readonly bindings: RDF.Bindings[];

  public constructor(args: IBindingsHashArgs) {
    this.algorithm = args.algorithm;
    this.encoding = args.encoding;
    this.bindings = [];
  }

  public digest(): string {
    const hash: Hash = createHash(this.algorithm, { defaultEncoding: 'utf-8' });
    const localeCompare = (first: string, second: string): number => first.localeCompare(second);

    const result: string[] = [];

    for (const binding of this.bindings) {
      const variables = [ ...binding.keys() ].map(key => key.value).sort(localeCompare);
      const values: string[] = [];
      for (const variable of variables) {
        values.push(`${variable} -> ${binding.get(variable).value}`);
      }
      values.sort(localeCompare);
      result.push(values.join('\n'));
    }

    result.sort(localeCompare);

    for (const value of result) {
      hash.update(value, 'utf-8');
    }

    return hash.digest(<BinaryToTextEncoding> this.encoding);
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
  encoding: string;
}
