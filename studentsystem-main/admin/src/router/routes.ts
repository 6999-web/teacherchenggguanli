import { RouteRecordRaw } from 'vue-router'

export const adminRoutes: Array<RouteRecordRaw> = [
  {
    path: '/admin',
    component: () => import('../layout/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: 'dashboard',
        name: 'adminDashboard',
        component: () => import('../components/admin/dashboard/AdminDashboard.vue'),
        meta: { title: '数据概览' },
      },
      {
        path: 'achievements',
        name: 'adminAchievements',
        component: () => import('../components/admin/achievement/AchievementList.vue'),
        meta: { title: '成果审核' },
      },
      {
        path: 'hr/teachers',
        name: 'adminHrTeachers',
        component: () => import('../components/admin/hr/HrTeachers.vue'),
        meta: { title: '教师档案管理' },
      },
      {
        path: 'hr/change-requests',
        name: 'adminHrChangeRequests',
        component: () => import('../components/admin/hr/HrChangeRequests.vue'),
        meta: { title: '档案变更审核' },
      },
      {
        path: 'hr/performance',
        name: 'adminHrPerformance',
        component: () => import('../components/admin/hr/HrPerformance.vue'),
        meta: { title: '绩效记录管理' },
      },
      {
        path: 'hr/title-rules',
        name: 'adminHrTitleRules',
        component: () => import('../components/admin/hr/HrTitleRules.vue'),
        meta: { title: '职称规则配置' },
      },
      {
        path: 'reward/rules',
        name: 'adminRewardRules',
        component: () => import('../components/admin/hr/RewardRules.vue'),
        meta: { title: '教学奖励规则配置' },
      },
      {
        path: 'reward/recognitions',
        name: 'adminRewardRecognition',
        component: () => import('../components/admin/hr/RewardRecognition.vue'),
        meta: { title: '教学奖励认定' },
      },
    ],
  },
]
