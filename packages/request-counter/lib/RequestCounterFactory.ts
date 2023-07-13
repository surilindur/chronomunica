import type { IRequestCounter } from './RequestCounter';

export class RequestCounterFactory {
  public create(): IRequestCounter {
    const counter: Record<string, any> = {
      count: 0,
    };
    counter.fetch = (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      counter.count++;
      return fetch(input, init);
    };
    return <IRequestCounter>counter;
  }
}

export interface IRequestCounterFactory {
  create: () => IRequestCounter;
}
