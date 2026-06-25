import { RouteRecordRaw } from 'vue-router'

export const studentRoutes: Array<RouteRecordRaw> = [
  {
    path: '/student',
    component: () => import('../layout/StudentLayout.vue'),
    meta: { requiresAuth: true, role: 'student' },
    children: [
      {
        path: 'achievement',
        name: 'studentAchievement',
        component: () => import('../components/student/honors/achievement.vue'),
        meta: { title: '成果收集与展示' },
      },
      {
        path: 'achievement-collect',
        name: 'achievementCollect',
        component: () => import('../components/student/honors/achievement-collect.vue'),
        meta: { title: '成果收集' },
      },
      {
        path: 'achievement-detail/:id',
        name: 'achievementDetail',
        component: () => import('../components/student/honors/AchievementDetail.vue'),
        meta: { title: '成果详情' },
      },
      {
        path: 'certificate-ocr',
        name: 'certificateOcr',
        component: () => import('../components/student/honors/CertificateOcr.vue'),
        meta: { title: '证书识别' },
      },
      {
        path: 'portrait',
        name: 'studentPortrait',
        component: () => import('../components/student/portrait/portrait-analysis.vue'),
        meta: { title: '个人画像' },
      },
      {
        path: 'portrait/ai-chat',
        name: 'studentPortraitAiChat',
        component: () => import('../components/student/portrait/ai-chat.vue'),
        meta: { title: 'AI 智能对话' },
      },
      {
        path: 'profile',
        name: 'studentProfile',
        component: () => import('../components/student/profile/ProfilePage.vue'),
        meta: { title: '个人资料' },
      },
      {
        path: 'hr-profile',
        name: 'hrProfile',
        component: () => import('../components/student/hr/HrProfile.vue'),
        meta: { title: '教师个人档案' },
      },
      {
        path: 'hr-attachments',
        name: 'hrAttachments',
        component: () => import('../components/student/hr/HrAttachments.vue'),
        meta: { title: '人事附件' },
      },
      {
        path: 'hr-performance',
        name: 'hrPerformance',
        component: () => import('../components/student/hr/HrPerformance.vue'),
        meta: { title: '历年绩效' },
      },
      {
        path: 'hr-title',
        name: 'hrTitleCheck',
        component: () => import('../components/student/hr/HrTitleCheck.vue'),
        meta: { title: '职称自查' },
      },
      {
        path: 'teaching-reward-apply',
        name: 'teachingRewardApply',
        component: () => import('../components/student/hr/TeachingRewardApply.vue'),
        meta: { title: '教学奖励申报' },
      },
    ],
  },
]
