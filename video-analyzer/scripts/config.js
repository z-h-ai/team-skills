/**
 * 配置文件
 *
 * 请在此文件中配置 API Keys
 * 注意：不要将此文件提交到 Git 仓库
 */

module.exports = {
  // 火山引擎 ARK API Key
  // 获取方式：https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey
  ARK_API_KEY: process.env.ARK_API_KEY || 'ARK_API_KEY',

  // 火山引擎语音识别 API 配置
  // 获取方式：https://console.volcengine.com/speech/service/8
  SPEECH_APP_KEY: process.env.SPEECH_APP_KEY || 'SPEECH_APP_KEY',
  SPEECH_ACCESS_KEY: process.env.SPEECH_ACCESS_KEY || 'SPEECH_ACCESS_KEY',

  // ImgBB 图床 API Key
  // 获取方式：
  // 1. 注册账号：https://imgbb.com/
  // 2. 获取 API Key：https://api.imgbb.com/
  IMGBB_API_KEY: process.env.IMGBB_API_KEY || 'YOUR_IMGBB_API_KEY',

  // 微信公众号 API Key
  // 获取方式：
  // 1. 注册账号：https://wx.limyai.com/register?inviteCode=396P6F6M
  // 2. 登录后台，添加公众号（扫码绑定）
  // 3. 进入"开放平台" → "创建密钥" → "复制"
  WECHAT_API_KEY: process.env.WECHAT_API_KEY || 'YOUR_WECHAT_API_KEY',

  // API 基础地址
  ARK_API_BASE_URL: 'https://ark.cn-beijing.volces.com/api/v3',
  WECHAT_API_BASE_URL: 'https://wx.limyai.com/api/openapi',
  IMGBB_API_BASE_URL: 'https://api.imgbb.com/1/upload',

  // 临时文件目录
  TEMP_DIR: './temp',

  // 支持的图片格式
  SUPPORTED_IMAGE_FORMATS: ['.jpg', '.jpeg', '.png', '.gif', '.webp'],

  // 图片大小限制（字节）
  MAX_IMAGE_SIZE: 32 * 1024 * 1024, // 32MB
};
