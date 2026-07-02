<template>
  <div class="hr-page">
    <n-card v-if="accessLoading" class="closed-card">
      <n-spin size="large" />
    </n-card>

    <n-card v-else-if="!performanceOpen" class="closed-card">
      <n-empty description="当前无法填写">
        <template #extra>
          <span class="closed-tip">历年绩效当前未开放填写，请等待管理员开放后再进入。</span>
        </template>
      </n-empty>
    </n-card>

    <template v-else>
    <n-card class="summary-card">
      <div class="summary-header">
        <div>
          <h2>我的历年绩效</h2>
          <p>查看管理端为本人档案录入的年度或聘期绩效记录</p>
        </div>
        <n-button type="primary" :loading="loading" @click="loadRows">刷新</n-button>
      </div>

      <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen">
        <n-grid-item>
          <div class="metric">
            <span>最新年度</span>
            <strong>{{ latestRecord?.year || '-' }}</strong>
          </div>
        </n-grid-item>
        <n-grid-item>
          <div class="metric">
            <span>最终得分</span>
            <strong>{{ scoreText(latestRecord?.final_score) }}</strong>
          </div>
        </n-grid-item>
        <n-grid-item>
          <div class="metric">
            <span>绩效等级</span>
            <strong>{{ latestRecord?.grade || '-' }}</strong>
          </div>
        </n-grid-item>
        <n-grid-item>
          <div class="metric">
            <span>记录数量</span>
            <strong>{{ rows.length }}</strong>
          </div>
        </n-grid-item>
      </n-grid>
    </n-card>

    <n-card title="绩效记录明细">
      <n-data-table :columns="columns" :data="rows" :loading="loading" />
      <n-empty v-if="!loading && rows.length === 0" description="暂无绩效记录，请联系管理员录入绩效。" class="empty-state" />
    </n-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { NTag, useMessage } from 'naive-ui'
import { getHrFillSettings, getHrPerformance } from '@/api'

const message = useMessage()
const rows = ref<any[]>([])
const loading = ref(false)
const accessLoading = ref(true)
const performanceOpen = ref(false)

const latestRecord = computed(() => rows.value[0] || null)

const columns = [
  { title: '年度', key: 'year' },
  { title: '周期', key: 'period_type', render: (row: any) => periodText(row.period_type) },
  { title: '教学成果分', key: 'teaching_score', render: (row: any) => scoreText(row.teaching_score) },
  { title: '评价考核分', key: 'evaluation_score', render: (row: any) => scoreText(row.evaluation_score) },
  { title: '奖励加分', key: 'reward_bonus', render: (row: any) => scoreText(row.reward_bonus) },
  { title: '管理员调整', key: 'admin_adjustment', render: (row: any) => scoreText(row.admin_adjustment) },
  { title: '最终得分', key: 'final_score', render: (row: any) => scoreText(row.final_score) },
  { title: '等级', key: 'grade', render: (row: any) => row.grade || '-' },
  {
    title: '状态',
    key: 'status',
    render: (row: any) => h(
      NTag,
      { type: row.status === 'published' ? 'success' : 'warning', bordered: false },
      { default: () => statusText(row.status) },
    ),
  },
  { title: '备注', key: 'note', render: (row: any) => row.note || '-' },
]

function scoreText(value: any) {
  const numberValue = Number(value)
  if (!Number.isFinite(numberValue)) return '-'
  return numberValue.toFixed(1).replace(/\.0$/, '')
}

function statusText(status: string) {
  return ({ draft: '草稿', published: '已发布' } as Record<string, string>)[status] || status || '-'
}

function periodText(value: string) {
  return ({ annual: '年度', appointment: '聘期' } as Record<string, string>)[value] || value || '-'
}

async function loadRows() {
  if (!performanceOpen.value) return
  loading.value = true
  try {
    rows.value = await getHrPerformance()
  } catch (error) {
    message.error('无法加载绩效记录，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function loadAccess() {
  accessLoading.value = true
  try {
    const settings = await getHrFillSettings()
    performanceOpen.value = Boolean(settings?.performance_open)
    if (performanceOpen.value) {
      await loadRows()
    }
  } catch (error) {
    message.error('无法加载开放填写状态，请稍后重试')
  } finally {
    accessLoading.value = false
  }
}

onMounted(loadAccess)
</script>

<style scoped>
.hr-page {
  padding: 20px;
}

.summary-card {
  margin-bottom: 16px;
}

.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 16px;
}

.summary-header h2 {
  margin: 0 0 6px;
  font-size: 22px;
}

.summary-header p {
  margin: 0;
  color: #64748b;
}

.metric {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 14px;
  min-height: 74px;
}

.metric span {
  display: block;
  color: #64748b;
  font-size: 13px;
  margin-bottom: 8px;
}

.metric strong {
  font-size: 20px;
  color: #111827;
}

.empty-state {
  margin-top: 18px;
}

.closed-card {
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.closed-tip {
  color: #64748b;
}
</style>
