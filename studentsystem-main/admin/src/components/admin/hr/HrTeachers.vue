<template>
  <div class="admin-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>教师档案管理</span>
          <div class="header-actions">
            <el-button :loading="exporting" @click="exportRows">批量导出档案数据</el-button>
            <el-button type="primary" @click="loadRows">刷新</el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="filters">
        <el-form-item label="院系"><el-input v-model="filters.department" clearable /></el-form-item>
        <el-form-item label="身份"><el-input v-model="filters.employment_type" clearable /></el-form-item>
        <el-form-item label="职称"><el-input v-model="filters.title" clearable /></el-form-item>
        <el-form-item><el-button type="primary" @click="loadRows">查询</el-button></el-form-item>
      </el-form>

      <el-table :data="rows" border stripe v-loading="loading">
        <el-table-column prop="employee_no" label="工号" width="110" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="department" label="院系" />
        <el-table-column prop="employment_type" label="身份" width="100" />
        <el-table-column prop="current_title" label="当前职称" width="120" />
        <el-table-column prop="position" label="岗位" width="120" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="openDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-drawer v-model="detailVisible" title="教师档案详情" size="56%">
      <template v-if="detail.profile">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="姓名">{{ detail.profile.name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="工号">{{ detail.profile.employee_no || '-' }}</el-descriptions-item>
          <el-descriptions-item label="院系">{{ detail.profile.department || '-' }}</el-descriptions-item>
          <el-descriptions-item label="学历/学位">
            {{ detail.profile.education || '-' }} / {{ detail.profile.degree || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="岗位/职称">
            {{ detail.profile.position || '-' }} / {{ detail.profile.current_title || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="联系方式">
            {{ detail.profile.phone || '-' }} {{ detail.profile.email || '' }}
          </el-descriptions-item>
        </el-descriptions>

        <h3>人事附件</h3>
        <el-table :data="detail.attachments || []" border empty-text="暂无人事附件">
          <el-table-column prop="attachment_type" label="类型" />
          <el-table-column prop="title" label="名称" />
          <el-table-column prop="original_filename" label="文件" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">{{ attachmentStatus(row.status) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button size="small" :disabled="!row.file_url" @click="openFile(row)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>

        <h3>绩效记录</h3>
        <el-table :data="detail.performances || []" border empty-text="暂无绩效记录">
          <el-table-column prop="year" label="年度" />
          <el-table-column label="周期">
            <template #default="{ row }">{{ periodText(row.period_type) }}</template>
          </el-table-column>
          <el-table-column prop="teaching_score" label="教学成果分" />
          <el-table-column prop="evaluation_score" label="评价考核分" />
          <el-table-column prop="reward_bonus" label="奖励加分" />
          <el-table-column prop="final_score" label="最终得分" />
          <el-table-column prop="grade" label="等级" />
          <el-table-column label="状态">
            <template #default="{ row }">{{ performanceStatus(row.status) }}</template>
          </el-table-column>
        </el-table>

        <h3>职称缺口</h3>
        <el-alert
          v-if="detail.title_gap?.eligible"
          :title="`当前条件满足 ${detail.title_gap.target_title} 申报要求`"
          type="success"
          :closable="false"
          show-icon
        />
        <el-table v-else :data="missingTitleItems" border empty-text="暂无职称规则或缺口">
          <el-table-column prop="name" label="待完善事项" />
        </el-table>

        <h3>职业事件</h3>
        <el-table :data="detail.career_events || []" border empty-text="暂无职业事件">
          <el-table-column prop="event_type" label="事件类型" />
          <el-table-column prop="event_date" label="日期" />
          <el-table-column prop="from_value" label="变更前" />
          <el-table-column prop="to_value" label="变更后" />
        </el-table>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { exportHrTeachers, getFileUrl, getHrTeacherDetail, getHrTeachers } from '@/api'

const rows = ref<any[]>([])
const detail = ref<any>({})
const loading = ref(false)
const exporting = ref(false)
const detailVisible = ref(false)
const filters = reactive<any>({})
const missingTitleItems = computed(() => (detail.value.title_gap?.missing_items || []).map((name: string) => ({ name })))

async function loadRows() {
  loading.value = true
  try {
    const res = await getHrTeachers(filters)
    rows.value = res.list || []
  } finally {
    loading.value = false
  }
}

async function openDetail(row: any) {
  detail.value = await getHrTeacherDetail(row.id)
  detailVisible.value = true
}

async function exportRows() {
  exporting.value = true
  try {
    const blob = await exportHrTeachers()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `教师档案数据_${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('档案数据已开始下载')
  } catch (error) {
    console.error('导出教师档案失败:', error)
    ElMessage.error('导出教师档案失败')
  } finally {
    exporting.value = false
  }
}

function openFile(row: any) {
  if (row.file_url) window.open(getFileUrl(row.file_url), '_blank')
}

function attachmentStatus(status: string) {
  return ({ active: '有效', archived: '已归档' } as Record<string, string>)[status] || status || '-'
}

function performanceStatus(status: string) {
  return ({ draft: '草稿', published: '已发布' } as Record<string, string>)[status] || status || '-'
}

function periodText(value: string) {
  return ({ annual: '年度', appointment: '聘期' } as Record<string, string>)[value] || value || '-'
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

h3 {
  margin: 20px 0 10px;
}
</style>
