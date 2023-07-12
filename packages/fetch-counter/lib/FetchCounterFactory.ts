import type { IFetchCounter } from './FetchCounter';

export class FetchCounterFactory {
  public create(): IFetchCounter {
    const fetchCounter: Record<string, any> = {
      count: 0,
    };
    fetchCounter.fetch = (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      fetchCounter.count++;
      return fetch(input, init);
    };
    return <IFetchCounter>fetchCounter;
  }
}

export interface IFetchCounterFactory {
  create: () => IFetchCounter;
}
