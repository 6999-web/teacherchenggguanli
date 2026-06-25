<template>
  <el-aside width="240px" class="sidebar-container">
    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      router
      background-color="#2c3e50"
      text-color="#ffffff"
      active-text-color="#409eff"
    >
      <el-menu-item index="/admin/dashboard">
        <el-icon><DataLine /></el-icon>
        <span>数据概览</span>
      </el-menu-item>
      <el-menu-item index="/admin/achievements">
        <el-icon><List /></el-icon>
        <span>成果审核</span>
      </el-menu-item>
      <el-menu-item index="/admin/hr/teachers">
        <el-icon><User /></el-icon>
        <span>教师档案</span>
      </el-menu-item>
      <el-menu-item index="/admin/hr/change-requests">
        <el-icon><Edit /></el-icon>
        <span>资料变更审核</span>
      </el-menu-item>
      <el-menu-item index="/admin/hr/performance">
        <el-icon><TrendCharts /></el-icon>
        <span>绩效记录</span>
      </el-menu-item>
      <el-menu-item index="/admin/hr/title-rules">
        <el-icon><Setting /></el-icon>
        <span>职称规则</span>
      </el-menu-item>
      <el-menu-item index="/admin/reward/rules">
        <el-icon><Setting /></el-icon>
        <span>教学奖励规则</span>
      </el-menu-item>
      <el-menu-item index="/admin/reward/recognitions">
        <el-icon><Medal /></el-icon>
        <span>奖励认定</span>
      </el-menu-item>
      <el-menu-item index="/admin/reward/batches">
        <el-icon><Tickets /></el-icon>
        <span>奖励批次</span>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { DataLine, Edit, List, Medal, Setting, Tickets, TrendCharts, User } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.sidebar-container {
  background-color: #2c3e50;
  height: 100%;
  overflow-y: auto;
}

.sidebar-menu {
  border-right: none;
  height: 100%;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}
</style>
