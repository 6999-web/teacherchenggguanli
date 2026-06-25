<template>
  <div class="admin-page">
    <el-card shadow="never">
      <template #header>资料变更审核</template>
      <el-table :data="rows" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="profile_id" label="档案ID" width="100" />
        <el-table-column label="修改内容" min-width="320">
          <template #default="{ row }"><pre>{{ JSON.stringify(row.after_data, null, 2) }}</pre></template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" type="success" :disabled="row.status !== 'pending'" @click="audit(row, 'approve')">通过</el-button>
            <el-button size="small" type="danger" :disabled="row.status !== 'pending'" @click="audit(row, 'reject')">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { auditHrChangeRequest, getHrChangeRequests } from '@/api'

const rows = ref<any[]>([])
const loading = ref(false)

async function loadRows() {
  loading.value = true
  try {
    rows.value = await getHrChangeRequests()
  } finally {
    loading.value = false
  }
}

async function audit(row: any, action: string) {
  await auditHrChangeRequest(row.id, { action })
  ElMessage.success('审核完成')
  loadRows()
}

onMounted(loadRows)
</script>

<style scoped>
.admin-page { padding: 20px; }
pre { white-space: pre-wrap; margin: 0; font-family: Consolas, monospace; font-size: 12px; }
</style>
