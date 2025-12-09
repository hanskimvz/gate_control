import { getCookie } from '../utils/cookie'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

class UserService {
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

  /**
   * 로그인 (user_id와 password로 api_key 받기)
   */
  async login(userId, password) {
    return this.request('/login', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, password: password }),
    })
  }

  /**
   * 사용자 목록 조회
   */
  async listUsers(filterData = []) {
    const apiKey = this.getApiKey()
    if (!apiKey) {
      throw new Error('로그인이 필요합니다')
    }
    const payload = {
      action: 'list',
      api_key: apiKey,
      data: filterData
    }
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  /**
   * 사용자 생성/수정
   */
  async modifyUser(data) {
    const apiKey = this.getApiKey()
    if (!apiKey) {
      throw new Error('로그인이 필요합니다')
    }
    
    // _id가 없거나 null이면 create, 있으면 modify
    const action = (!data._id || data._id === null) ? 'create' : 'modify'
    
    const payload = {
      action: action,
      api_key: apiKey,
      data: data
    }
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  /**
   * 사용자 삭제
   */
  async deleteUser(userId) {
    const apiKey = this.getApiKey()
    if (!apiKey) {
      throw new Error('로그인이 필요합니다')
    }
    
    const payload = {
      action: 'remove',
      api_key: apiKey,
      data: {
        _id: userId
      }
    }
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }
}

export default new UserService()

