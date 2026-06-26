<template>
  <div class="matches-page" v-if="matches.length">
    <div class="page-header">
      <h1 class="page-title">对局记录</h1>
      <div class="filters">
        <button
          v-for="m in modes"
          :key="m.value"
          :class="['filter-btn', { active: filterMode === m.value }]"
          @click="filterMode = m.value"
        >{{ m.label }}</button>
      </div>
    </div>

    <div class="match-list">
      <div
        v-for="m in filteredMatches"
        :key="m.matchId"
        class="match-card card"
        :class="{ win: isWin(m), loss: !isWin(m) }"
        @click="$router.push(`/match/${m.matchId}`)"
      >
        <!-- 结果条 -->
        <div class="result-bar" :class="{ win: isWin(m), loss: !isWin(m) }">
          <span class="result-text">{{ isWin(m) ? 'VICTORY' : 'DEFEAT' }}</span>
        </div>

        <div class="match-body">
          <!-- 模式 & 时间 -->
          <div class="match-meta">
            <span class="game-mode">{{ m.gameMode }}</span>
            <span class="game-time">{{ formatDate(m.gameCreation) }}</span>
            <span class="game-duration">{{ formatDuration(m.gameDuration) }}</span>
          </div>

          <!-- 玩家信息 -->
          <div class="player-row" v-if="getTarget(m)">
            <img
              :src="`https://ddragon.leagueoflegends.com/cdn/14.10.1/img/champion/${getTarget(m).championName}.png`"
              class="champ-img"
              @error="e => e.target.src = 'https://via.placeholder.com/56?text=?'"
            />
            <div class="player-info">
              <div class="champ-name">{{ getTarget(m).championName }}</div>
              <div class="kda">
                <span class="kills">{{ getTarget(m).kills }}</span>
                <span class="sep">/</span>
                <span class="deaths">{{ getTarget(m).deaths }}</span>
                <span class="sep">/</span>
                <span class="assists">{{ getTarget(m).assists }}</span>
                <span class="kda-val">({{ getTarget(m).kda }})</span>
              </div>
            </div>
            <div class="player-stats">
              <span class="gold">{{ formatGold(getTarget(m).goldEarned) }}</span>
              <span class="cs">CS: {{ getCS(m) }}</span>
            </div>
          </div>

          <!-- 装备 -->
          <div class="items-row" v-if="getTarget(m)">
            <template v-for="i in 6" :key="i">
              <img
                v-if="getTarget(m)[`item${i-1}`] > 0"
                :src="`https://ddragon.leagueoflegends.com/cdn/14.10.1/img/item/${getTarget(m)[`item${i-1}`]}.png`"
                class="item-icon"
                @error="e => e.target.style.display='none'"
              />
              <div v-else class="item-empty"></div>
            </template>
            <div class="ward-item" :class="{ has: getTarget(m).item6 > 0 }">
              <img
                v-if="getTarget(m).item6 > 0"
                :src="`https://ddragon.leagueoflegends.com/cdn/14.10.1/img/item/${getTarget(m).item6}.png`"
                class="item-icon"
                @error="e => e.target.style.display='none'"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="loading-state">
    <div class="spinner"></div>
    <p>加载中...</p>
  </div>

  <div v-else class="empty-state">
    <p>暂无对局记录</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { summonerApi } from '../api'

const route = useRoute()
const puuid = decodeURIComponent(route.params.puuid)
const matches = ref([])
const loading = ref(true)
const filterMode = ref('ALL')

const modes = [
  { label: '全部', value: 'ALL' },
  { label: '单双排', value: 'RANKED_SOLO_5x5' },
  { label: '灵活排位', value: 'RANKED_FLEX_SR' },
  { label: '大乱斗', value: 'ARAM' },
  { label: '无限火力', value: 'URF' },
]

const filteredMatches = computed(() => {
  if (filterMode.value === 'ALL') return matches.value
  return matches.value.filter(m => m.gameMode === filterMode.value)
})

onMounted(async () => {
  try {
    const res = await summonerApi.getMatches(puuid, 50)
    if (res.success) {
      matches.value = res.data.matches
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

function getTarget(m) {
  return m.participants?.find(p => p.summonerName === route.query.name)
}

function isWin(m) {
  const p = getTarget(m)
  return p ? p.win : false
}

function formatDate(ts) {
  const d = new Date(ts)
  return `${d.getFullYear()}-${(d.getMonth()+1).toString().padStart(2,'0')}-${d.getDate().toString().padStart(2,'0')} ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`
}

function formatDuration(s) {
  const m = Math.floor(s / 60)
  return `${m}分钟`
}

function formatGold(n) {
  if (n >= 10000) return `${(n / 10000).toFixed(1)}w`
  return `${Math.round(n / 100) / 10}k`
}

function getCS(m) {
  const p = getTarget(m)
  return p?.champLevel || 0
}
</script>

<style scoped>
.matches-page { max-width: 900px; margin: 0 auto; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.page-title { font-size: 22px; font-weight: 700; color: #1a2a3a; }
.filters { display: flex; gap: 6px; flex-wrap: wrap; }
.filter-btn {
  padding: 6px 14px;
  border-radius: 16px;
  font-size: 13px;
  border: 1px solid #e8ecf0;
  background: white;
  color: #5a6a7a;
  cursor: pointer;
  transition: all 0.15s;
}
.filter-btn:hover { background: #f8fafc; }
.filter-btn.active {
  background: #0ac8b9;
  color: white;
  border-color: #0ac8b9;
}

.match-card {
  background: white;
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid #e8ecf0;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.match-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }

.result-bar {
  height: 4px;
}
.result-bar.win { background: linear-gradient(90deg, #22c55e, #4ade80); }
.result-bar.loss { background: linear-gradient(90deg, #ef4444, #f87171); }
.result-text {
  float: right;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  padding: 3px 10px;
  margin-top: -16px;
}
.result-bar.win .result-text { color: #22c55e; }
.result-bar.loss .result-text { color: #ef4444; }

.match-body { padding: 14px 18px; }

.match-meta {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: #7a8a9a;
  margin-bottom: 12px;
}

.player-row {
  display: flex;
  align-items: center;
  gap: 14px;
}
.champ-img {
  width: 52px;
  height: 52px;
  border-radius: 8px;
  flex-shrink: 0;
}
.player-info { flex: 1; }
.champ-name { font-weight: 600; color: #1a2a3a; font-size: 15px; }
.kda { margin-top: 2px; font-size: 14px; }
.kills { color: #22c55e; font-weight: 700; }
.deaths { color: #ef4444; }
.assists { color: #0ac8b9; }
.sep { color: #ccc; margin: 0 2px; }
.kda-val { color: #f0c020; font-weight: 600; }

.player-stats {
  text-align: right;
  font-size: 13px;
  color: #5a6a7a;
}
.gold { display: block; font-weight: 600; color: #f0c020; margin-bottom: 2px; }

.items-row {
  display: flex;
  gap: 4px;
  margin-top: 12px;
}
.item-icon {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  border: 1px solid #e8ecf0;
}
.item-empty {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  border: 1px dashed #ddd;
  background: #fafafa;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #aaa;
}
.spinner {
  width: 40px; height: 40px;
  border: 3px solid #e8ecf0;
  border-top-color: #0ac8b9;
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
