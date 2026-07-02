<template>
  <div class="admin-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>职称规则配置</span>
          <div class="header-actions">
            <el-tag :type="fillSettings.title_check_open ? 'success' : 'info'">
              {{ fillSettings.title_check_open ? '教师端已开放填写' : '教师端当前关闭' }}
            </el-tag>
            <el-button
              :type="fillSettings.title_check_open ? 'danger' : 'success'"
              :loading="settingsLoading"
              @click="toggleTitleCheckOpen"
            >
              {{ fillSettings.title_check_open ? '关闭开放填写' : '开放填写' }}
            </el-button>
            <el-button type="primary" @click="refreshAll">刷新</el-button>
          </div>
        </div>
      </template>
      <el-form :model="form" label-width="150px">
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="目标职称"><el-input v-model="form.target_title" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="身份类型"><el-input v-model="form.employment_type" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="最少成果数"><el-input-number v-model="form.min_approved_achievements" :min="0" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="绩效等级"><el-select v-model="form.required_performance_grade" clearable><el-option label="优秀" value="优秀" /><el-option label="良好" value="良好" /><el-option label="合格" value="合格" /></el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="任现职年限"><el-input-number v-model="form.min_years_in_current_title" :min="0" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="必需附件"><el-input v-model="attachmentText" placeholder="逗号分隔" /></el-form-item></el-col>
        </el-row>
        <el-button type="primary" @click="submit">保存规则</el-button>
      </el-form>
      <el-table :data="rows" border stripe style="margin-top: 18px">
        <el-table-column prop="target_title" label="目标职称" />
        <el-table-column prop="employment_type" label="身份" />
        <el-table-column prop="min_approved_achievements" label="成果数" />
        <el-table-column prop="required_performance_grade" label="绩效等级" />
        <el-table-column prop="min_years_in_current_title" label="任职年限" />
        <el-table-column label="必需附件" min-width="180">
          <template #default="{ row }">{{ (row.required_attachment_types || []).join('、') || '无' }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createHrTitleRule, getHrFillSettings, getHrTitleRules, updateHrFillSetting } from '@/api'

const rows = ref<any[]>([])
const settingsLoading = ref(false)
const fillSettings = reactive({
  performance_open: false,
  title_check_open: false,
})
const attachmentText = ref('职称证书')
const form = reactive<any>({ target_title: '副教授', employment_type: 'all', min_approved_achievements: 2, required_performance_grade: '优秀', min_years_in_current_title: 3 })

async function loadRows() {
  rows.value = await getHrTitleRules()
}

async function loadFillSettings() {
  const data = await getHrFillSettings()
  Object.assign(fillSettings, data || {})
}

async function refreshAll() {
  await Promise.all([loadRows(), loadFillSettings()])
}

async function submit() {
  await createHrTitleRule({ ...form, required_attachment_types: attachmentText.value.split(',').map(v => v.trim()).filter(Boolean) })
  ElMessage.success('规则已保存')
  loadRows()
}

async function toggleTitleCheckOpen() {
  settingsLoading.value = true
  try {
    const data = await updateHrFillSetting('title_check', !fillSettings.title_check_open)
    Object.assign(fillSettings, data || {})
    ElMessage.success(fillSettings.title_check_open ? '已开放教师端职称自查填写' : '已关闭教师端职称自查填写')
  } finally {
    settingsLoading.value = false
  }
}

onMounted(refreshAll)
</script>

<style scoped>
.admin-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.header-actions { display: flex; align-items: center; gap: 10px; }
</style>
