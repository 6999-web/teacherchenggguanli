<template>
  <div class="admin-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>教学奖励认定</span>
          <el-button type="primary" @click="loadRows">刷新</el-button>
        </div>
      </template>
      <el-table :data="rows" border stripe style="margin-top: 18px">
        <el-table-column label="奖励类别" min-width="150">
          <template #default="{ row }">{{ rewardCategory(row) }}</template>
        </el-table-column>
        <el-table-column label="奖励内容" min-width="260">
          <template #default="{ row }">{{ rewardContent(row) }}</template>
        </el-table-column>
        <el-table-column label="奖励金额" width="140">
          <template #default="{ row }">{{ money(row.final_amount) }}</template>
        </el-table-column>
        <el-table-column label="是否批准" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="170">
          <template #default="{ row }">
            <el-button size="small" type="success" :disabled="row.status !== 'pending'" @click="audit(row, 'approve')">通过</el-button>
            <el-button size="small" type="danger" :disabled="row.status !== 'pending'" @click="audit(row, 'reject')">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { auditRewardRecognition, getRewardRecognitions } from '@/api'
import {
  categoryMap,
  money,
  rewardContentLabel,
  rewardRules2024,
  type RewardRuleOption,
} from '../../../../../frontend/src/utils/teaching-reward-policy'

const rows = ref<any[]>([])

async function loadRows() {
  rows.value = await getRewardRecognitions()
}

function matchingRule(row: any): RewardRuleOption | null {
  const data = row?.calculation_detail?.request_data || {}
  const category = data.category || row.category
  const subcategory = category === 'teaching_competition'
    ? data.competition_scope
    : category === 'teaching_reform'
      ? data.project_type
      : data.subcategory
  return rewardRules2024.find(rule => {
    if (rule.category !== category) return false
    if ((rule.subcategory || null) !== (subcategory || null)) return false
    if ((rule.level || null) !== (data.level || row.level || null)) return false
    if ((rule.rank || null) !== (data.rank || row.rank || null)) return false
    return true
  }) || null
}

function rewardCategory(row: any) {
  return categoryMap[row.category] || row.category || '-'
}

function rewardContent(row: any) {
  const rule = matchingRule(row)
  if (rule) return rewardContentLabel(rule)
  return row?.calculation_detail?.policy_basis || '-'
}

function statusText(status: string) {
  const map: Record<string, string> = { pending: '待审核', approved: '已批准', rejected: '已驳回' }
  return map[status] || status || '-'
}

function statusTag(status: string) {
  const map: Record<string, string> = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

async function audit(row: any, action: string) {
  await auditRewardRecognition(row.id, { action })
  ElMessage.success('审核完成')
  loadRows()
}

onMounted(loadRows)
</script>

<style scoped>
.admin-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
