import axios from 'axios'

const api = axios.create({
    baseURL: '/api',
    timeout: 600000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
api.interceptors.request.use(
    config => {
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// 响应拦截器
api.interceptors.response.use(
    response => {
        return response.data
    },
    error => {
        return Promise.reject(error)
    }
)

// 故事相关 API
export const storyApi = {
    // 生成故事
    generateStory(data) {
        return api.post('/story/generate-story', data)
    },

    // 生成图片描述
    generateImageDescriptions(data) {
        return api.post('/story/generate-image-descriptions', data)
    },

    // 获取支持的艺术风格
    getArtStyles() {
        return api.get('/story/art-styles')
    },

    // 获取支持的年龄范围
    getAgeRanges() {
        return api.get('/story/age-ranges')
    },

    // 创建故事到数据库
    createStoryInDB(data) {
        return api.post('/stories', data)
    },

    // 添加段落到数据库
    addParagraphsToDB(storyId, paragraphs) {
        return api.post(`/stories/${storyId}/paragraphs`, paragraphs)
    },

    // 添加人物到数据库
    addCharactersToDB(storyId, characters) {
        return api.post(`/stories/${storyId}/characters`, characters)
    },

    // 获取故事列表
    getStories() {
        return api.get('/stories')
    },

    // 获取故事详情
    getStory(storyId) {
        return api.get(`/stories/${storyId}`)
    }
}

// 图片相关 API
export const imageApi = {
    // 根据提示词生成图片
    generateImages(data) {
        return api.post('/image/generate-images-from-prompts', data)
    },

    // 获取支持的图片比例
    getAspectRatios() {
        return api.get('/image/aspect-ratios')
    },

    // 获取支持的图片生成模型
    getImageModels() {
        return api.get('/image/image-models')
    }
}

// 语音相关 API
export const speechApi = {
    // 生成段落音频
    generateParagraphAudio(data) {
        // 确保数据格式正确
        const requestData = {
            title: data.title || `故事_${Date.now()}`,
            paragraphs: data.paragraphs || [],
            emotion: data.emotion || 'happy'
        };

        console.log('发送语音生成请求:', requestData);
        return api.post('/speech/generate_paragraph_audio', requestData);
    },

    // 生成段落视频
    generateParagraphVideo(data) {
        // 确保数据格式正确
        const requestData = {
            image_paths: data.image_paths || [],
            audio_paths: data.audio_paths || [],
            subtitle_paths: data.subtitle_paths || [],
            output_filename: data.output_filename || `video_${Date.now()}`,
            transition_duration: data.transition_duration || 1.0,
            fade_duration: data.fade_duration || 0.5
        };

        console.log('发送视频生成请求:', requestData);
        return api.post('/speech/generate_paragraph_video', requestData);
    }
}

export default {
    storyApi,
    imageApi,
    speechApi
} 