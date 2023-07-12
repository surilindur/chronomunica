import { createHash, type Hash, type BinaryToTextEncoding } from 'node:crypto';
import type * as RDF from '@rdfjs/types';

export class BindingsHash {
  private readonly bindings: RDF.Bindings[];

  public constructor() {
    this.bindings = [];
  }

  public digest(encoding: BinaryToTextEncoding): string {
    const hash: Hash = createHash('md5', { defaultEncoding: 'utf-8' });
    const sortedValues = this.bindings
      .map(bindings => [ ...bindings.values() ].map(value => value.value).join(':'))
      .sort((first, second) => first.localeCompare(second));
    for (const value of sortedValues) {
      hash.push(value);
    }
    return hash.digest(encoding);
  }

  public add(bindings: RDF.Bindings): void {
    this.bindings.push(bindings);
  }

  public clear(): void {
    while (this.bindings.length > 0) {
      this.bindings.pop();
    }
  }
}
