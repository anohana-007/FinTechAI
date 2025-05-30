import requests
import json

# 服务器地址
BASE_URL = 'http://localhost:5000'

def test_add_stock():
    """测试添加股票API"""
    url = f"{BASE_URL}/api/add_stock"
    
    # 测试数据
    data = {
        "stock_code": "600036.SH",
        "stock_name": "招商银行",
        "upper_threshold": 45.50,
        "lower_threshold": 35.80,
        "user_email": "test@example.com"
    }
    
    # 发送请求
    response = requests.post(url, json=data)
    
    # 打印结果
    print(f"添加股票响应: {response.status_code}")
    print(response.json())

def test_get_watchlist():
    """测试获取关注列表API"""
    url = f"{BASE_URL}/api/watchlist"
    
    # 发送请求
    response = requests.get(url)
    
    # 打印结果
    print(f"获取关注列表响应: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_stock_price():
    """测试获取股票价格API"""
    stock_code = "600036.SH"
    url = f"{BASE_URL}/api/stock_price/{stock_code}"
    
    # 发送请求
    response = requests.get(url)
    
    # 打印结果
    print(f"获取股票价格响应: {response.status_code}")
    print(response.json())

if __name__ == "__main__":
    # 测试添加股票
    test_add_stock()
    
    # 测试获取关注列表
    test_get_watchlist()
    
    # 测试获取股票价格
    test_stock_price() 