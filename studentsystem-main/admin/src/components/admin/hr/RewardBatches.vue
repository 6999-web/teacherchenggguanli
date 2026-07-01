<template>
  <div class="admin-page">
    <el-card shadow="never">
      <template #header>奖励批次与汇总</template>
      <el-form :inline="true" :model="form">
        <el-form-item label="年度"><el-input-number v-model="form.year" :min="2020" /></el-form-item>
        <el-form-item label="批次名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item><el-button type="primary" @click="create">创建年度批次</el-button></el-form-item>
      </el-form>
      <el-alert
        :title="`当前待入批次的已批准奖励 ${pendingApproved.length} 条，合计 ${formatMoney(pendingTotal)}`"
        type="info"
        show-icon
        :closable="false"
        style="margin-bottom: 16px"
      />
      <el-table :data="rows" border stripe>
        <el-table-column prop="year" label="年度" />
        <el-table-column prop="name" label="批次名称" />
        <el-table-column label="总金额"><template #default="{ row }">{{ formatMoney(row.total_amount) }}</template></el-table-column>
        <el-table-column label="状态"><template #default="{ row }">{{ statusText(row.status) }}</template></el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createRewardBatch, getRewardBatches, getRewardRecognitions } from '@/api'
import { money } from '../../../../../frontend/src/utils/teaching-reward-policy'

const rows = ref<any[]>([])
const recognitions = ref<any[]>([])
const form = reactive({ year: new Date().getFullYear(), name: '' })
const pendingApproved = computed(() => recognitions.value.filter(row => row.status === 'approved' && !row.batch_id))
const pendingTotal = computed(() => pendingApproved.value.reduce((sum, row) => sum + Number(row.final_amount || 0), 0))

async function loadRows() {
  const [batchRows, recognitionRows] = await Promise.all([getRewardBatches(), getRewardRecognitions({ status: 'approved' })])
  rows.value = batchRows
  recognitions.value = recognitionRows
}

async function create() {
  await createRewardBatch(form)
  ElMessage.success('批次已创建')
  loadRows()
}

function formatMoney(value: number) {
  return money(Number(value || 0))
}

function statusText(status: string) {
  return ({ draft: '草稿', approved: '已批准', paid: '已发放' } as Record<string, string>)[status] || status || '-'
}

onMounted(loadRows)
</script>

<style scoped>
.admin-page { padding: 20px; }
</style>
