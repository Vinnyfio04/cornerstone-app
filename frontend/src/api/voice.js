import { apiClient } from './client.js'

export function createVoiceApi(client = apiClient) {
  return {
    getConfig() {
      return client.request('/api/voice/config')
    },
    createSession(sdpOffer) {
      return client.request('/api/voice/sessions', {
        method: 'POST',
        body: JSON.stringify({ sdp_offer: sdpOffer }),
      })
    },
  }
}

export const voiceApi = createVoiceApi()
