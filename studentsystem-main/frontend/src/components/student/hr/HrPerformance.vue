<template>
  <div class="hr-page">
    <n-card title="历年绩效记录">
      <n-data-table :columns="columns" :data="rows" :loading="loading" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getHrPerformance } from '@/api'

const rows = ref<any[]>([])
const loading = ref(false)
const columns = [
  { title: '年度', key: 'year' },
  { title: '周期', key: 'period_type' },
  { title: '教学成果分', key: 'teaching_score' },
  { title: '评价考核分', key: 'evaluation_score' },
  { title: '奖励加分', key: 'reward_bonus' },
  { title: '最终得分', key: 'final_score' },
  { title: '等级', key: 'grade' },
  { title: '状态', key: 'status' },
]

async function loadRows() {
  loading.value = true
  try {
    rows.value = await getHrPerformance()
  } finally {
    loading.value = false
  }
}

onMounted(loadRows)
</script>

<style scoped>
.hr-page { padding: 20px; }
</style>
