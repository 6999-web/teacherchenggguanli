<template>
  <div class="admin-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>绩效记录管理</span>
          <el-button type="primary" @click="refreshAll">刷新</el-button>
        </div>
      </template>

      <el-alert
        v-if="!teacherOptions.length"
        title="暂无可选择的教师档案，请先进入“教师档案”页面刷新或确认教师账号已经生成档案。"
        type="warning"
        :closable="false"
        show-icon
        class="page-alert"
      />

      <el-form :inline="true" :model="filters">
        <el-form-item label="教师档案">
          <el-select
            v-model="filters.profile_id"
            clearable
            filterable
            placeholder="全部教师"
            style="width: 260px"
          >
            <el-option
              v-for="teacher in teacherOptions"
              :key="teacher.id"
              :label="teacher.label"
              :value="teacher.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="年度">
          <el-input-number v-model="filters.year" :min="2020" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable style="width: 140px">
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadRows">查询</el-button>
        </el-form-item>
      </el-form>

      <el-form :model="form" label-width="110px" class="form">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="教师档案" required>
              <el-select
                v-model="form.profile_id"
                filterable
                placeholder="请选择教师档案"
                style="width: 100%"
                :disabled="Boolean(form.id)"
              >
                <el-option
                  v-for="teacher in teacherOptions"
                  :key="teacher.id"
                  :label="teacher.label"
                  :value="teacher.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="年度">
              <el-input-number v-model="form.year" :min="2020" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="周期">
              <el-select v-model="form.period_type">
                <el-option label="年度" value="annual" />
                <el-option label="聘期" value="appointment" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="等级">
              <el-select v-model="form.grade">
                <el-option label="优秀" value="优秀" />
                <el-option label="良好" value="良好" />
                <el-option label="合格" value="合格" />
                <el-option label="不合格" value="不合格" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="教学成果分">
              <el-input-number v-model="form.teaching_score" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="评价考核分">
              <el-input-number v-model="form.evaluation_score" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="奖励加分">
              <el-input-number v-model="form.reward_bonus" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="管理员调整">
              <el-input-number v-model="form.admin_adjustment" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="最终得分">
              <el-input-number v-model="form.final_score" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="状态">
              <el-select v-model="form.status">
                <el-option label="草稿" value="draft" />
                <el-option label="已发布" value="published" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="备注">
              <el-input v-model="form.note" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-button type="primary" @click="submit">
          {{ form.id ? '更新绩效记录' : '保存绩效记录' }}
        </el-button>
        <el-button @click="resetForm">清空</el-button>
      </el-form>

      <el-table :data="rows" border stripe v-loading="loading" style="margin-top: 18px" empty-text="暂无绩效记录">
        <el-table-column prop="employee_no" label="工号" width="110" />
        <el-table-column prop="teacher_name" label="姓名" width="120" />
        <el-table-column prop="department" label="院系" min-width="140" />
        <el-table-column prop="year" label="年度" width="90" />
        <el-table-column label="周期" width="90">
          <template #default="{ row }">{{ periodText(row.period_type) }}</template>
        </el-table-column>
        <el-table-column prop="teaching_score" label="教学成果分" width="110" />
        <el-table-column prop="evaluation_score" label="评价考核分" width="110" />
        <el-table-column prop="reward_bonus" label="奖励加分" width="100" />
        <el-table-column prop="admin_adjustment" label="管理员调整" width="110" />
        <el-table-column prop="final_score" label="最终得分" width="100" />
        <el-table-column prop="grade" label="等级" width="90" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">{{ statusText(row.status) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="90">
          <template #default="{ row }">
            <el-button size="small" @click="edit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createHrPerformance, getHrPerformanceRecords, getHrTeachers, updateHrPerformance } from '@/api'

const rows = ref<any[]>([])
const teachers = ref<any[]>([])
const loading = ref(false)
const filters = reactive<any>({})
const form = reactive<any>(defaultForm())

const teacherOptions = computed(() =>
  teachers.value.map((teacher) => ({
    id: teacher.id,
    label: [teacher.employee_no, teacher.name, teacher.department].filter(Boolean).join(' - '),
  })),
)

function defaultForm() {
  return {
    id: null,
    profile_id: null,
    year: new Date().getFullYear(),
    period_type: 'annual',
    grade: '合格',
    teaching_score: 0,
    evaluation_score: 0,
    reward_bonus: 0,
    admin_adjustment: 0,
    final_score: 0,
    status: 'published',
    note: '',
  }
}

function buildQuery() {
  const query: Record<string, any> = {}
  if (filters.profile_id) query.profile_id = filters.profile_id
  if (filters.year) query.year = filters.year
  if (filters.status) query.status = filters.status
  return query
}

async function loadTeachers() {
  const data = await getHrTeachers({ page_size: 100 })
  teachers.value = data.list || []
}

async function loadRows() {
  loading.value = true
  try {
    const data = await getHrPerformanceRecords(buildQuery())
    rows.value = data.list || []
  } finally {
    loading.value = false
  }
}

async function refreshAll() {
  await loadTeachers()
  await loadRows()
}

function resetForm() {
  Object.assign(form, defaultForm())
}

function edit(row: any) {
  Object.assign(form, row)
}

function statusText(status: string) {
  return ({ draft: '草稿', published: '已发布' } as Record<string, string>)[status] || status || '-'
}

function periodText(value: string) {
  return ({ annual: '年度', appointment: '聘期' } as Record<string, string>)[value] || value || '-'
}

async function submit() {
  if (!form.profile_id) {
    ElMessage.warning('请选择教师档案')
    return
  }

  if (form.id) {
    await updateHrPerformance(form.id, form)
    ElMessage.success('绩效记录已更新')
  } else {
    await createHrPerformance(form)
    ElMessage.success('绩效记录已保存')
  }
  resetForm()
  await loadRows()
}

onMounted(refreshAll)
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

.page-alert {
  margin-bottom: 16px;
}

.form {
  max-width: 1180px;
  margin-top: 8px;
}
</style>
