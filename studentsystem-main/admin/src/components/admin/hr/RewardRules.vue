<template>
  <div class="admin-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>教学奖励规则配置</span>
          <div class="header-actions">
            <el-button @click="seedPolicy">导入2024版政策</el-button>
            <el-button type="primary" @click="loadAll">刷新</el-button>
          </div>
        </div>
      </template>

      <el-tabs>
        <el-tab-pane label="金额规则">
          <el-form :model="ruleForm" label-width="110px">
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="奖金规则">
                  <el-select
                    v-model="selectedRuleKey"
                    filterable
                    placeholder="请选择2024版奖励办法规则"
                    @change="applyRulePreset"
                  >
                    <el-option
                      v-for="option in policyRuleOptions"
                      :key="option.value"
                      :label="option.label"
                      :value="option.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="政策版本">
                  <el-input v-model="ruleForm.policy_version" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="奖励类别">
                  <el-input :model-value="labelCategory(ruleForm.category)" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="级别">
                  <el-input :model-value="labelLevel(ruleForm.level)" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="等级">
                  <el-input :model-value="labelRank(ruleForm.rank)" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="金额">
                  <el-input-number v-model="ruleForm.amount" :min="0" />
                </el-form-item>
              </el-col>
              <el-col :span="3">
                <el-form-item>
                  <el-button type="primary" @click="saveRule">保存</el-button>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>

          <el-table :data="rules" border stripe>
            <el-table-column prop="policy_version" label="政策版本" width="100" />
            <el-table-column label="类别" min-width="150">
              <template #default="{ row }">{{ labelCategory(row.category) }}</template>
            </el-table-column>
            <el-table-column prop="subcategory" label="细分内容" min-width="180" />
            <el-table-column label="级别" width="110">
              <template #default="{ row }">{{ labelLevel(row.level) }}</template>
            </el-table-column>
            <el-table-column label="等级" width="120">
              <template #default="{ row }">{{ labelRank(row.rank) }}</template>
            </el-table-column>
            <el-table-column label="金额" width="120">
              <template #default="{ row }">{{ formatMoney(row.amount) }}</template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="赛事认定库">
          <el-form :model="competitionForm" label-width="110px">
            <el-row :gutter="16">
              <el-col :span="7">
                <el-form-item label="赛事名称">
                  <el-input v-model="competitionForm.name" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="赛事类型">
                  <el-input v-model="competitionForm.competition_type" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="最高级别">
                  <el-input v-model="competitionForm.max_level" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="主办单位">
                  <el-input v-model="competitionForm.organizer" />
                </el-form-item>
              </el-col>
              <el-col :span="3">
                <el-form-item>
                  <el-button type="primary" @click="saveCompetition">保存</el-button>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>

          <el-table :data="competitions" border stripe>
            <el-table-column prop="name" label="赛事名称" />
            <el-table-column prop="competition_type" label="类型" width="120" />
            <el-table-column prop="max_level" label="最高级别" width="120" />
            <el-table-column prop="organizer" label="主办单位" />
            <el-table-column prop="policy_version" label="政策版本" width="110" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createCompetitionCatalog, createRewardRule, getCompetitionCatalog, getRewardRules, initRewardPolicy2024 } from '@/api'
import {
  categoryMap,
  levelMap,
  money,
  optionLabel,
  rankMap,
  rewardRules2024,
  ruleTitle,
  type RewardRuleOption,
} from '../../../../../frontend/src/utils/teaching-reward-policy'

const rules = ref<any[]>([])
const competitions = ref<any[]>([])
const selectedRuleKey = ref('')
const ruleForm = reactive<any>({
  policy_version: '2024',
  category: 'teaching_competition',
  subcategory: 'individual',
  level: 'provincial',
  rank: 'first_prize',
  amount: 0,
  manual_required: false,
  staged: false,
  annual_cap: 0,
  allow_duplicate: false,
})
const competitionForm = reactive<any>({
  name: '',
  competition_type: 'teacher',
  max_level: 'provincial',
  organizer: '',
  policy_version: '2024',
})

const policyRuleOptions = rewardRules2024.map((rule, index) => ({
  label: `${ruleTitle(rule)} - ${money(rule.amount)}`,
  value: String(index),
}))

function labelCategory(value?: string) {
  return optionLabel(categoryMap, value)
}

function labelLevel(value?: string) {
  return optionLabel(levelMap, value)
}

function labelRank(value?: string) {
  return optionLabel(rankMap, value)
}

function formatMoney(value: number) {
  return money(Number(value || 0))
}

function applyRule(rule: RewardRuleOption) {
  Object.assign(ruleForm, {
    policy_version: '2024',
    category: rule.category,
    subcategory: rule.subcategory,
    level: rule.level,
    rank: rule.rank,
    amount: rule.amount,
    manual_required: false,
    staged: false,
    annual_cap: 0,
    allow_duplicate: false,
  })
}

function applyRulePreset(value: string) {
  const rule = rewardRules2024[Number(value)]
  if (rule) applyRule(rule)
}

async function loadAll() {
  rules.value = await getRewardRules()
  competitions.value = await getCompetitionCatalog()
}

async function saveRule() {
  await createRewardRule(ruleForm)
  ElMessage.success('奖励规则已保存')
  loadAll()
}

async function saveCompetition() {
  await createCompetitionCatalog(competitionForm)
  ElMessage.success('赛事认定已保存')
  loadAll()
}

async function seedPolicy() {
  const result = await initRewardPolicy2024()
  ElMessage.success(`已导入规则 ${result.inserted_rules} 条、赛事 ${result.inserted_competitions} 条`)
  loadAll()
}

onMounted(loadAll)
applyRule(rewardRules2024[0])
</script>

<style scoped>
.admin-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style>
