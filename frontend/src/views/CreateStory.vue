<template>
  <app-layout :active-index="activeIndex">
    <div class="content">
      <h1>创建新绘本</h1>

      <el-form :model="storyForm" label-position="top" :rules="rules" ref="storyFormRef">
        <el-form-item label="故事主题" prop="theme">
          <el-input v-model="storyForm.theme" placeholder="例如：太空探险、海底世界、森林冒险等"></el-input>
        </el-form-item>

        <el-form-item label="故事类型" prop="story_type">
          <el-select v-model="storyForm.story_type" placeholder="请选择故事类型" style="width: 100%">
            <el-option
              v-for="type in storyTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            ></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="适合年龄段" prop="age_range">
          <el-select v-model="storyForm.age_range" placeholder="请选择适合的年龄段" style="width: 100%">
            <el-option
              v-for="age in ageRanges"
              :key="age.value"
              :label="age.label"
              :value="age.value"
            ></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="故事语言" prop="language">
          <el-radio-group v-model="storyForm.language">
            <el-radio label="中文">中文</el-radio>
            <el-radio label="英文">英文</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="故事字数" prop="word_count">
          <el-slider v-model="storyForm.word_count" :min="500" :max="5000" :step="100" show-input></el-slider>
        </el-form-item>

        <el-form-item label="绘本页数" prop="pages">
          <el-slider v-model="storyForm.pages" :min="5" :max="20" :step="1" show-input></el-slider>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="generateStory" :loading="loading">生成故事</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </app-layout>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { storyApi } from "@/api";
import { ElMessage } from "element-plus";
import { storage, generateUUID } from "@/utils";
import AppLayout from "@/components/AppLayout.vue";

const router = useRouter();
const activeIndex = ref("/create-story");
const storyFormRef = ref(null);
const loading = ref(false);

// 故事类型选项
const storyTypes = ref([
  { value: "冒险", label: "冒险" },
  { value: "奇幻", label: "奇幻" },
  { value: "教育", label: "教育" },
  { value: "寓言", label: "寓言" },
  { value: "科幻", label: "科幻" },
  { value: "悬疑", label: "悬疑" },
  { value: "友谊", label: "友谊" },
  { value: "自然", label: "自然" }
]);

// 年龄段选项
const ageRanges = ref([
  { value: "0-3岁", label: "0-3岁" },
  { value: "3-8岁", label: "3-8岁" },
  { value: "8-14岁", label: "8-14岁" }
]);

// 表单数据
const storyForm = reactive({
  theme: "",
  story_type: "",
  age_range: "",
  language: "中文",
  word_count: 1000,
  pages: 10
});

// 表单验证规则
const rules = {
  theme: [
    { required: true, message: "请输入故事主题", trigger: "blur" },
    { min: 2, max: 50, message: "长度在 2 到 50 个字符", trigger: "blur" }
  ],
  story_type: [
    { required: true, message: "请选择故事类型", trigger: "change" }
  ],
  age_range: [
    { required: true, message: "请选择适合的年龄段", trigger: "change" }
  ]
};

// 获取支持的年龄范围
const fetchAgeRanges = async () => {
  try {
    const res = await storyApi.getAgeRanges();
    if (res && res.length) {
      ageRanges.value = res;
    }
  } catch (error) {
    console.error("获取年龄范围失败:", error);
  }
};

// 生成故事
const generateStory = async () => {
  if (!storyFormRef.value) return;

  await storyFormRef.value.validate(async valid => {
    if (valid) {
      loading.value = true;
      try {
        // 生成故事内容
        const res = await storyApi.generateStory(storyForm);

        // 创建故事到数据库
        const dbRes = await storyApi.createStoryInDB(storyForm);
        const storyId = dbRes.id;

        // 添加段落到数据库
        await storyApi.addParagraphsToDB(storyId, res.paragraphs);

        // 添加人物到数据库
        if (res.characters && res.characters.length > 0) {
          await storyApi.addCharactersToDB(storyId, res.characters);
        }

        // 保存故事数据到本地存储
        const storyData = {
          id: storyId,
          ...storyForm,
          paragraphs: res.paragraphs,
          characters: res.characters,
          createdAt: new Date().toISOString()
        };

        // 获取已有的故事列表
        const stories = storage.get("stories") || [];
        stories.push(storyData);
        storage.set("stories", stories);

        // 跳转到故事编辑页面
        router.push(`/story-editor/${storyData.id}`);
      } catch (error) {
        console.error("生成故事失败:", error);
        ElMessage.error("生成故事失败，请稍后重试");
      } finally {
        loading.value = false;
      }
    }
  });
};

// 重置表单
const resetForm = () => {
  if (storyFormRef.value) {
    storyFormRef.value.resetFields();
  }
};

onMounted(() => {
  fetchAgeRanges();
});
</script>

<style scoped>
.content {
  flex: 1;
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.content h1 {
  margin-bottom: 30px;
  text-align: center;
  color: #303133;
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

  .el-form-item {
    margin-bottom: 15px;
  }
}
</style> 