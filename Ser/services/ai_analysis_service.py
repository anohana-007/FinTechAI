import os
import logging
import requests
import json
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from datetime import datetime

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger('ai_analysis_service')

# 全局AI API配置（作为后备配置）
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

# 结构化提示词模板
STOCK_ANALYSIS_PROMPT = """
你是一位资深的股票分析师，请基于提供的股票信息进行专业分析。

股票信息：
- 股票代码：{stock_code}
- 当前价格：{current_price}
- 价格变动：{price_change_info}

请提供结构化的分析结果，必须按照以下JSON格式返回：

{{
    "overall_score": 数字 (0-100的评分),
    "recommendation": "字符串 (Buy/Sell/Hold/Monitor 之一)",
    "technical_summary": "字符串 (技术面分析摘要，简洁明了)",
    "fundamental_summary": "字符串 (基本面分析摘要，可基于通用行业知识)",
    "sentiment_summary": "字符串 (市场情绪分析，可基于通用市场认知)",
    "key_reasons": ["理由1", "理由2", "理由3"],
    "confidence_level": "字符串 (High/Medium/Low 之一)"
}}

分析要求：
1. overall_score: 综合评分，考虑技术面、基本面、市场情绪
2. recommendation: 基于当前信息给出明确建议
3. technical_summary: 基于价格变动等技术指标分析
4. fundamental_summary: 基于公司基本面和行业地位分析
5. sentiment_summary: 基于市场情绪和投资者心理分析
6. key_reasons: 提供3-5个支持推荐决策的关键理由
7. confidence_level: 评估分析置信度

请确保输出为有效的JSON格式，不要包含任何其他文字。
"""

