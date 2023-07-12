type Fetch = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

export interface IFetchCounter {
  fetch: Fetch;
  count: number;
}
