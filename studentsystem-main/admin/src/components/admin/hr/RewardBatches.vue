<template>
  <div class="admin-page">
    <el-card shadow="never">
      <template #header>奖励批次与汇总</template>
      <el-form :inline="true" :model="form">
        <el-form-item label="年度"><el-input-number v-model="form.year" :min="2020" /></el-form-item>
        <el-form-item label="批次名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item><el-button type="primary" @click="create">创建年度批次</el-button></el-form-item>
      </el-form>
      <el-table :data="rows" border stripe>
        <el-table-column prop="year" label="年度" />
        <el-table-column prop="name" label="批次名称" />
        <el-table-column prop="total_amount" label="总金额" />
        <el-table-column prop="status" label="状态" />
        <el-table-column prop="created_at" label="创建时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createRewardBatch, getRewardBatches } from '@/api'

const rows = ref<any[]>([])
const form = reactive({ year: new Date().getFullYear(), name: '' })

async function loadRows() {
  rows.value = await getRewardBatches()
}

async function create() {
  await createRewardBatch(form)
  ElMessage.success('批次已创建')
  loadRows()
}

onMounted(loadRows)
</script>

<style scoped>
.admin-page { padding: 20px; }
</style>
