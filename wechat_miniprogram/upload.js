/**
 * wechat_miniprogram/upload.js
 * ----------------------------
 * 微信小程序官方 miniprogram-ci 自动化上传脚本
 * 使用方式：
 * 1. 在微信公众平台 (mp.weixin.qq.com) -> 开发管理 -> 开发设置 -> 小程序代码上传
 *    生成并下载代码上传密钥，保存至本目录并命名为: private.wxe41eb3a86da4e4e8.key
 * 2. 运行: node upload.js
 */

const ci = require('miniprogram-ci');
const path = require('path');
const fs = require('fs');

const APP_ID = 'wxe41eb3a86da4e4e8';
const KEY_PATH = path.join(__dirname, `private.${APP_ID}.key`);

async function main() {
  if (!fs.existsSync(KEY_PATH)) {
    console.error(`\n⚠️ 未找到代码上传私钥: ${KEY_PATH}`);
    console.error('----------------------------------------------------');
    console.error('请前往微信公众平台后台获取并放入该文件：');
    console.error('1. 登录 https://mp.weixin.qq.com/');
    console.error('2. 进入「开发」->「开发管理」->「开发设置」');
    console.error('3. 找到「小程序代码上传」一栏，点击生成并下载上传密钥');
    console.error(`4. 将下载的 .key 文件重命名为: private.${APP_ID}.key 并放置在 wechat_miniprogram 目录下`);
    console.error('5. 建议将「IP白名单」选择关闭（或将本机公网IP填入）');
    console.error('----------------------------------------------------\n');
    process.exit(1);
  }

  console.log('🚀 正在初始化 miniprogram-ci 项目配置...');
  const project = new ci.Project({
    appid: APP_ID,
    type: 'miniProgram',
    projectPath: __dirname,
    privateKeyPath: KEY_PATH,
    ignores: ['node_modules/**', '.git/**']
  });

  console.log('📦 正在打包编译并上传代码到微信后台...');
  const uploadResult = await ci.upload({
    project,
    version: '1.0.0',
    desc: 'LingBuddy 灵宠伴侣首发版本：迪士尼微表情渲染、BLE 智能配网与移动热点流量保护',
    setting: {
      es6: true,
      minify: true,
      autoPrefixWXSS: true
    },
    onProgressUpdate: (progress) => {
      if (progress && progress.message) {
        console.log(`[CI] ${progress.message}`);
      }
    }
  });

  console.log('\n🎉 代码上传成功！详情如下：');
  console.log(uploadResult);
  console.log('\n👉 接下来请前往微信公众平台 (mp.weixin.qq.com) ->「版本管理」中查看开发版本并设为体验版或提交审核！');
}

main().catch(err => {
  console.error('\n❌ 上传异常：', err);
});
