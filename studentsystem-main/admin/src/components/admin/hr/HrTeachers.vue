<template>
  <div class="admin-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>教师档案管理</span>
          <el-button type="primary" @click="loadRows">刷新</el-button>
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

    <el-drawer v-model="detailVisible" title="教师档案详情" size="50%">
      <template v-if="detail.profile">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="姓名">{{ detail.profile.name }}</el-descriptions-item>
          <el-descriptions-item label="工号">{{ detail.profile.employee_no }}</el-descriptions-item>
          <el-descriptions-item label="院系">{{ detail.profile.department }}</el-descriptions-item>
          <el-descriptions-item label="学历/学位">{{ detail.profile.education }} / {{ detail.profile.degree }}</el-descriptions-item>
          <el-descriptions-item label="岗位/职称">{{ detail.profile.position }} / {{ detail.profile.current_title }}</el-descriptions-item>
          <el-descriptions-item label="联系方式">{{ detail.profile.phone }} {{ detail.profile.email }}</el-descriptions-item>
        </el-descriptions>
        <h3>人事附件</h3>
        <el-table :data="detail.attachments || []" border>
          <el-table-column prop="attachment_type" label="类型" />
          <el-table-column prop="title" label="名称" />
          <el-table-column prop="original_filename" label="文件" />
        </el-table>
        <h3>绩效记录</h3>
        <el-table :data="detail.performances || []" border>
          <el-table-column prop="year" label="年度" />
          <el-table-column prop="final_score" label="得分" />
          <el-table-column prop="grade" label="等级" />
        </el-table>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { getHrTeacherDetail, getHrTeachers } from '@/api'

const rows = ref<any[]>([])
const detail = ref<any>({})
const loading = ref(false)
const detailVisible = ref(false)
const filters = reactive<any>({})

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

onMounted(loadRows)
</script>

<style scoped>
.admin-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
h3 { margin: 20px 0 10px; }
</style>
