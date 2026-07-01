<template>
  <div class="hr-page">
    <n-card title="教学奖励申报">
      <n-alert type="info" class="section-gap">
        教学奖励申报和教师人事档案共用同一份认定数据。这里提交后，会自动同步到“教师人事管理体系”的个人档案中。
      </n-alert>

      <div class="apply-table section-gap">
        <div class="apply-head">
          <span>奖励类别</span>
          <span>奖励内容</span>
          <span>奖励金额</span>
          <span>操作</span>
        </div>

        <div v-for="(row, index) in rows" :key="row.id" class="apply-line">
          <n-select
            v-model:value="row.category"
            :options="categoryOptions"
            placeholder="选择奖励类别"
            clearable
            @update:value="handleCategoryChange(row)"
          />
          <n-select
            v-model:value="row.ruleKey"
            :options="contentOptions(row)"
            :disabled="!row.category"
            filterable
            clearable
            placeholder="选择奖励内容"
          />
          <n-input :value="rowAmountText(row)" readonly placeholder="自动显示" />
          <n-button
            tertiary
            type="error"
            :disabled="rows.length === 1"
            @click="removeRow(index)"
          >
            删除
          </n-button>
        </div>
      </div>

      <n-space class="section-gap">
        <n-button @click="addRow">添加一条新的内容</n-button>
        <n-button type="primary" :loading="submitting" @click="submit">统一提交奖励认定</n-button>
        <n-button @click="loadExisting">读取已有数据</n-button>
      </n-space>

      <n-alert v-if="selectedRules.length > 0" type="success" class="section-gap">
        当前已选择 {{ selectedRules.length }} 条奖励内容，预计总金额：{{ money(totalAmount) }}。
      </n-alert>

      <n-alert v-if="submitSummary" type="success" class="section-gap">
        已提交 {{ submitSummary.count }} 条奖励认定，后端拟认定总金额：{{ money(submitSummary.total) }}。记录已同步到人事档案。
      </n-alert>
    </n-card>

    <n-card title="已有教学奖励认定" class="section-gap">
      <n-empty v-if="recognitions.length === 0" description="暂无奖励认定记录" />
      <n-list v-else bordered>
        <n-list-item v-for="item in recognitions" :key="item.id">
          <div class="reward-row">
            <div>
              <strong>{{ label(categoryMap, item.category) }}</strong>
              <span>{{ label(levelMap, item.level) }} / {{ label(rankMap, item.rank) }}</span>
              <small>{{ requestText(item) }}</small>
            </div>
            <div class="reward-amount">
              <strong>{{ money(item.final_amount) }}</strong>
              <span>{{ statusText(item.status) }}</span>
            </div>
          </div>
        </n-list-item>
      </n-list>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useMessage } from 'naive-ui'
import { createMyRewardRecognition, getMyRewardRecognitions } from '@/api'
import {
  categoryMap,
  levelMap,
  money,
  rankMap,
  rewardContentLabel,
  rewardRuleKey,
  rewardRules2024,
  type RewardRuleOption,
} from '@/utils/teaching-reward-policy'

type RewardApplyRow = {
  id: number
  category: string | null
  ruleKey: string | null
}

const message = useMessage()
const submitting = ref(false)
const submitSummary = ref<{ count: number; total: number } | null>(null)
const recognitions = ref<any[]>([])
let nextRowId = 1

const rows = reactive<RewardApplyRow[]>([createRow()])

const categoryOptions = Object.entries(categoryMap).map(([value, label]) => ({
  label,
  value,
}))

const selectedRules = computed(() => rows.map(rowRule).filter(Boolean) as RewardRuleOption[])
const totalAmount = computed(() => selectedRules.value.reduce((sum, rule) => sum + rule.amount, 0))

function createRow(): RewardApplyRow {
  return { id: nextRowId++, category: null, ruleKey: null }
}

function addRow() {
  rows.push(createRow())
}

function removeRow(index: number) {
  rows.splice(index, 1)
  submitSummary.value = null
}

function handleCategoryChange(row: RewardApplyRow) {
  row.ruleKey = null
  submitSummary.value = null
}

