type FetchFunction = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

export class RequestCounter implements IRequestCounter {
  private count: number;
  private readonly fetch: FetchFunction;

  public constructor() {
    this.count = 0;
    this.fetch = (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      this.count++;
      return fetch(input, init);
    };
  }

  public getFetch(): FetchFunction {
    return this.fetch;
  }

  public getCount(): number {
    return this.count;
  }
}

export interface IRequestCounter {
  getFetch: () => FetchFunction;
  getCount: () => number;
}
