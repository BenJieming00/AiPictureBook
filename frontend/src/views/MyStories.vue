<template>
  <app-layout :active-index="activeIndex">
    <div class="content">
      <h1>我的绘本</h1>

      <div class="stories-empty" v-if="!stories.length">
        <el-empty description="您还没有创建任何绘本">
          <el-button type="primary" @click="$router.push('/create-story')">创建新绘本</el-button>
        </el-empty>
      </div>

      <div class="stories-grid" v-else>
        <el-card v-for="story in stories" :key="story.id" class="story-card">
          <div class="story-cover">
            <img
              v-if="story.images && story.images.length"
              :src="getImageUrl(story.images[0])"
              alt="封面"
            />
            <div v-else class="no-cover">
              <el-icon size="40">
                <Picture />
              </el-icon>
            </div>
          </div>

          <div class="story-info">
            <h2>{{ story.theme }}</h2>
            <div class="story-tags">
              <el-tag size="small">{{ story.story_type }}</el-tag>
              <el-tag size="small" type="success">{{ story.age_range }}</el-tag>
              <el-tag size="small" type="info">{{ story.language }}</el-tag>
            </div>
            <p class="story-date">创建时间：{{ formatDate(story.createdAt) }}</p>
            <p class="story-progress">
              进度：
              <el-progress
                :percentage="calculateProgress(story)"
                :status="story.video ? 'success' : ''"
              ></el-progress>
            </p>
          </div>

          <div class="story-actions">
            <el-button-group class="action-buttons">
              <el-button
                type="primary"
                @click="$router.push(`/story-editor/${story.id}`)"
              >{{ story.video ? '查看' : '继续编辑' }}</el-button>
              <el-button
                v-if="story.video"
                type="success"
                @click="$router.push(`/preview/${story.id}`)"
              >预览</el-button>
              <el-button type="danger" @click="confirmDelete(story)">删除</el-button>
            </el-button-group>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <el-dialog v-model="deleteDialogVisible" title="确认删除" width="30%">
      <span>确定要删除绘本"{{ storyToDelete ? storyToDelete.theme : '' }}"吗？此操作不可恢复。</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteStory">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </app-layout>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { storage, formatDate, getImageUrl } from "@/utils";
import { Picture } from "@element-plus/icons-vue";
import AppLayout from "@/components/AppLayout.vue";

const router = useRouter();
const activeIndex = ref("/my-stories");
const stories = ref([]);
const deleteDialogVisible = ref(false);
const storyToDelete = ref(null);

// 获取所有故事
const fetchStories = () => {
  const storedStories = storage.get("stories") || [];
  stories.value = storedStories.sort(
    (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
  );
};

// 计算故事完成进度
const calculateProgress = story => {
  let progress = 0;

  if (story.paragraphs) progress += 20;
  if (story.imageDescriptions) progress += 20;
  if (story.images) progress += 20;
  if (story.audio) progress += 20;
  if (story.video) progress += 20;

  return progress;
};

// 确认删除
const confirmDelete = story => {
  storyToDelete.value = story;
  deleteDialogVisible.value = true;
};

// 删除故事
const deleteStory = () => {
  if (!storyToDelete.value) return;

  const storedStories = storage.get("stories") || [];
  const updatedStories = storedStories.filter(
    s => s.id !== storyToDelete.value.id
  );
  storage.set("stories", updatedStories);

  stories.value = updatedStories;
  deleteDialogVisible.value = false;
  storyToDelete.value = null;

  ElMessage.success("绘本已删除");
};

onMounted(() => {
  fetchStories();
});
</script>

<style scoped>
.content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.content h1 {
  margin-bottom: 30px;
  text-align: center;
  color: #303133;
}

.stories-empty {
  margin-top: 50px;
}

.stories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
}

.story-card {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.story-cover {
  height: 200px;
  overflow: hidden;
  border-radius: 4px;
  margin-bottom: 15px;
}

.story-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-cover {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  color: #909399;
}

.story-info {
  flex: 1;
}

.story-info h2 {
  margin: 0 0 10px;
  font-size: 1.2rem;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.story-tags {
  display: flex;
  gap: 5px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.story-date {
  font-size: 0.9rem;
  color: #909399;
  margin-bottom: 10px;
}

.story-progress {
  margin-bottom: 15px;
}

.story-actions {
  margin-top: 15px;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .content {
    padding: 20px 15px;
  }

  .content h1 {
    font-size: 1.8rem;
    margin-bottom: 20px;
  }

  .stories-grid {
    grid-template-columns: 1fr;
  }

  .story-cover {
    height: 180px;
  }

  .action-buttons {
    display: flex;
    flex-direction: column;
    width: 100%;
  }

  .action-buttons .el-button {
    margin-left: 0 !important;
    margin-top: 8px;
    width: 100%;
  }

  .action-buttons .el-button:first-child {
    margin-top: 0;
  }
}
</style> 