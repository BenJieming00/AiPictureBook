// 格式化日期
export function formatDate(date, fmt = 'YYYY-MM-DD HH:mm:ss') {
    if (!date) return ''
    if (typeof date === 'string') {
        date = new Date(date.replace(/-/g, '/'))
    }
    if (typeof date === 'number') {
        date = new Date(date)
    }

    const o = {
        'M+': date.getMonth() + 1,
        'D+': date.getDate(),
        'H+': date.getHours(),
        'm+': date.getMinutes(),
        's+': date.getSeconds(),
        'q+': Math.floor((date.getMonth() + 3) / 3),
        'S': date.getMilliseconds()
    }

    if (/(Y+)/.test(fmt)) {
        fmt = fmt.replace(RegExp.$1, (date.getFullYear() + '').substr(4 - RegExp.$1.length))
    }

    for (const k in o) {
        if (new RegExp('(' + k + ')').test(fmt)) {
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length === 1) ? (o[k]) : (('00' + o[k]).substr(('' + o[k]).length)))
        }
    }

    return fmt
}

// 防抖函数
export function debounce(fn, delay) {
    let timer = null
    return function () {
        const context = this
        const args = arguments
        clearTimeout(timer)
        timer = setTimeout(() => {
            fn.apply(context, args)
        }, delay)
    }
}

// 节流函数
export function throttle(fn, delay) {
    let lastTime = 0
    return function () {
        const context = this
        const args = arguments
        const nowTime = Date.now()
        if (nowTime - lastTime > delay) {
            fn.apply(context, args)
            lastTime = nowTime
        }
    }
}

// 生成唯一ID
export function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0
        const v = c === 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
    })
}

// 本地存储封装
export const storage = {
    set(key, value) {
        if (typeof value === 'object') {
            value = JSON.stringify(value)
        }
        localStorage.setItem(key, value)
    },
    get(key) {
        const value = localStorage.getItem(key)
        try {
            return JSON.parse(value)
        } catch (e) {
            return value
        }
    },
    remove(key) {
        localStorage.removeItem(key)
    },
    clear() {
        localStorage.clear()
    }
}

// 处理图片路径
export function getImageUrl(path) {
    // 如果是完整的URL，直接返回
    if (path && (path.startsWith('http://') || path.startsWith('https://'))) {
        return path
    }

    // 如果是以/static开头的路径，转换为后端API地址
    if (path && path.startsWith('/static/')) {
        // 开发环境下，使用代理
        return `/api${path}`
    }

    return path
} 