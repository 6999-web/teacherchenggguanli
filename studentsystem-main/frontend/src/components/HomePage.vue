<template>
  <div class="home-container">
    <section class="login-shell">
      <div class="platform-title">
        <div class="icon-box">
          <n-icon size="32" class="title-icon">
            <IconSchool :size="32" />
          </n-icon>
        </div>
        <div>
          <h1>工作奖励体系</h1>
          <p>请选择登录入口</p>
        </div>
      </div>

      <div class="login-options">
        <button class="login-card" type="button" @click="goToStudentLogin">
          <span class="card-icon">
            <IconUser :size="34" />
          </span>
          <span class="card-title">教师端登录</span>
          <span class="card-desc">提交教学成果材料，查看审核与奖励认定</span>
          <span class="card-action">进入教师端</span>
        </button>

        <button class="login-card admin-card" type="button" @click="goToAdminLogin">
          <span class="card-icon">
            <IconShieldCheck :size="34" />
          </span>
          <span class="card-title">管理端登录</span>
          <span class="card-desc">审核成果材料，管理奖励认定流程</span>
          <span class="card-action">进入管理端</span>
        </button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import {
  IconUser,
  IconSchool,
  IconShieldCheck
} from '@tabler/icons-vue'

const router = useRouter()
const adminLoginUrl = import.meta.env.VITE_ADMIN_LOGIN_URL || 'http://localhost:5005/admin/login'

const goToStudentLogin = () => {
  router.push('/student/login')
}

const goToAdminLogin = () => {
  window.location.href = adminLoginUrl
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  width: 100%;
  background: #333f89;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
  box-sizing: border-box;
}

.login-shell {
  width: min(920px, 100%);
}

.platform-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin-bottom: 28px;
  color: #ffffff;
}

.icon-box {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 52px;
  height: 52px;
  background-color: #1890ff;
  border-radius: 6px;
  box-shadow: 0 10px 22px rgba(24, 144, 255, 0.28);
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
  color: rgba(255, 255, 255, 0.82);
  font-size: 15px;
}

.login-options {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 22px;
}

.login-card {
  appearance: none;
  border: 1px solid rgba(24, 144, 255, 0.16);
  background: rgba(255, 255, 255, 0.94);
  border-radius: 8px;
  padding: 34px 28px;
  min-height: 260px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  box-shadow: 0 12px 34px rgba(15, 23, 42, 0.12);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.login-card:hover {
  transform: translateY(-4px);
  border-color: rgba(24, 144, 255, 0.4);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.16);
}

.card-icon {
  width: 68px;
  height: 68px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  border-radius: 8px;
  margin-bottom: 18px;
}

.admin-card .card-icon {
  background: linear-gradient(135deg, #0f766e, #134e4a);
}

.card-title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 10px;
}

.card-desc {
  min-height: 44px;
  color: #64748b;
  font-size: 15px;
  line-height: 1.6;
}

.card-action {
  margin-top: auto;
  color: #096dd9;
  font-size: 15px;
  font-weight: 600;
}

.admin-card .card-action {
  color: #0f766e;
}

@media (max-width: 720px) {
  .platform-title {
    justify-content: flex-start;
  }

  .platform-title h1 {
    font-size: 28px;
  }

  .login-options {
    grid-template-columns: 1fr;
  }

  .login-card {
    min-height: 220px;
  }
}
</style>
