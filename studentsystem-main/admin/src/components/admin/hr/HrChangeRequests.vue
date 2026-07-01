<template>
  <div class="admin-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>档案变更审核</span>
          <el-button type="primary" @click="loadRows">刷新</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="filters">
        <el-form-item label="审核状态">
          <el-select v-model="filters.status" clearable style="width: 140px" @change="loadRows">
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadRows">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="rows" border stripe v-loading="loading">
        <el-table-column prop="employee_no" label="工号" width="120" />
        <el-table-column prop="teacher_name" label="姓名" width="120" />
        <el-table-column prop="department" label="院系" min-width="140" />
        <el-table-column label="变更内容" min-width="260">
          <template #default="{ row }">
            <el-tag
              v-for="field in changedFields(row)"
              :key="field"
              class="field-tag"
              type="info"
            >
              {{ fieldLabel(field) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">{{ statusText(row.status) }}</template>
        </el-table-column>
        <el-table-column label="提交时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDetail(row)">详情</el-button>
            <el-button
              size="small"
              type="success"
              :disabled="row.status !== 'pending'"
              @click="audit(row, 'approve')"
            >
              通过
            </el-button>
            <el-button
              size="small"
              type="danger"
              :disabled="row.status !== 'pending'"
              @click="audit(row, 'reject')"
            >
              驳回
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-drawer v-model="detailVisible" title="档案变更详情" size="560px">
      <template v-if="current">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="教师">
            {{ current.employee_no || '-' }} / {{ current.teacher_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">{{ statusText(current.status) }}</el-descriptions-item>
          <el-descriptions-item label="审核意见">{{ current.audit_comment || '-' }}</el-descriptions-item>
        </el-descriptions>

        <el-table :data="detailRows" border class="detail-table">
          <el-table-column prop="label" label="字段" width="120" />
          <el-table-column prop="before" label="原值" />
          <el-table-column prop="after" label="申请值" />
        </el-table>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { auditHrChangeRequest, getHrChangeRequests } from '@/api'

const rows = ref<any[]>([])
const loading = ref(false)
const detailVisible = ref(false)
const current = ref<any>(null)
const filters = reactive<any>({ status: 'pending' })

const fieldLabels: Record<string, string> = {
  education: '学历',
  degree: '学位',
  position: '岗位',
  current_title: '职称',
  employment_type: '身份类型',
  phone: '电话',
  email: '邮箱',
  office_location: '办公室',
  bio: '个人简介',
  department: '院系',
}

const detailRows = computed(() => {
  if (!current.value) return []
  return changedFields(current.value).map((field) => ({
    label: fieldLabel(field),
    before: valueText(current.value.before_data?.[field]),
    after: valueText(current.value.after_data?.[field]),
  }))
})

function buildQuery() {
  const query: Record<string, any> = {}
  if (filters.status) query.status = filters.status
  return query
}

async function loadRows() {
  loading.value = true
  try {
    rows.value = await getHrChangeRequests(buildQuery())
  } finally {
    loading.value = false
  }
}

function changedFields(row: any) {
  const after = row.after_data || {}
  return Object.keys(after).filter((field) => field in fieldLabels)
}

function fieldLabel(field: string) {
  return fieldLabels[field] || field
}

function valueText(value: any) {
  if (value === null || value === undefined || value === '') return '-'
  return String(value)
}

function statusText(status: string) {
  return ({ pending: '待审核', approved: '已通过', rejected: '已驳回' } as Record<string, string>)[status] || status || '-'
}

function formatTime(value: string) {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}

function openDetail(row: any) {
  current.value = row
  detailVisible.value = true
}

async function audit(row: any, action: 'approve' | 'reject') {
  const verb = action === 'approve' ? '通过' : '驳回'
  const { value } = await ElMessageBox.prompt(`请输入${verb}意见`, '档案变更审核', {
    confirmButtonText: verb,
    cancelButtonText: '取消',
    inputPlaceholder: '可选',
  })
  await auditHrChangeRequest(row.id, { action, comment: value || '' })
  ElMessage.success(`已${verb}`)
  await loadRows()
}

onMounted(loadRows)
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

.field-tag {
  margin: 2px 6px 2px 0;
}

.detail-table {
  margin-top: 18px;
}
</style>
