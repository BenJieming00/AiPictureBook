<template>
  <div class="story-editor-container">
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
        <el-button type="primary" @click="$router.push('/create-story')">创建新故事</el-button>
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

        <el-steps :active="activeStep" finish-status="success" class="steps">
          <el-step title="生成故事" description="已完成"></el-step>
          <el-step title="生成图片描述" description="为每个场景生成图片描述"></el-step>
          <el-step title="生成图片" description="根据描述生成插图"></el-step>
          <el-step title="生成语音" description="为故事添加语音朗读"></el-step>
          <el-step title="生成视频" description="合成绘本视频"></el-step>
        </el-steps>

        <!-- 步骤1：故事内容 -->
        <div v-if="activeStep === 0" class="step-content">
          <h2>故事内容</h2>
          <div class="paragraphs">
            <div v-for="(paragraph, index) in story.paragraphs" :key="index" class="paragraph">
              <h3>第 {{ index + 1 }} 页</h3>
              <p>{{ paragraph }}</p>
            </div>
          </div>

          <div class="step-actions">
            <el-button type="primary" @click="goToNextStep">下一步：生成图片描述</el-button>
          </div>
        </div>

        <!-- 步骤2：生成图片描述 -->
        <div v-if="activeStep === 1" class="step-content">
          <h2>生成图片描述</h2>

          <el-form :model="imageDescForm" label-position="top">
            <el-form-item label="图片风格">
              <el-select v-model="imageDescForm.style" placeholder="请选择图片风格" style="width: 100%">
                <el-option
                  v-for="style in artStyles"
                  :key="style.value"
                  :label="style.label"
                  :value="style.value"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-form>

          <div class="step-actions">
            <el-button @click="activeStep = 0">上一步</el-button>
            <el-button
              type="primary"
              @click="generateImageDescriptions"
              :loading="generatingDesc"
            >生成图片描述</el-button>
          </div>
        </div>

        <!-- 步骤3：生成图片 -->
        <div v-if="activeStep === 2" class="step-content">
          <h2>生成图片</h2>

          <el-form :model="imageGenForm" label-position="top">
            <el-form-item label="图片比例">
              <el-select
                v-model="imageGenForm.aspect_ratio"
                placeholder="请选择图片比例"
                style="width: 100%"
              >
                <el-option
                  v-for="ratio in aspectRatios"
                  :key="ratio.value"
                  :label="ratio.label"
                  :value="ratio.value"
                ></el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="图片生成模型">
              <el-select
                v-model="imageGenForm.image_model"
                placeholder="请选择图片生成模型"
                style="width: 100%"
              >
                <el-option
                  v-for="model in imageModels"
                  :key="model.name"
                  :label="model.display_name"
                  :value="model.name"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-form>

          <div class="image-descriptions" v-if="story.imageDescriptions">
            <div class="image-desc">
              <h3>封面</h3>
              <p>{{ story.imageDescriptions.cover_description }}</p>
            </div>

            <div
              v-for="(desc, index) in story.imageDescriptions.descriptions"
              :key="index"
              class="image-desc"
            >
              <h3>第 {{ index + 1 }} 页</h3>
              <p>{{ desc }}</p>
            </div>
          </div>

          <div class="step-actions">
            <el-button @click="activeStep = 1">上一步</el-button>
            <el-button type="primary" @click="generateImages" :loading="generatingImages">生成图片</el-button>
          </div>
        </div>

        <!-- 步骤4：生成语音 -->
        <div v-if="activeStep === 3" class="step-content">
          <h2>生成语音</h2>

          <div class="images-preview" v-if="story.images && story.images.length">
            <div v-for="(image, index) in story.images" :key="index" class="image-item">
              <h3>{{ index === 0 ? '封面' : `第 ${index} 页` }}</h3>
              <img :src="getImageUrl(image)" :alt="`页面 ${index}`" />
            </div>
          </div>

          <el-form :model="speechForm" label-position="top">
            <el-form-item label="语音情感">
              <el-select v-model="speechForm.emotion" placeholder="请选择语音情感" style="width: 100%">
                <el-option label="开心" value="happy"></el-option>
                <el-option label="悲伤" value="sad"></el-option>
                <el-option label="兴奋" value="excited"></el-option>
                <el-option label="平静" value="calm"></el-option>
                <el-option label="好奇" value="curious"></el-option>
              </el-select>
            </el-form-item>
          </el-form>

          <div class="step-actions">
            <el-button @click="activeStep = 2">上一步</el-button>
            <el-button type="primary" @click="generateAudio" :loading="generatingAudio">生成语音</el-button>
          </div>
        </div>

        <!-- 步骤5：生成视频 -->
        <div v-if="activeStep === 4" class="step-content">
          <h2>生成视频</h2>

          <div class="audio-preview" v-if="story.audio && story.audio.length">
            <div v-for="(audio, index) in story.audio" :key="index" class="audio-item">
              <h3>{{ index === 0 ? '封面' : `第 ${index} 页` }}</h3>
              <audio controls :src="getImageUrl(audio)"></audio>
            </div>
          </div>

          <el-form :model="videoForm" label-position="top">
            <el-form-item label="过渡时间（秒）">
              <el-slider
                v-model="videoForm.transition_duration"
                :min="0.5"
                :max="3"
                :step="0.1"
                show-input
              ></el-slider>
            </el-form-item>

            <el-form-item label="淡入淡出时间（秒）">
              <el-slider
                v-model="videoForm.fade_duration"
                :min="0.2"
                :max="1.5"
                :step="0.1"
                show-input
              ></el-slider>
            </el-form-item>
          </el-form>

          <div class="step-actions">
            <el-button @click="activeStep = 3">上一步</el-button>
            <el-button type="primary" @click="generateVideo" :loading="generatingVideo">生成视频</el-button>
          </div>
        </div>

        <!-- 完成步骤 -->
        <div v-if="activeStep === 5" class="step-content">
          <h2>绘本创建完成</h2>

          <div class="video-preview" v-if="story.video">
            <video controls :src="getImageUrl(story.video)" style="width: 100%"></video>
          </div>

          <div class="step-actions">
            <el-button @click="activeStep = 4">上一步</el-button>
            <el-button type="primary" @click="$router.push(`/preview/${story.id}`)">预览绘本</el-button>
            <el-button type="success" @click="$router.push('/my-stories')">返回我的绘本</el-button>
          </div>
        </div>
      </template>
    </div>

    <el-footer class="footer">
      <p>© {{ new Date().getFullYear() }} AI 儿童绘本生成平台 | 版权所有</p>
    </el-footer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storyApi, imageApi, speechApi } from "@/api";
