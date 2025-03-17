<template>
  <div class="app-container">
    <el-config-provider :locale="zhCn">
      <router-view />
    </el-config-provider>
  </div>
</template>

<script setup>
import zhCn from "element-plus/es/locale/lang/zh-cn";
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  height: 100%;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

.app-container {
  height: 100vh;
  width: 100%;
}
</style> 