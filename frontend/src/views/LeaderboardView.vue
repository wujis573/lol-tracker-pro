<template>
  <div class="leaderboard-page">
    <h1 class="page-title">排行榜</h1>

    <div class="tabs">
      <button :class="['tab', { active: activeTab === 'challenger' }]" @click="load('challenger')">
        最强王者
      </button>
      <button :class="['tab', { active: activeTab === 'grandmaster' }]" @click="load('grandmaster')">
        傲世宗师
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载排行榜...</p>
    </div>

    <div v-else-if="entries.length" class="leaderboard-table card">
      <div class="table-header">
        <span class="col-rank">排名</span>
        <span class="col-summoner">召唤师</span>
        <span class="col-tier">段位</span>
        <span class="col-lp">胜点</span>
        <span class="col-wr">胜率</span>
      </div>
      <div
        v-for="(e, i) in entries"
        :key="e.puuid"
        class="table-row"
        :class="{ top3: i < 3 }"
      >
        <span class="col-rank" :class="rankClass(i)">
          {{ i + 1 }}
        </span>
        <span class="col-summoner">
          <span class="summoner-name">{{ e.summonerName }}</span>
        </span>
        <span class="col-tier">
          <span :class="tierClass(e.tier)">{{ e.tier }} {{ e.rankNum }}</span>
        </span>
        <span class="col-lp">{{ e.leaguePoints }}</span>
        <span class="col-wr" :class="{ positive: e.winRate >= 50 }">
          {{ e.winRate }}%
          <span class="w-l">({{ e.wins }}W {{ e.losses }}L)</span>
        </span>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>暂无排行数据</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { leaderboardApi } from '../api'

const activeTab = ref('challenger')
const entries = ref([])
const loading = ref(false)

async function load(tab) {
  activeTab.value = tab
  loading.value = true
  try {
    const res = tab === 'challenger'
      ? await leaderboardApi.getChallenger()
      : await leaderboardApi.getGrandmaster()
    if (res.success) {
      entries.value = res.data
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
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

function rankClass(i) {
  if (i === 0) return 'rank-1'
  if (i === 1) return 'rank-2'
  if (i === 2) return 'rank-3'
  return ''
}

onMounted(() => load('challenger'))
</script>

<style scoped>
.leaderboard-page { max-width: 900px; margin: 0 auto; }
.page-title { font-size: 24px; font-weight: 700; color: #1a2a3a; margin-bottom: 20px; }

/* 标签页 */
.tabs { display: flex; gap: 8px; margin-bottom: 20px; }
.tab {
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  border: 1px solid #e8ecf0;
  background: white;
  color: #5a6a7a;
  cursor: pointer;
  transition: all 0.15s;
}
.tab:hover { background: #f8fafc; }
.tab.active { background: #0ac8b9; color: white; border-color: #0ac8b9; }

/* 排行榜表格 */
.leaderboard-table {
  overflow: hidden;
}
.table-header {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #e8ecf0;
  font-size: 12px;
  color: #7a8a9a;
  font-weight: 600;
  text-transform: uppercase;
}
.table-row {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.1s;
}
.table-row:hover { background: #fafbfc; }
.table-row.top3 { background: #fffbeb; }
.table-row.top3:hover { background: #fef3c7; }

.col-rank { width: 50px; font-weight: 700; font-size: 16px; }
.rank-1 { color: #f0c020; font-size: 20px; }
.rank-2 { color: #a8a8a8; font-size: 18px; }
.rank-3 { color: #cd7f32; font-size: 18px; }

.col-summoner { flex: 1; }
.summoner-name { font-weight: 600; color: #1a2a3a; }

.col-tier { width: 140px; }
.tier-challenger { color: #c8aa6e; font-weight: 700; }
.tier-grandmaster { color: #e04848; font-weight: 700; }
.tier-master { color: #b44aff; font-weight: 700; }
.tier-diamond { color: #a0d2f0; }
.tier-platinum { color: #30efd0; }
.tier-gold { color: #f0c020; }
.tier-silver { color: #a8a8a8; }
.tier-bronze { color: #cd7f32; }
.tier-iron { color: #7a7a7a; }

.col-lp { width: 80px; text-align: center; font-weight: 600; color: #1a2a3a; }

.col-wr { width: 120px; text-align: right; }
.w-l { font-size: 12px; color: #aaa; margin-left: 4px; }
.positive { color: #22c55e; font-weight: 600; }

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