import { ElMessage } from "element-plus";
import { storage, getImageUrl } from "@/utils";

const route = useRoute();
const router = useRouter();
const activeIndex = ref("/create-story");
const loading = ref(false);
const story = ref(null);
const activeStep = ref(0);

// 生成状态
const generatingDesc = ref(false);
const generatingImages = ref(false);
const generatingAudio = ref(false);
const generatingVideo = ref(false);

// 艺术风格选项
const artStyles = ref([
  { value: "水彩风格", label: "水彩风格" },
  { value: "扁平风格", label: "扁平风格" },
  { value: "卡通风格", label: "卡通风格" },
  { value: "水墨画风格", label: "水墨画风格" },
  { value: "动漫风格", label: "动漫风格" },
  { value: "皮克斯风格", label: "皮克斯风格" },
  { value: "宫崎骏风格", label: "宫崎骏风格" },
  { value: "童书插画风格", label: "童书插画风格" }
]);

// 图片比例选项
const aspectRatios = ref([
  { value: "1:1", label: "正方形 (1:1)" },
  { value: "4:3", label: "标准照片 (4:3)" },
  { value: "16:9", label: "宽屏 (16:9)" },
  { value: "9:16", label: "竖屏 (9:16)" }
]);

// 图片生成模型选项
const imageModels = ref([
  {
    name: "black-forest-labs/FLUX-1-schnell",
    display_name: "FLUX Schnell",
    default: true
  },
  {
    name: "black-forest-labs/FLUX-1-dev",
    display_name: "FLUX Dev",
    default: false
  }
]);

// 图片描述表单
const imageDescForm = reactive({
  style: "童书插画风格",
  age_range: ""
});

// 图片生成表单
const imageGenForm = reactive({
  aspect_ratio: "16:9",
  image_model: "black-forest-labs/FLUX-1-schnell",
  num: 1
});

