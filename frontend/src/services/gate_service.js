const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

class GateService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.detail || 'API 요청 실패')
      }
      
      return data
    } catch (error) {
      console.error('API Error:', error)
      throw error
    }
  }

  // Gate 관련 API (action 기반)
  async gateAction(apiKey, action, data = {}) {
    return this.request('/gate', {
      method: 'POST',
      body: JSON.stringify({
        action: action,
        api_key: apiKey,
        data: data
      }),
    })
  }

  // 준비 화면 - 사용자 확인 (Gate 조작용 - action 기반)
  async ready(apiKey) {
    return this.gateAction(apiKey, 'ready')
  }

  // 문 열기 (Gate 조작용 - action 기반)
  async openDoor(apiKey, requestInfo = {}) {
    return this.gateAction(apiKey, 'open', requestInfo)
  }

  // 스냅샷 가져오기 (Gate 조작용 - action 기반)
  async getSnapshot(apiKey, camName = 'main') {
    return this.gateAction(apiKey, 'snapshot', { cam_name: camName })
  }
}

export default new GateService()

