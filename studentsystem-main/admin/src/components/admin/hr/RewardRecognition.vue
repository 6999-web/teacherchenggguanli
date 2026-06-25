<template>
  <div class="admin-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>教学奖励认定</span>
          <el-button type="primary" @click="loadRows">刷新</el-button>
        </div>
      </template>
      <el-form :model="form" label-width="110px">
        <el-row :gutter="16">
          <el-col :span="6"><el-form-item label="档案ID"><el-input-number v-model="form.profile_id" :min="1" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="类别"><el-select v-model="form.category"><el-option label="教学竞赛" value="teaching_competition" /><el-option label="教学成果" value="teaching_achievement" /><el-option label="教改项目" value="teaching_reform" /><el-option label="教材建设" value="textbook_construction" /></el-select></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="级别"><el-select v-model="form.level"><el-option label="国家级" value="national" /><el-option label="省部级" value="provincial" /><el-option label="市厅级" value="municipal" /><el-option label="校级" value="school" /></el-select></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="等级"><el-select v-model="form.rank"><el-option label="特等奖" value="grand_prize" /><el-option label="一等奖" value="first_prize" /><el-option label="二等奖" value="second_prize" /><el-option label="三等奖" value="third_prize" /></el-select></el-form-item></el-col>
        </el-row>
        <el-button type="primary" @click="create">创建认定</el-button>
      </el-form>
      <el-table :data="rows" border stripe style="margin-top: 18px">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="profile_id" label="档案ID" width="90" />
        <el-table-column prop="category" label="类别" />
        <el-table-column prop="base_amount" label="基础金额" />
        <el-table-column prop="final_amount" label="拟定金额" />
        <el-table-column prop="status" label="状态" />
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
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { auditRewardRecognition, createRewardRecognition, getRewardRecognitions } from '@/api'

const rows = ref<any[]>([])
const form = reactive<any>({ profile_id: 1, category: 'teaching_competition', level: 'national', rank: 'first_prize' })

async function loadRows() {
  rows.value = await getRewardRecognitions()
}

async function create() {
  await createRewardRecognition(form)
  ElMessage.success('奖励认定已创建')
  loadRows()
}

async function audit(row: any, action: string) {
  await auditRewardRecognition(row.id, { action })
  ElMessage.success('审核完成')
  loadRows()
}

onMounted(loadRows)
</script>

<style scoped>
.admin-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