// 语音生成表单
const speechForm = reactive({
  emotion: "happy"
});

// 视频生成表单
const videoForm = reactive({
  transition_duration: 1.0,
  fade_duration: 0.5
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

    // 设置表单默认值
    imageDescForm.age_range = foundStory.age_range;

    // 根据故事状态设置当前步骤
    if (foundStory.video) {
      activeStep.value = 5;
    } else if (foundStory.audio) {
      activeStep.value = 4;
    } else if (foundStory.images) {
      activeStep.value = 3;
    } else if (foundStory.imageDescriptions) {
      activeStep.value = 2;
    } else {
      activeStep.value = 0;
    }
  } else {
    ElMessage.error("未找到故事");
  }

  loading.value = false;
};

// 获取支持的艺术风格
const fetchArtStyles = async () => {
  try {
    const res = await storyApi.getArtStyles();
    if (res && res.length) {
      artStyles.value = res;
    }
  } catch (error) {
    console.error("获取艺术风格失败:", error);
  }
};

// 获取支持的图片比例
const fetchAspectRatios = async () => {
  try {
    const res = await imageApi.getAspectRatios();
    if (res && res.length) {
      aspectRatios.value = res;
    }
  } catch (error) {
    console.error("获取图片比例失败:", error);
  }
};

// 获取支持的图片生成模型
const fetchImageModels = async () => {
  try {
    const res = await imageApi.getImageModels();
    if (res && res.length) {
      imageModels.value = res;
    }
  } catch (error) {
    console.error("获取图片生成模型失败:", error);
  }
};

// 下一步
const goToNextStep = () => {
  activeStep.value++;
};

// 生成图片描述
const generateImageDescriptions = async () => {
  if (!story.value) return;

  generatingDesc.value = true;

  try {
    const params = {
      theme: story.value.theme,
      paragraphs: story.value.paragraphs,
      style: imageDescForm.style,
      age_range: imageDescForm.age_range || story.value.age_range,
      characters: story.value.characters || [],
      story_id: story.value.id
    };

    const res = await storyApi.generateImageDescriptions(params);

    // 更新故事数据
    story.value.imageDescriptions = res;

    // 保存到本地存储
    const stories = storage.get("stories") || [];
    const index = stories.findIndex(s => s.id === story.value.id);
    if (index !== -1) {
      stories[index] = story.value;
      storage.set("stories", stories);
    }

    ElMessage.success("图片描述生成成功！");
    activeStep.value = 2;
  } catch (error) {
    console.error("生成图片描述失败:", error);
    ElMessage.error("生成图片描述失败，请稍后重试");
  } finally {
    generatingDesc.value = false;
  }
};

// 生成图片
const generateImages = async () => {
  if (!story.value || !story.value.imageDescriptions) {
    ElMessage.warning("请先生成图片描述");
    return;
  }

  generatingImages.value = true;

  try {
    const params = {
      title: story.value.theme,
      cover_description: story.value.imageDescriptions.cover_description,
      descriptions: story.value.imageDescriptions.descriptions,
      aspect_ratio: imageGenForm.aspect_ratio,
      image_model: imageGenForm.image_model,
      story_id: story.value.id
    };

    const res = await imageApi.generateImages(params);

    // 更新故事数据
    story.value.images = res.image_paths;

    // 保存到本地存储
    const stories = storage.get("stories") || [];
    const index = stories.findIndex(s => s.id === story.value.id);
    if (index !== -1) {
      stories[index] = story.value;
      storage.set("stories", stories);
    }

    ElMessage.success("图片生成成功！");
    activeStep.value = 3;
  } catch (error) {
    console.error("生成图片失败:", error);
    ElMessage.error("生成图片失败，请稍后重试");
  } finally {
    generatingImages.value = false;
  }
};

