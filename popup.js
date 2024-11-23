document.addEventListener('DOMContentLoaded', () => {
  // 标签切换
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // 移除所有active类
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('#answerSection, #configSection').forEach(section => {
        section.classList.remove('active');
      });
      
      // 添加active类到当前标签和对应section
      tab.classList.add('active');
      document.getElementById(tab.dataset.section).classList.add('active');
    });
  });

  // 开始答题按钮
  const startBtn = document.getElementById('startBtn');
  const stopBtn = document.getElementById('stopBtn');
  
  startBtn.addEventListener('click', async () => {
    try {
      const tabs = await chrome.tabs.query({active: true, currentWindow: true});
      if (!tabs[0]) {
        throw new Error('未找到活动标签页');
      }

      // 先检查URL是否匹配
      if (!tabs[0].url.includes('chaoxing.com') && !tabs[0].url.includes('edu.cn')) {
        throw new Error('请在超星学习通页面使用');
      }

      // 先注入content script
      await chrome.scripting.executeScript({
        target: { tabId: tabs[0].id },
        files: ['content.js']
      });

      // 等待一小段时间确保脚本加载
      await new Promise(resolve => setTimeout(resolve, 500));

      // 获取配置
      const config = await getConfig();

      // 发送消息到background
      chrome.runtime.sendMessage({
        action: 'startAnswering',
        tabId: tabs[0].id,
        config: config
      }, response => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError);
          document.getElementById('log').innerHTML += `<p style="color: red">错误: ${chrome.runtime.lastError.message}</p>`;
          return;
        }
        startBtn.style.display = 'none';
        stopBtn.style.display = 'block';
        document.getElementById('log').innerHTML += `<p style="color: green">开始答题...</p>`;
      });

    } catch (error) {
      console.error(error);
      document.getElementById('log').innerHTML += `<p style="color: red">错误: ${error.message}</p>`;
    }
  });

  // 停止答题按钮
  stopBtn.addEventListener('click', async () => {
    try {
      const tabs = await chrome.tabs.query({active: true, currentWindow: true});
      if (tabs[0]) {
        await chrome.tabs.sendMessage(tabs[0].id, {
          action: 'stopAnswering'
        });
      }
      stopBtn.style.display = 'none';
      startBtn.style.display = 'block';
      document.getElementById('log').innerHTML += `<p style="color: orange">停止答题</p>`;
    } catch (error) {
      console.error(error);
      document.getElementById('log').innerHTML += `<p style="color: red">错误: ${error.message}</p>`;
    }
  });

  // 在popup打开时检查答题状态
  chrome.runtime.sendMessage({action: 'getStatus'}, (status) => {
    if (status.isAnswering) {
      startBtn.style.display = 'none';
      stopBtn.style.display = 'block';
    }
  });

  // 保存配置按钮
  document.getElementById('saveBtn').addEventListener('click', () => {
    const config = {
      token: document.getElementById('token').value.trim(),
      appId: document.getElementById('appId').value.trim(),
      apiKey: document.getElementById('apiKey').value.trim(),
      apiSecret: document.getElementById('apiSecret').value.trim()
    };

    // 验证配置
    if (!config.token && (!config.appId || !config.apiKey || !config.apiSecret)) {
      alert('请填写题库Token或完整的星火API配置！');
      return;
    }

    // 保存配置
    chrome.storage.sync.set(config, () => {
      alert('配置已保存！');
    });
  });

  // 加载保存的配置
  chrome.storage.sync.get(['token', 'appId', 'apiKey', 'apiSecret'], (result) => {
    if (result.token) document.getElementById('token').value = result.token;
    if (result.appId) document.getElementById('appId').value = result.appId;
    if (result.apiKey) document.getElementById('apiKey').value = result.apiKey;
    if (result.apiSecret) document.getElementById('apiSecret').value = result.apiSecret;
  });
});

// 获取配置函数
function getConfig() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(['token', 'appId', 'apiKey', 'apiSecret'], (result) => {
      resolve(result);
    });
  });
} 