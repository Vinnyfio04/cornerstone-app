const DEFAULT_API_BASE_URL = import.meta.env?.VITE_API_BASE_URL ?? ''

export class ApiError extends Error {
  constructor(message, { code = 'backend_unavailable', status = 0 } = {}) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
  }
}

export function createApiClient({ baseUrl = DEFAULT_API_BASE_URL, fetchImpl = globalThis.fetch } = {}) {
  async function request(path, options = {}) {
    let response

    try {
      response = await fetchImpl(`${baseUrl}${path}`, {
        ...options,
        headers: {
          Accept: 'application/json',
          ...(options.body ? { 'Content-Type': 'application/json' } : {}),
          ...options.headers,
        },
      })
    } catch {
      throw new ApiError('The Cornerstone server is unavailable. Your exercise can still continue.')
    }

    let envelope
    try {
      envelope = await response.json()
    } catch {
      throw new ApiError('The Cornerstone server returned an unreadable response.', {
        code: 'invalid_response',
        status: response.status,
      })
    }

    if (!response.ok || envelope.error) {
      throw new ApiError(envelope.error?.message ?? 'The request could not be completed.', {
        code: envelope.error?.code ?? 'request_failed',
        status: response.status,
      })
    }

    return envelope.data
  }

  return { request }
}

export const apiClient = createApiClient()
