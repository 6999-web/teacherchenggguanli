<template>
  <div class="home-container">
    <section class="home-shell">
      <div class="platform-title">
        <div class="icon-box">
          <n-icon size="32" class="title-icon">
            <IconSchool :size="32" />
          </n-icon>
        </div>
        <div>
          <h1>教师综合管理平台</h1>
          <p>评价体系、教师人事管理体系统一入口</p>
        </div>
      </div>

      <div class="system-grid">
        <button class="system-card evaluation-card" type="button" @click="goToStudentLogin">
          <span class="card-icon">
            <IconChartBar :size="34" />
          </span>
          <span class="card-title">评价管理体系</span>
          <span class="card-desc">保留现有教学评价与分析能力，查看评价结果和教学画像。</span>
          <span class="card-action">进入评价体系</span>
        </button>

        <button class="system-card reward-card" type="button" @click="goToReward">
          <span class="card-icon">
            <IconAward :size="34" />
          </span>
          <span class="card-title">人事奖励申报</span>
          <span class="card-desc">教学成果申报、奖励规则匹配、奖励认定审核、年度批次发放。</span>
          <span class="card-action">进入人事奖励</span>
        </button>

        <button class="system-card hr-card" type="button" @click="goToHr">
          <span class="card-icon">
            <IconUsers :size="34" />
          </span>
          <span class="card-title">教师人事管理体系</span>
          <span class="card-desc">教师一张表、档案附件、绩效记录、职称自查与材料缺口提醒。</span>
          <span class="card-action">进入人事体系</span>
        </button>
      </div>

      <div class="admin-entry">
        <button type="button" @click="goToAdminLogin">
          <IconShieldCheck :size="18" />
          管理端入口
        </button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import {
  IconAward,
  IconChartBar,
  IconSchool,
  IconShieldCheck,
  IconUsers
} from '@tabler/icons-vue'

const router = useRouter()
const adminLoginUrl = import.meta.env.VITE_ADMIN_LOGIN_URL || 'http://localhost:5005/admin/login'

const goToStudentLogin = () => {
  router.push('/student/login')
}

const goToReward = () => {
  router.push('/student/login?redirect=/student/teaching-reward-apply')
}

const goToHr = () => {
  router.push('/student/login?redirect=/student/hr-profile')
}

const goToAdminLogin = () => {
  window.location.href = adminLoginUrl
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  width: 100%;
  background: #f4f7fb;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 28px;
  box-sizing: border-box;
}

.home-shell {
  width: min(1120px, 100%);
}

.platform-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin-bottom: 28px;
  color: #0f172a;
}

.icon-box {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 52px;
  height: 52px;
  background-color: #1d4ed8;
  border-radius: 8px;
  box-shadow: 0 10px 22px rgba(29, 78, 216, 0.22);
}

.title-icon {
  color: white;
}

.platform-title h1 {
  font-size: 34px;
  font-weight: 700;
  margin: 0;
  letter-spacing: 0;
}

.platform-title p {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 15px;
}

.system-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.system-card {
  appearance: none;
  border: 1px solid #dbe3ef;
  background: #ffffff;
  border-radius: 8px;
  padding: 30px 24px;
  min-height: 260px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  cursor: pointer;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.system-card:hover {
  transform: translateY(-4px);
  border-color: #93c5fd;
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.13);
}

.card-icon {
  width: 64px;
  height: 64px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  border-radius: 8px;
  margin-bottom: 18px;
}

.evaluation-card .card-icon { background: #2563eb; }
.reward-card .card-icon { background: #0f766e; }
.hr-card .card-icon { background: #7c3aed; }

.card-title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 10px;
}

.card-desc {
  min-height: 72px;
  color: #64748b;
  font-size: 15px;
  line-height: 1.65;
}

.card-action {
  margin-top: auto;
  color: #1d4ed8;
  font-size: 15px;
  font-weight: 600;
}

.admin-entry {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.admin-entry button {
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #334155;
  height: 40px;
  padding: 0 16px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

@media (max-width: 900px) {
  .platform-title {
    justify-content: flex-start;
  }

  .platform-title h1 {
    font-size: 28px;
  }

  .system-grid {
    grid-template-columns: 1fr;
  }

  .system-card {
    min-height: 220px;
  }
}
</style>
