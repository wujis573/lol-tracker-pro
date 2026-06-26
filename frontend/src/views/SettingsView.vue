<template>
  <div class="settings-page">
    <h1 class="page-title">设置</h1>

    <div class="settings-card card">
      <h2 class="settings-section">API 配置</h2>

      <div class="setting-item">
        <label class="setting-label">Riot API 地址（国服代理）</label>
        <input v-model="form.riotUrl" class="setting-input" placeholder="https://api.riot-gateway.cn" />
      </div>

      <div class="setting-item">
        <label class="setting-label">Riot API Key（可选）</label>
        <input v-model="form.riotKey" class="setting-input" type="password" placeholder="输入 API Key" />
      </div>

      <div class="setting-item">
        <label class="setting-label">OP.GG API 地址</label>
        <input v-model="form.opggUrl" class="setting-input" placeholder="https://api.op.gg" />
      </div>

      <div class="setting-item">
        <label class="setting-label">OP.GG API Key（可选）</label>
        <input v-model="form.opggKey" class="setting-input" type="password" placeholder="输入 API Key" />
      </div>
    </div>

    <div class="settings-card card">
      <h2 class="settings-section">缓存设置</h2>

      <div class="setting-item">
        <label class="setting-label">缓存有效期（秒）</label>
        <input v-model.number="form.cacheTtl" class="setting-input" type="number" min="60" max="3600" />
        <span class="setting-hint">默认 300 秒（5分钟）</span>
      </div>
    </div>

    <div class="settings-card card">
      <h2 class="settings-section">关于</h2>
      <div class="about-text">
        <p><strong>LOL 战绩查询</strong> v1.0.0</p>
        <p class="text-gray-500 text-sm mt-2">基于 FastAPI + Vue 3 构建</p>
        <p class="text-gray-500 text-sm">数据来源：Riot API、OP.GG API</p>
        <p class="text-gray-400 text-xs mt-4">本工具仅供学习交流使用，与 Riot Games 无关</p>
      </div>
    </div>

    <div class="settings-actions">
      <button @click="saveSettings" class="btn btn-primary" :disabled="saving">
        {{ saving ? '保存中...' : '保存设置' }}
      </button>
    </div>

    <div v-if="message" :class="['toast', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const form = ref({
  riotUrl: 'https://api.riot-gateway.cn',
  riotKey: '',
  opggUrl: 'https://api.op.gg',
  opggKey: '',
  cacheTtl: 300,
})
const saving = ref(false)
const message = ref('')
const messageType = ref('success')

onMounted(() => {
  const saved = localStorage.getItem('lol-tracker-settings')
  if (saved) {
    try { form.value = JSON.parse(saved) } catch {}
  }
})

async function saveSettings() {
  saving.value = true
  try {
    localStorage.setItem('lol-tracker-settings', JSON.stringify(form.value))
    message.value = '设置已保存'
    messageType.value = 'success'
    setTimeout(() => message.value = '', 3000)
  } catch (e) {
    message.value = '保存失败'
    messageType.value = 'error'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.settings-page { max-width: 640px; margin: 0 auto; }
.page-title { font-size: 24px; font-weight: 700; color: #1a2a3a; margin-bottom: 24px; }

.settings-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e8ecf0;
  margin-bottom: 16px;
}
.settings-section {
  font-size: 16px;
  font-weight: 600;
  color: #1a2a3a;
  margin-bottom: 16px;
}
.setting-item { margin-bottom: 16px; }
.setting-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #5a6a7a;
  margin-bottom: 6px;
}
.setting-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #dde3ea;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s;
}
.setting-input:focus { border-color: #0ac8b9; }
.setting-hint {
  display: block;
  font-size: 12px;
  color: #aaa;
  margin-top: 4px;
}
.about-text { font-size: 14px; color: #5a6a7a; line-height: 1.7; }

.settings-actions { margin-top: 24px; }

.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  z-index: 200;
  animation: slideUp 0.3s;
}
.toast.success { background: #dcfce7; color: #166534; }
.toast.error { background: #fee2e2; color: #991b1b; }

@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
