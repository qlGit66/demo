// 添加调试函数
const DEBUG = true;
function debugLog(message, data = null) {
  if (DEBUG) {
    console.log(`[Debug] ${message}`, data || '');
  }
}

// 添加随机延时函数
function randomDelay(min = 1000, max = 3000) {
  const delay = Math.floor(Math.random() * (max - min + 1)) + min;
  return new Promise(resolve => setTimeout(resolve, delay));
}

// 添加初始化消息监听器
console.log('Content script loaded');

// 确保消息监听器只添加一次
if (!window.hasMessageListener) {
  window.hasMessageListener = true;
  
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Received message:', request);
    try {
      if (request.action === 'startAnswering') {
        startAutoProcess(request.config);
        sendResponse({success: true});
      } else if (request.action === 'stopAnswering') {
        isAnswering = false;
        sendResponse({success: true});
      }
    } catch (error) {
      console.error('Message handling error:', error);
      sendResponse({success: false, error: error.message});
    }
    return true;  // 保持消息通道开启
  });
}

async function getContentFrame() {
  debugLog('开始获取内容框架');
  
  return new Promise((resolve) => {
    // 直接在当前文档中查找元素
    const checkDocument = () => {
      try {
        // 检查当前文档是否包含题目元素
        const questions = document.querySelectorAll('.TiMu');
        if (questions.length > 0) {
          debugLog('在当前文档中找到题目');
          return resolve(document);
        }

        // 如果当前文档没有题目，检查所有iframe
        const frames = Array.from(document.getElementsByTagName('iframe'));
        for (const frame of frames) {
          try {
            const frameDoc = frame.contentDocument || frame.contentWindow.document;
            const frameQuestions = frameDoc.querySelectorAll('.TiMu');
            if (frameQuestions.length > 0) {
              debugLog('在iframe中找到题目');
              return resolve(frameDoc);
            }
          } catch (e) {
            debugLog('访问iframe失败:', e);
          }
        }

        // 如果还没找到，继续尝试
        setTimeout(checkDocument, 500);
      } catch (error) {
        debugLog('检查文档出错:', error);
        setTimeout(checkDocument, 500);
      }
    };

    checkDocument();
  });
}

// 修改等待元素函数
async function waitForElement(selector, timeout = 10000) {
  debugLog(`等待元素: ${selector}`);
  
  return new Promise((resolve) => {
    const startTime = Date.now();
    
    const checkElement = async () => {
      const doc = await getContentFrame();
      const element = doc.querySelector(selector);
      
      debugLog('查找元素结果:', {
        selector,
        found: !!element,
        timeElapsed: Date.now() - startTime
      });
      
      if (element) {
        return resolve(element);
      }
      
      if (Date.now() - startTime > timeout) {
        debugLog(`等待元素超时: ${selector}`);
        return resolve(null);
      }
      
      setTimeout(checkElement, 100);
    };
    
    checkElement();
  });
}

// 修改获取题目信息函数
async function getQuestionInfo(questionElement) {
  debugLog('开始获取题目信息');
  
  try {
    // 记录DOM结构
    debugLog('题目元素:', {
      html: questionElement.outerHTML,
      selectors: {
        title: !!questionElement.querySelector('.Zy_TItle .clearfix'),
        options: questionElement.querySelectorAll('.Zy_ulTop li').length,
        inputs: {
          radio: questionElement.querySelectorAll('input[type="radio"]').length,
          checkbox: questionElement.querySelectorAll('input[type="checkbox"]').length,
          text: questionElement.querySelectorAll('input[type="text"]').length
        }
      }
    });

    // 获取题目文本
    const questionText = questionElement.querySelector('.Zy_TItle .clearfix')?.textContent.trim();
    debugLog('题目文本:', questionText);

    // 获取选项
    const options = Array.from(questionElement.querySelectorAll('.Zy_ulTop li'))
      .map(opt => {
        const data = {
          text: opt.textContent.trim(),
          element: opt,
          value: opt.querySelector('input')?.value || '',
          type: opt.querySelector('input')?.type || 'unknown'
        };
        debugLog('选项数据:', data);
        return data;
      })
      .filter(opt => opt.text);

    // 判断题目类型
    let type = 'unknown';
    if (questionElement.querySelector('input[type="radio"]')) {
      type = 'single';
    } else if (questionElement.querySelector('input[type="checkbox"]')) {
      type = 'multiple';
    } else if (questionElement.querySelector('input[type="text"]')) {
      type = 'fill';
    } else if (questionText?.includes('判断') || options.length === 2) {
      type = 'judge';
    }
    
    debugLog('题目类型:', type);

    return {
      type,
      question: questionText,
      options,
      element: questionElement
    };
  } catch (error) {
    console.error('获取题目信息失败:', error);
    debugLog('题目信息错误:', error);
    return null;
  }
}

// 修改填写答案函数
async function fillAnswer(questionInfo, answer) {
  debugLog('开始填写答案:', { questionInfo, answer });
  
  try {
    const { type, options, element } = questionInfo;
    
    switch (type) {
      case 'single':
      case 'multiple':
        if (typeof answer === 'string' && answer.match(/[A-D]/)) {
          const answers = answer.split('');
          for (const ans of answers) {
            const index = ans.charCodeAt(0) - 65;
            if (options[index]) {
              debugLog(`点击选项: ${ans}`, options[index]);
              const input = options[index].element.querySelector('input');
              if (input) {
                input.click();
                await randomDelay(500, 1000);
              }
            }
          }
          return true;
        }
        break;

      case 'judge':
        const isCorrect = answer === '正确' || answer === '√';
        const judgeOptions = element.querySelectorAll('input[type="radio"]');
        if (judgeOptions.length >= 2) {
          debugLog('判断题选择:', isCorrect ? '正确' : '错误');
          judgeOptions[isCorrect ? 0 : 1].click();
          return true;
        }
        break;

      case 'fill':
        const input = element.querySelector('input[type="text"]');
        if (input) {
          debugLog('填空题填写:', answer);
          input.value = answer;
          input.dispatchEvent(new Event('input', { bubbles: true }));
          input.dispatchEvent(new Event('change', { bubbles: true }));
          return true;
        }
        break;
    }
    
    debugLog('答案填写失败');
    return false;
  } catch (error) {
    console.error('填写答案失败:', error);
    debugLog('答案填写错误:', error);
    return false;
  }
}

