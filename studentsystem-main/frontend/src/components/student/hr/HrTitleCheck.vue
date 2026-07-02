<template>
  <div class="hr-page">
    <n-card v-if="accessLoading" class="closed-card">
      <n-spin size="large" />
    </n-card>

    <n-card v-else-if="!titleCheckOpen" class="closed-card">
      <n-empty description="当前无法填写">
        <template #extra>
          <span class="closed-tip">职称自查当前未开放填写，请等待管理员开放后再进入。</span>
        </template>
      </n-empty>
    </n-card>

    <n-card v-else title="职称申报自查">
      <div class="toolbar">
        <n-input v-model:value="targetTitle" placeholder="目标职称，如：副教授" style="max-width: 260px" />
        <n-button type="primary" @click="loadGap">开始自查</n-button>
      </div>
      <n-alert :type="gap?.eligible ? 'success' : 'warning'" class="result">
        {{ gap?.eligible ? `当前满足 ${gap?.target_title} 申报条件` : `当前暂未满足 ${gap?.target_title || targetTitle} 申报条件` }}
      </n-alert>
      <n-grid :cols="2" :x-gap="16" responsive="screen">
        <n-grid-item>
          <n-card title="已满足">
            <n-list bordered>
              <n-list-item v-for="item in gap?.satisfied_items || []" :key="item">{{ item }}</n-list-item>
            </n-list>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="待补齐">
            <n-list bordered>
              <n-list-item v-for="item in gap?.missing_items || []" :key="item">{{ item }}</n-list-item>
            </n-list>
          </n-card>
        </n-grid-item>
      </n-grid>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getHrFillSettings, getHrTitleGap } from '@/api'

const targetTitle = ref('副教授')
const gap = ref<any>(null)
const accessLoading = ref(true)
const titleCheckOpen = ref(false)

async function loadGap() {
  if (!titleCheckOpen.value) return
  gap.value = await getHrTitleGap(targetTitle.value)
}

async function loadAccess() {
  accessLoading.value = true
  try {
    const settings = await getHrFillSettings()
    titleCheckOpen.value = Boolean(settings?.title_check_open)
    if (titleCheckOpen.value) {
      await loadGap()
    }
  } finally {
    accessLoading.value = false
  }
}

onMounted(loadAccess)
</script>

<style scoped>
.hr-page { padding: 20px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.result { margin-bottom: 16px; }
.closed-card {
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.closed-tip { color: #64748b; }
</style>
