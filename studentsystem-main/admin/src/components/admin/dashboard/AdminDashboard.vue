<template>
  <div class="admin-dashboard">
    <el-card class="welcome-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>欢迎，{{ adminName }}</span>
          <el-button type="primary" :loading="loading" @click="loadStats">刷新</el-button>
        </div>
      </template>
      <div class="welcome-content">
        <p>您已成功登录教师成果管理平台管理端。</p>
        <p>这里统一统计教师端提交到管理端的档案变更和奖励认定审核。</p>
      </div>
    </el-card>

    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card pending">
          <el-statistic title="总待审核" :value="summary.total.pending">
            <template #suffix><span class="stat-unit">项</span></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card approved">
          <el-statistic title="总已通过" :value="summary.total.approved">
            <template #suffix><span class="stat-unit">项</span></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card rejected">
          <el-statistic title="总已驳回" :value="summary.total.rejected">
            <template #suffix><span class="stat-unit">项</span></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card submitted">
          <el-statistic title="累计提交" :value="summary.total.submitted">
            <template #suffix><span class="stat-unit">项</span></template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="detail-actions-card" shadow="never">
      <div class="detail-actions">
        <el-button type="warning" plain @click="openDetail('pending')">查看总待审核详情</el-button>
        <el-button type="success" plain @click="openDetail('approved')">查看总已通过详情</el-button>
        <el-button type="danger" plain @click="openDetail('rejected')">查看总已驳回详情</el-button>
        <el-button type="primary" plain @click="openDetail('submitted')">查看累计提交详情</el-button>
      </div>
    </el-card>

    <el-card class="audit-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>审核分类统计</span>
        </div>
      </template>

      <el-table :data="summary.modules" border stripe v-loading="loading">
        <el-table-column prop="title" label="审核类型" min-width="180" />
        <el-table-column prop="pending" label="待审核" width="110" />
        <el-table-column prop="approved" label="已通过" width="110" />
        <el-table-column prop="rejected" label="已驳回" width="110" />
        <el-table-column prop="submitted" label="累计提交" width="120" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="goTo(row.route)">去处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-drawer v-model="detailVisible" :title="detailTitle" size="72%">
      <el-alert
        :title="`${detailTitle}：${detailTotal} 项`"
        type="info"
        :closable="false"
        show-icon
        class="detail-summary"
      />
      <el-table :data="detailRows" border stripe v-loading="detailLoading" empty-text="暂无相关明细">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="detail-expand">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="审核类型">{{ row.module_title }}</el-descriptions-item>
                <el-descriptions-item label="状态">{{ statusText(row.status) }}</el-descriptions-item>
                <el-descriptions-item label="教师姓名">{{ row.teacher_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="工号">{{ row.employee_no || '-' }}</el-descriptions-item>
                <el-descriptions-item label="院系">{{ row.department || '-' }}</el-descriptions-item>
                <el-descriptions-item label="金额">{{ row.amount === null || row.amount === undefined ? '-' : money(row.amount) }}</el-descriptions-item>
                <el-descriptions-item label="提交时间">{{ formatTime(row.created_at) }}</el-descriptions-item>
                <el-descriptions-item label="审核时间">{{ formatTime(row.audited_at) }}</el-descriptions-item>
                <el-descriptions-item label="审核意见" :span="2">{{ row.audit_comment || '-' }}</el-descriptions-item>
              </el-descriptions>
              <div class="json-detail">
                <strong>原始详情</strong>
                <pre>{{ formatJson(row.detail) }}</pre>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="module_title" label="审核类型" min-width="150" />
        <el-table-column prop="teacher_name" label="教师" width="110" />
        <el-table-column prop="employee_no" label="工号" width="110" />
        <el-table-column prop="department" label="院系" min-width="140" />
        <el-table-column prop="title" label="事项名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="summary" label="内容摘要" min-width="180" show-overflow-tooltip />
        <el-table-column label="金额" width="110">
          <template #default="{ row }">{{ row.amount === null || row.amount === undefined ? '-' : money(row.amount) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">{{ statusText(row.status) }}</template>
        </el-table-column>
        <el-table-column label="提交时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="goTo(row.route)">去处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAdminInfo } from '@/utils/admin-auth'
import { getAdminAuditDetails, getAdminAuditSummary } from '@/api'

const router = useRouter()
const adminName = ref('管理员')
const loading = ref(false)
type AuditStatusKey = 'pending' | 'approved' | 'rejected' | 'submitted'
const detailVisible = ref(false)
const detailLoading = ref(false)
const detailTotal = ref(0)
const activeDetail = ref<AuditStatusKey | null>(null)
const detailRows = ref<any[]>([])

const summary = reactive({
  total: {
    submitted: 0,
    pending: 0,
    approved: 0,
    rejected: 0,
  },
  modules: [] as Array<{
    key: string
    title: string
    pending: number
    approved: number
    rejected: number
    submitted: number
    route: string
  }>,
})

const detailLabels: Record<AuditStatusKey, string> = {
  pending: '总待审核详情',
  approved: '总已通过详情',
  rejected: '总已驳回详情',
  submitted: '累计提交详情',
}

const detailTitle = computed(() => (activeDetail.value ? detailLabels[activeDetail.value] : '审核详情'))

async function loadStats() {
  loading.value = true
  try {
    const data = await getAdminAuditSummary()
    Object.assign(summary.total, data.total || {})
    summary.modules = data.modules || []
  } catch (error) {
    console.error('加载审核统计失败:', error)
    ElMessage.error('加载审核统计失败')
  } finally {
    loading.value = false
  }
}

function goTo(route: string) {
  router.push(route)
}

async function openDetail(status: AuditStatusKey) {
  activeDetail.value = status
  detailVisible.value = true
  detailLoading.value = true
  try {
    const data = await getAdminAuditDetails(status)
    detailRows.value = data.list || []
    detailTotal.value = data.total || detailRows.value.length
  } catch (error) {
    console.error('加载审核明细失败:', error)
    ElMessage.error('加载审核明细失败')
    detailRows.value = []
    detailTotal.value = 0
  } finally {
    detailLoading.value = false
  }
}

function statusText(status: string) {
  return ({ pending: '待审核', approved: '已通过', rejected: '已驳回' } as Record<string, string>)[status] || status || '-'
}

function money(value: number) {
  return `${Number(value || 0).toLocaleString('zh-CN')} 元`
}

function formatTime(value?: string | null) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

function formatJson(value: any) {
  return JSON.stringify(value || {}, null, 2)
}

onMounted(() => {
  const adminInfo = getAdminInfo()
  if (adminInfo) {
    adminName.value = adminInfo.name || '管理员'
  }
  loadStats()
})
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
}

.welcome-card,
.audit-card,
.detail-actions-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
}

.welcome-content {
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
}

.stats-row {
  margin-bottom: 20px;
}

.detail-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.detail-summary {
  margin-bottom: 16px;
}

.detail-expand {
  padding: 8px 20px 16px;
  background: #f8fafc;
}

.json-detail {
  margin-top: 14px;
}

.json-detail strong {
  display: block;
  margin-bottom: 8px;
  color: #303133;
}

.json-detail pre {
  margin: 0;
  padding: 12px;
  overflow: auto;
  max-height: 260px;
  border-radius: 6px;
  background: #111827;
  color: #e5e7eb;
  font-size: 12px;
  line-height: 1.6;
}

.stat-card {
  text-align: center;
  border-top: 3px solid #d1d5db;
}

.stat-card.pending {
  border-top-color: #f59e0b;
}

.stat-card.approved {
  border-top-color: #10b981;
}

.stat-card.rejected {
  border-top-color: #ef4444;
}

.stat-card.submitted {
  border-top-color: #3b82f6;
}

.stat-unit {
  font-size: 14px;
  color: #909399;
}
</style>
