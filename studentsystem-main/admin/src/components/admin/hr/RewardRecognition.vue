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
        <el-table-column label="教师" min-width="140">
          <template #default="{ row }">{{ row.teacher_name || row.profile_name || row.profile_id || '-' }}</template>
        </el-table-column>
        <el-table-column label="成果名称" min-width="180">
          <template #default="{ row }">{{ row.achievement_title || '-' }}</template>
        </el-table-column>
        <el-table-column label="申报奖项" min-width="160">
          <template #default="{ row }">{{ row.declared_award || '-' }}</template>
        </el-table-column>
        <el-table-column label="奖励类别" min-width="150">
          <template #default="{ row }">{{ rewardCategory(row) }}</template>
        </el-table-column>
        <el-table-column label="奖励内容" min-width="260">
          <template #default="{ row }">{{ rewardContent(row) }}</template>
        </el-table-column>
        <el-table-column label="附件" width="90">
          <template #default="{ row }">
            <el-link v-if="row.evidence_url" type="primary" :href="row.evidence_url" target="_blank">查看</el-link>
            <span v-else>-</span>
          </template>
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

      <div class="assistant-bar">
        <el-button type="primary" round :loading="assistantLoading" @click="openAssistant">
          AI助手
        </el-button>
      </div>
    </el-card>

    <el-drawer v-model="assistantVisible" title="AI助手 · 教学奖励汇总" size="520px">
      <div v-if="assistantSummary" class="assistant-panel">
        <div class="summary-grid">
          <div class="summary-item">
            <span>符合条件老师</span>
            <strong>{{ assistantSummary.teacher_count || 0 }}</strong>
          </div>
          <div class="summary-item">
            <span>通过认定条数</span>
            <strong>{{ assistantSummary.recognition_count || 0 }}</strong>
          </div>
          <div class="summary-item">
            <span>总奖金</span>
            <strong>{{ money(assistantSummary.total_amount || 0) }}</strong>
          </div>
        </div>

        <el-empty
          v-if="!assistantSummary.teachers || assistantSummary.teachers.length === 0"
          description="暂无单个老师通过 2 条及以上奖励认定"
        />

        <div v-else class="teacher-list">
          <section v-for="teacher in assistantSummary.teachers" :key="teacher.profile_id" class="teacher-block">
            <div class="teacher-head">
              <div>
                <h3>{{ teacher.teacher_name || '未命名教师' }}</h3>
                <p>{{ teacher.employee_no || '-' }} · {{ teacher.department || '-' }}</p>
              </div>
              <div class="teacher-total">
                <span>{{ teacher.approved_count }} 项</span>
                <strong>{{ money(teacher.total_amount) }}</strong>
              </div>
            </div>

            <el-table :data="teacher.awards || []" size="small" border>
              <el-table-column label="奖励类别" width="120">
                <template #default="{ row }">{{ row.category_text || '-' }}</template>
              </el-table-column>
              <el-table-column label="认定级别" width="130">
                <template #default="{ row }">
                  {{ [row.level_text, row.rank_text].filter(Boolean).join(' / ') || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="奖项内容" min-width="190">
                <template #default="{ row }">{{ assistantAwardContent(row) }}</template>
              </el-table-column>
              <el-table-column label="奖金" width="110">
                <template #default="{ row }">{{ money(row.final_amount) }}</template>
              </el-table-column>
              <el-table-column label="政策依据" min-width="170">
                <template #default="{ row }">{{ row.policy_basis || '-' }}</template>
              </el-table-column>
            </el-table>
          </section>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { auditRewardRecognition, getRewardAssistantSummary, getRewardRecognitions } from '@/api'
import {
  categoryMap,
  levelMap,
  money,
  rankMap,
  rewardContentLabel,
  rewardRules2024,
  type RewardRuleOption,
} from '../../../../../frontend/src/utils/teaching-reward-policy'

const rows = ref<any[]>([])
const assistantVisible = ref(false)
const assistantLoading = ref(false)
const assistantSummary = ref<any>(null)

async function loadRows() {
  rows.value = await getRewardRecognitions()
}

async function loadAssistantSummary() {
  assistantLoading.value = true
  try {
    assistantSummary.value = await getRewardAssistantSummary()
  } finally {
    assistantLoading.value = false
  }
}

async function openAssistant() {
  assistantVisible.value = true
  await loadAssistantSummary()
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
  return row.category_text || categoryMap[row.category] || row.category || '-'
}

function rewardContent(row: any) {
  if (row.content) return row.content
  const rule = matchingRule(row)
  if (rule) return rewardContentLabel(rule)
  return row?.calculation_detail?.policy_basis || row?.policy_basis || '-'
}

function assistantAwardContent(row: any) {
  if (row.content) return row.content
  const category = categoryMap[row.category] || row.category || ''
  const level = levelMap[row.level] || row.level || ''
  const rank = rankMap[row.rank] || row.rank || ''
  return row.content || [category, level, rank].filter(Boolean).join(' / ') || '-'
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
  await loadRows()
  await loadAssistantSummary()
}

onMounted(async () => {
  await loadRows()
  await loadAssistantSummary()
})
</script>

<style scoped>
.admin-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.assistant-bar {
  display: flex;
  justify-content: center;
  padding: 20px 0 4px;
}
.assistant-panel { display: grid; gap: 18px; }
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.summary-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  background: #f8fafc;
}
.summary-item span {
  display: block;
  color: #64748b;
  font-size: 12px;
  margin-bottom: 6px;
}
.summary-item strong {
  color: #0f172a;
  font-size: 18px;
}
.teacher-list { display: grid; gap: 16px; }
.teacher-block {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 14px;
}
.teacher-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 12px;
}
.teacher-head h3 {
  margin: 0;
  font-size: 16px;
  color: #111827;
}
.teacher-head p {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 13px;
}
.teacher-total {
  text-align: right;
  min-width: 120px;
}
.teacher-total span {
  display: block;
  color: #64748b;
  font-size: 12px;
}
.teacher-total strong {
  display: block;
  color: #0f766e;
  margin-top: 4px;
}
</style>
