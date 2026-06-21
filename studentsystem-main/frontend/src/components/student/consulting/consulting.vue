<template>
  <div class="consultation_page">
    <!-- 页面标题 -->
    <div class="page_header">
      <h1>咨询预约</h1>
      <p>专业的生涯规划与心理健康咨询服务</p>
    </div>

    <!-- 紧急心理支持横幅 -->
    <div class="emergency_banner">
      <div class="emergency_content">
        <div class="emergency_left">
          <AlertTriangle :size="20" class="emergency_icon" />
          <div class="emergency_text">
            <span class="emergency_title">需要紧急心理支持？</span>
            <span class="emergency_desc">我们提供24小时危机干预服务</span>
          </div>
        </div>
        <button class="emergency_btn">紧急咨询</button>
      </div>
    </div>

    <!-- 统计数据区域 -->
<div class="stats_section">
  <div class="stat_card">
    <Users :size="24" />
    <div class="stat_number">{{ consultants.length || 0 }}</div>
    <div class="stat_label">咨询师总数</div>
  </div>
  <div class="stat_card">
    <Briefcase :size="24" />
    <div class="stat_number">{{ consultants.filter(c => c.type === 'career').length || 0 }}</div>
    <div class="stat_label">生涯规划师</div>
  </div>
  <div class="stat_card">
    <Heart :size="24" />
    <div class="stat_number">{{ consultants.filter(c => c.type === 'counseling').length || 0 }}</div>
    <div class="stat_label">心理咨询师</div>
  </div>
  <div class="stat_card">
    <Users :size="24" />
    <div class="stat_number">{{ consultants.filter(c => c.isOnline).length || 0 }}</div>
    <div class="stat_label">在线咨询师</div>
  </div>
  <div class="stat_card">
    <Star :size="24" />
    <div class="stat_number">{{ consultants.length ? (consultants.reduce((sum, c) => sum + c.rating, 0) / consultants.length).toFixed(1) : '0.0' }}</div>
    <div class="stat_label">平均评分</div>
  </div>