// 添加启动答题流程函数
async function startAutoProcess(config) {
  debugLog('开始自动答题流程', config);
  
  try {
    while (true) {
      // 检查答题状态
      const status = await new Promise(resolve => {
        chrome.runtime.sendMessage({action: 'getStatus'}, resolve);
      });
      
      if (!status.isAnswering) {
        debugLog('答题已停止');
        break;
      }

      // 等待iframe加载
      debugLog('等待iframe加载...');
      const doc = await getContentFrame();
      if (!doc) {
        debugLog('未找到iframe，等待重试');
        await randomDelay(2000, 3000);
        continue;
      }

      // 查找答题按钮并点击
      const answerBtn = doc.querySelector('button:contains("答题"), .ans-btn');
      if (answerBtn) {
        debugLog('找到答题按钮，点击进入答题');
        answerBtn.click();
        await randomDelay(1000, 2000);
      }

      // 查找题目
      const questions = doc.querySelectorAll('.TiMu');
      debugLog('找到题目数量:', questions.length);

      if (!questions.length) {
        debugLog('未找到题目，继续查找');
        await randomDelay(2000, 3000);
        continue;
      }

      // 处理每个题目
      for (const question of questions) {
        try {
          // 获取题目信息
          const questionInfo = await getQuestionInfo(question);
          if (!questionInfo) {
            debugLog('获取题目信息失败，跳过');
            continue;
          }

          // 获取答案
          let answer = null;
          if (config.token) {
            debugLog('尝试从题库获取答案');
            answer = await queryAnswerFromDatabase(questionInfo, config.token);
          }
          
          if (!answer && config.appId) {
            debugLog('从题库未获取到答案，尝试使用AI');
            answer = await getAIAnswer(questionInfo, config);
          }

          if (!answer) {
            debugLog('未能获取答案，跳过此题');
            continue;
          }

          // 填写答案
          debugLog('开始填写答案');
          await fillAnswer(questionInfo, answer);
          await randomDelay(1000, 2000);

        } catch (error) {
          console.error('处理题目失败:', error);
          debugLog('题目处理出错:', error);
        }
      }

      // 提交答案
      debugLog('尝试提交答案');
      const submitted = await submitAnswer();
      if (submitted) {
        debugLog('答案提交成功');
      } else {
        debugLog('答案提交失败');
      }

      // 查找下一页
      debugLog('查找下一页');
      const hasNext = await goToNext();
      if (!hasNext) {
        debugLog('没有下一页，答题完成');
        break;
      }

      await randomDelay(2000, 3000);
    }
  } catch (error) {
    console.error('答题流程出错:', error);
    debugLog('答题流程错误:', error);
  }
}

// 添加题库查询函数
async function queryAnswerFromDatabase(questionInfo, token) {
  debugLog('开始查询题库', questionInfo);
  try {
    const response = await fetch('https://your-api-endpoint/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        question: questionInfo.question,
        type: questionInfo.type,
        options: questionInfo.options.map(opt => opt.text)
      })
    });

    if (!response.ok) {
      throw new Error('题库请求失败');
    }

    const data = await response.json();
    debugLog('题库返回数据:', data);
    return data.answer;
  } catch (error) {
    console.error('题库查询失败:', error);
    debugLog('题库查询错误:', error);
    return null;
  }
}

// 添加AI答案获取函数
async function getAIAnswer(questionInfo, config) {
  debugLog('开始请求AI答案', questionInfo);
  try {
    // 构建提示词
    let prompt = `请回答以下题目：${questionInfo.question}\n`;
    if (questionInfo.options.length > 0) {
      prompt += '选项：\n';
      questionInfo.options.forEach((opt, index) => {
        prompt += `${String.fromCharCode(65 + index)}. ${opt.text}\n`;
      });
    }
    prompt += `\n题型：${questionInfo.type}`;

    const response = await fetch('https://your-ai-endpoint/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'APPID': config.appId,
        'APIKey': config.apiKey,
        'APISecret': config.apiSecret
      },
      body: JSON.stringify({ prompt })
    });

    if (!response.ok) {
      throw new Error('AI请求失败');
    }

    const data = await response.json();
    debugLog('AI返回数据:', data);
    return parseAIResponse(data.answer, questionInfo.type);
  } catch (error) {
    console.error('AI回答失败:', error);
    debugLog('AI请求错误:', error);
    return null;
  }
}

// 添加AI响应解析函数
function parseAIResponse(aiResponse, questionType) {
  debugLog('解析AI响应:', { aiResponse, questionType });
  try {
    switch (questionType) {
      case 'single':
        return aiResponse.match(/[A-D]/)?.[0];
      case 'multiple':
        return aiResponse.match(/[A-D]/g) || [];
      case 'judge':
        return aiResponse.includes('正确') || aiResponse.includes('√') ? '正确' : '错误';
      case 'fill':
        return aiResponse.trim();
      default:
        return null;
    }
  } catch (error) {
    console.error('解析AI响应失败:', error);
    debugLog('响应解析错误:', error);
    return null;
  }
}

// ... 其他代码保持不变 ... 