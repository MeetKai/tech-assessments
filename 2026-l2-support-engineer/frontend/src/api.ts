export class ApiError extends Error {
  constructor(public status: number, message: string, public requestId: string) { super(message); }
}

export async function api<T>(path: string, token = '', options: RequestInit = {}): Promise<T> {
  const requestId = crypto.randomUUID();
  let response: Response;
  try {
    response = await fetch(`/api${path}`, { ...options, headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      'X-Request-ID': requestId,
    }});
  } catch {
    throw new ApiError(0, 'Não foi possível conectar. Confira a conexão e tente novamente.', requestId);
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new ApiError(response.status, payload.message || 'Não foi possível concluir a solicitação.', payload.request_id || response.headers.get('x-request-id') || requestId);
  }
  return response.status === 204 ? undefined as T : response.json();
}
