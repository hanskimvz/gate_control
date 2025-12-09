import { getCookie } from '../utils/cookie'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1' 

class ApiService {
  /**
   * 쿠키에서 api_key 가져오기
   */
  getApiKey() {
    return getCookie('api_key')
  }

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

  // 로그 목록 조회 (웹 관리용 - cookie에서 api_key 사용)
  async listLogs(page = 1, offset = 20) {
    const apiKey = this.getApiKey()
    if (!apiKey) {
      throw new Error('로그인이 필요합니다')
    }
    const url = `/logs?page=${page}&offset=${offset}&api_key=${encodeURIComponent(apiKey)}`
    return this.request(url)
  }
}

export default new ApiService()

