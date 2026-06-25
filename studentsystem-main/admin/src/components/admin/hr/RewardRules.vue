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
              <el-col :span="4"><el-form-item label="政策版本"><el-input v-model="ruleForm.policy_version" /></el-form-item></el-col>
              <el-col :span="5"><el-form-item label="奖励类别"><el-input v-model="ruleForm.category" /></el-form-item></el-col>
              <el-col :span="4"><el-form-item label="级别"><el-input v-model="ruleForm.level" /></el-form-item></el-col>
              <el-col :span="4"><el-form-item label="等级"><el-input v-model="ruleForm.rank" /></el-form-item></el-col>
              <el-col :span="4"><el-form-item label="金额"><el-input-number v-model="ruleForm.amount" :min="0" /></el-form-item></el-col>
              <el-col :span="3"><el-form-item><el-button type="primary" @click="saveRule">保存</el-button></el-form-item></el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="4"><el-form-item label="人工认定"><el-switch v-model="ruleForm.manual_required" /></el-form-item></el-col>
              <el-col :span="4"><el-form-item label="阶段发放"><el-switch v-model="ruleForm.staged" /></el-form-item></el-col>
              <el-col :span="4"><el-form-item label="允许重复"><el-switch v-model="ruleForm.allow_duplicate" /></el-form-item></el-col>
              <el-col :span="5"><el-form-item label="年度封顶"><el-input-number v-model="ruleForm.annual_cap" :min="0" /></el-form-item></el-col>
            </el-row>
          </el-form>
          <el-table :data="rules" border stripe>
            <el-table-column prop="policy_version" label="政策版本" width="100" />
            <el-table-column prop="category" label="类别" />
            <el-table-column prop="level" label="级别" width="110" />
            <el-table-column prop="rank" label="等级" width="120" />
            <el-table-column prop="amount" label="金额" width="120" />
            <el-table-column prop="manual_required" label="人工认定" width="100" />
            <el-table-column prop="staged" label="阶段发放" width="100" />
            <el-table-column prop="annual_cap" label="年度封顶" width="120" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="赛事认定库">
          <el-form :model="competitionForm" label-width="110px">
            <el-row :gutter="16">
              <el-col :span="7"><el-form-item label="赛事名称"><el-input v-model="competitionForm.name" /></el-form-item></el-col>
              <el-col :span="4"><el-form-item label="赛事类型"><el-input v-model="competitionForm.competition_type" /></el-form-item></el-col>
              <el-col :span="4"><el-form-item label="最高级别"><el-input v-model="competitionForm.max_level" /></el-form-item></el-col>
              <el-col :span="6"><el-form-item label="主办单位"><el-input v-model="competitionForm.organizer" /></el-form-item></el-col>
              <el-col :span="3"><el-form-item><el-button type="primary" @click="saveCompetition">保存</el-button></el-form-item></el-col>
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

const rules = ref<any[]>([])
const competitions = ref<any[]>([])
const ruleForm = reactive<any>({
  policy_version: '2024',
  category: 'teaching_competition',
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
</script>

<style scoped>
.admin-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-actions { display: flex; gap: 10px; }
</style>
