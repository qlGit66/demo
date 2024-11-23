const sharp = require('sharp');
const path = require('path');

// 创建icons目录
const fs = require('fs');
if (!fs.existsSync('icons')) {
    fs.mkdirSync('icons');
}

// 处理图片
sharp('cat.jpg')  // 替换为你的猫咪图片路径
    .resize(48, 48)  // 调整大小为48x48
    .toFile('icons/icon48.png')
    .then(() => {
        console.log('图标已创建: icons/icon48.png');
    })
    .catch(err => {
        console.error('创建图标失败:', err);
    }); 