</div>

    <!-- 搜索和筛选区域 -->
    <div class="search_section">
      <div class="search_input_wrapper">
        <Search :size="18" class="search_icon" />
        <input 
          type="text" 
          placeholder="搜索咨询师姓名或专长领域"
          v-model="searchQuery"
          class="search_input"
        />
      </div>
      <select v-model="categoryFilter" @change="fetchConsultantData()" class="category_select">
        <option value="">全部类别</option>
        <option value="career">生涯规划</option>
        <option value="counseling">心理健康</option>
      </select>
      <div v-if="loading" class="loading_indicator">加载中...</div>
    </div>

    <!-- 类别筛选标签 -->
    <div class="category_tabs">
      <button 
        class="category_tab"
        :class="{ active: activeCategory === 'all' }"
        @click="() => { activeCategory = 'all'; fetchConsultantData(); }"
      >
        <Users :size="16" />
        全部咨询师
        <span v-if="loading && activeCategory === 'all'" class="loading_dot"></span>
      </button>
      <button 
        class="category_tab"
        :class="{ active: activeCategory === 'career' }"
        @click="() => { activeCategory = 'career'; fetchConsultantData(); }"
      >
        <Briefcase :size="16" />
        生涯规划
        <span v-if="loading && activeCategory === 'career'" class="loading_dot"></span>
      </button>
      <button 
        class="category_tab"
        :class="{ active: activeCategory === 'counseling' }"
      @click="() => { activeCategory = 'counseling'; fetchConsultantData(); }"
      >
        <Heart :size="16" />
        心理健康
        <span v-if="loading && activeCategory === 'counseling'" class="loading_dot"></span>
      </button>
    </div>

    <!-- 咨询师列表 -->
    <div class="consultants_container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading_container">
        <div class="loading_spinner"></div>
        <p>正在加载咨询师数据...</p>
      </div>
      
      <!-- 错误提示 -->
      <div v-else-if="error" class="error_container">
        <AlertTriangle :size="32" />
        <p>{{ error }}</p>
        <button @click="fetchConsultantData" class="retry_button">重试</button>
      </div>
      
      <!-- 无数据提示 -->
      <div v-else-if="filteredConsultants.length === 0" class="empty_container">
        <Search :size="32" />
        <p>没有找到符合条件的咨询师</p>
      </div>
      
      <!-- 咨询师列表 -->
      <div v-else class="consultants_grid">
        <div 
          v-for="consultant in filteredConsultants" 
          :key="consultant.id"
          class="consultant_card"
        >
          <div class="consultant_header">
            <div class="consultant_avatar">
              <img :src="consultant.avatar" :alt="consultant.name" />
            </div>
            <div class="consultant_basic_info">
              <div class="consultant_name_row">
                <span class="consultant_name">{{ consultant.name }}</span>
                <span class="consultant_badge" :class="consultant.type">{{ consultant.badge }}</span>
              </div>
              <div class="consultant_title">{{ consultant.title }}</div>
              <div class="consultant_rating">
                <Star :size="14" class="star_icon" />
                <span class="rating_number">{{ consultant.rating }}</span>
                <span class="rating_count">{{ consultant.reviewCount }}条评价</span>
                <span class="experience">{{ consultant.experience }}年经验</span>
              </div>
            </div>
            <div class="online_status" :class="{ online: consultant.isOnline }">
              <div class="status_dot"></div>
            </div>
          </div>

          <div class="consultant_description">
            {{ consultant.description }}
          </div>

          <div class="consultant_tags">
            <span 
              v-for="tag in consultant.tags" 
              :key="tag"
              class="tag"
            >
              {{ tag }}
            </span>
          </div>

          <div class="consultant_availability">
            <Clock :size="14" />
            <span class="availability_label">最早可约:</span>
            <span class="availability_time">{{ consultant.nextAvailable }}</span>
            <span class="availability_status" :class="consultant.availabilityStatus">
              {{ consultant.availabilityText }}
            </span>
          </div>

          <div class="consultant_actions">
            <button class="btn_secondary" @click="viewDetails(consultant.id)">
              详情
            </button>
            <button class="btn_primary" @click="bookConsultation(consultant.id)">
              立即预约
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
  IconAlertTriangle as AlertTriangle,
  IconSearch as Search,
  IconUsers as Users,
  IconBriefcase as Briefcase,
  IconHeart as Heart,
  IconStar as Star,
  IconClock as Clock
} from '@tabler/icons-vue'

// 响应式数据
const searchQuery = ref('')
const categoryFilter = ref('')
const activeCategory = ref('all')

import { 
  getConsultTeachers, 
  getConsultTeacherById, 
  getConsultTeachersByType, 
  getOnlineConsultTeachers,
  getFileUrl
} from '@/api'
import type { IConsultTeacherItem } from '../../../types/api.d.ts'



// 响应式状态
const loading = ref(false)
const consultants = ref<ConsultantItem[]>([])
const error = ref<string | null>(null)

// 咨询师数据类型定义
interface ConsultantItem {
  id: string | number
  name: string
  title: string
  badge: string
  type: string
  avatar: string
  rating: number
  reviewCount: number
  experience: number
  isOnline: boolean
  description: string
  tags: string[]
  nextAvailable: string
  availabilityStatus: string
  availabilityText: string
}

