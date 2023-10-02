type FetchFunction = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

export class RequestCounter implements IRequestCounter {
  private count: number;
  private readonly fetch: FetchFunction;
  private readonly links: string[];

  public constructor() {
    this.count = 0;
    this.links = [];
    this.fetch = (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      this.count++;
      if (typeof input === 'string') {
        this.links.push(input);
      } else if (input instanceof URL) {
        this.links.push(input.href);
      } else if (input instanceof Request) {
        this.links.push(input.url);
      }
      return fetch(input, init);
    };
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

export interface IRequestCounter {
  getFetch: () => FetchFunction;
  getCount: () => number;
  getLinks: () => string[];
}
