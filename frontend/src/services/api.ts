import type { AnalysisResult, ApiErrorShape, Channel } from '../types/api';

const BASE = ((import.meta as unknown as { env?: Record<string, string | undefined> }).env?.VITE_API_BASE_URL ?? '').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = `Request failed (${response.status}).`;
    try {
      const data = (await response.json()) as ApiErrorShape;
      if (data.error?.message) message = data.error.message;
      else if (typeof data.detail === 'string') message = data.detail;
      else if (Array.isArray(data.detail)) message = data.detail.map(d => d.msg).filter(Boolean).join('; ') || message;
    } catch { /* Preserve status-based error message. */ }
    if (response.status === 404 || response.status === 405) {
      message = 'The analysis endpoint is not available on the backend yet. Please ask the backend team to implement the documented API.';
    }
    throw new ApiError(message, response.status);
  }
  return (await response.json()) as T;
}

async function postAnalysis(path: string, body: object, signal?: AbortSignal) {
  try {
    const response = await fetch(`${BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal,
    });
    return await parseResponse<AnalysisResult>(response);
  } catch (error) {
    if (error instanceof ApiError || (error instanceof DOMException && error.name === 'AbortError')) throw error;
    throw new ApiError('Could not connect to VeriSafe API. Confirm that the backend is running and the API URL is configured correctly.');
  }
}

export function analyzeMessage(payload: { message_text: string; sender?: string; channel: Channel }, signal?: AbortSignal) {
  return postAnalysis('/api/messages/analyze', payload, signal);
}

export function analyzeUrl(payload: { url: string; context?: string }, signal?: AbortSignal) {
  return postAnalysis('/api/urls/analyze', payload, signal);
}

export async function checkHealth(signal?: AbortSignal): Promise<boolean> {
  try {
    const response = await fetch(`${BASE}/api/health`, { signal });
    if (!response.ok) return false;
    const data = await response.json() as { status?: string };
    return data.status === 'healthy' || data.status === 'ok';
  } catch { return false; }
}
