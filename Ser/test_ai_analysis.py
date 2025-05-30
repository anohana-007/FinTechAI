"""
测试AI分析功能
"""
import os
from dotenv import load_dotenv
from services.ai_analysis_service import get_basic_ai_analysis, get_analysis_with_gemini

# 加载环境变量
load_dotenv()

def test_ai_config():
    """测试AI配置是否正确"""
    print("检查AI配置...")
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    print(f"OpenAI API Key: {'已设置' if openai_api_key else '未设置'}")
    print(f"Gemini API Key: {'已设置' if gemini_api_key else '未设置'}")
    
    if not openai_api_key and not gemini_api_key:
        print("\n警告: 未设置任何AI API密钥，无法使用AI分析功能")
        print("请在.env文件中设置OPENAI_API_KEY或GEMINI_API_KEY")
        return False
    
    print("\nAI配置正确")
    return True

def test_openai_analysis():
    """测试OpenAI分析功能"""
    if not os.getenv('OPENAI_API_KEY'):
        print("\n未设置OpenAI API Key，跳过测试")
        return
    
    print("\n测试OpenAI分析功能...")
    
    # 测试上涨分析
    print("\n上涨分析示例:")
    analysis_up = get_basic_ai_analysis('600036.SH', 45.75, 'UP')
    print(analysis_up)
    
    # 测试下跌分析
    print("\n下跌分析示例:")
    analysis_down = get_basic_ai_analysis('600036.SH', 35.50, 'DOWN')
    print(analysis_down)

def test_gemini_analysis():
    """测试Gemini分析功能"""
    if not os.getenv('GEMINI_API_KEY'):
        print("\n未设置Gemini API Key，跳过测试")
        return
    
    print("\n测试Gemini分析功能...")
    
    # 测试上涨分析
    print("\n上涨分析示例:")
    analysis_up = get_analysis_with_gemini('600036.SH', 45.75, 'UP')
    print(analysis_up)
    
    # 测试下跌分析
    print("\n下跌分析示例:")
    analysis_down = get_analysis_with_gemini('600036.SH', 35.50, 'DOWN')
    print(analysis_down)

if __name__ == "__main__":
    # 测试AI配置
    if test_ai_config():
        # 测试OpenAI分析
        test_openai_analysis()
        
        # 测试Gemini分析
        test_gemini_analysis() 