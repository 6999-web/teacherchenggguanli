<template>
  <div class="collect-page">
    <header class="page-head">
      <n-button text @click="goBack">
        <template #icon><ArrowLeft :size="18" /></template>
        返回成果展示
      </n-button>
      <div>
        <h1>成果收集</h1>
        <p>提交教学类成果或科研类成果，统一进入管理端奖励认定审核。</p>
      </div>
    </header>

    <n-card v-if="!selectedDomain" class="choice-card" :bordered="false">
      <div class="choice-grid">
        <button class="choice-tile" type="button" @click="selectDomain('teaching')">
          <strong>教学成果类</strong>
          <span>填写名称、附件，由系统识别奖项类型和奖金，教师可手动修改。</span>
        </button>
        <button class="choice-tile" type="button" @click="selectDomain('research')">
          <strong>科研成果类</strong>
          <span>填写名称、奖项内容、奖金数额，提交后进入管理端人工认定。</span>
        </button>
      </div>
    </n-card>

    <n-card v-else class="form-card" :bordered="false">
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
        <div class="form-toolbar">
          <strong>{{ selectedDomain === 'teaching' ? '教学成果类' : '科研成果类' }}</strong>
          <n-button size="small" secondary @click="backToChoices">重新选择</n-button>
        </div>

        <template v-if="form.achievementDomain === 'teaching'">
          <n-grid :cols="2" :x-gap="18" :y-gap="12" responsive="screen">
            <n-grid-item>
              <n-form-item label="名称" path="title">
                <n-input v-model:value="form.title" placeholder="请输入教学成果名称" clearable />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="附件" path="attachments">
                <n-upload
                  v-model:file-list="fileList"
                  multiple
                  :max="5"
                  :default-upload="false"
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                >
                  <n-button>选择附件</n-button>
                </n-upload>
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="成果细分类型" path="teachingCategory">
                <n-select
                  v-model:value="form.teachingCategory"
                  :options="teachingCategoryOptions"
                  placeholder="请选择教学成果细分类型"
                  clearable
                  @update:value="handleTeachingCategoryChange"
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="奖金" path="declaredBonus">
                <n-input-number
                  v-model:value="form.declaredBonus"
                  :min="0"
                  :precision="0"
                  placeholder="AI识别后可手动修改"
                  style="width: 100%"
                  @update:value="handleBonusChange"
                >
                  <template #suffix>元</template>
                </n-input-number>
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="奖项类型" path="ruleKey">
                <n-select
                  v-model:value="form.ruleKey"
                  :options="ruleOptions"
                  placeholder="AI识别后可手动修改"
                  filterable
                  clearable
                  @update:value="handleRuleChange"
                />
              </n-form-item>
            </n-grid-item>
          </n-grid>

          <section class="policy-section">
            <div class="section-title">
              <span>AI识别结果</span>
              <n-button size="small" secondary :loading="recognizing" @click="autoRecognize(false)">
                重新识别
              </n-button>
            </div>

            <div v-if="selectedRule" class="recognition-preview">
              <div>
                <span>奖项类型</span>
                <strong>{{ rewardContentLabel(selectedRule) }}</strong>
              </div>
              <div>
                <span>政策奖金</span>
                <strong>{{ money(selectedRule.amount) }}</strong>
              </div>
              <div>
                <span>提交奖金</span>
                <strong>{{ money(form.declaredBonus || 0) }}</strong>
              </div>
            </div>

            <n-alert v-else type="warning" :bordered="false" class="section-gap">
              暂未识别到明确的教学奖励类型，请补充名称或附件后重新识别，也可以手动选择奖项类型和奖金。
            </n-alert>
          </section>
        </template>

        <template v-else>
          <n-grid :cols="2" :x-gap="18" :y-gap="12" responsive="screen">
            <n-grid-item>
              <n-form-item label="名称" path="title">
                <n-input v-model:value="form.title" placeholder="请输入科研成果名称" clearable />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="科研成果类型" path="researchType">
                <n-select
                  v-model:value="form.researchType"
                  :options="researchTypeOptions"
                  placeholder="请选择科研成果类型"
                  clearable
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="奖项内容" path="award">
                <n-input v-model:value="form.award" placeholder="请输入奖项内容" clearable />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="奖金数额" path="declaredBonus">
                <n-input-number
                  v-model:value="form.declaredBonus"
                  :min="0"
                  :precision="0"
                  placeholder="请输入奖金数额"
                  style="width: 100%"
                >
                  <template #suffix>元</template>
                </n-input-number>
              </n-form-item>
            </n-grid-item>
          </n-grid>
        </template>

        <div class="actions">
          <n-button @click="resetForm">重置</n-button>
          <n-button type="primary" :loading="submitting" @click="submit">提交审核</n-button>
        </div>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import type { FormInst, FormRules, UploadFileInfo } from 'naive-ui'
