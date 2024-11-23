from core.auto_answer import ChaoXingAutoAnswer
import logging

logging.basicConfig(level=logging.INFO)

def test_login():
    # 初始化自动答题系统
    auto_answer = ChaoXingAutoAnswer()
    
    # 使用您提供的账号密码测试登录
    username = "18244136008"
    password = "zql6997757"
    
    print("开始测试登录...")
    result = auto_answer.login(username, password)
    
    if result:
        print("登录成功！")
        # 测试导航到课程
        if auto_answer.login_and_navigate(username, password):
            print("成功进入课程页面！")
        else:
            print("进入课程页面失败！")
    else:
        print("登录失败！")

if __name__ == "__main__":
    test_login() 