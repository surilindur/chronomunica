export interface IFetchCounter {
  fetch: (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;
  count: number;
}

export function createFetchCounter(): IFetchCounter {
  const fetchCounter: Record<string, any> = {
    count: 0,
  };
  fetchCounter.fetch = (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    fetchCounter.count++;
    return fetch(input, init);
  };
  return <IFetchCounter>fetchCounter;
}