// 开发环境备用数据
const fallbackConsultants = [
  {
    id: '1',
    name: '李教授',
    title: '生涯规划导师',
    badge: '💼',
    type: 'career',
    avatar: 'https://via.placeholder.com/60x60/4285f4/ffffff?text=李',
    rating: 4.9,
    reviewCount: 156,
    experience: 15,
    isOnline: false,
    description: '资深生涯规划专家，曾在多家知名企业担任HR总监，擅长帮助教师制定个性化职业发展规划。',
    tags: ['职业规划', '简历指导', '就业规划'],
    nextAvailable: '今天 14:00',
    availabilityStatus: 'available',
    availabilityText: '在线'
  },
  {
    id: '2',
    name: '王老师',
    title: '心理咨询师',
    badge: '❤️',
    type: 'counseling',
    avatar: 'https://via.placeholder.com/60x60/ea4335/ffffff?text=王',
    rating: 4.8,
    reviewCount: 203,
    experience: 12,
    isOnline: false,
    description: '国家二级心理咨询师，专注大学教师心理健康，温和细心，善于倾听和引导。',
    tags: ['情感管理', '人际关系', '学习压力'],
    nextAvailable: '明天 09:00',
    availabilityStatus: 'available',
    availabilityText: '在线'
  },
  {
    id: '3',
    name: '张博士',
    title: '职业发展顾问',
    badge: '💼',
    type: 'career',
    avatar: 'https://via.placeholder.com/60x60/34a853/ffffff?text=张',
    rating: 4.7,
    reviewCount: 89,
    experience: 10,
    isOnline: true,
    description: '创业导师和职业发展专家，曾成功指导多名教师创业和职业，实战经验丰富。',
    tags: ['创业指导', '技能提升', '行业分析'],
    nextAvailable: '今天 16:30',
    availabilityStatus: 'available',
    availabilityText: '在线'
  },
  {
    id: '4',
    name: '陈医生',
    title: '临床心理医师',
    badge: '❤️',
    type: 'counseling',
    avatar: 'https://via.placeholder.com/60x60/9c27b0/ffffff?text=陈',
    rating: 4.9,
    reviewCount: 167,
    experience: 18,
    isOnline: true,
    description: '临床心理学专家，专注于青少年心理健康问题，提供专业心理疏导服务。',
    tags: ['焦虑抑郁', '情绪调节', '心理创伤'],
    nextAvailable: '今天 10:30',
    availabilityStatus: 'available',
    availabilityText: '在线'
  }
]

// 计算属性：过滤后的咨询师
const filteredConsultants = computed(() => {
  let result = consultants.value

  // 根据搜索关键词过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(consultant => 
      consultant.name.toLowerCase().includes(query) ||
      consultant.title.toLowerCase().includes(query) ||
      consultant.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }

  // 根据类别过滤
  if (categoryFilter.value) {
    result = result.filter(consultant => consultant.type === categoryFilter.value)
  }

  // 根据激活的类别标签过滤
  if (activeCategory.value !== 'all') {
    result = result.filter(consultant => consultant.type === activeCategory.value)
  }

  return result
})

// 获取咨询师数据
const fetchConsultantData = async () => {
  loading.value = true
  try {
    let response
    
    // 根据筛选条件选择不同的API调用
    if (categoryFilter.value !== '') {
      // 按类型筛选
      response = await getConsultTeachersByType(categoryFilter.value)
    } else if (activeCategory.value === 'online') {
      // 获取在线咨询师
      response = await getOnlineConsultTeachers()
    } else {
      // 获取所有咨询师
      response = await getConsultTeachers()
    }
    
    console.log('API响应数据:', response)
    
    if (response && response.data) {
      // 将API返回的数据转换为前端展示格式
      consultants.value = response.data.map((item: IConsultTeacherItem) => {
        return {
          id: item.id,
          name: item.name,
          title: getTitleDisplay(item.title, item.type),
          badge: item.type === 'career' ? '💼' : '❤️',
          type: item.type,
          avatar: getAvatarUrl(item.avatar),
          rating: item.rating,
          reviewCount: Math.floor(Math.random() * 200) + 50, // 模拟评价数量
          experience: item.experience_years,
          isOnline: item.is_online,
          description: item.persitonal,
          tags: getTagsByType(item.type),
          nextAvailable: formatAvailableTime(item.next_available_time),
          availabilityStatus: 'available', // 默认可预约
          availabilityText: item.is_online ? '在线' : '离线'
        }
      })
    } else {
      console.warn('API返回数据格式不符合预期，使用备用数据')
      consultants.value = fallbackConsultants
    }
  } catch (error) {
    console.error('获取咨询师数据失败:', error)
    // 使用备用数据
    consultants.value = fallbackConsultants
  } finally {
    loading.value = false
  }
}

