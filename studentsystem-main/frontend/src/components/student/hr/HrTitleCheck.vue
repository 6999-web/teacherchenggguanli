<template>
  <div class="hr-page">
    <n-card title="职称申报自查">
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
import { getHrTitleGap } from '@/api'

const targetTitle = ref('副教授')
const gap = ref<any>(null)

async function loadGap() {
  gap.value = await getHrTitleGap(targetTitle.value)
}

onMounted(loadGap)
</script>

<style scoped>
.hr-page { padding: 20px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.result { margin-bottom: 16px; }
</style>
