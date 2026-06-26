<template>
  <div class="profile-page" v-if="profile">
    <!-- 召唤师基本信息 -->
    <div class="profile-header card">
      <div class="profile-main">
        <img
          :src="profile.summoner.profileIconUrl"
          :alt="profile.summoner.name"
          class="avatar"
          @error="e => e.target.src = 'https://via.placeholder.com/120?text=?'"
        />
        <div class="profile-info">
          <h1 class="summoner-name">{{ profile.summoner.name }}</h1>
          <p class="summoner-level">Lv.{{ profile.summoner.level }}</p>
        </div>
        <div class="profile-actions">
          <button @click="$router.push(`/matches/${encodeURIComponent(puuid)}`)" class="btn btn-outline">
            查看对局
          </button>
        </div>
      </div>

      <!-- 排位信息 -->
      <div class="ranks" v-if="profile.ranks.length">
        <div
          v-for="r in profile.ranks"
          :key="r.queueType"
          class="rank-card"
        >
          <div class="rank-queue">{{ queueTypeName(r.queueType) }}</div>
          <div class="rank-tier" :class="tierClass(r.tier)">
            <img
              :src="`https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/content/src/leagueclient/rankedcrests/emblem-cb-tier${tierIndex(r.tier)}_tier1.png`"
              class="rank-icon"
              @error="e => e.target.style.display='none'"
            />
            <div>
              <div class="tier-text">{{ tierName(r.tier) }} {{ r.rank }}</div>
              <div class="lp-text">{{ r.leaguePoints }} LP</div>
            </div>
          </div>
          <div class="rank-stats">
            <span class="wins">{{ r.wins }}W</span>
            <span class="sep">/</span>
            <span class="losses">{{ r.losses }}L</span>
            <span class="win-rate" :class="{ positive: r.winRate >= 50 }">{{ r.winRate }}%</span>
          </div>
          <div v-if="r.isHotStreak" class="badge badge-gold">🔥 连胜</div>
          <div v-if="r.isFreshBlood" class="badge badge-blue">✨ 新星</div>
          <div v-if="r.isVeteran" class="badge badge-purple">⭐ 老将</div>
        </div>
      </div>

      <div v-else class="unranked-hint">
        暂无排位信息
      </div>
    </div>

    <!-- 最近对局预览 -->
    <div class="recent-matches card" v-if="recentMatches.length">
      <h2 class="section-title">最近对局</h2>
      <div class="match-list">
        <div
          v-for="m in recentMatches"
          :key="m.matchId"
          class="match-item"
          :class="{ win: isWin(m), loss: !isWin(m) }"
          @click="$router.push(`/match/${m.matchId}`)"
        >
          <div class="match-result">
            <span class="result-text">{{ isWin(m) ? '胜' : '负' }}</span>
          </div>
          <img
            :src="`https://ddragon.leagueoflegends.com/cdn/14.10.1/img/champion/${getParticipant(m).championName}.png`"
            class="champ-icon"
            @error="e => e.target.src = 'https://via.placeholder.com/48?text=?'"
          />
          <div class="match-mode">{{ m.gameMode }}</div>
          <div class="match-kda">
            {{ getParticipant(m).kills }} / {{ getParticipant(m).deaths }} / {{ getParticipant(m).assists }}
          </div>
          <div class="match-time">{{ formatDuration(m.gameDuration) }}</div>
        </div>
      </div>
      <div class="more-matches">
        <router-link :to="`/matches/${encodeURIComponent(puuid)}`" class="btn btn-outline">
          查看全部对局 →
        </router-link>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview card" v-if="stats">
      <h2 class="section-title">数据统计（近{{ stats.totalGames }}场）</h2>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">{{ stats.winRate }}%</div>
          <div class="stat-label">胜率</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.avgKDA }}</div>
          <div class="stat-label">平均 KDA</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.avgKills }}</div>
          <div class="stat-label">平均击杀</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.avgDeaths }}</div>
          <div class="stat-label">平均死亡</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.avgAssists }}</div>
          <div class="stat-label">平均助攻</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ formatGold(stats.avgGold) }}</div>
          <div class="stat-label">平均金币</div>
        </div>
      </div>

      <!-- 常用英雄 -->
      <div class="top-champs" v-if="stats.topChampions.length">
        <h3 class="subsection-title">常用英雄</h3>
        <div class="champ-grid">
          <div v-for="c in stats.topChampions.slice(0, 5)" :key="c.name" class="champ-item">
            <span class="champ-name">{{ c.name }}</span>
            <span class="champ-games">{{ c.games }}场</span>
            <span class="champ-wr" :class="{ positive: c.winRate >= 50 }">{{ c.winRate }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在加载召唤师数据...</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { summonerApi } from '../api'

const route = useRoute()
const puuid = decodeURIComponent(route.params.puuid)
const profile = ref(null)
const recentMatches = ref([])
const stats = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const [profileRes, matchesRes, statsRes] = await Promise.all([
      summonerApi.getProfile(puuid),
      summonerApi.getMatches(puuid, 10),
      summonerApi.getStats(puuid, 20),
    ])

    if (profileRes.success) {
      profile.value = profileRes.data
    } else {
      error.value = profileRes.message
      return
    }

    if (matchesRes.success) {
      recentMatches.value = matchesRes.data.matches.slice(0, 8)
    }

    if (statsRes.success) {
      stats.value = statsRes.data
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

function tierName(tier) {
  const map = { IRON: '铁', BRONZE: '铜', SILVER: '银', GOLD: '金', PLATINUM: '铂金', DIAMOND: '钻石', EMERALD: '翡翠', MASTER: '大师', GRANDMASTER: '宗师', CHALLENGER: '王者' }
  return map[tier] || tier
}

function tierIndex(tier) {
  const map = { IRON: 0, BRONZE: 1, SILVER: 2, GOLD: 3, PLATINUM: 4, DIAMOND: 5, EMERALD: 5, MASTER: 6, GRANDMASTER: 7, CHALLENGER: 8 }
  return map[tier] ?? 0
}

function tierClass(tier) {
  return {
    'tier-iron': tier === 'IRON',
    'tier-bronze': tier === 'BRONZE',
    'tier-silver': tier === 'SILVER',
    'tier-gold': tier === 'GOLD',
    'tier-platinum': tier === 'PLATINUM',
    'tier-diamond': tier === 'DIAMOND',
    'tier-emerald': tier === 'EMERALD',
    'tier-master': tier === 'MASTER',
    'tier-grandmaster': tier === 'GRANDMASTER',
    'tier-challenger': tier === 'CHALLENGER',
  }
}

function queueTypeName(q) {
  return q === 'RANKED_SOLO_5x5' ? '单双排' : q === 'RANKED_FLEX_SR' ? '灵活排位' : q
}

function getParticipant(m) {
  const p = m.participants?.find(p => p.summonerName === profile.value?.summoner.name)
  return p || { kills: 0, deaths: 0, assists: 0, championName: '?', kda: 0 }
}

function isWin(m) {
  return getParticipant(m).win
}

function formatDuration(s) {
  if (s < 60) return `${s}s`
  const m = Math.floor(s / 60)
  const sec = s % 60
  return sec > 0 ? `${m}:${sec.toString().padStart(2, '0')}` : `${m}:00`
}

function formatGold(n) {
  if (n >= 10000) return `${(n / 10000).toFixed(1)}w`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return n.toString()
}
</script>

<style scoped>
.profile-page { max-width: 900px; margin: 0 auto; }

.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e8ecf0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  margin-bottom: 20px;
}

/* ── 头部 ── */
.profile-main {
  display: flex;
  align-items: center;
  gap: 20px;
}
.avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  border: 3px solid #c8aa6e;
  flex-shrink: 0;
}
.summoner-name {
  font-size: 24px;
  font-weight: 700;
  color: #091428;
}
.summoner-level {
  font-size: 13px;
  color: #7a8a9a;
  margin-top: 2px;
}

