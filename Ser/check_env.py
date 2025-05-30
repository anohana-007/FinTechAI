import os
from dotenv import load_dotenv
import sys

# 显示Python版本和执行路径
print(f"Python版本: {sys.version}")
print(f"执行路径: {sys.executable}")
print(f"当前工作目录: {os.getcwd()}")
print(f".env文件预期位置: {os.path.join(os.getcwd(), '.env')}")
print(f".env文件是否存在: {os.path.exists(os.path.join(os.getcwd(), '.env'))}")

# 尝试加载.env文件
print("\n尝试加载.env文件...")
load_dotenv()
print("加载完成\n")

# 显示环境变量
print("环境变量检查:")
tushare_token = os.getenv('TUSHARE_TOKEN', '未设置')
print(f"TUSHARE_TOKEN: {tushare_token[:4] + '***' if len(tushare_token) > 4 and tushare_token != '未设置' else tushare_token}")

# 输出所有环境变量名称(不显示值)
print("\n所有环境变量名称:")
env_vars = list(os.environ.keys())
for var in env_vars:
    if 'TOKEN' in var or 'KEY' in var:
        print(f"- {var}")

print("\n说明:")
print("1. 如果TUSHARE_TOKEN显示为'未设置'，请检查.env文件格式是否正确")
print("2. .env文件格式应该是:")
print("   TUSHARE_TOKEN=your_token_here")
print("3. .env文件应该放在当前目录下")
print("4. 确保没有额外的空格或引号")

if tushare_token == '未设置':
    print("\n请确保.env文件内容格式正确，例如:")
    print("TUSHARE_TOKEN=12345678901234567890")
    print("不要添加引号或空格") 