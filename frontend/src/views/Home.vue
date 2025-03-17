<template>
  <app-layout :active-index="activeIndex">
    <div class="hero-section">
      <div class="hero-content">
        <h1>用 AI 创造专属于孩子的绘本世界</h1>
        <p>只需几分钟，即可生成精美的儿童绘本，让孩子的想象力翱翔</p>
        <el-button type="primary" size="large" @click="goToCreateStory">开始创作</el-button>
      </div>
      <div class="hero-image">
        <img src="@/assets/hero-image.png" alt="儿童绘本示例" />
      </div>
    </div>

    <div class="features-section">
      <h2>我们的特色</h2>
      <div class="features-grid">
        <div class="feature-card">
          <el-icon size="40">
            <MagicStick />
          </el-icon>
          <h3>AI 故事生成</h3>
          <p>根据您的主题和要求，AI 自动生成精彩的儿童故事</p>
        </div>
        <div class="feature-card">
          <el-icon size="40">
            <Picture />
          </el-icon>
          <h3>精美插图生成</h3>
          <p>为每个故事场景生成精美的插图，多种艺术风格可选</p>
        </div>
        <div class="feature-card">
          <el-icon size="40">
            <Headset />
          </el-icon>
          <h3>语音朗读</h3>
          <p>自动为故事生成语音朗读，让孩子更好地沉浸在故事中</p>
        </div>
        <div class="feature-card">
          <el-icon size="40">
            <VideoPlay />
          </el-icon>
          <h3>视频生成</h3>
          <p>将故事、图片和语音合成为视频，创造更丰富的阅读体验</p>
        </div>
      </div>
    </div>

    <div class="how-it-works">
      <h2>如何使用</h2>
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <h3>选择主题和风格</h3>
          <p>选择故事主题、类型和适合的年龄段</p>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <h3>生成故事</h3>
          <p>AI 根据您的要求生成精彩的儿童故事</p>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <h3>生成插图</h3>
          <p>为故事的每个场景生成精美的插图</p>
        </div>
        <div class="step">
          <div class="step-number">4</div>
          <h3>添加语音和视频</h3>
          <p>为故事添加语音朗读，并生成视频</p>
        </div>
      </div>
    </div>
  </app-layout>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import {
  MagicStick,
  Picture,
  Headset,
  VideoPlay
} from "@element-plus/icons-vue";
import AppLayout from "@/components/AppLayout.vue";

const router = useRouter();
const activeIndex = ref("/");

const goToCreateStory = () => {
  router.push("/create-story");
};
</script>

<style scoped>
.hero-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 60px 10%;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  flex-wrap: wrap;
}

.hero-content {
  flex: 1;
  padding-right: 40px;
  min-width: 300px;
}

.hero-content h1 {
  font-size: 2.5rem;
  margin-bottom: 20px;
  color: #303133;
}

.hero-content p {
  font-size: 1.2rem;
  margin-bottom: 30px;
  color: #606266;
}

.hero-image {
  flex: 1;
  display: flex;
  justify-content: center;
  min-width: 300px;
  margin-top: 20px;
}

.hero-image img {
  max-width: 100%;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.features-section {
  padding: 60px 10%;
  text-align: center;
}

.features-section h2 {
  font-size: 2rem;
  margin-bottom: 40px;
  color: #303133;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.feature-card {
  padding: 30px;
  border-radius: 10px;
  background-color: #fff;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-card h3 {
  margin: 20px 0 10px;
  color: #303133;
}

.feature-card p {
  color: #606266;
}

.how-it-works {
  padding: 60px 10%;
  background-color: #f5f7fa;
  text-align: center;
}

.how-it-works h2 {
  font-size: 2rem;
  margin-bottom: 40px;
  color: #303133;
}

.steps {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 20px;
}

.step {
  flex: 1;
  min-width: 200px;
  padding: 20px;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.step-number {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  margin: 0 auto 15px;
  background-color: #409eff;
  color: #fff;
  border-radius: 50%;
  font-weight: bold;
}

.step h3 {
  margin-bottom: 10px;
  color: #303133;
}

.step p {
  color: #606266;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .hero-section {
    flex-direction: column;
    padding: 40px 5%;
  }

  .hero-content {
    padding-right: 0;
    text-align: center;
    margin-bottom: 30px;
  }

  .hero-content h1 {
    font-size: 2rem;
  }

  .hero-content p {
    font-size: 1rem;
  }

  .features-section,
  .how-it-works {
    padding: 40px 5%;
  }

  .features-section h2,
  .how-it-works h2 {
    font-size: 1.8rem;
  }

  .steps {
    flex-direction: column;
  }

  .step {
    width: 100%;
  }
}
</style> 