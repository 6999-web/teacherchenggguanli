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
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAdminInfo } from '@/utils/admin-auth'
import { getAdminAuditSummary } from '@/api'

const router = useRouter()
const adminName = ref('管理员')
const loading = ref(false)

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
.audit-card {
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
