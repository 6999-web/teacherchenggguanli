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
      <el-sub-menu index="hr-system">
        <template #title>
          <el-icon><User /></el-icon>
          <span>人事体系</span>
        </template>
        <el-menu-item index="/admin/hr/teachers">
          <el-icon><User /></el-icon>
          <span>教师档案</span>
        </el-menu-item>
        <el-menu-item index="/admin/hr/change-requests">
          <el-icon><EditPen /></el-icon>
          <span>档案审核</span>
        </el-menu-item>
        <el-menu-item index="/admin/hr/performance">
          <el-icon><TrendCharts /></el-icon>
          <span>绩效记录</span>
        </el-menu-item>
        <el-menu-item index="/admin/hr/title-rules">
          <el-icon><Setting /></el-icon>
          <span>职称规则</span>
        </el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="reward-system">
        <template #title>
          <el-icon><Medal /></el-icon>
          <span>奖励体系</span>
        </template>
        <el-menu-item index="/admin/reward/rules">
          <el-icon><Setting /></el-icon>
          <span>教学奖励规则</span>
        </el-menu-item>
        <el-menu-item index="/admin/reward/recognitions">
          <el-icon><Medal /></el-icon>
          <span>奖励认定</span>
        </el-menu-item>
      </el-sub-menu>
    </el-menu>
  </el-aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { DataLine, EditPen, Medal, Setting, TrendCharts, User } from '@element-plus/icons-vue'

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