def get_ai_analysis(stock_code: str, current_price: float, llm_preference: str, 
                   user_config: Optional[Dict[str, Any]] = None, 
                   additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    获取股票的AI分析
    
    参数:
    stock_code (str): 股票代码
    current_price (float): 当前价格
    llm_preference (str): LLM偏好 ('openai', 'gemini', 'deepseek')
    user_config (dict, optional): 用户配置，包含AI API密钥
    additional_data (dict, optional): 额外数据如新闻、财报等
    
    返回:
    dict: 结构化的AI分析结果
    """
    try:
        # 获取用户配置的AI API密钥
        ai_api_keys = {}
        
        # 优先从新的ai_configurations字段获取
        if user_config and user_config.get('ai_configurations'):
            ai_configurations = user_config['ai_configurations']
            for provider_id, config in ai_configurations.items():
                if config.get('enabled') and config.get('api_key'):
                    ai_api_keys[provider_id] = config['api_key']
        
        # 兼容旧的ai_api_keys字段
        elif user_config and user_config.get('ai_api_keys'):
            ai_api_keys = user_config['ai_api_keys']
        
        logger.info(f"从用户配置获取到 {len(ai_api_keys)} 个AI API密钥")
        
        # 获取代理设置
        proxy_settings = user_config.get('proxy_settings', {}) if user_config else {}
        proxies = None
        
        if proxy_settings and proxy_settings.get('enabled'):
            proxy_host = proxy_settings.get('host')
            proxy_port = proxy_settings.get('port')
            proxy_username = proxy_settings.get('username')
            proxy_password = proxy_settings.get('password')
            
            if proxy_host and proxy_port:
                if proxy_username and proxy_password:
                    proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
                else:
                    proxy_url = f"http://{proxy_host}:{proxy_port}"
                
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                logger.info(f"使用代理进行AI分析: {proxy_host}:{proxy_port}")
        
        # Provider ID映射：将前端的provider ID映射为后端期望的ID
        provider_mapping = {
            'google': 'gemini',  # Google AI -> Gemini
            'openai': 'openai',
            'deepseek': 'deepseek',
            'gemini': 'gemini'
        }
        
        # 映射llm_preference
        mapped_preference = provider_mapping.get(llm_preference.lower(), llm_preference.lower())
        logger.info(f"Provider映射: {llm_preference} -> {mapped_preference}")
        
        # 映射AI API密钥
        mapped_api_keys = {}
        for original_key, api_key in ai_api_keys.items():
            mapped_key = provider_mapping.get(original_key.lower(), original_key.lower())
            mapped_api_keys[mapped_key] = api_key
        
        ai_api_keys = mapped_api_keys
        
        # 获取价格变化信息
        price_change_info = "价格变化信息暂不可用"
        if additional_data:
            price_change_info = additional_data.get('price_change_info', price_change_info)
        
        # 根据LLM偏好选择分析方法
        if mapped_preference == 'openai':
            api_key = ai_api_keys.get('openai') or OPENAI_API_KEY
            if not api_key:
                return _create_error_response("OpenAI API密钥未配置")
            return _analyze_with_openai(stock_code, current_price, price_change_info, api_key, proxies)
            
        elif mapped_preference == 'gemini':
            api_key = ai_api_keys.get('gemini') or os.getenv('GEMINI_API_KEY', '')
            if not api_key:
                return _create_error_response("Gemini API密钥未配置")
            return _analyze_with_gemini(stock_code, current_price, price_change_info, api_key, proxies, user_config)
            
        elif mapped_preference == 'deepseek':
            api_key = ai_api_keys.get('deepseek') or os.getenv('DEEPSEEK_API_KEY', '')
            if not api_key:
                return _create_error_response("DeepSeek API密钥未配置")
            return _analyze_with_deepseek(stock_code, current_price, price_change_info, api_key, proxies)
            
        else:
            return _create_error_response(f"不支持的LLM类型: {mapped_preference}")
            
    except Exception as e:
        logger.error(f"AI分析过程中发生错误: {e}")
        return _create_error_response("AI分析服务暂时不可用")

def _create_error_response(error_message: str) -> Dict[str, Any]:
    """创建错误响应"""
    return {
        "error": True,
        "message": error_message,
        "overall_score": 50,
        "recommendation": "Monitor",
        "technical_summary": "分析暂不可用",
        "fundamental_summary": "分析暂不可用", 
        "sentiment_summary": "分析暂不可用",
        "key_reasons": ["API配置错误或服务不可用"],
        "confidence_level": "Low"
    }

def _analyze_with_openai(stock_code: str, current_price: float, price_change_info: str, api_key: str, proxies: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """使用OpenAI API进行分析"""
    try:
        # 构建提示词
        prompt = STOCK_ANALYSIS_PROMPT.format(
            stock_code=stock_code,
            current_price=current_price,
            price_change_info=price_change_info
        )
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": "你是一位专业的股票分析师，擅长A股市场分析。请严格按照要求的JSON格式返回分析结果。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30, proxies=proxies)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            # 尝试解析JSON响应
            try:
                analysis_result = json.loads(content)
                analysis_result['provider'] = 'openai'
                logger.info(f"OpenAI分析成功: {stock_code}")
                return analysis_result
            except json.JSONDecodeError:
                logger.error(f"OpenAI返回的不是有效JSON: {content}")
                return _create_fallback_response(content, 'openai')
        else:
            logger.error(f"OpenAI API请求失败: {response.status_code} {response.text}")
            return _create_error_response(f"OpenAI API请求失败 (HTTP {response.status_code})")
            
    except Exception as e:
        logger.error(f"OpenAI分析出错: {e}")
        return _create_error_response("OpenAI分析服务连接失败")

def _analyze_with_gemini(stock_code: str, current_price: float, price_change_info: str, api_key: str, proxies: Optional[Dict[str, str]] = None, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """使用Gemini API进行分析"""
    try:
        # 从用户配置获取模型信息
        model_name = "gemini-pro"  # 默认模型
        base_url = "https://generativelanguage.googleapis.com/v1beta/models/"
        
        # 尝试从用户配置获取Google/Gemini的具体模型配置
        if user_config and user_config.get('ai_configurations'):
            ai_configurations = user_config['ai_configurations']
            
            # 查找Google/Gemini配置
            google_config = None
            for provider_id, config in ai_configurations.items():
                if provider_id.lower() in ['google', 'gemini'] and config.get('enabled'):
                    google_config = config
                    break
            
            if google_config:
                configured_model = google_config.get('model_name') or google_config.get('model_id')
                if configured_model:
                    model_name = configured_model
                    logger.info(f"使用用户配置的Gemini模型: {model_name}")
                
                # 也可以从配置中获取base_url
                configured_base_url = google_config.get('base_url')
                if configured_base_url:
                    # 确保base_url正确格式
                    if not configured_base_url.endswith('/'):
                        configured_base_url += '/'
                    base_url = configured_base_url
                    logger.info(f"使用用户配置的base_url: {base_url}")
        
        prompt = STOCK_ANALYSIS_PROMPT.format(
            stock_code=stock_code,
            current_price=current_price,
            price_change_info=price_change_info
        )
        
        # 构建正确的Gemini API URL
        url = f"{base_url}{model_name}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1500
            }
        }
        
        logger.info(f"调用Gemini API: {url}")
        logger.info(f"使用模型: {model_name}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=30, proxies=proxies)
        
        logger.info(f"Gemini API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # 尝试解析JSON响应
            try:
                analysis_result = json.loads(content)
                analysis_result['provider'] = 'gemini'
                analysis_result['model_used'] = model_name  # 记录实际使用的模型
                logger.info(f"Gemini分析成功: {stock_code}")
                return analysis_result
            except json.JSONDecodeError:
                logger.error(f"Gemini返回的不是有效JSON: {content}")
                return _create_fallback_response(content, 'gemini')
        else:
            error_text = response.text
            logger.error(f"Gemini API请求失败: {response.status_code}")
            logger.error(f"响应内容: {error_text}")
            
            # 检查是否是404错误（模型不存在）
            if response.status_code == 404:
                return _create_error_response(f"Gemini API请求失败 (HTTP 404)，请确保API Key正确传递。当前使用模型: {model_name}，请检查模型名称是否正确")
            else:
                return _create_error_response(f"Gemini API请求失败 (HTTP {response.status_code}): {error_text}")
            
    except Exception as e:
        logger.error(f"Gemini分析出错: {e}")
        return _create_error_response("Gemini分析服务连接失败")

def _analyze_with_deepseek(stock_code: str, current_price: float, price_change_info: str, api_key: str, proxies: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """使用DeepSeek API进行分析"""
    try:
        DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
        
        prompt = STOCK_ANALYSIS_PROMPT.format(
            stock_code=stock_code,
            current_price=current_price,
            price_change_info=price_change_info
        )
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一位专业的股票分析师，擅长A股市场分析。请严格按照要求的JSON格式返回分析结果。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30, proxies=proxies)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            # 尝试解析JSON响应
            try:
                analysis_result = json.loads(content)
                analysis_result['provider'] = 'deepseek'
                logger.info(f"DeepSeek分析成功: {stock_code}")
                return analysis_result
            except json.JSONDecodeError:
                logger.error(f"DeepSeek返回的不是有效JSON: {content}")
                return _create_fallback_response(content, 'deepseek')
        else:
            logger.error(f"DeepSeek API请求失败: {response.status_code} {response.text}")
            return _create_error_response(f"DeepSeek API请求失败 (HTTP {response.status_code})")
            
    except Exception as e:
        logger.error(f"DeepSeek分析出错: {e}")
        return _create_error_response("DeepSeek分析服务连接失败")

def _create_fallback_response(content: str, provider: str) -> Dict[str, Any]:
    """当AI返回非JSON格式时的备用响应"""
    return {
        "provider": provider,
        "overall_score": 60,
        "recommendation": "Monitor",
        "technical_summary": content[:200] + "..." if len(content) > 200 else content,
        "fundamental_summary": "需要更多数据进行基本面分析",
        "sentiment_summary": "市场情绪需进一步观察",
        "key_reasons": ["AI分析结果格式异常", "建议人工复核"],
        "confidence_level": "Low",
        "raw_response": content
    }

# 保持向后兼容的函数
def get_basic_ai_analysis(stock_code, current_price, breakout_direction, user_config: Optional[Dict[str, Any]] = None):
    """
    向后兼容的基本AI分析函数
    
    参数:
    stock_code (str): 股票代码
    current_price (float): 当前价格
    breakout_direction (str): 突破方向 ('UP' 或 'DOWN')
    user_config (dict, optional): 用户配置，包含AI API密钥
    
    返回:
    str: AI生成的分析文本
    """
    # 使用新的结构化分析函数
    additional_data = {'breakout_direction': breakout_direction}
    
    # 尝试使用用户配置的首选LLM，否则按优先级尝试
    preferred_llm = 'openai'  # 默认使用OpenAI
    if user_config and user_config.get('preferred_llm'):
        preferred_llm = user_config['preferred_llm']
    
    result = get_ai_analysis(stock_code, current_price, preferred_llm, user_config, additional_data)
    
    if result.get('error'):
        return result['message']
    
    # 转换为简单文本格式，保持向后兼容
    direction_text = "上涨" if breakout_direction == 'UP' else "下跌"
    summary = f"股票{stock_code}价格{direction_text}突破，评分：{result['overall_score']}/100。"
    summary += f"建议：{result['recommendation']}。"
    summary += f"技术面：{result['technical_summary']}"
    
    return summary 