<template>
  <div class="hr-page">
    <n-card class="summary-card">
      <div class="summary-header">
        <div>
          <h2>教师个人档案</h2>
          <p>统一查看成果认定、教学奖励、绩效考核、职称申报和人事资料</p>
        </div>
        <n-button type="primary" @click="loadData">刷新</n-button>
      </div>

      <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen">
        <n-grid-item>
          <div class="metric"><span>已认定成果</span><strong>{{ summary.approved_count }}</strong></div>
        </n-grid-item>
        <n-grid-item>
          <div class="metric"><span>教学奖励认定</span><strong>{{ money(rewardSummary.total_amount) }}</strong></div>
        </n-grid-item>
        <n-grid-item>
          <div class="metric"><span>当期绩效</span><strong>{{ performanceText }}</strong></div>
        </n-grid-item>
        <n-grid-item>
          <div class="metric" :class="{ warn: !titleGap?.eligible }">
            <span>职称自查</span><strong>{{ titleGap?.eligible ? '已达标' : '待完善' }}</strong>
          </div>
        </n-grid-item>
      </n-grid>
    </n-card>

    <n-grid :cols="2" :x-gap="16" :y-gap="16" responsive="screen">
      <n-grid-item>
        <n-card title="基本信息">
          <n-descriptions :column="1" bordered>
            <n-descriptions-item label="姓名">{{ profile.name || '-' }}</n-descriptions-item>
            <n-descriptions-item label="工号">{{ profile.employee_no || '-' }}</n-descriptions-item>
            <n-descriptions-item label="院系">{{ profile.department || '-' }}</n-descriptions-item>
            <n-descriptions-item label="身份类型">{{ profile.employment_type || '-' }}</n-descriptions-item>
            <n-descriptions-item label="学历/学位">{{ profile.education || '-' }} / {{ profile.degree || '-' }}</n-descriptions-item>
            <n-descriptions-item label="岗位/职称">{{ profile.position || '-' }} / {{ profile.current_title || '-' }}</n-descriptions-item>
            <n-descriptions-item label="联系方式">{{ profile.phone || '-' }} {{ profile.email || '' }}</n-descriptions-item>
          </n-descriptions>
        </n-card>
      </n-grid-item>

      <n-grid-item>
        <n-card title="资料修改申请">
          <n-form :model="editForm" label-placement="left" label-width="86">
            <n-form-item label="学历"><n-input v-model:value="editForm.education" /></n-form-item>
            <n-form-item label="学位"><n-input v-model:value="editForm.degree" /></n-form-item>
            <n-form-item label="岗位"><n-input v-model:value="editForm.position" /></n-form-item>
            <n-form-item label="职称"><n-input v-model:value="editForm.current_title" /></n-form-item>
            <n-form-item label="电话"><n-input v-model:value="editForm.phone" /></n-form-item>
            <n-form-item label="邮箱"><n-input v-model:value="editForm.email" /></n-form-item>
            <n-form-item label="办公室"><n-input v-model:value="editForm.office_location" /></n-form-item>
          </n-form>
          <n-button type="primary" :loading="submitting" @click="submitChange">提交审核</n-button>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card title="教学奖励认定记录" class="section-card">
      <n-empty v-if="rewardRecognitions.length === 0" description="暂无教学奖励认定记录" />
      <n-list v-else bordered>
        <n-list-item v-for="item in rewardRecognitions" :key="item.id">
          <div class="reward-row">
            <div>
              <strong>{{ label(categoryMap, item.category) }}</strong>
              <span>{{ label(levelMap, item.level) }} / {{ label(rankMap, item.rank) }}</span>
              <small>{{ rewardContent(item) }}</small>
            </div>
            <div class="reward-amount">
              <strong>{{ money(item.final_amount) }}</strong>
              <span>{{ statusText(item.status) }}</span>
            </div>
          </div>
        </n-list-item>
      </n-list>
    </n-card>

    <n-card title="职称缺口提醒" class="section-card">
      <n-alert v-if="titleGap?.eligible" type="success">当前条件满足 {{ titleGap.target_title }} 申报要求。</n-alert>
      <n-list v-else bordered>
        <n-list-item v-for="item in titleGap?.missing_items || []" :key="item">{{ item }}</n-list-item>
      </n-list>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useMessage } from 'naive-ui'
import { getHrDashboard, submitHrProfileChange } from '@/api'
import {
  categoryMap,
  levelMap,
  money,
  rankMap,
  rewardContentLabel,
  rewardRules2024,
  type RewardRuleOption,
} from '@/utils/teaching-reward-policy'

const message = useMessage()
const profile = ref<any>({})
const summary = reactive({ approved_count: 0, estimated_reward_total: 0 })
const rewardSummary = reactive({ count: 0, total_amount: 0, approved_total_amount: 0, pending_count: 0 })
const rewardRecognitions = ref<any[]>([])
const currentPerformance = ref<any>(null)
const titleGap = ref<any>(null)
const submitting = ref(false)
const editForm = reactive<any>({})

const performanceText = computed(() => currentPerformance.value ? `${currentPerformance.value.final_score} / ${currentPerformance.value.grade || '-'}` : '暂无')

function label(map: Record<string, string>, value: string) {
  return map[value] || value || '-'
}

function statusText(status: string) {
  const map: Record<string, string> = { pending: '待认定', approved: '已认定', rejected: '已驳回' }
  return map[status] || status || '-'
}

function matchingRule(item: any): RewardRuleOption | null {
  const data = item?.calculation_detail?.request_data || {}
  const category = data.category || item.category
  const subcategory = category === 'teaching_competition'
    ? data.competition_scope
    : category === 'teaching_reform'
      ? data.project_type
      : data.subcategory
  return rewardRules2024.find(rule => {
    if (rule.category !== category) return false
    if ((rule.subcategory || null) !== (subcategory || null)) return false
    if ((rule.level || null) !== (data.level || item.level || null)) return false
    if ((rule.rank || null) !== (data.rank || item.rank || null)) return false
    return true
  }) || null
}

function rewardContent(item: any) {
  const rule = matchingRule(item)
  if (rule) return rewardContentLabel(rule)
  return item?.policy_basis || ''
}

async function loadData() {
  const data = await getHrDashboard()
  profile.value = data.profile || {}
  Object.assign(summary, data.achievement_summary || {})
  Object.assign(rewardSummary, data.reward_recognition_summary || {})
  rewardRecognitions.value = data.reward_recognitions || []
  currentPerformance.value = data.current_performance
  titleGap.value = data.title_gap
  Object.assign(editForm, profile.value)
}

async function submitChange() {
  submitting.value = true
  try {
    await submitHrProfileChange(editForm)
    message.success('已提交管理员审核')
  } finally {
    submitting.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.hr-page { padding: 20px; }
.summary-card, .section-card { margin-bottom: 16px; }
.summary-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; gap: 16px; }
.summary-header h2 { margin: 0 0 6px; font-size: 22px; }
.summary-header p { margin: 0; color: #64748b; }
.metric { border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px; min-height: 74px; }
.metric span { display: block; color: #64748b; font-size: 13px; margin-bottom: 8px; }
.metric strong { font-size: 20px; color: #111827; }
.metric.warn strong { color: #d97706; }
.reward-row { display: flex; justify-content: space-between; gap: 16px; width: 100%; align-items: center; }
.reward-row span, .reward-row small { display: block; color: #64748b; margin-top: 4px; }
.reward-amount { text-align: right; min-width: 120px; }
.reward-amount strong { color: #0f766e; }
</style>
