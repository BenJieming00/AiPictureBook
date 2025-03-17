import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: () => import('@/views/Home.vue')
    },
    {
        path: '/create-story',
        name: 'CreateStory',
        component: () => import('@/views/CreateStory.vue')
    },
    {
        path: '/story-editor/:id?',
        name: 'StoryEditor',
        component: () => import('@/views/StoryEditor.vue')
    },
    {
        path: '/preview/:id',
        name: 'StoryPreview',
        component: () => import('@/views/StoryPreview.vue')
    },
    {
        path: '/my-stories',
        name: 'MyStories',
        component: () => import('@/views/MyStories.vue')
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('@/views/NotFound.vue')
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router 