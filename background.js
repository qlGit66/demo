let isEnabled = false;

// 使用 chrome.storage.local 来存储状态
let answeringStatus = {
  isAnswering: false,
  tabId: null,
  config: null
};

// 初始化状态
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    answeringStatus: {
      isAnswering: false,
      tabId: null,
      config: null
    }
  });
});

// 监听消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'startAnswering') {
    // 更新状态
    answeringStatus = {
      isAnswering: true,
      tabId: request.tabId,
      config: request.config
    };
    
    // 保存状态
    chrome.storage.local.set({ answeringStatus });
    
    // 发送消息到content script
    chrome.tabs.sendMessage(request.tabId, {
      action: 'startAnswering',
      config: request.config
    }).catch(error => console.error('发送消息失败:', error));
    
    sendResponse({success: true});
  } 
  else if (request.action === 'stopAnswering') {
    if (answeringStatus.tabId) {
      chrome.tabs.sendMessage(answeringStatus.tabId, {
        action: 'stopAnswering'
      }).catch(error => console.error('发送停止消息失败:', error));
    }
    
    // 更新状态
    answeringStatus = {
      isAnswering: false,
      tabId: null,
      config: null
    };
    
    // 保存状态
    chrome.storage.local.set({ answeringStatus });
    
    sendResponse({success: true});
  }
  else if (request.action === 'getStatus') {
    sendResponse(answeringStatus);
  }
  
  return true; // 保持消息通道开启
});

// 监听标签页关闭
chrome.tabs.onRemoved.addListener((tabId) => {
  if (tabId === answeringStatus.tabId) {
    answeringStatus = {
      isAnswering: false,
      tabId: null,
      config: null
    };
    chrome.storage.local.set({ answeringStatus });
  }
});

// 监听标签页更新
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (tabId === answeringStatus.tabId && changeInfo.status === 'complete') {
    // 页面加载完成后，如果正在答题，则重新发送开始消息
    if (answeringStatus.isAnswering) {
      chrome.tabs.sendMessage(tabId, {
        action: 'startAnswering',
        config: answeringStatus.config
      }).catch(error => console.error('重新发送开始消息失败:', error));
    }
  }
});

// 恢复状态
chrome.runtime.onStartup.addListener(() => {
  chrome.storage.local.get(['answeringStatus'], (result) => {
    if (result.answeringStatus) {
      answeringStatus = result.answeringStatus;
    }
  });
});

chrome.runtime.onSuspend.addListener(function() {
  if (answeringStatus.isAnswering && answeringStatus.tabId) {
    // 在扩展即将被挂起时保存状态
    chrome.storage.local.set({
      answeringStatus: answeringStatus
    });
  }
});

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({ isEnabled: false });
});

chrome.tabs.onRemoved.addListener((tabId) => {
  if (tabId === answeringStatus.tabId) {
    answeringStatus = {
      isAnswering: false,
      tabId: null,
      config: null
    };
  }
}); 