/* ── 排位 ── */
.ranks {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 14px;
  margin-top: 24px;
}
.rank-card {
  background: #f8fafc;
  border: 1px solid #e8ecf0;
  border-radius: 10px;
  padding: 16px;
}
.rank-queue {
  font-size: 12px;
  color: #7a8a9a;
  margin-bottom: 8px;
}
.rank-tier {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.rank-icon { width: 48px; height: 48px; }
.tier-text { font-size: 18px; font-weight: 700; }
.tier-challenger .tier-text { color: #c8aa6e; }
.tier-grandmaster .tier-text { color: #e04848; }
.tier-master .tier-text { color: #b44aff; }
.tier-diamond .tier-text { color: #a0d2f0; }
.tier-emerald .tier-text { color: #22c55e; }
.tier-platinum .tier-text { color: #30efd0; }
.tier-gold .tier-text { color: #f0c020; }
.tier-silver .tier-text { color: #a8a8a8; }
.tier-bronze .tier-text { color: #cd7f32; }
.tier-iron .tier-text { color: #7a7a7a; }
.lp-text { font-size: 13px; color: #7a8a9a; }
.rank-stats { font-size: 15px; color: #1a2a3a; }
.rank-stats .wins { color: #22c55e; font-weight: 600; }
.rank-stats .sep { color: #ccc; margin: 0 2px; }
.rank-stats .losses { color: #ef4444; }
.rank-stats .win-rate { margin-left: 12px; font-weight: 600; }
.rank-stats .win-rate.positive { color: #22c55e; }
.badge {
  display: inline-block;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  margin-top: 6px;
  margin-right: 6px;
}
.badge-gold { background: #fef9c3; color: #92400e; }
.badge-blue { background: #dbeafe; color: #1e40af; }
.badge-purple { background: #ede9fe; color: #6d28d9; }

.unranked-hint {
  margin-top: 24px;
  text-align: center;
  color: #aaa;
  padding: 20px;
}

/* ── 对局列表 ── */
.section-title { font-size: 18px; font-weight: 700; color: #1a2a3a; margin-bottom: 14px; }
.match-list { display: flex; flex-direction: column; gap: 8px; }
.match-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e8ecf0;
  cursor: pointer;
  transition: background 0.15s;
}
.match-item:hover { background: #f8fafc; }
.match-item.win { border-left: 4px solid #22c55e; }
.match-item.loss { border-left: 4px solid #ef4444; }

.result-text {
  font-size: 13px;
  font-weight: 700;
  width: 22px;
  text-align: center;
}
.match-item.win .result-text { color: #22c55e; }
.match-item.loss .result-text { color: #ef4444; }

.champ-icon { width: 40px; height: 40px; border-radius: 6px; flex-shrink: 0; }
.match-mode { font-size: 13px; color: #7a8a9a; flex-shrink: 0; width: 100px; }
.match-kda { font-size: 15px; font-weight: 600; color: #1a2a3a; flex: 1; }
.match-time { font-size: 12px; color: #aaa; flex-shrink: 0; }

.more-matches { margin-top: 16px; text-align: center; }

/* ── 统计 ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 14px;
  margin: 16px 0 24px;
}
.stat-item {
  text-align: center;
  padding: 14px;
  background: #f8fafc;
  border-radius: 8px;
}
.stat-value { font-size: 22px; font-weight: 700; color: #0ac8b9; }
.stat-label { font-size: 12px; color: #7a8a9a; margin-top: 4px; }

.subsection-title { font-size: 15px; font-weight: 600; color: #1a2a3a; margin-bottom: 12px; }
.champ-grid { display: flex; gap: 10px; flex-wrap: wrap; }
.champ-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 13px;
}
.champ-name { font-weight: 600; color: #1a2a3a; }
.champ-games { color: #7a8a9a; }
.champ-wr { font-weight: 600; }
.champ-wr.positive { color: #22c55e; }
.champ-wr:not(.positive) { color: #ef4444; }

.loading-state, .error-state {
  text-align: center;
  padding: 60px 20px;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e8ecf0;
  border-top-color: #0ac8b9;
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
