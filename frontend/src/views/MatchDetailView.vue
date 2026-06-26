<template>
  <div class="match-detail" v-if="match">
    <!-- 对局基本信息 -->
    <div class="match-header card">
      <div class="match-result-bar" :class="isWin(match) ? 'win' : 'loss'">
        <span class="result-label">{{ isWin(match) ? '胜利' : '失败' }}</span>
        <span class="mode-label">{{ match.gameMode }}</span>
        <span class="duration">{{ formatDuration(match.gameDuration) }}</span>
      </div>
    </div>

    <!-- 蓝队 vs 红队 -->
    <div class="teams card">
      <div v-for="team in teams" :key="team.id" class="team" :class="{ winner: team.win }">
        <h3 class="team-name">{{ team.win ? '胜利方' : '失败方' }}</h3>
        <div v-for="p in team.players" :key="p.puuid" class="player-row" :class="{ isMe: p.isMe }">
          <img
            :src="`https://ddragon.leagueoflegends.com/cdn/14.10.1/img/champion/${p.championName}.png`"
            class="champ-img"
            @error="e => e.target.src = 'https://via.placeholder.com/48?text=?'"
          />
          <div class="player-info">
            <div class="player-name" :class="{ highlight: p.isMe }">{{ p.summonerName }}</div>
            <div class="player-kda">
              <span class="kills">{{ p.kills }}</span>/<span class="deaths">{{ p.deaths }}</span>/<span class="assists">{{ p.assists }}</span>
              <span class="kda-text">({{ p.kda }})</span>
            </div>
          </div>
          <div class="player-dmg">
            <div class="dmg-label">伤害</div>
            <div class="dmg-value">{{ formatNum(p.totalDamageDealt) }}</div>
          </div>
          <div class="player-items">
            <template v-for="i in 6" :key="i">
              <img v-if="p[`item${i-1}`] > 0"
                :src="`https://ddragon.leagueoflegends.com/cdn/14.10.1/img/item/${p[`item${i-1}`]}.png`"
                class="item-icon"
                @error="e => e.target.style.display='none'"
              />
              <div v-else class="item-empty" />
            </template>
          </div>
        </div>
      </div>
    </div>

    <div class="back-btn">
      <button @click="$router.back()" class="btn btn-outline">← 返回</button>
    </div>
  </div>

  <div v-else-if="loading" class="loading-state">
    <div class="spinner"></div>
    <p>加载对局详情...</p>
  </div>

  <div v-else class="error-state">
    <p>对局数据加载失败</p>
    <button @click="$router.back()" class="btn btn-primary mt-4">返回</button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { summonerApi } from '../api'

const route = useRoute()
const matchId = route.params.matchId
const match = ref(null)
const loading = ref(true)

const teams = computed(() => {
  if (!match.value) return []
  const participants = match.value.participants || []
  const byTeam = {}
  for (const p of participants) {
    if (!byTeam[p.teamId]) byTeam[p.teamId] = []
    byTeam[p.teamId].push(p)
  }
  return Object.values(byTeam).map((players, i) => ({
    id: i + 100,
    win: players[0]?.win || false,
    players: players.map(p => ({ ...p, isMe: p.summonerName === myName.value })),
  })).sort((a, b) => (b.win ? 1 : 0) - (a.win ? 1 : 0))
})

const myName = ref('')

onMounted(async () => {
  try {
    // 从 query 获取 summoner name
    myName.value = route.query.name || ''
    const res = await summonerApi.getMatches(route.query.puuid || '', 50)
    if (res.success) {
      match.value = res.data.matches.find(m => m.matchId === matchId) || null
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

function isWin(m) {
  return m.winningTeam === match.value?.participants?.find(p => p.summonerName === myName.value)?.teamId
}

function formatDuration(s) {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m}:${sec.toString().padStart(2, '0')}`
}

function formatNum(n) {
  if (n >= 10000) return `${(n / 10000).toFixed(1)}w`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return n.toString()
}
</script>

<style scoped>
.match-detail { max-width: 960px; margin: 0 auto; }

.card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e8ecf0;
  margin-bottom: 16px;
  overflow: hidden;
}

/* 结果条 */
.match-header { padding: 0; }
.match-result-bar {
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 16px;
  font-weight: 700;
}
.match-result-bar.win { background: #dcfce7; color: #166534; }
.match-result-bar.loss { background: #fee2e2; color: #991b1b; }
.result-label { font-size: 20px; }
.mode-label { opacity: 0.8; }
.duration { margin-left: auto; font-weight: 400; font-size: 14px; }

/* 队伍 */
.team { padding: 16px 20px; }
.team.winner { border-bottom: 1px solid #e8ecf0; }
.team-name {
  font-size: 13px;
  font-weight: 600;
  color: #7a8a9a;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
}
.player-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}
.player-row:last-child { border-bottom: none; }
.player-row.isMe { background: #fefce8; margin: 0 -20px; padding: 8px 20px; border-radius: 6px; }

.champ-img { width: 40px; height: 40px; border-radius: 6px; flex-shrink: 0; }
.player-info { flex: 1; min-width: 0; }
.player-name { font-size: 14px; color: #1a2a3a; font-weight: 500; }
.player-name.highlight { color: #ca8a04; font-weight: 700; }
.player-kda { font-size: 13px; margin-top: 2px; }
.kills { color: #22c55e; font-weight: 600; }
.deaths { color: #ef4444; }
.assists { color: #0ac8b9; }
.kda-text { color: #f0c020; font-weight: 600; margin-left: 4px; }

.player-dmg { text-align: right; min-width: 70px; }
.dmg-label { font-size: 11px; color: #aaa; }
.dmg-value { font-size: 13px; color: #5a6a7a; }

.player-items { display: flex; gap: 4px; }
.item-icon { width: 28px; height: 28px; border-radius: 4px; border: 1px solid #e8ecf0; }
.item-empty { width: 28px; height: 28px; border-radius: 4px; border: 1px dashed #ddd; background: #fafafa; }

.back-btn { text-align: center; padding: 12px 0 40px; }

.loading-state, .error-state {
  text-align: center;
  padding: 80px 20px;
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
.mt-4 { margin-top: 16px; }
</style>
