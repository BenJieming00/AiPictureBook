<template>
  <div class="story-preview-container">
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

    <div class="content" v-loading="loading">
      <div v-if="!story" class="not-found">
        <h2>未找到故事</h2>
        <el-button type="primary" @click="$router.push('/my-stories')">返回我的绘本</el-button>
      </div>

      <template v-else>
        <div class="story-header">
          <h1>{{ story.theme }}</h1>
          <div class="story-info">
            <el-tag>{{ story.story_type }}</el-tag>
            <el-tag type="success">{{ story.age_range }}</el-tag>
            <el-tag type="info">{{ story.language }}</el-tag>
          </div>
        </div>

        <div class="preview-tabs">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="绘本模式" name="book">
              <div class="book-preview">
                <div class="book-controls">
                  <el-button-group>
                    <el-button :disabled="currentPage <= 0" @click="prevPage">
                      <el-icon>
                        <ArrowLeft />
                      </el-icon>
                    </el-button>
                    <el-button :disabled="currentPage >= totalPages - 1" @click="nextPage">
                      <el-icon>
                        <ArrowRight />
                      </el-icon>
                    </el-button>
                  </el-button-group>
                  <span class="page-indicator">{{ currentPage + 1 }} / {{ totalPages }}</span>
                </div>

                <div class="book-page">
                  <div class="page-image">
                    <img :src="getImageUrl(currentImage)" :alt="`页面 ${currentPage + 1}`" />
                  </div>
                  <div class="page-text">
                    <p>{{ currentText }}</p>
                  </div>
                  <div class="page-audio" v-if="story.audio && story.audio.length">
                    <audio :src="getImageUrl(currentAudio)" controls></audio>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="视频模式" name="video" v-if="story.video">
              <div class="video-preview">
                <video :src="getImageUrl(story.video)" controls style="width: 100%"></video>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>

        <div class="preview-actions">
          <el-button @click="$router.push('/my-stories')">返回我的绘本</el-button>
          <el-button type="primary" @click="$router.push(`/story-editor/${story.id}`)">编辑绘本</el-button>
          <el-button type="success" @click="downloadStory">下载绘本</el-button>
        </div>
      </template>
    </div>

    <el-footer class="footer">
      <p>© {{ new Date().getFullYear() }} AI 儿童绘本生成平台 | 版权所有</p>
    </el-footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { storage, getImageUrl } from "@/utils";

const route = useRoute();
const router = useRouter();
const activeIndex = ref("/my-stories");
const loading = ref(false);
const story = ref(null);
const activeTab = ref("book");
const currentPage = ref(0);

// 计算总页数
const totalPages = computed(() => {
  if (!story.value || !story.value.images) return 0;
  return story.value.images.length;
});

// 当前页面图片
const currentImage = computed(() => {
  if (!story.value || !story.value.images || !story.value.images.length)
    return "";
  return story.value.images[currentPage.value];
});

// 当前页面文本
const currentText = computed(() => {
  if (!story.value || !story.value.paragraphs || !story.value.paragraphs.length)
    return "";
  // 封面页显示标题
  if (currentPage.value === 0) {
    return story.value.theme;
  }
  // 内容页显示对应段落
  return story.value.paragraphs[currentPage.value - 1] || "";
});

// 当前页面音频
const currentAudio = computed(() => {
  if (!story.value || !story.value.audio || !story.value.audio.length)
    return "";
  return story.value.audio[currentPage.value];
});

// 获取故事数据
const fetchStory = () => {
  const storyId = route.params.id;
  if (!storyId) {
    ElMessage.error("故事ID不能为空");
    return;
  }

  loading.value = true;

  // 从本地存储获取故事数据
  const stories = storage.get("stories") || [];
  const foundStory = stories.find(s => s.id === storyId);

  if (foundStory) {
    story.value = foundStory;
  } else {
    ElMessage.error("未找到故事");
  }

  loading.value = false;
};

// 上一页
const prevPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--;
  }
};

// 下一页
const nextPage = () => {
  if (currentPage.value < totalPages.value - 1) {
    currentPage.value++;
  }
};

// 下载绘本
const downloadStory = () => {
  if (!story.value) return;

  if (story.value.video) {
    // 下载视频
    const link = document.createElement("a");
    link.href = getImageUrl(story.value.video);
    link.download = `${story.value.theme}.mp4`;
    link.click();
  } else if (story.value.images && story.value.images.length) {
    // 下载图片
    ElMessage.info("正在准备下载图片...");

    // 这里可以实现批量下载图片的逻辑
    // 简单起见，这里只下载第一张图片
    const link = document.createElement("a");
    link.href = getImageUrl(story.value.images[0]);
    link.download = `${story.value.theme}_cover.jpg`;
    link.click();
  } else {
    ElMessage.warning("没有可下载的内容");
  }
};

onMounted(() => {
  fetchStory();
});
</script>

<style scoped>
.story-preview-container {
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
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
}

.not-found {
  text-align: center;
  padding: 50px 0;
}

.story-header {
  text-align: center;
  margin-bottom: 30px;
}

.story-header h1 {
  margin-bottom: 10px;
  color: #303133;
}

.story-info {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.preview-tabs {
  margin-bottom: 30px;
}

.book-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.book-controls {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.page-indicator {
  margin-left: 15px;
  color: #606266;
}

.book-page {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-image {
  width: 100%;
  margin-bottom: 20px;
}

.page-image img {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.page-text {
  width: 100%;
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  text-align: center;
}

.page-audio {
  width: 100%;
  margin-bottom: 20px;
}

.video-preview {
  width: 100%;
}

.preview-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 30px;
}

.footer {
  padding: 20px;
  background-color: #303133;
  color: #fff;
  text-align: center;
}
</style> 