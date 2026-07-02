<template>
  <div class="sidebar-container">
    <!-- 椤堕儴鏍囬鍖哄煙 -->
    <div class="logo-container">
      <div class="logo-icon">
        <n-icon size="24" style="display: flex; align-items: center;">
          <IconSchool :size="24" />
        </n-icon>
      </div>
      <h1 class="logo-title">{{ systemTitle }}</h1>
    </div>

    <!-- 涓儴鑿滃崟鍖哄煙 -->
    <div class="menu-container">
      <n-scrollbar style="max-height: 100%;">
        <div class="menu-wrapper">
          <div class="menu-items">
            <div
              v-for="item in menu_items"
              :key="item.key"
              class="menu-item"
              :class="{ 'is-active': activeMenu === item.key }"
              @click="handleMenuClick(item.key)"
            >
              <div class="menu-item-content">
                <div class="menu-item-icon">
                  <n-icon size="18">
                    <component :is="item.icon" />
                  </n-icon>
                </div>
                <span class="menu-item-text">{{ item.label }}</span>
                <div class="menu-item-indicator" v-if="activeMenu === item.key"></div>
              </div>
            </div>
          </div>
        </div>
      </n-scrollbar>
    </div>

    <!-- 搴曢儴鐢ㄦ埛淇℃伅鍖哄煙 -->
    <div class="user-container">
      <n-dropdown :options="user_options" @select="handleUserSelect" trigger="click">
        <div class="user-info">
          <div class="user-avatar">
            <n-avatar
              round
              size="medium"
              :src="avatarDisplayUrl"
              style="background-color: #409eff;"
            >
              <template #fallback>
                <n-icon size="20"><IconUser /></n-icon>
              </template>
            </n-avatar>
          </div>
          <div class="user-detail">
            <span class="user-name" :class="{ 'loading': loading }">{{ username }}</span>
            <span class="user-role">{{ user_role }}</span>
          </div>
          <n-icon class="user-dropdown-icon" size="14">
            <CaretDown />
          </n-icon>
        </div>
      </n-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NAvatar, NDropdown, NIcon, NScrollbar } from 'naive-ui'
import {
  CaretDown,
  IconAward,
  IconChartBar,
  IconFileText,
  IconLogout,
  IconSchool,
  IconUser,
} from '../utils/icons'
import { getStudentMe, getStudentProfile } from '@/api'

const router = useRouter()
const route = useRoute()
const user_name = ref('加载中...')
const username = computed(() => user_name.value)
const user_role = ref('教师')
const user_avatar = ref('')
const activeMenu = ref('achievement')
const loading = ref(false)
const systemTitle = computed(() => {
  if (route.path.startsWith('/student/hr')) return '教师成果管理平台'
  return '教师成果管理平台'
})

const default_avatar = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23e0e0e0"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>'

const avatarDisplayUrl = computed(() => {
  if (!user_avatar.value) return default_avatar
  if (user_avatar.value.startsWith('/uploads/')) {
    const token = localStorage.getItem('token')
    return user_avatar.value + (token ? `?token=${encodeURIComponent(token)}` : '')
  }
  return user_avatar.value
})

const menu_items = ref([
  { label: '成果收集与展示', key: 'achievement', icon: () => h(IconAward) },
  { label: '教师个人档案', key: 'hr_profile', icon: () => h(IconFileText) },
  { label: '人事附件', key: 'hr_attachments', icon: () => h(IconFileText) },
  { label: '历年绩效', key: 'hr_performance', icon: () => h(IconChartBar) },
  { label: '职称自查', key: 'hr_title', icon: () => h(IconAward) },
  { label: 'AI智能分析', key: 'portrait_analysis', icon: () => h(IconChartBar) },
])

const user_options = ref([
  { label: '退出登录', key: 'logout', icon: () => h(IconLogout) },
])

async function fetchUserInfo() {
  loading.value = true
  try {
    const userResponse = await getStudentMe()
    user_name.value = userResponse?.name || userResponse?.username || '教师'
    const roleName = typeof userResponse?.role === 'string' ? userResponse.role : userResponse?.role?.name
    user_role.value = roleName === 'admin' ? '管理员' : '教师'
    try {
      const profileResponse = await getStudentProfile()
      if (profileResponse?.basic_info?.name) user_name.value = profileResponse.basic_info.name
      if (profileResponse?.basic_info?.avatar_url) user_avatar.value = profileResponse.basic_info.avatar_url
    } catch (error) {
      console.warn('获取教师档案信息失败:', error)
    }
  } catch (error: any) {
    user_name.value = error?.response?.status === 401 ? '未登录用户' : '教师'
    user_role.value = '教师'
  } finally {
    loading.value = false
  }
}

const pathToMenu: Record<string, string> = {
  '/student/achievement': 'achievement',
  '/student/achievement-collect': 'achievement',
  '/student/achievement-detail': 'achievement',
  '/student/certificate-ocr': 'achievement',
  '/student/hr-profile': 'hr_profile',
  '/student/hr-attachments': 'hr_attachments',
  '/student/hr-performance': 'hr_performance',
  '/student/hr-title': 'hr_title',
  '/student/portrait': 'portrait_analysis',
}

