<template>
  <div class="hr-page">
    <n-card title="教学奖励申报">
      <n-alert type="info" class="section-gap">
        教学奖励申报和教师人事档案共用同一份认定数据。这里提交后，会自动同步到“教师人事管理体系”的个人档案中。
      </n-alert>

      <n-form :model="form" label-placement="left" label-width="110">
        <n-grid :cols="2" :x-gap="16" responsive="screen">
          <n-grid-item>
            <n-form-item label="奖励类别">
              <n-select v-model:value="form.category" :options="categoryOptions" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="级别">
              <n-select v-model:value="form.level" :options="levelOptions" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="等级">
              <n-select v-model:value="form.rank" :options="rankOptions" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="竞赛类型">
              <n-select v-model:value="form.competition_scope" :options="scopeOptions" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="参与方式">
              <n-select v-model:value="form.participation_type" :options="participationOptions" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="教改阶段">
              <n-select v-model:value="form.project_stage" :options="stageOptions" clearable />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="项目类型">
              <n-input v-model:value="form.project_type" placeholder="重点 / 一般 / A / B" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="教材字数">
              <n-input-number v-model:value="form.word_count" :min="0" style="width: 100%" />
            </n-form-item>
          </n-grid-item>
        </n-grid>
      </n-form>

      <n-space>
        <n-button type="primary" :loading="submitting" @click="submit">提交奖励认定</n-button>
        <n-button @click="loadExisting">读取已有数据</n-button>
      </n-space>

      <n-alert v-if="result" type="success" class="section-gap">
        已提交，拟认定金额：{{ money(result.final_amount) }}。该记录已同步到人事档案。
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
              <small>{{ requestText(item.calculation_detail?.request_data) }}</small>
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
import { onMounted, reactive, ref } from 'vue'
import { useMessage } from 'naive-ui'
import { createMyRewardRecognition, getMyRewardRecognitions } from '@/api'

const message = useMessage()
const submitting = ref(false)
const result = ref<any>(null)
const recognitions = ref<any[]>([])
const form = reactive<any>({
  category: 'teaching_competition',
  level: 'national',
  rank: 'first_prize',
  competition_scope: 'individual',
  participation_type: 'self',
  project_stage: null,
  project_type: '',
  word_count: 0,
})

const categoryMap: Record<string, string> = {
  teaching_achievement: '教学成果类',
  major_construction: '专业建设类',
  course_construction: '课程建设类',
  textbook_construction: '教材建设类',
  practice_teaching: '实践教学类',
  teaching_competition: '教学竞赛类',
  teaching_team: '教师队伍类',
  teaching_reform: '教学改革项目奖',
  teaching_quality: '教学质量奖',
  lecture_competition: '讲课比赛奖',
  ideological_political: '思政专项奖',
}
const levelMap: Record<string, string> = { national: '国家级', provincial: '省部级', municipal: '市厅级', school: '校级' }
const rankMap: Record<string, string> = { grand_prize: '特等奖', first_prize: '一等奖', second_prize: '二等奖', third_prize: '三等奖' }

const categoryOptions = Object.entries(categoryMap).map(([value, label]) => ({ label, value }))
const levelOptions = Object.entries(levelMap).map(([value, label]) => ({ label, value }))
const rankOptions = Object.entries(rankMap).map(([value, label]) => ({ label, value }))
const scopeOptions = [{ label: '单项', value: 'individual' }, { label: '团体', value: 'group' }]
const participationOptions = [{ label: '本人参赛', value: 'self' }, { label: '指导学生', value: 'guided_student' }]
const stageOptions = [{ label: '立项阶段', value: 'established' }, { label: '结题阶段', value: 'completed' }]

function money(value: number) {
  return `${Number(value || 0).toLocaleString('zh-CN')} 元`
}

function label(map: Record<string, string>, value: string) {
  return map[value] || value || '-'
}

function statusText(status: string) {
  const map: Record<string, string> = { pending: '待认定', approved: '已认定', rejected: '已驳回' }
  return map[status] || status || '-'
}

function requestText(data: any) {
  if (!data) return ''
  return [
    data.participation_type === 'guided_student' ? '指导学生' : data.participation_type === 'self' ? '本人参赛' : '',
    data.competition_scope === 'group' ? '团体' : data.competition_scope === 'individual' ? '单项' : '',
    data.project_stage === 'established' ? '立项阶段' : data.project_stage === 'completed' ? '结题阶段' : '',
    data.project_type ? `项目类型：${data.project_type}` : '',
  ].filter(Boolean).join(' · ')
}

function applyRecognitionToForm(item: any) {
  const data = item?.calculation_detail?.request_data
  if (!data) return
  Object.assign(form, {
    category: data.category || item.category || form.category,
    level: data.level || item.level || form.level,
    rank: data.rank || item.rank || form.rank,
    competition_scope: data.competition_scope || form.competition_scope,
    participation_type: data.participation_type || form.participation_type,
    project_stage: data.project_stage || null,
    project_type: data.project_type || '',
    word_count: Number(data.word_count || 0),
  })
}

async function loadExisting() {
  recognitions.value = await getMyRewardRecognitions()
  if (recognitions.value.length > 0) {
    applyRecognitionToForm(recognitions.value[0])
  }
}

async function submit() {
  submitting.value = true
  try {
    result.value = await createMyRewardRecognition(form)
    message.success('奖励认定已提交，并同步到人事档案')
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
.reward-row { display: flex; justify-content: space-between; gap: 16px; width: 100%; align-items: center; }
.reward-row span, .reward-row small { display: block; color: #64748b; margin-top: 4px; }
.reward-amount { text-align: right; min-width: 120px; }
.reward-amount strong { color: #0f766e; }
</style>
