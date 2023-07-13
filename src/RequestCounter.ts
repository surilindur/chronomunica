type FetchFunction = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

export class RequestCounter implements IRequestCounter {
  public count: number;
  public readonly fetch: FetchFunction;

  public constructor() {
    this.count = 0;
    this.fetch = (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      this.count++;
      return fetch(input, init);
    };
  }
}

export interface IRequestCounter {
  fetch: FetchFunction;
  count: number;
}
