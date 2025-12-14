from loguru import logger
import time


class LoginAction:
    def __init__(self, service):
        """初始化登录操作"""
        self.service = service
        self.page = service.page
        self.login_url = "https://www.xiaohongshu.com/explore"
    
    def check_login_status(self):
        """检查登录状态"""
        try:
            # 导航到主页
            self.page.goto(self.login_url)
            time.sleep(2)
            
            # 检查是否存在登录按钮或用户头像来判断登录状态
            try:
                # 尝试查找登录按钮
                self.page.wait_for_selector('button:has-text("登录")', timeout=2000)
                logger.info("未登录")
                return {
                    "is_logged_in": False,
                    "message": "未登录"
                }
            except:
                # 检查是否存在用户头像或登录后的元素
                try:
                    # 尝试查找用户头像
                    self.page.wait_for_selector('.avatar', timeout=2000)
                    logger.info("已登录")
                    return {
                        "is_logged_in": True,
                        "message": "已登录"
                    }
                except:
                    # 超时或其他情况，默认返回未登录
                    logger.warning("无法确定登录状态")
                    return {
                        "is_logged_in": False,
                        "message": "无法确定登录状态"
                    }
        except Exception as e:
            logger.error(f"检查登录状态失败: {str(e)}")
            return {
                "is_logged_in": False,
                "message": f"检查登录状态失败: {str(e)}"
            }
    
    def login(self):
        """手动登录 - 打开浏览器让用户手动登录"""
        try:
            # 打开登录页面
            self.page.goto(self.login_url)
            logger.info("请在浏览器窗口中手动登录")
            
            # 等待用户登录完成
            # 这里会一直等待直到用户手动登录或超时
            # 实际实现中可能需要根据实际情况调整等待逻辑
            while True:
                login_status = self.check_login_status()
                if login_status["is_logged_in"]:
                    logger.info("登录成功")
                    return True
                
                # 每5秒检查一次
                time.sleep(5)
                
                # 可以添加超时逻辑
                # if time.time() - start_time > timeout:
                #     logger.error("Login timeout")
                #     return False
                     
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            return False