function contentOptions(row: RewardApplyRow) {
  if (!row.category) return []
  return rewardRules2024
    .filter(rule => rule.category === row.category)
    .map(rule => ({
      label: rewardContentLabel(rule),
      value: rewardRuleKey(rule),
    }))
}

function rowRule(row: RewardApplyRow) {
  if (!row.category || !row.ruleKey) return null
  return rewardRules2024.find(rule => rule.category === row.category && rewardRuleKey(rule) === row.ruleKey) || null
}

function rowAmountText(row: RewardApplyRow) {
  const rule = rowRule(row)
  return rule ? money(rule.amount) : ''
}

function label(map: Record<string, string>, value: string) {
  return map[value] || value || '-'
}

function statusText(status: string) {
  const map: Record<string, string> = { pending: '待认定', approved: '已认定', rejected: '已驳回' }
  return map[status] || status || '-'
}

function requestText(item: any) {
  const data = item?.calculation_detail?.request_data || {}
  const rule = recognitionRule(item)
  const extras = [
    data.project_stage === 'established' ? '立项阶段' : data.project_stage === 'completed' ? '结题阶段' : '',
  ].filter(Boolean)
  return [rule ? rewardContentLabel(rule) : '', ...extras].filter(Boolean).join(' · ')
}

function recognitionRule(item: any) {
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

function payloadFromRule(rule: RewardRuleOption) {
  const payload: Record<string, any> = {
    category: rule.category,
    subcategory: rule.subcategory,
    level: rule.level,
    rank: rule.rank,
  }

  if (rule.category === 'teaching_competition') {
    payload.competition_scope = rule.subcategory
    payload.participation_type = 'self'
  }

  if (rule.category === 'teaching_reform') {
    payload.project_type = rule.rank
  }

  if (rule.category === 'textbook_construction' && rule.subcategory?.includes('20万字以上')) {
    payload.word_count = 200000
  }

  if (rule.category === 'textbook_construction' && rule.subcategory?.includes('20万字以下')) {
    payload.word_count = 1
  }

  return payload
}

async function loadExisting() {
  recognitions.value = await getMyRewardRecognitions()
}

async function submit() {
  const hasTouchedIncomplete = rows.some(row => (row.category || row.ruleKey) && !rowRule(row))
  const completeRows = rows.filter(row => rowRule(row))

  if (hasTouchedIncomplete) {
    message.warning('请把已开始填写的奖励内容选择完整后再提交')
    return
  }

  if (completeRows.length === 0) {
    message.warning('请至少选择一条奖励内容')
    return
  }

  submitting.value = true
  try {
    const submitted = []
    for (const row of completeRows) {
      const rule = rowRule(row)
      if (rule) {
        submitted.push(await createMyRewardRecognition(payloadFromRule(rule)))
      }
    }
    submitSummary.value = {
      count: submitted.length,
      total: submitted.reduce((sum, item) => sum + Number(item?.final_amount || 0), 0),
    }
    message.success('奖励认定已提交，并同步到人事档案')
    rows.splice(0, rows.length, createRow())
    await loadExisting()
  } finally {
    submitting.value = false
  }
}

onMounted(loadExisting)
</script>

<style scoped>
.hr-page { padding: 20px; }
.section-gap { margin-top: 16px; }
.apply-table { display: grid; gap: 10px; }
.apply-head,
.apply-line {
  display: grid;
  grid-template-columns: minmax(210px, 1fr) minmax(320px, 1.4fr) minmax(150px, 0.7fr) 80px;
  gap: 12px;
  align-items: center;
}
.apply-head {
  color: #475569;
  font-size: 13px;
  font-weight: 600;
  padding: 0 2px;
}
.reward-row { display: flex; justify-content: space-between; gap: 16px; width: 100%; align-items: center; }
.reward-row span, .reward-row small { display: block; color: #64748b; margin-top: 4px; }
.reward-amount { text-align: right; min-width: 120px; }
.reward-amount strong { color: #0f766e; }

@media (max-width: 900px) {
  .apply-head { display: none; }
  .apply-line {
    grid-template-columns: 1fr;
    padding: 12px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
  }
}
</style>
