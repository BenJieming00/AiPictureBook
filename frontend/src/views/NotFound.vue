<template>
  <div class="not-found-container">
    <el-header class="header">
      <div class="logo">
        <h1>AI 儿童绘本生成平台</h1>
      </div>
      <div class="nav">
        <el-menu mode="horizontal" :router="true" :default-active="activeIndex">
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/create-story">创建绘本</el-menu-item>
          <el-menu-item index="/my-stories">我的绘本</el-menu-item>
        </el-menu>
      </div>
    </el-header>

    <div class="content">
      <el-result icon="error" title="404" sub-title="抱歉，您访问的页面不存在">
        <template #extra>
          <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
        </template>
      </el-result>
    </div>

    <el-footer class="footer">
      <p>© {{ new Date().getFullYear() }} AI 儿童绘本生成平台 | 版权所有</p>
    </el-footer>
  </div>
</template>

<script setup>
import { ref } from "vue";

const activeIndex = ref("/");
</script>

<style scoped>
.not-found-container {
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
}

.logo h1 {
  font-size: 1.5rem;
  color: #409eff;
  margin: 0;
}

.content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

.footer {
  padding: 20px;
  background-color: #303133;
  color: #fff;
  text-align: center;
}
</style> 