import { IconArrowLeft as ArrowLeft } from '@tabler/icons-vue'
import { recognizeTeachingReward, submitAchievement, uploadFile } from '@/api'
import {
  money,
  rewardContentLabel,
  rewardRuleKey,
  rewardRules2024,
  categoryMap,
  type RewardRuleOption,
} from '@/utils/teaching-reward-policy'

type AchievementDomain = 'teaching' | 'research'

const router = useRouter()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const submitting = ref(false)
const recognizing = ref(false)
const manualOverride = ref(false)
const lastAiMatched = ref(false)
const fileList = ref<UploadFileInfo[]>([])
const selectedDomain = ref<AchievementDomain | null>(null)
let recognitionTimer: ReturnType<typeof setTimeout> | null = null

const form = reactive({
  achievementDomain: 'teaching' as AchievementDomain,
  title: '',
  award: '',
  teachingCategory: null as string | null,
  researchType: null as string | null,
  declaredBonus: null as number | null,
  ruleKey: null as string | null,
})

const rules: FormRules = {
  achievementDomain: { required: true, message: '请选择成果类型', trigger: ['change'] },
  title: {
    validator() {
      if (!form.title.trim()) {
        return new Error(form.achievementDomain === 'teaching' ? '请输入教学成果名称' : '请输入科研成果名称')
      }
      return true
    },
    trigger: ['input', 'blur'],
  },
  award: {
    validator() {
      if (form.achievementDomain === 'research' && !form.award.trim()) {
        return new Error('请输入奖项内容')
      }
      return true
    },
    trigger: ['input', 'blur'],
  },
  teachingCategory: {
    validator() {
      if (form.achievementDomain === 'teaching' && !form.teachingCategory) {
        return new Error('请选择教学成果细分类型')
      }
      return true
    },
    trigger: ['change'],
  },
  researchType: {
    validator() {
      if (form.achievementDomain === 'research' && !form.researchType) {
        return new Error('请选择科研成果类型')
      }
      return true
    },
    trigger: ['change'],
  },
  declaredBonus: {
    required: true,
    type: 'number',
    message: '请输入奖金金额',
    trigger: ['input', 'blur', 'change'],
  },
  ruleKey: {
    validator() {
      if (form.achievementDomain === 'teaching' && !form.ruleKey) {
        return new Error('请选择奖项类型')
      }
      return true
    },
    trigger: ['change'],
  },
}

const teachingCategoryOptions = computed(() => {
  const categories = [...new Set(rewardRules2024.map(rule => rule.category))]
  return categories.map(value => ({ label: categoryMap[value] || value, value }))
})

const researchTypeOptions = [
  { label: '科研论文', value: 'paper' },
  { label: '科研项目', value: 'project' },
  { label: '专利成果', value: 'patent' },
  { label: '著作出版', value: 'book' },
  { label: '科研获奖', value: 'award' },
  { label: '咨政成果', value: 'consulting_report' },
  { label: '其他科研成果', value: 'other' },
]

