<template>
  <div class="app-layout">
    <!-- 顶部导航 -->
    <header class="top-nav">
      <div class="nav-inner">
        <router-link to="/" class="logo">
          <img src="https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/29.png" alt="logo" class="logo-icon" />
          <span class="logo-text">LOL 战绩查询</span>
        </router-link>

        <div class="search-box">
          <input
            v-model="query"
            @keyup.enter="handleSearch"
            type="text"
            placeholder="输入召唤师昵称..."
            class="search-input"
          />
          <button @click="handleSearch" class="search-btn" :disabled="loading">
            <svg v-if="loading" class="spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" stroke-dasharray="60" stroke-dashoffset="20" />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="7"/><path d="m21 21-4.35-4.35"/>
            </svg>
          </button>
        </div>

        <nav class="nav-links">
          <router-link to="/leaderboard" class="nav-link">排行榜</router-link>
          <router-link to="/settings" class="nav-link">设置</router-link>
        </nav>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { summonerApi } from './api'

const router = useRouter()
const query = ref('')
const loading = ref(false)

async function handleSearch() {
  if (!query.value.trim() || loading.value) return
  loading.value = true
  try {
    const res = await summonerApi.search(query.value.trim())
    if (res.success) {
      const data = res.data
      router.push(`/summoner/${encodeURIComponent(data.puuid)}`)
    } else {
      alert(res.message || '未找到该召唤师')
    }
  } catch (e) {
    alert(e.message || '查询失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

/* ── 顶部导航 ── */
.top-nav {
  background: linear-gradient(135deg, #0a3251 0%, #091428 100%);
  border-bottom: 3px solid #c8aa6e;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 12px rgba(0,0,0,0.25);
}

.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #c8aa6e;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #f0e6d2;
  letter-spacing: 1px;
  white-space: nowrap;
}

/* ── 搜索框 ── */
.search-box {
  flex: 1;
  max-width: 520px;
  display: flex;
  align-items: center;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(200,170,110,0.3);
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.2s;
}
.search-box:focus-within {
  border-color: #c8aa6e;
}

.search-input {
  flex: 1;
  padding: 10px 16px;
  background: transparent;
  border: none;
  color: #f0e6d2;
  font-size: 15px;
  outline: none;
}
.search-input::placeholder {
  color: rgba(240,230,210,0.45);
}

.search-btn {
  padding: 10px 16px;
  background: #c8aa6e;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}
.search-btn:hover { background: #b5954d; }
.search-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.search-btn svg { width: 18px; height: 18px; color: #091428; }

@keyframes spin {
  to { transform: rotate(360deg); }
}
.spin { animation: spin 0.8s linear infinite; }

/* ── 导航链接 ── */
.nav-links {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.nav-link {
  padding: 8px 18px;
  color: rgba(240,230,210,0.7);
  text-decoration: none;
  font-size: 14px;
  border-radius: 6px;
  transition: all 0.15s;
  white-space: nowrap;
}
.nav-link:hover {
  color: #f0e6d2;
  background: rgba(200,170,110,0.12);
}
.nav-link.router-link-active {
  color: #091428;
  background: #c8aa6e;
  font-weight: 600;
}

/* ── 主内容区 ── */
.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 28px 24px;
}

/* ── 过渡动画 ── */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.fade-enter-from { opacity: 0; transform: translateY(8px); }
.fade-leave-to   { opacity: 0; transform: translateY(-8px); }

/* ── 响应式 ── */
@media (max-width: 768px) {
  .nav-inner { padding: 0 12px; gap: 12px; }
  .logo-text { display: none; }
  .search-box { max-width: 100%; }
  .main-content { padding: 16px 12px; }
}
</style>
