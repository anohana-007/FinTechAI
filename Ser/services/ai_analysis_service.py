import json
import requests
from typing import Optional, Dict, Any, List, Tuple
import logging
import re

# 日志配置
logger = logging.getLogger('ai_analysis_service')

# OpenAI API配置（仅作为常量）
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = 'gpt-3.5-turbo'

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

def _clean_markdown_json(content: str) -> str:
    """
    清理Markdown代码块格式，提取纯JSON内容
    
    参数:
    content (str): 可能包含Markdown格式的内容
    
    返回:
    str: 清理后的JSON字符串
    """
    if not content:
        return content
    
    # 移除开头和结尾的空白字符
    content = content.strip()
    
    # 使用正则表达式匹配并移除Markdown代码块标记
    # 匹配 ```json 或 ``` 开头，以及结尾的 ```
    
    # 处理开头的代码块标记
    # 匹配: ```json, ```JSON, ``` 等
    content = re.sub(r'^```(?:json|JSON)?\s*\n?', '', content, flags=re.MULTILINE)
    
    # 处理结尾的代码块标记
    # 匹配结尾的 ```
    content = re.sub(r'\n?```\s*$', '', content, flags=re.MULTILINE)
    
    # 再次清理首尾空白
    content = content.strip()
    
    logger.debug(f"Markdown清理后的内容: {content[:200]}...")
    
    return content

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
            
            # 如果有突破方向信息，生成更详细的价格变化描述
            breakout_direction = additional_data.get('breakout_direction')
            if breakout_direction:
                if breakout_direction.upper() == 'UP':
                    price_change_info = f"股票价格突破上涨，当前价格为{current_price}元，建议分析上涨动力和后续走势"
                elif breakout_direction.upper() == 'DOWN':
                    price_change_info = f"股票价格突破下跌，当前价格为{current_price}元，建议分析下跌原因和支撑位"
                else:
                    price_change_info = f"股票当前价格为{current_price}元，请综合分析其技术面和基本面情况"
        
        # 根据LLM偏好选择分析方法
        if mapped_preference == 'openai':
            api_key = ai_api_keys.get('openai')
            if not api_key:
                return _create_error_response("OpenAI API密钥未配置")
            return _analyze_with_openai(stock_code, current_price, price_change_info, api_key, proxies)
            
        elif mapped_preference == 'gemini':
            api_key = ai_api_keys.get('gemini')
            if not api_key:
                return _create_error_response("Gemini API密钥未配置")
            return _analyze_with_gemini(stock_code, current_price, price_change_info, api_key, proxies, user_config)
            
        elif mapped_preference == 'deepseek':
            api_key = ai_api_keys.get('deepseek')
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
            
            # 清理Markdown格式并尝试解析JSON响应
            try:
                cleaned_content = _clean_markdown_json(content)
                analysis_result = json.loads(cleaned_content)
                analysis_result['provider'] = 'openai'
                logger.info(f"OpenAI分析成功: {stock_code}")
                return analysis_result
            except json.JSONDecodeError as e:
                logger.error(f"OpenAI返回的不是有效JSON: {content}")
                logger.error(f"JSON解析错误: {e}")
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
                    # 标准化模型名称格式 - 统一转换为小写并用连字符分隔
                    original_model = configured_model
                    model_name = configured_model.lower().replace(' ', '-')
                    logger.info(f"原始配置模型: {original_model}, 标准化后: {model_name}")
                
                # 也可以从配置中获取base_url
                configured_base_url = google_config.get('base_url')
                if configured_base_url:
                    # 确保base_url正确格式
                    if not configured_base_url.endswith('/'):
                        configured_base_url += '/'
                    base_url = configured_base_url
                    logger.info(f"使用用户配置的base_url: {base_url}")
        
        # 定义回退模型配置（与连通性测试保持一致）
        fallback_models = [
            model_name,  # 用户配置的模型（已标准化）
            "gemini-pro",  # 稳定版
            "gemini-1.5-pro",  # 推荐版本
            "gemini-1.5-flash",  # 快速版本
        ]
        
        # 去重，保持顺序
        unique_models = []
        for m in fallback_models:
            if m not in unique_models:
                unique_models.append(m)
        
        prompt = STOCK_ANALYSIS_PROMPT.format(
            stock_code=stock_code,
            current_price=current_price,
            price_change_info=price_change_info
        )
        
        last_error = None
        
        # 尝试不同的模型配置（与连通性测试保持一致）
        for test_model in unique_models:
            logger.info(f"尝试Gemini分析模型: {test_model}")
            
            try:
                # 构建正确的Gemini API URL
                url = f"{base_url}{test_model}:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 3000  # 增加到3000，避免被截断
                    }
                }
                
                logger.info(f"调用Gemini API: {url}")
                logger.info(f"使用模型: {test_model}")
                
                response = requests.post(url, headers=headers, json=payload, timeout=30, proxies=proxies)
                
                logger.info(f"Gemini API响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 改进的响应解析逻辑，处理不同版本的响应格式
                    try:
                        content = None
                        
                        # 检查响应是否有candidates
                        if 'candidates' not in result or not result['candidates']:
                            logger.error(f"Gemini API响应中没有candidates: {json.dumps(result, indent=2)}")
                            return _create_error_response(f"Gemini API响应格式异常：缺少candidates")
                        
                        candidate = result['candidates'][0]
                        
                        # 检查finish reason
                        finish_reason = candidate.get('finishReason', '')
                        if finish_reason == 'MAX_TOKENS':
                            logger.warning(f"Gemini响应被截断 (MAX_TOKENS)，模型: {test_model}")
                        elif finish_reason and finish_reason != 'STOP':
                            logger.warning(f"Gemini响应异常结束: {finish_reason}")
                        
                        # 尝试解析content字段
                        if 'content' not in candidate:
                            logger.error(f"候选结果中没有content字段: {json.dumps(candidate, indent=2)}")
                            return _create_error_response(f"Gemini API响应格式异常：候选结果缺少content")
                        
                        candidate_content = candidate['content']
                        
                        # 处理标准格式：content.parts[0].text
                        if 'parts' in candidate_content and candidate_content['parts']:
                            parts = candidate_content['parts']
                            if len(parts) > 0 and 'text' in parts[0]:
                                content = parts[0]['text'].strip()
                                logger.info(f"使用标准格式解析成功，模型: {test_model}")
                            else:
                                logger.error(f"Parts格式异常: {json.dumps(parts, indent=2)}")
                        
                        # 处理预览版本格式：检查是否有其他字段包含实际内容
                        elif 'text' in candidate_content:
                            content = candidate_content['text'].strip()
                            logger.info(f"使用预览版格式解析成功，模型: {test_model}")
                        
                        # 如果都没有找到内容，记录详细信息
                        if not content:
                            logger.error(f"无法提取内容，candidate_content结构: {json.dumps(candidate_content, indent=2)}")
                            logger.error(f"完整响应: {json.dumps(result, indent=2)}")
                            
                            # 检查是否是因为被截断导致的空响应
                            if finish_reason == 'MAX_TOKENS':
                                return _create_error_response(f"Gemini API响应被截断，请尝试增加maxOutputTokens设置")
                            else:
                                return _create_error_response(f"Gemini API返回空内容，响应格式可能不兼容")
                        
                        # 有内容时继续处理
                        if content:
                            # 清理Markdown格式并尝试解析JSON响应
                            try:
                                cleaned_content = _clean_markdown_json(content)
                                analysis_result = json.loads(cleaned_content)
                                analysis_result['provider'] = 'gemini'
                                analysis_result['model_used'] = test_model  # 记录实际使用的模型
                                
                                success_message = f"Gemini分析成功: {stock_code}，使用模型: {test_model}"
                                if test_model != model_name:
                                    success_message += f" (原配置模型 {model_name} 不可用，已自动切换)"
                                
                                logger.info(success_message)
                                return analysis_result
                            except json.JSONDecodeError as e:
                                logger.error(f"Gemini返回的不是有效JSON: {content}")
                                logger.error(f"JSON解析错误: {e}")
                                logger.error(f"清理后的内容: {_clean_markdown_json(content)}")
                                return _create_fallback_response(content, 'gemini')
                        
                    except KeyError as e:
                        logger.error(f"解析Gemini响应时缺少必要字段: {e}")
                        logger.error(f"完整响应: {json.dumps(result, indent=2)}")
                        return _create_error_response(f"Gemini API响应格式错误：缺少字段 {e}")
                else:
                    error_text = response.text
                    logger.error(f"Gemini API请求失败: {response.status_code}")
                    logger.error(f"响应内容: {error_text}")
                    
                    # 如果是404错误，尝试下一个模型
                    if response.status_code == 404:
                        logger.info(f"模型 {test_model} 不存在，尝试下一个模型")
                        last_error = f"模型 {test_model} 不存在"
                        continue
                    else:
                        # 非404错误，直接返回错误
                        return _create_error_response(f"Gemini API请求失败 (HTTP {response.status_code}): {error_text}")
                        
            except requests.exceptions.RequestException as e:
                logger.error(f"Gemini模型 {test_model} 请求异常: {e}")
                last_error = f"模型 {test_model} 网络请求失败: {str(e)}"
                continue
        
        # 所有模型都失败了
        return _create_error_response(f"Gemini API所有模型都不可用。最后错误: {last_error}")
            
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
            
            # 清理Markdown格式并尝试解析JSON响应
            try:
                cleaned_content = _clean_markdown_json(content)
                analysis_result = json.loads(cleaned_content)
                analysis_result['provider'] = 'deepseek'
                logger.info(f"DeepSeek分析成功: {stock_code}")
                return analysis_result
            except json.JSONDecodeError as e:
                logger.error(f"DeepSeek返回的不是有效JSON: {content}")
                logger.error(f"JSON解析错误: {e}")
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