const ruleOptions = computed(() =>
  rewardRules2024.filter(rule => !form.teachingCategory || rule.category === form.teachingCategory).map(rule => ({
    label: `${rewardContentLabel(rule)} - ${money(rule.amount)}`,
    value: rewardRuleKey(rule),
  })),
)

const selectedRule = computed(() => {
  if (!form.ruleKey) return null
  return rewardRules2024.find(rule => rewardRuleKey(rule) === form.ruleKey) || null
})

const attachmentNames = computed(() => fileList.value.map(item => item.name).filter(Boolean))

watch(
  () => [form.title, attachmentNames.value.join('|'), form.achievementDomain],
  () => {
    if (form.achievementDomain === 'teaching' && !manualOverride.value) scheduleRecognize()
  },
)

function selectDomain(domain: AchievementDomain) {
  form.achievementDomain = domain
  selectedDomain.value = domain
  resetFormFields()
  if (domain === 'teaching') scheduleRecognize()
}

function backToChoices() {
  selectedDomain.value = null
  resetFormFields()
}

function resetFormFields() {
  if (recognitionTimer) clearTimeout(recognitionTimer)
  manualOverride.value = false
  lastAiMatched.value = false
  form.title = ''
  form.award = ''
  form.teachingCategory = null
  form.researchType = null
  form.declaredBonus = null
  form.ruleKey = null
  fileList.value = []
  formRef.value?.restoreValidation()
}

function handleTeachingCategoryChange() {
  if (selectedRule.value && selectedRule.value.category !== form.teachingCategory) {
    form.ruleKey = null
    form.declaredBonus = null
  }
}

function handleRuleChange() {
  manualOverride.value = true
  if (selectedRule.value) {
    form.teachingCategory = selectedRule.value.category
    form.declaredBonus = selectedRule.value.amount
  }
}

function handleBonusChange() {
  manualOverride.value = true
}

function scheduleRecognize() {
  if (recognitionTimer) clearTimeout(recognitionTimer)
  recognitionTimer = setTimeout(() => autoRecognize(true), 450)
}

async function autoRecognize(silent = false) {
  const hasInput = form.title.trim() || attachmentNames.value.length > 0
  if (!hasInput) return

  recognizing.value = true
  try {
    const response = await recognizeTeachingReward({
      title: form.title.trim(),
      attachment_names: attachmentNames.value,
    })
    const data = response?.data || response
    if (data?.matched && data.rule_key) {
      const matchedRule = rewardRules2024.find(rule => rewardRuleKey(rule) === data.rule_key)
      if (matchedRule) {
        form.teachingCategory = matchedRule.category
        form.ruleKey = rewardRuleKey(matchedRule)
        form.declaredBonus = Number(data.amount || matchedRule.amount || 0)
        manualOverride.value = false
        lastAiMatched.value = true
      }
    } else {
      lastAiMatched.value = false
      if (!silent) message.warning('暂未识别到明确的教学奖励类型')
    }
  } catch (error) {
    lastAiMatched.value = false
    if (!silent) message.error('AI识别失败，请稍后重试或手动填写')
  } finally {
    recognizing.value = false
  }
}

