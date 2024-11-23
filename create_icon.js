// 创建一个临时的 canvas 来生成图标
const canvas = document.createElement('canvas');
canvas.width = 48;
canvas.height = 48;
const ctx = canvas.getContext('2d');

// 绘制背景
ctx.fillStyle = '#4CAF50';
ctx.fillRect(0, 0, 48, 48);

// 绘制文字
ctx.fillStyle = 'white';
ctx.font = 'bold 24px Arial';
ctx.textAlign = 'center';
ctx.textBaseline = 'middle';
ctx.fillText('答', 24, 24);

// 将 canvas 转换为图片
const dataURL = canvas.toDataURL('image/png'); 