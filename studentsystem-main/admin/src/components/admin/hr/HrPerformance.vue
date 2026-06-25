<template>
  <div class="admin-page">
    <el-card shadow="never">
      <template #header>绩效记录管理</template>
      <el-form :model="form" label-width="110px" class="form">
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="档案ID"><el-input-number v-model="form.profile_id" :min="1" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="年度"><el-input-number v-model="form.year" :min="2020" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="等级"><el-select v-model="form.grade"><el-option label="优秀" value="优秀" /><el-option label="良好" value="良好" /><el-option label="合格" value="合格" /></el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="教学成果分"><el-input-number v-model="form.teaching_score" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="评价考核分"><el-input-number v-model="form.evaluation_score" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="奖励加分"><el-input-number v-model="form.reward_bonus" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="管理员调整"><el-input-number v-model="form.admin_adjustment" /></el-form-item></el-col>
        </el-row>
        <el-button type="primary" @click="submit">保存绩效记录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { createHrPerformance } from '@/api'

const form = reactive<any>({ profile_id: 1, year: new Date().getFullYear(), grade: '合格', teaching_score: 0, evaluation_score: 0, reward_bonus: 0, admin_adjustment: 0 })

async function submit() {
  await createHrPerformance(form)
  ElMessage.success('绩效记录已保存')
}
</script>

<style scoped>
.admin-page { padding: 20px; }
.form { max-width: 980px; }
</style>