// 生成语音
const generateAudio = async () => {
  if (!story.value || !story.value.paragraphs) {
    ElMessage.warning("请先生成故事");
    return;
  }

  generatingAudio.value = true;

  try {
    // 先获取故事详情，包括段落ID
    let paragraphIds = [];
    let paragraphContents = [];
    try {
      const storyDetails = await storyApi.getStory(story.value.id);
      if (storyDetails && storyDetails.paragraphs) {
        // 新的段落格式是对象数组，包含id和content
        paragraphIds = storyDetails.paragraphs.map(p => p.id);
        paragraphContents = storyDetails.paragraphs.map(p => p.content);
      } else {
        // 如果获取失败，使用本地存储的段落内容
        paragraphContents = story.value.paragraphs;
        paragraphIds = story.value.paragraphs.map(
          (_, index) => `paragraph_${index + 1}`
        );
      }
    } catch (error) {
      console.error("获取故事详情失败:", error);
      // 如果获取失败，使用本地存储的段落内容
      paragraphContents = story.value.paragraphs;
      paragraphIds = story.value.paragraphs.map(
        (_, index) => `paragraph_${index + 1}`
      );
    }

    const params = {
      title: story.value.theme,
      paragraphs: paragraphContents,
      emotion: speechForm.emotion,
      story_id: story.value.id,
      paragraph_ids: paragraphIds
    };

    const res = await speechApi.generateParagraphAudio(params);

    // 更新故事数据
    story.value.audio = res.audio_paths;
    story.value.subtitles = res.subtitle_paths;

    // 保存到本地存储
    const stories = storage.get("stories") || [];
    const index = stories.findIndex(s => s.id === story.value.id);
    if (index !== -1) {
      stories[index] = story.value;
      storage.set("stories", stories);
    }

    ElMessage.success("语音生成成功！");
    activeStep.value = 4;
  } catch (error) {
    console.error("生成语音失败:", error);
    ElMessage.error("生成语音失败，请稍后重试");
  } finally {
    generatingAudio.value = false;
  }
};

// 生成视频
const generateVideo = async () => {
  if (!story.value || !story.value.images || !story.value.audio) {
    ElMessage.warning("请先生成图片和语音");
    return;
  }

  generatingVideo.value = true;

  try {
    const params = {
      image_paths: story.value.images,
      audio_paths: story.value.audio,
      subtitle_paths: story.value.subtitles,
      output_filename: `${story.value.theme}_${story.value.id}`,
      transition_duration: videoForm.transition_duration,
      fade_duration: videoForm.fade_duration
    };

    const res = await speechApi.generateParagraphVideo(params);

    // 更新故事数据
    story.value.video = res.video_path;

    // 保存到本地存储
    const stories = storage.get("stories") || [];
    const index = stories.findIndex(s => s.id === story.value.id);
    if (index !== -1) {
      stories[index] = story.value;
      storage.set("stories", stories);
    }

    ElMessage.success("视频生成成功！");
    activeStep.value = 5;
  } catch (error) {
    console.error("生成视频失败:", error);
    ElMessage.error("生成视频失败，请稍后重试");
  } finally {
    generatingVideo.value = false;
  }
};

onMounted(() => {
  fetchStory();
  fetchArtStyles();
  fetchAspectRatios();
  fetchImageModels();
});
</script>

<style scoped>
.story-editor-container {
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

.steps {
  margin-bottom: 40px;
}

.step-content {
  margin-top: 30px;
}

.step-content h2 {
  margin-bottom: 20px;
  color: #303133;
}

.paragraphs {
  margin-bottom: 30px;
}

.paragraph {
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 8px;
  background-color: #f5f7fa;
}

.paragraph h3 {
  margin-bottom: 10px;
  color: #409eff;
}

.step-actions {
  margin-top: 30px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.image-descriptions {
  margin-top: 20px;
}

.image-desc {
  margin-bottom: 15px;
  padding: 15px;
  border-radius: 8px;
  background-color: #f5f7fa;
}

.image-desc h3 {
  margin-bottom: 10px;
  color: #409eff;
}

.images-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.image-item {
  text-align: center;
}

.image-item h3 {
  margin-bottom: 10px;
  color: #409eff;
}

.image-item img {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.audio-preview {
  margin-bottom: 30px;
}

.audio-item {
  margin-bottom: 15px;
  padding: 15px;
  border-radius: 8px;
  background-color: #f5f7fa;
}

.audio-item h3 {
  margin-bottom: 10px;
  color: #409eff;
}

.video-preview {
  margin-bottom: 30px;
}

.footer {
  padding: 20px;
  background-color: #303133;
  color: #fff;
  text-align: center;
}
</style> 