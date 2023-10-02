import { createHash, type Hash, type BinaryToTextEncoding } from 'node:crypto';
import type * as RDF from '@rdfjs/types';

export class BindingsHash implements IBindingsHash {
  private readonly algorithm: string;
  private readonly encoding: string;

  private readonly bindings: RDF.Bindings[];
  private digested: boolean;

  public constructor(args: IBindingsHashArgs) {
    this.algorithm = args.algorithm;
    this.encoding = args.encoding;
    this.bindings = [];
    this.digested = false;
  }

  public digest(): string {
    if (this.digested) {
      throw new Error(`${this.constructor.name} can only be digested once!`);
    }
    this.digested = true;
    const hash: Hash = createHash(this.algorithm, { defaultEncoding: 'utf-8' });
    const bindingsValues: string[] = [];
    for (const binding of this.bindings) {
      const variablesAndValues: string[] = [];
      for (const [ variable, value ] of binding) {
        variablesAndValues.push(`${variable.value}:${value.value}`);
      }
      const valueAsString = variablesAndValues.sort((first, second) => first.localeCompare(second)).join('');
      bindingsValues.push(valueAsString);
    }
    const sortedBindingsValues = bindingsValues.sort((first, second) => first.localeCompare(second));
    for (const value of sortedBindingsValues) {
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
