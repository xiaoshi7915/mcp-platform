import moment from 'moment'

// 设置中文语言环境
moment.locale('zh-cn')

/**
 * 格式化日期时间
 * @param {string|Date} date 日期对象或日期字符串
 * @param {string} format 格式化模式，默认为 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return '无日期'
  return moment(date).format(format)
}

/**
 * 获取相对时间（如：几分钟前，几小时前）
 * @param {string|Date} date 日期对象或日期字符串
 * @returns {string} 相对时间
 */
export function fromNow(date) {
  if (!date) return '无日期'
  return moment(date).fromNow()
}

/**
 * 格式化数字
 * @param {number} num 数字
 * @param {number} digits 小数位数
 * @returns {string} 格式化后的数字
 */
export function formatNumber(num, digits = 2) {
  if (num === undefined || num === null) return '0'
  return Number(num).toFixed(digits)
}

/**
 * 格式化文件大小
 * @param {number} bytes 字节数
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 格式化持续时间
 * @param {number} seconds 秒数
 * @returns {string} 格式化后的持续时间
 */
export function formatDuration(seconds) {
  if (!seconds) return '0秒'
  
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes % 60}分钟${seconds % 60}秒`
  } else if (minutes > 0) {
    return `${minutes}分钟${seconds % 60}秒`
  } else {
    return `${seconds}秒`
  }
}

/**
 * 截断文本，添加省略号
 * @param {string} text 文本
 * @param {number} length 最大长度
 * @returns {string} 截断后的文本
 */
export function truncate(text, length = 20) {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
} 