function payloadFromRule(rule: RewardRuleOption) {
  const payload: Record<string, any> = {
    category: rule.category,
    subcategory: rule.subcategory,
    level: rule.level,
    rank: rule.rank,
    rule_key: rewardRuleKey(rule),
    ai_suggested: lastAiMatched.value && !manualOverride.value,
    policy_content: rewardContentLabel(rule),
    policy_amount: rule.amount,
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

async function uploadAttachments() {
  const urls: string[] = []
  for (const item of fileList.value) {
    const rawFile = item.file as File | undefined
    if (!rawFile) continue
    const result = await uploadFile(rawFile)
    if (result?.url) urls.push(result.url)
  }
  return urls
}

async function submit() {
  await formRef.value?.validate()

  if (form.achievementDomain === 'teaching' && !selectedRule.value) {
    message.warning('请确认教学类成果的奖项类型和奖金')
    return
  }

  submitting.value = true
  try {
    const attachmentUrls = await uploadAttachments()
    const isTeaching = form.achievementDomain === 'teaching'
    const title = form.title.trim()
    const awardText = isTeaching && selectedRule.value ? rewardContentLabel(selectedRule.value) : form.award.trim()
    const contentJson: Record<string, any> = {
      achievement_domain: form.achievementDomain,
      achievement_type: isTeaching ? form.teachingCategory : form.researchType,
      achievement_type_text: isTeaching
        ? (form.teachingCategory ? categoryMap[form.teachingCategory] || form.teachingCategory : '')
        : (researchTypeOptions.find(item => item.value === form.researchType)?.label || ''),
      award: awardText,
      declared_bonus: Number(form.declaredBonus || 0),
      attachment_urls: attachmentUrls,
      attachment_names: attachmentNames.value,
      reward_policy_source: isTeaching
        ? '广西警察学院教学工作奖励办法（2024年修订）'
        : '科研类成果由管理员人工认定',
    }

    if (isTeaching && selectedRule.value) {
      Object.assign(contentJson, payloadFromRule(selectedRule.value))
    }

    await submitAchievement({
      title,
      type: form.achievementDomain as any,
      content_json: contentJson,
      evidence_url: attachmentUrls[0] || '',
    })

    message.success('成果已提交，等待管理端奖励认定审核')
    router.push('/student/achievement')
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  resetFormFields()
}

function goBack() {
  if (selectedDomain.value) {
    backToChoices()
    return
  }
  router.push('/student/achievement')
}
</script>

<style scoped>
.collect-page {
  min-height: 100%;
  padding: 24px;
  background: #f6f8fb;
}

.page-head {
  max-width: 1080px;
  margin: 0 auto 16px;
  display: grid;
  gap: 12px;
}

.page-head h1 {
  margin: 0;
  color: #0f172a;
  font-size: 26px;
}

.page-head p {
  margin: 6px 0 0;
  color: #64748b;
}

.choice-card,
.form-card {
  max-width: 1080px;
  margin: 0 auto;
  border-radius: 8px;
}

.choice-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.choice-tile {
  min-height: 180px;
  border: 1px solid #dbe4ee;
  border-radius: 8px;
  background: #ffffff;
  color: #0f172a;
  text-align: left;
  padding: 24px;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.choice-tile:hover {
  border-color: #2563eb;
  box-shadow: 0 12px 28px rgba(37, 99, 235, 0.12);
  transform: translateY(-2px);
}

.choice-tile strong {
  display: block;
  font-size: 22px;
  margin-bottom: 12px;
}

.choice-tile span {
  display: block;
  color: #64748b;
  line-height: 1.7;
}

.form-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
  color: #0f172a;
  font-size: 18px;
}

.policy-section {
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  color: #0f172a;
  font-weight: 700;
}

.recognition-preview {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 12px;
  margin-top: 8px;
}

.recognition-preview > div {
  border: 1px solid #dbe4ee;
  border-radius: 8px;
  padding: 12px;
  background: #f8fafc;
}

.recognition-preview span {
  display: block;
  color: #64748b;
  font-size: 13px;
  margin-bottom: 6px;
}

.recognition-preview strong {
  color: #0f172a;
}

.section-gap {
  margin-top: 12px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 22px;
}

@media (max-width: 720px) {
  .collect-page {
    padding: 16px;
  }

  .recognition-preview {
    grid-template-columns: 1fr;
  }

  .choice-grid {
    grid-template-columns: 1fr;
  }

  .actions {
    justify-content: stretch;
  }

  .actions :deep(.n-button) {
    flex: 1;
  }
}
</style>
