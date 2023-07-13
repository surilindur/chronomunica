export interface IRequestCounter {
  fetch: (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;
  count: number;
}
