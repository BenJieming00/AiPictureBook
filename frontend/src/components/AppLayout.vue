<template>
  <div class="app-layout">
    <el-header class="header">
      <div class="logo">
        <h1>AI 儿童绘本生成平台</h1>
      </div>

      <!-- 桌面导航 -->
      <div class="nav desktop-nav">
        <el-menu mode="horizontal" :router="true" :default-active="activeIndex">
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/create-story">创建绘本</el-menu-item>
          <el-menu-item index="/my-stories">我的绘本</el-menu-item>
        </el-menu>
      </div>

      <!-- 移动端导航按钮 -->
      <div class="mobile-nav-toggle" @click="mobileMenuVisible = !mobileMenuVisible">
        <el-icon size="24">
          <Menu />
        </el-icon>
      </div>
    </el-header>

    <!-- 移动端导航菜单 -->
    <div class="mobile-nav" v-show="mobileMenuVisible">
      <el-menu :default-active="activeIndex" @select="handleSelect">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/create-story">创建绘本</el-menu-item>
        <el-menu-item index="/my-stories">我的绘本</el-menu-item>
      </el-menu>
    </div>

    <div class="main-content">
      <slot></slot>
    </div>

    <el-footer class="footer">
      <p>© {{ new Date().getFullYear() }} AI 儿童绘本生成平台 | 版权所有</p>
    </el-footer>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { Menu } from "@element-plus/icons-vue";

const props = defineProps({
  activeIndex: {
    type: String,
    default: "/"
  }
});

const router = useRouter();
const mobileMenuVisible = ref(false);

const handleSelect = index => {
  router.push(index);
  mobileMenuVisible.value = false;
};
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  background-color: #fff;
  z-index: 100;
}

.logo h1 {
  font-size: 1.5rem;
  color: #409eff;
  margin: 0;
}

.mobile-nav-toggle {
  display: none;
  cursor: pointer;
}

.mobile-nav {
  display: none;
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  background-color: #fff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  z-index: 99;
}

.main-content {
  flex: 1;
}

.footer {
  padding: 20px;
  background-color: #303133;
  color: #fff;
  text-align: center;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .desktop-nav {
    display: none;
  }

  .mobile-nav-toggle {
    display: block;
  }

  .mobile-nav {
    display: block;
  }

  .logo h1 {
    font-size: 1.2rem;
  }
}
</style> 