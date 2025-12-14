import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:18060/api/v1"


def test_health():
    """测试健康检查接口"""
    url = "http://localhost:18060/health"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")


def test_check_login():
    """测试登录状态检查接口"""
    url = f"{BASE_URL}/check_login"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 登录状态检查成功")
            print(f"   登录状态: {'已登录' if data['data']['is_logged_in'] else '未登录'}")
            print(f"   消息: {data['data']['message']}")
        else:
            print(f"❌ 登录状态检查失败: HTTP {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 登录状态检查异常: {str(e)}")


def test_get_feeds():
    """测试获取推荐列表接口"""
    url = f"{BASE_URL}/feeds?page=1&size=10"
    try:
        print("正在获取推荐列表...")
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取推荐列表成功")
            print(f"   总数: {data['data']['total_count']}")
            if data['data']['feeds']:
                print(f"   示例笔记标题: {data['data']['feeds'][0]['title']}")
        else:
            print(f"❌ 获取推荐列表失败: HTTP {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 获取推荐列表异常: {str(e)}")


def test_search():
    """测试搜索接口"""
    keyword = "美食"
    url = f"{BASE_URL}/search?keyword={keyword}&page=1&size=10"
    try:
        print(f"正在搜索关键词 '{keyword}'...")
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 搜索成功")
            print(f"   关键词: {data['data']['keyword']}")
            print(f"   结果数量: {data['data']['total_count']}")
            if data['data']['results']:
                print(f"   示例结果标题: {data['data']['results'][0]['title']}")
        else:
            print(f"❌ 搜索失败: HTTP {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 搜索异常: {str(e)}")


def main():
    """运行所有测试"""
    print("===== 小红书MCP服务测试 ======")
    
    # 首先检查服务是否启动
    test_health()
    time.sleep(1)
    
    # 如果服务启动成功，继续其他测试
    print("\n" + "="*40)
    test_check_login()
    time.sleep(2)
    
    print("\n" + "="*40)
    test_get_feeds()
    time.sleep(2)
    
    print("\n" + "="*40)
    test_search()
    
    print("\n" + "===== 测试完成 ======")
    print("提示: ")
    print("1. 如果未登录，请使用非无头模式运行服务，手动完成登录")
    print("2. 对于发布和评论功能，请参考README中的API文档进行测试")
    print("3. 如果遇到问题，请检查服务日志获取详细错误信息")


if __name__ == '__main__':
    main()