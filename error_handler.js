class ErrorHandler {
  static handleError(error, context) {
    console.error(`错误发生在 ${context}:`, error);
    
    // 发送错误通知
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'images/icon48.png',
      title: '超星学习通助手错误',
      message: `${context}: ${error.message}`
    });
    
    // 记录错误日志
    chrome.storage.local.get(['errorLogs'], (result) => {
      const logs = result.errorLogs || [];
      logs.push({
        timestamp: new Date().toISOString(),
        context,
        error: error.message
      });
      
      // 只保留最近100条错误记录
      if (logs.length > 100) {
        logs.shift();
      }
      
      chrome.storage.local.set({ errorLogs: logs });
    });
  }
} 