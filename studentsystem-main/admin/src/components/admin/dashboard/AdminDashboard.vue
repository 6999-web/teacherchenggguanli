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
              <div class="detail-content">
                <strong>具体内容</strong>
                <el-descriptions :column="1" border>
                  <el-descriptions-item
                    v-for="item in detailItems(row)"
                    :key="item.label"
                    :label="item.label"
                  >
                    {{ item.value }}
                  </el-descriptions-item>
                </el-descriptions>
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

const fieldLabels: Record<string, string> = {
  profile_id: '档案编号',
  achievement_id: '成果编号',
  before_data: '变更前信息',
  after_data: '变更后信息',
  request_data: '申报信息',
  calculation_detail: '计算明细',
  education: '学历',
  degree: '学位',
  position: '岗位',
  current_title: '当前职称',
  title_start_date: '职称起始时间',
  employment_type: '身份',
  hire_date: '入职时间',
  contract_start: '合同开始时间',
  contract_end: '合同结束时间',
  phone: '电话',
  email: '邮箱',
  office_location: '办公地点',
  bio: '个人简介',
  achievement_title: '成果名称',
  achievement_domain: '成果类别',
  achievement_type: '成果细分类型',
  achievement_type_text: '成果细分类型',
  award: '奖项内容',
  declared_bonus: '申报奖金',
  reward_policy_source: '政策来源',
  category: '奖励类别',
  subcategory: '细分类别',
  level: '认定级别',
  rank: '奖项等级',
  base_amount: '基础金额',
  final_amount: '最终金额',
  policy_basis: '政策依据',
  attachment_urls: '附件地址',
  attachment_names: '附件名称',
  evidence_url: '主要附件',
  rule_key: '规则编号',
  ai_suggested: 'AI识别',
  policy_content: '政策内容',
  policy_amount: '政策金额',
}

const valueLabels: Record<string, string> = {
  teaching: '教学类成果',
  research: '科研类成果',
  teaching_achievement: '教学成果奖',
  major_construction: '专业建设类',
  course_construction: '课程建设类',
  textbook_construction: '教材建设类',
  practice_teaching: '实践教学建设类',
  teaching_competition: '教学竞赛类',
  teacher_team: '教师队伍建设类',
  teaching_reform: '教学改革项目奖',
  teaching_quality: '教学质量奖',
  lecture_competition: '讲课比赛奖',
  sanquan_education: '三全育人专项奖',
  teaching_management: '教学管理奖',
  national: '国家级',
  provincial: '省（部）级',
  municipal: '市（厅）级',
  school: '校级',
  grand_prize: '特等奖',
  first_prize: '一等奖',
  second_prize: '二等奖',
  third_prize: '三等奖',
  pending: '待审核',
  approved: '已通过',
  rejected: '已驳回',
  true: '是',
  false: '否',
}

function detailItems(row: any) {
  if (row.module_key === 'profile_changes') {
    return [
      { label: '变更前信息', value: readableObject(row.detail?.before_data) },
      { label: '变更后信息', value: readableObject(row.detail?.after_data) },
    ]
  }

  const requestData = row.detail?.request_data || {}
  const content = row.content || {}
  return [
    { label: '成果编号', value: readableValue(row.detail?.achievement_id) },
    { label: '档案编号', value: readableValue(row.detail?.profile_id) },
    { label: '成果名称', value: readableValue(requestData.achievement_title || row.title) },
    { label: '成果类别', value: readableValue(requestData.achievement_domain) },
    { label: '成果细分类型', value: readableValue(requestData.achievement_type_text || requestData.achievement_type) },
    { label: '申报奖项内容', value: readableValue(requestData.award || row.summary) },
    { label: '申报奖金', value: requestData.declared_bonus === undefined ? '-' : money(Number(requestData.declared_bonus || 0)) },
    { label: '认定类别', value: readableValue(content.category) },
    { label: '认定级别', value: readableValue(content.level) },
    { label: '认定等级', value: readableValue(content.rank) },
    { label: '基础金额', value: money(Number(content.base_amount || 0)) },
    { label: '最终金额', value: money(Number(content.final_amount || row.amount || 0)) },
    { label: '政策依据', value: readableValue(content.policy_basis || requestData.reward_policy_source) },
    { label: '附件名称', value: readableValue(requestData.attachment_names) },
    { label: '附件地址', value: readableValue(requestData.attachment_urls || requestData.evidence_url) },
  ].filter(item => item.value !== '-')
}

function readableObject(value: Record<string, any> | null | undefined) {
  if (!value || Object.keys(value).length === 0) return '-'
  return Object.entries(value)
    .map(([key, item]) => `${fieldLabels[key] || key}：${readableValue(item)}`)
    .join('；')
}

function readableValue(value: any): string {
  if (value === null || value === undefined || value === '') return '-'
  if (Array.isArray(value)) return value.length ? value.map(item => readableValue(item)).join('、') : '-'
  if (typeof value === 'boolean') return value ? '是' : '否'
  if (typeof value === 'number') return String(value)
  if (typeof value === 'object') return readableObject(value)
  const text = String(value)
  return valueLabels[text] || text
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

.detail-content {
  margin-top: 14px;
}

.detail-content strong {
  display: block;
  margin-bottom: 8px;
  color: #303133;
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