// 使用本地 getBaseURL 函数替代已移除的模块
const getBaseURL = () => (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
const backendUrl = getBaseURL().replace('/api', '');


// 辅助函数：获取头像URL
const getAvatarUrl = (avatar: any): string => {
  // 如果头像对象不存在，返回默认头像
  if (!avatar) {
    return backendUrl + '/uploads/avatar_88e8d14b8c.jpg';
  }
  
  // 处理字符串类型的头像URL
  if (typeof avatar === 'string') {
    // 如果是完整URL则直接返回，否则拼接后端URL
    return avatar.startsWith('http') ? avatar : backendUrl + avatar;
  }

  // 处理新的Strapi媒体对象格式
  // 新格式包含id、hash和ext属性，例如：{id: 1, hash: 'avatar_88e8d14b8c', ext: '.jpg'}
  if (avatar.id && avatar.hash) {
    // 直接使用hash作为文件名
    return `${backendUrl}/uploads/${avatar.hash}${avatar.ext}`;
  }
  
  // 处理标准Strapi媒体对象类型的头像
  // 标准格式包含data.attributes.url路径，例如：{data: {attributes: {url: '/uploads/avatar.jpg'}}}
  const data = avatar?.data;
  if (data && data.attributes && data.attributes.url) {
    return backendUrl + data.attributes.url;
  }
  
  // 如果无法获取有效的头像URL，返回默认头像
  return backendUrl + '/uploads/avatar_88e8d14b8c.jpg';
}

// 辅助函数：根据类型获取标签
const getTagsByType = (type: string): string[] => {
  if (type === 'career') {
    return ['职业规划', '简历指导', '就业规划']
  } else if (type === 'counseling') {
    return ['情感管理', '人际关系', '学习压力']
  } else {
    return ['其他服务']
  }
}

// 辅助函数：格式化可用时间
const formatAvailableTime = (timeStr: string): string => {
  if (!timeStr) return '暂无可预约时间'
  
  try {
    const date = new Date(timeStr)
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    
    // 格式化时间部分
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    const timeFormat = `${hours}:${minutes}`
    
    // 判断是今天、明天还是其他日期
    if (date.toDateString() === today.toDateString()) {
      return `今天 ${timeFormat}`
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return `明天 ${timeFormat}`
    } else {
      return `${date.getMonth() + 1}月${date.getDate()}日 ${timeFormat}`
    }
  } catch (e) {
    console.error('日期格式化错误:', e)
    return timeStr // 如果解析失败，返回原始字符串
  }
}

// 辅助函数：获取职称显示
const getTitleDisplay = (title: string, type: string): string => {
  if (title === 'Professor') {
    return type === 'career' ? '职业发展教授' : '心理咨询教授'
  } else if (title === 'Lecturer') {
    return type === 'career' ? '生涯规划导师' : '心理咨询师'
  } else {
    return type === 'career' ? '职业顾问' : '心理顾问'
  }
}

// 方法
const viewDetails = async (consultantId: string | number) => {
  try {
    const response = await getConsultTeacherById(consultantId)
    if (response && response.data) {
      console.log('咨询师详情:', response.data)
      // 实现跳转到详情页的逻辑
      // router.push(`/student/consultant/${consultantId}`)
    }
  } catch (error) {
    console.error('获取咨询师详情失败:', error)
  }
}

const bookConsultation = (consultantId: string | number) => {
  console.log('预约咨询:', consultantId)
  // 这里可以跳转到预约页面
}

onMounted(() => {
  // 组件挂载后的初始化逻辑
  fetchConsultantData()
})
</script>

<style scoped>
.consultation_page {
  width: 100%;
  padding: 16px 24px;
  background-color: #f8f9fa;
  min-height: 100vh;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* 页面标题 */
.page_header {
  text-align: left;
  margin-bottom: 20px;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.page_header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.page_header p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 紧急支持横幅 */
.emergency_banner {
  background: linear-gradient(135deg, #fff1f0 0%, #ffe7e6 100%);
  border: 1px solid #ffa39e;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 20px;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.emergency_content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.emergency_left {
  display: flex;
  align-items: center;
  flex: 1;
}

.emergency_icon {
  color: #d32f2f;
  margin-right: 12px;
  flex-shrink: 0;
}

.emergency_text {
  display: flex;
  flex-direction: column;
}

.emergency_title {
  font-weight: 600;
  color: #d32f2f;
  font-size: 14px;
  margin-bottom: 2px;
}

.emergency_desc {
  font-size: 12px;
  color: #666;
}

.emergency_btn {
  background: #d32f2f;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.2s;
  flex-shrink: 0;
}

.emergency_btn:hover {
  background: #b71c1c;
}

/* 统计数据区域 */
.stats_section {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 20px;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.stat_card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s;
}

.stat_card:hover {
  transform: translateY(-2px);
}

.stat_number {
  font-size: 28px;
  font-weight: 600;
  color: #1976d2;
  margin-bottom: 8px;
}

.stat_label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

/* 搜索区域 */
.search_section {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.search_input_wrapper {
  position: relative;
  flex: 1;
}

.search_input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  transition: border-color 0.2s;
}

.search_input:focus {
  outline: none;
  border-color: #1976d2;
}

.search_icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.category_select {
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  min-width: 140px;
}

/* 类别标签 */
.category_tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.category_tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  background: white;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.category_tab:hover {
  border-color: #1976d2;
  color: #1976d2;
}

.category_tab.active {
  background: #1976d2;
  border-color: #1976d2;
  color: white;
}

/* 咨询师容器 */
.consultants_container {
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

/* 咨询师网格 */
.consultants_grid {
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

/* 咨询师卡片 */
.consultant_card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.2s;
  border: 1px solid #f0f0f0;
}

.consultant_card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.consultant_header {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  position: relative;
}

.consultant_avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 16px;
  flex-shrink: 0;
}

.consultant_avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.consultant_basic_info {
  flex: 1;
}

.consultant_name_row {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.consultant_name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-right: 8px;
}

.consultant_badge {
  font-size: 16px;
}

.consultant_title {
  color: #666;
  font-size: 13px;
  margin-bottom: 8px;
}

.consultant_rating {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.star_icon {
  color: #ff9800;
}

.rating_number {
  color: #ff9800;
  font-weight: 600;
  margin-right: 4px;
}

.rating_count {
  color: #666;
  margin-right: 8px;
}

.experience {
  color: #666;
}

.online_status {
  position: absolute;
  top: 0;
  right: 0;
}

.status_dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
}

.online_status.online .status_dot {
  background: #4caf50;
}

.consultant_description {
  color: #666;
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 16px;
}

.consultant_tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.tag {
  background: #f5f5f5;
  color: #666;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
}

.consultant_availability {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 16px;
  font-size: 12px;
}

.availability_label {
  color: #666;
}

.availability_time {
  color: #333;
  font-weight: 500;
}

.availability_status {
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  margin-left: 4px;
}

.availability_status.available {
  background: #e8f5e8;
  color: #4caf50;
}

.consultant_actions {
  display: flex;
  gap: 12px;
}

.btn_secondary {
  flex: 1;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn_secondary:hover {
  border-color: #1976d2;
  color: #1976d2;
}

.btn_primary {
  flex: 2;
  padding: 10px;
  border: none;
  border-radius: 6px;
  background: #1976d2;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn_primary:hover {
  background: #1565c0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .consultants_grid {
    grid-template-columns: 1fr;
    width: 100%;
    box-sizing: border-box;
    overflow: hidden;
  }
  
  .stats_section {
    grid-template-columns: repeat(3, 1fr);
    width: 100%;
    box-sizing: border-box;
    overflow: hidden;
  }
}

@media (max-width: 768px) {
  .consultation_page {
    padding: 12px 16px;
    width: 100%;
    box-sizing: border-box;
    overflow-x: hidden;
  }
  
  .stats_section {
    grid-template-columns: repeat(2, 1fr);
    width: 100%;
    box-sizing: border-box;
    overflow: hidden;
  }
  
  .search_section {
    flex-direction: column;
    width: 100%;
    box-sizing: border-box;
    overflow: hidden;
  }
  
  .category_tabs {
    flex-wrap: wrap;
    width: 100%;
    box-sizing: border-box;
    overflow: hidden;
  }
  
  .emergency_content {
    flex-direction: column;
    gap: 12px;
    text-align: center;
    width: 100%;
    box-sizing: border-box;
  }
  
  .emergency_left {
    justify-content: center;
    width: 100%;
    box-sizing: border-box;
  }
  
  .consultants_container {
    width: 100%;
    box-sizing: border-box;
    overflow: hidden;
  }
}
</style>
