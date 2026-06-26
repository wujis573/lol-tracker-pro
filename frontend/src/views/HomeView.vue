<template>
  <div class="home-page">
    <div class="hero">
      <div class="hero-content">
        <img src="https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/29.png" alt="LOL" class="hero-icon" />
        <h1 class="hero-title">英雄联盟战绩查询</h1>
        <p class="hero-subtitle">查询国服召唤师信息、排位段位、最近对局</p>
      </div>
    </div>

    <div class="features">
      <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <h3>召唤师搜索</h3>
        <p>输入昵称即可查询召唤师信息</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>战绩统计</h3>
        <p>KDA、胜率、常用英雄一目了然</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🏆</div>
        <h3>排行榜</h3>
        <p>查看最强王者、傲世宗师排行</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📜</div>
        <h3>对局详情</h3>
        <p>击杀、装备、符文完整展示</p>
      </div>
    </div>

    <div class="quick-search">
      <h2 class="section-title">快速查询</h2>
      <p class="section-desc">试试搜索以下召唤师</p>
      <div class="example-tags">
        <span
          v-for="name in examples"
          :key="name"
          class="example-tag"
          @click="search(name)"
        >{{ name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { summonerApi } from '../api'

const router = useRouter()
const examples = ['Faker', 'Uzi', 'Clearlove', 'Rookie']

async function search(name) {
  try {
    const res = await summonerApi.search(name)
    if (res.success) {
      router.push(`/summoner/${encodeURIComponent(res.data.puuid)}`)
    } else {
      alert(res.message || '未找到该召唤师')
    }
  } catch (e) {
    alert(e.message || '查询失败')
  }
}
</script>

<style scoped>
.home-page {
  max-width: 900px;
  margin: 0 auto;
}

/* ── Hero 区 ── */
.hero {
  text-align: center;
  padding: 48px 0 36px;
  background: linear-gradient(180deg, #0a3251 0%, #f0f4f8 100%);
  border-radius: 16px;
  margin-bottom: 32px;
}
.hero-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.hero-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin-bottom: 16px;
  border: 3px solid #c8aa6e;
}
.hero-title {
  font-size: 32px;
  font-weight: 800;
  color: #091428;
  letter-spacing: 2px;
}
.hero-subtitle {
  margin-top: 8px;
  color: #5a6a7a;
  font-size: 15px;
}

/* ── 功能卡片 ── */
.features {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 36px;
}
.feature-card {
  background: white;
  border-radius: 12px;
  padding: 24px 16px;
  text-align: center;
  border: 1px solid #e8ecf0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  transition: transform 0.15s, box-shadow 0.15s;
}
.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
.feature-icon { font-size: 36px; margin-bottom: 10px; }
.feature-card h3 {
  font-size: 15px;
  font-weight: 600;
  color: #1a2a3a;
  margin-bottom: 6px;
}
.feature-card p {
  font-size: 12px;
  color: #7a8a9a;
}

/* ── 快速查询 ── */
.quick-search {
  background: white;
  border-radius: 12px;
  padding: 28px;
  border: 1px solid #e8ecf0;
}
.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a2a3a;
}
.section-desc {
  color: #7a8a9a;
  font-size: 13px;
  margin: 4px 0 16px;
}
.example-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.example-tag {
  padding: 6px 16px;
  background: #f0f4f8;
  border-radius: 20px;
  font-size: 13px;
  color: #3a506b;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid transparent;
}
.example-tag:hover {
  background: #0ac8b9;
  color: white;
  border-color: #0ac8b9;
}
</style>