const menuToPath: Record<string, string> = {
  achievement: '/student/achievement',
  hr_profile: '/student/hr-profile',
  hr_attachments: '/student/hr-attachments',
  hr_performance: '/student/hr-performance',
  hr_title: '/student/hr-title',
  portrait_analysis: '/student/portrait',
}

function updateActiveMenu() {
  const matched = Object.entries(pathToMenu).find(([path]) => route.path.startsWith(path))
  activeMenu.value = matched?.[1] || 'achievement'
  document.title = `${String(route.meta.title || systemTitle.value)} - ${systemTitle.value}`
}

function handleMenuClick(key: string) {
  activeMenu.value = key
  if (menuToPath[key]) router.push(menuToPath[key])
}

function handleUserSelect(key: string) {
  if (key === 'logout') handleLogout()
}

function handleLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  router.push('/student/login')
}

function handleGlobalAvatarUpdate(e: any) {
  if (e.detail?.url) user_avatar.value = e.detail.url
}

watch(() => route.path, updateActiveMenu, { immediate: true })

onMounted(() => {
  updateActiveMenu()
  fetchUserInfo()
  window.addEventListener('avatar-updated', handleGlobalAvatarUpdate)
})

onUnmounted(() => {
  window.removeEventListener('avatar-updated', handleGlobalAvatarUpdate)
})
</script>

<style scoped>
/* ========== 容器样式 ========== */
.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(180deg, #1a237e 0%, #0d47a1 100%);
  color: #fff;
  transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
  width: 260px;
  position: relative;
  overflow: hidden;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
}

/* ========== 顶部Logo区域 ========== */
.logo-container {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  height: 64px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
}

.logo-icon {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  color: #fff;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.logo-icon:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.logo-title {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
  color: #fff;
  letter-spacing: 0.5px;
}

/* ========== 菜单容器 ========== */
.menu-container {
  flex: 1;
  overflow: hidden;
  padding: 8px 0;
}

.menu-wrapper {
  padding: 0 8px;
}

/* ========== 菜单项 ========== */
.menu-items {
  padding: 0 8px;
}

.menu-item {
  position: relative;
  margin-bottom: 4px;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateX(2px);
}

.menu-item.is-active {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.menu-item.is-active:hover {
  transform: translateX(0);
}

.menu-item-content {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  position: relative;
}

.menu-item-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: 12px;
  color: #bfcbd9;
  transition: all 0.3s ease;
}

.menu-item.is-active .menu-item-icon {
  color: #fff;
}

.menu-item-text {
  font-size: 14px;
  font-weight: 500;
  color: #e4e7ed;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.menu-item.is-active .menu-item-text {
  color: #fff;
  font-weight: 600;
}

.menu-item-indicator {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: #fff;
  border-radius: 2px;
  opacity: 0.8;
}

/* ========== 用户信息区域 ========== */
.user-container {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.08);
}

.user-avatar {
  margin-right: 12px;
  position: relative;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  transition: all 0.3s ease;
}

.user-avatar:hover {
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.4);
}

.user-avatar::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  width: 8px;
  height: 8px;
  background: #67c23a;
  border: 2px solid #304156;
  border-radius: 50%;
}

.avatar-edit-hint {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 16px;
  height: 16px;
  background: #409eff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  border: 1.5px solid #304156;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 1;
}

.user-avatar:hover .avatar-edit-hint {
  opacity: 1;
}

.user-avatar {
  cursor: pointer;
}

.user-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 2px;
  transition: opacity 0.3s ease;
}

.user-name.loading {
  opacity: 0.7;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
}

.user-role {
  font-size: 12px;
  color: #bfcbd9;
}

.user-dropdown-icon {
  color: #bfcbd9;
  transition: transform 0.3s ease;
}

.user-info:hover .user-dropdown-icon {
  transform: rotate(180deg);
}

/* ========== 响应式设计 ========== */
@media (max-width: 768px) {
  .sidebar-container {
    width: 100%;
    position: fixed;
    z-index: 1000;
  }
}

/* ========== 滚动条样式 ========== */
:deep(.n-scrollbar-rail) {
  background: rgba(255, 255, 255, 0.05);
}

:deep(.n-scrollbar-rail__scrollbar) {
  background: rgba(255, 255, 255, 0.2);
}

:deep(.n-scrollbar-rail__scrollbar:hover) {
  background: rgba(255, 255, 255, 0.3);
}

/* ========== 暗色模式适配 ========== */
@media (prefers-color-scheme: dark) {
  .sidebar-container {
    background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
  }
  
  .logo-container {
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }
  
  .user-container {
    border-top-color: rgba(255, 255, 255, 0.1);
  }
  
  .sidebar-tooltip {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
  }
}
</style>
