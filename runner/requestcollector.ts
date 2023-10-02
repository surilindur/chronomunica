type FetchFunction = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

export class RequestCollector implements IRequestCollector {
  private count: number;
  private readonly fetch: FetchFunction;
  private readonly links: string[];

  public constructor(args: IRequestCollectorArgs) {
    this.count = 0;
    this.links = [];
    this.fetch = args.count || args.links ?
      (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
        if (args.count) {
          this.count++;
        }
        if (args.links) {
          if (typeof input === 'string') {
            this.links.push(input);
          } else if (input instanceof URL) {
            this.links.push(input.href);
          } else if (input instanceof Request) {
            this.links.push(input.url);
          }
        }
        return fetch(input, init);
      } :
      fetch;
  }

  public getFetch(): FetchFunction {
    return this.fetch;
  }

  public getCount(): number {
    return this.count;
  }

  public getLinks(): string[] {
    return this.links;
  }
}

export interface IRequestCollector {
  getFetch: () => FetchFunction;
  getCount: () => number;
  getLinks: () => string[];
}

export interface IRequestCollectorArgs {
  count: boolean;
  links: boolean;
}
