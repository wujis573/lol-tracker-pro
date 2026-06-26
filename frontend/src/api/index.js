import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  (res) => res.data,
  (error) => {
    const msg = error.response?.data?.message || error.message || '请求失败'
    return Promise.reject(new Error(msg))
  }
)

// 召唤师
export const summonerApi = {
  search(name) {
    return api.get('/summoner/search', { params: { name } })
  },
  getProfile(puuid) {
    return api.get('/summoner/' + encodeURIComponent(puuid) + '/profile')
  },
  getMatches(puuid, count = 20, start = 0) {
    return api.get('/summoner/' + encodeURIComponent(puuid) + '/matches', { params: { count, start } })
  },
  getStats(puuid, matchCount = 20) {
    return api.get('/summoner/' + encodeURIComponent(puuid) + '/stats', { params: { match_count: matchCount } })
  },
}

// 排行榜
export const leaderboardApi = {
  getChallenger(queue = 'RANKED_SOLO_5x5', count = 20) {
    return api.get('/leaderboard/challenger', { params: { queue, count } })
  },
  getGrandmaster(queue = 'RANKED_SOLO_5x5', count = 20) {
    return api.get('/leaderboard/grandmaster', { params: { queue, count } })
  },
}
