import json
import requests
from typing import Optional, Dict, Any, List, Tuple
import logging
import re
import google.generativeai as genai # 导入Gemini SDK
import os # 用于设置代理环境变量
from google.api_core import exceptions as google_api_exceptions # 导入Google API核心异常

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
- 股票名称：{stock_name}
- 当前价格：{current_price}
- 价格变动：{price_change_info}

**技术面数据参考：**
{technical_data_section}

**基本面数据参考 (来自AkShare)：**
{fundamental_data_section}

**重要分析指导：**
如果上述基本面数据缺失或不完整，请你主动运用以下方法进行分析：
1. **利用知识库信息**：基于你对该公司/行业的了解，提供市盈率、市净率、ROE等关键指标的大致范围和行业对比
2. **行业分析法**：结合该公司所属行业的平均估值水平和发展趋势进行分析
3. **历史数据推理**：基于该公司历史表现和发展阶段，推测当前可能的财务状况
4. **市场对比法**：与同行业类似规模公司进行对比分析
5. **最新市场信息**：结合你所了解的最新行业动态、政策影响等进行综合判断

**特别要求：**
- 注意: 股票代码和股票名称是配对的，请确保你基于正确的公司进行分析
- 在技术面分析中明确说明你运用了哪些技术分析方法和推理依据
- 在基本面分析中明确说明你采用了哪种分析方法
- 提供基于行业经验和市场常识的合理估值判断
- 指出该股票在当前市场环境下的投资价值和风险点
- 即使没有实时数据，也要给出专业的技术面和基本面分析意见

请提供结构化的分析结果，必须按照以下JSON格式返回：

{{
    "overall_score": 数字 (0-100的评分),
    "recommendation": "字符串 (Buy/Sell/Hold/Monitor 之一)",
    "technical_summary": "字符串 (技术面分析摘要，请主动运用技术分析知识进行专业分析)",
    "fundamental_summary": "字符串 (基本面分析摘要，当数据缺失时请主动运用上述分析方法)",
    "sentiment_summary": "字符串 (市场情绪分析，可基于通用市场认知)",
    "key_reasons": ["理由1", "理由2", "理由3"],
    "confidence_level": "字符串 (High/Medium/Low 之一)"
}}

分析要求：
1. overall_score: 综合评分，考虑技术面、基本面、市场情绪
2. recommendation: 基于当前信息给出明确建议
3. technical_summary: **即使缺少实时技术数据，也要基于股票历史走势和技术分析知识提供专业的技术面分析**
4. fundamental_summary: **即使缺少实时数据，也要基于行业知识和市场经验提供专业的基本面分析**
5. sentiment_summary: 基于市场情绪和投资者心理分析
6. key_reasons: 提供3-5个支持推荐决策的关键理由
7. confidence_level: 评估分析置信度（数据缺失时可设为Medium或Low）

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
        # 获取股票名称
        stock_name = "未知"
        if additional_data and additional_data.get("stock_name"):
            stock_name = additional_data.get("stock_name")
        else:
            # 尝试从watchlist获取股票名称
            try:
                from .stock_service import get_watchlist
                watchlist = get_watchlist()
                for stock in watchlist:
                    if stock.get('stock_code') == stock_code:
                        stock_name = stock.get('stock_name', "未知")
                        break
            except Exception as e:
                logger.warning(f"获取股票名称失败: {e}，将使用默认值")

        # 获取基本面数据
        logger.info(f"🔍 开始获取 {stock_code} ({stock_name}) 的基本面数据...")
        
        from .stock_service import get_akshare_fundamental_data
        fundamental_data = get_akshare_fundamental_data(stock_code)
        
        # 格式化基本面数据为可读文本
        fundamental_data_section = _format_fundamental_data(fundamental_data)
        logger.info(f"✅ 基本面数据获取完成")
        
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
        
        # 格式化技术面数据为可读文本
        technical_data_section = _format_technical_data(stock_code, current_price, additional_data)
        
        # 根据LLM偏好选择分析方法
        if mapped_preference == 'openai':
            api_key = ai_api_keys.get('openai')
            if not api_key:
                return _create_error_response("OpenAI API密钥未配置")
            return _analyze_with_openai(stock_code, stock_name, current_price, price_change_info, technical_data_section, fundamental_data_section, api_key, proxies)
            
        elif mapped_preference == 'gemini':
            api_key = ai_api_keys.get('gemini')
            if not api_key:
                return _create_error_response("Gemini API密钥未配置")
            return _analyze_with_gemini(stock_code, stock_name, current_price, price_change_info, technical_data_section, fundamental_data_section, api_key, proxies, user_config)
            
        elif mapped_preference == 'deepseek':
            api_key = ai_api_keys.get('deepseek')
            if not api_key:
                return _create_error_response("DeepSeek API密钥未配置")
            return _analyze_with_deepseek(stock_code, stock_name, current_price, price_change_info, technical_data_section, fundamental_data_section, api_key, proxies)
            
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

def _analyze_with_openai(stock_code: str, stock_name: str, current_price: float, price_change_info: str, technical_data_section: str, fundamental_data_section: str, api_key: str, proxies: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """使用OpenAI API进行分析"""
    try:
        # 构建提示词
        prompt = STOCK_ANALYSIS_PROMPT.format(
            stock_code=stock_code,
            stock_name=stock_name,
            current_price=current_price,
            price_change_info=price_change_info,
            technical_data_section=technical_data_section,
            fundamental_data_section=fundamental_data_section
        )
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": "你是一位专业的股票分析师，擅长A股市场分析。你精通技术分析和基本面分析。当技术面数据缺失时，请主动运用你的技术分析知识，基于股票历史走势、技术指标理论和图表模式识别能力进行分析。当基本面数据缺失时，请主动运用你的知识库信息、行业经验和市场常识进行分析。你有能力基于有限信息提供专业的综合分析意见。请严格按照要求的JSON格式返回分析结果。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 15000
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

def _analyze_with_gemini(stock_code: str, stock_name: str, current_price: float, price_change_info: str, technical_data_section: str, fundamental_data_section: str, api_key: str, proxies: Optional[Dict[str, str]] = None, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """使用Gemini API进行分析"""
    try:
        # 配置Gemini SDK
        # 注意：SDK可能通过全局配置或环境变量来处理API密钥和代理
        # 这里我们优先使用传入的api_key
        genai.configure(api_key=api_key)

        # 处理代理设置
        # Gemini Python SDK 目前不直接支持proxies参数传递给requests
        # 它依赖于标准环境变量 HTTP_PROXY 和 HTTPS_PROXY
        # 我们需要在这里临时设置环境变量，并在函数结束时恢复
        original_http_proxy = os.environ.get('HTTP_PROXY')
        original_https_proxy = os.environ.get('HTTPS_PROXY')

        if proxies and proxies.get('https'): # Gemini API 使用 HTTPS
            os.environ['HTTPS_PROXY'] = proxies['https']
            os.environ['HTTP_PROXY'] = proxies.get('http', proxies['https']) # 也设置HTTP以防万一
            logger.info(f"为Gemini SDK设置代理: {proxies['https']}")
        elif proxies:
             logger.warning("代理已提供但缺少 'https' 键，Gemini SDK代理可能未正确设置")

        # 从用户配置获取模型信息
        model_name = "gemini-pro"  # 默认模型
        # base_url 不再直接用于requests.post, SDK会处理
        
        if user_config and user_config.get('ai_configurations'):
            ai_configurations = user_config['ai_configurations']
            google_config = None
            for provider_id, config_data in ai_configurations.items():
                if provider_id.lower() in ['google', 'gemini'] and config_data.get('enabled'):
                    google_config = config_data
                    break
            
            if google_config:
                configured_model = google_config.get('model_name') or google_config.get('model_id')
                if configured_model:
                    original_model = configured_model
                    model_name = configured_model.lower().replace(' ', '-')
                    logger.info(f"原始配置模型: {original_model}, SDK将使用标准化模型: {model_name}")
        
        fallback_models = [
            model_name,  # 用户配置的模型（已标准化）
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro",
            "gemini-1.5-pro-latest",
        ]
        
        unique_models = []
        for m in fallback_models:
            if m not in unique_models:
                unique_models.append(m)
        
        prompt = STOCK_ANALYSIS_PROMPT.format(
            stock_code=stock_code,
            stock_name=stock_name,
            current_price=current_price,
            price_change_info=price_change_info,
            technical_data_section=technical_data_section,
            fundamental_data_section=fundamental_data_section
        )
        
        last_error = None
        
        for test_model in unique_models:
            logger.info(f"尝试Gemini SDK分析模型: {test_model}")
            
            try:
                # 创建Gemini模型实例
                model_sdk = genai.GenerativeModel(model_name=test_model)
                
                # 配置生成参数 (generationConfig)
                generation_config = genai.types.GenerationConfig(
                    candidate_count=1,
                    stop_sequences=['},'],
                    max_output_tokens=8192,  # 将 max_tokens 调整到合理范围
                    temperature=0.7,
                    top_p=0.9,
                )
                
                # 调用SDK的generate_content方法
                # SDK的超时处理机制可能与requests不同，这里依赖SDK的默认或内部超时
                # 如果需要自定义超时，需要查看SDK是否支持相关参数
                response_sdk = model_sdk.generate_content(
                    contents=prompt, 
                    generation_config=generation_config
                )
                
                # 更安全地处理SDK的响应
                content = None
                if response_sdk.candidates and len(response_sdk.candidates) > 0:
                    candidate = response_sdk.candidates[0]
                    if candidate.content and candidate.content.parts and len(candidate.content.parts) > 0:
                        content = candidate.content.parts[0].text.strip()
                        # 检查 finish_reason
                        if candidate.finish_reason != "STOP":
                            logger.warning(f"Gemini SDK模型 {test_model} 响应的 finish_reason 为 {candidate.finish_reason} (不是STOP)。内容可能不完整或有问题。")
                            if candidate.finish_reason == "MAX_TOKENS":
                                logger.warning(f"模型 {test_model} 输出因 MAX_TOKENS 而被截断。将尝试使用部分内容。")
                            # 对于其他非STOP的原因，也尝试使用内容，但记录警告
                    else:
                        finish_reason_name = str(candidate.finish_reason) if candidate.finish_reason else 'N/A'
                        log_message = f"Gemini SDK模型 {test_model} 的候选内容 (candidate.content.parts) 为空或无效。Finish reason: {finish_reason_name}"
                        if candidate.finish_reason == "MAX_TOKENS":
                            log_message += " 这通常意味着模型因达到最大Token数限制而被截断，并且未能返回任何部分文本内容。"
                        logger.warning(log_message)
                        # 即使parts为空，如果是因为MAX_TOKENS，也设置last_error，但不立即continue，下面content为None时会处理
                        if candidate.finish_reason == "MAX_TOKENS":
                            last_error = f"模型 {test_model} 因MAX_TOKENS被截断且未返回任何文本。"
                        else:
                            last_error = f"模型 {test_model} 响应中无有效文本部分 (FinishReason: {finish_reason_name})。"
                        # content 此时为 None
                else:
                    logger.error(f"Gemini SDK模型 {test_model} 未返回任何候选内容 (response_sdk.candidates 为空)。")
                    # 检查 prompt_feedback，这可能提供为何没有候选内容的原因
                    if response_sdk.prompt_feedback and response_sdk.prompt_feedback.block_reason:
                        block_reason_message = response_sdk.prompt_feedback.block_reason_message or "原因未知"
                        logger.error(f"Prompt feedback: 内容被阻止，原因: {response_sdk.prompt_feedback.block_reason}, 详情: {block_reason_message}")
                        last_error = f"模型 {test_model} 内容被阻止: {block_reason_message}"
                    else:
                        last_error = f"模型 {test_model} 未返回任何候选内容。"
                    continue # 尝试下一个模型

                if content:
                    # 清理Markdown格式并尝试解析JSON响应
                    try:
                        cleaned_content = _clean_markdown_json(content)
                        analysis_result = json.loads(cleaned_content)
                        analysis_result['provider'] = 'gemini'
                        analysis_result['model_used'] = test_model  # 记录实际使用的模型
                        
                        success_message = f"Gemini SDK分析成功: {stock_code}，使用模型: {test_model}"
                        if candidate.finish_reason == "MAX_TOKENS":
                            success_message += " (注意: 输出可能因MAX_TOKENS被截断)"
                        elif candidate.finish_reason != "STOP":
                            success_message += f" (警告: Finish reason: {candidate.finish_reason})"

                        if test_model != model_name:
                            success_message += f" (原配置模型 {model_name} 不可用，已自动切换)"
                        
                        logger.info(success_message)
                        return analysis_result
                    except json.JSONDecodeError as e:
                        logger.error(f"Gemini SDK返回的不是有效JSON (模型: {test_model}, FinishReason: {candidate.finish_reason if response_sdk.candidates and response_sdk.candidates[0].finish_reason else 'N/A'}): {content[:500]}...")
                        logger.error(f"JSON解析错误: {e}")
                        logger.error(f"清理后的内容: {_clean_markdown_json(content)[:500]}...")
                        # 即使JSON解析失败，如果是因为MAX_TOKENS，也可能需要特殊处理或提示
                        # 但目前还是走通用fallback
                        return _create_fallback_response(content, 'gemini', model_name=test_model, finish_reason=candidate.finish_reason if response_sdk.candidates and response_sdk.candidates[0].finish_reason else None)
                else:
                    # 如果在之前的检查后 content 仍然是 None，这意味着虽然有 candidate，但无法提取文本
                    logger.error(f"Gemini SDK模型 {test_model} 虽然有候选内容，但无法提取有效文本。将尝试下一个模型。")
                    last_error = f"模型 {test_model} 响应中无有效文本内容。"
                    continue # 尝试下一个模型

            except genai.types.BlockedPromptException as bpe: # 更具体地捕获提示被阻止的异常
                logger.error(f"Gemini SDK模型 {test_model} 的提示被阻止: {bpe}")
                last_error = f"模型 {test_model} 的提示因安全或其他原因被阻止。"
                continue # 提示被阻止，尝试下一个模型可能也一样，但还是尝试
            except google_api_exceptions.GoogleAPIError as gae:
                # 捕获更广泛的Google API错误，例如 DeadlineExceeded, ResourceExhausted 等
                error_message = str(gae)
                logger.error(f"Gemini SDK模型 {test_model} Google API Error: {gae}")
                if isinstance(gae, google_api_exceptions.InvalidArgument):
                    # 通常是模型名称错误或请求结构问题
                    logger.error(f"Gemini SDK模型 {test_model} 请求参数无效 (InvalidArgument): {error_message}")
                    last_error = f"模型 {test_model} 请求参数无效。可能是模型名称不支持。"
                    # 如果是参数无效，通常意味着这个模型名称有问题，可以继续尝试其他的
                elif isinstance(gae, google_api_exceptions.PermissionDenied):
                     logger.error(f"Gemini SDK模型 {test_model} 权限不足: {error_message}")
                     last_error = f"模型 {test_model} 权限不足 (检查API密钥是否有权访问此模型)"
                elif isinstance(gae, google_api_exceptions.NotFound):
                    logger.info(f"Gemini SDK模型 {test_model} 不存在 (NotFound)，尝试下一个模型")
                    last_error = f"模型 {test_model} 不存在"
                elif isinstance(gae, google_api_exceptions.DeadlineExceeded):
                    logger.error(f"Gemini SDK模型 {test_model} 请求超时 (DeadlineExceeded): {error_message}")
                    last_error = f"模型 {test_model} 请求超时。"
                elif isinstance(gae, google_api_exceptions.ResourceExhausted):
                    logger.error(f"Gemini SDK模型 {test_model} 资源耗尽 (ResourceExhausted) (可能达到配额): {error_message}")
                    last_error = f"模型 {test_model} 资源耗尽 (已达到API配额限制)。"
                elif "API key not valid" in error_message or "API_KEY_INVALID" in error_message:
                    logger.error(f"Gemini SDK模型 {test_model} API密钥无效: {error_message}")
                    return _create_error_response("Gemini API密钥无效或未配置，请检查用户设置。") # API密钥问题是致命的
                else:
                    logger.error(f"Gemini SDK模型 {test_model} 发生未分类的Google API错误: {error_message}")
                    last_error = f"模型 {test_model} 发生Google API错误: {error_message}"
                
                if "preview" in test_model.lower() and not isinstance(gae, google_api_exceptions.NotFound):
                     last_error += " (预览版模型可能不稳定，建议检查或更换)"
                continue # 发生API错误，尝试下一个模型
            except Exception as e: # 其他所有 Python 异常
                error_message = str(e)
                # 这个 Exception 块现在主要捕获非 GoogleAPIError 的 Python 级别错误
                # 例如，之前在这里捕获的 API key 无效的逻辑已经移到 GoogleAPIError 中处理
                logger.error(f"Gemini SDK模型 {test_model} 发生Python级别未知异常: {e}", exc_info=True) # 添加exc_info获取堆栈
                last_error = f"模型 {test_model} 发生未知本地错误: {error_message}"
                
                if "preview" in test_model.lower():
                    last_error += " (预览版模型可能不稳定)"
                
                continue # 尝试下一个模型

    except genai.types.generation_types.StopCandidateException as e:
        # 这个异常在 generate_content.candidates 为空时可能发生
        logger.error(f"Gemini SDK内容生成停止，无有效候选: {e}")
        last_error = f"内容生成停止，无有效候选: {str(e)}"
    except Exception as e:
        logger.error(f"Gemini SDK分析过程发生严重错误: {e}")
        # 捕获 genai.configure 或其他SDK初始化时的错误
        if "API key not valid" in str(e) or "API_KEY_INVALID" in str(e):
            return _create_error_response("Gemini API密钥无效或未配置，请检查用户设置。")
        return _create_error_response(f"Gemini分析服务连接或配置失败: {str(e)}")
    finally:
        # 恢复原始的代理环境变量
        if original_http_proxy is not None:
            os.environ['HTTP_PROXY'] = original_http_proxy
        elif 'HTTP_PROXY' in os.environ:
            del os.environ['HTTP_PROXY']
        
        if original_https_proxy is not None:
            os.environ['HTTPS_PROXY'] = original_https_proxy
        elif 'HTTPS_PROXY' in os.environ:
            del os.environ['HTTPS_PROXY']
        
        if proxies and proxies.get('https'):
            logger.info("已恢复原始代理环境变量设置")

    # 所有模型都失败了
    final_error_message = f"Gemini SDK所有模型都不可用。"
    
    if last_error:
        final_error_message += f"\n最后错误: {last_error}"
    
    # 如果原始模型是预览版，提供特别建议
    if "preview" in model_name.lower():
        final_error_message += f"\n\n💡 建议：\n"
        final_error_message += f"• 您配置的模型 '{model_name}' 是预览版，可能已被弃用\n"
        final_error_message += f"• 建议改用稳定版模型：gemini-1.5-pro 或 gemini-pro\n"
        final_error_message += f"• 预览版模型通常不稳定，不建议用于生产环境"
    else:
        final_error_message += f"\n\n💡 建议：\n"
        final_error_message += f"• 检查网络连接和代理设置\n"
        final_error_message += f"• 验证API密钥是否有效\n"
        final_error_message += f"• 尝试使用其他AI模型如OpenAI或DeepSeek"
    
    return _create_error_response(final_error_message)

def _analyze_with_deepseek(stock_code: str, stock_name: str, current_price: float, price_change_info: str, technical_data_section: str, fundamental_data_section: str, api_key: str, proxies: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """使用DeepSeek API进行分析"""
    try:
        DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
        
        prompt = STOCK_ANALYSIS_PROMPT.format(
            stock_code=stock_code,
            stock_name=stock_name,
            current_price=current_price,
            price_change_info=price_change_info,
            technical_data_section=technical_data_section,
            fundamental_data_section=fundamental_data_section
        )
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一位专业的股票分析师，擅长A股市场分析。你精通技术分析和基本面分析。当技术面数据缺失时，请主动运用你的技术分析知识，基于股票历史走势、技术指标理论和图表模式识别能力进行分析。当基本面数据缺失时，请主动运用你的知识库信息、行业经验和市场常识进行分析。你有能力基于有限信息提供专业的综合分析意见。请严格按照要求的JSON格式返回分析结果。"},
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

def _create_fallback_response(content: str, provider: str, model_name: Optional[str] = None, finish_reason: Optional[str] = None) -> Dict[str, Any]:
    """当AI返回非JSON格式时的备用响应"""
    message = f"AI分析结果格式异常 (来自 {provider}{f', 模型: {model_name}' if model_name else ''}{f', FinishReason: {finish_reason}' if finish_reason else ''})。建议人工复核。"
    if finish_reason == "MAX_TOKENS":
        message += " 注意：输出可能因达到最大Token数被截断。"

    return {
        "provider": provider,
        "model_used": model_name,
        "finish_reason": finish_reason,
        "overall_score": 60,
        "recommendation": "Monitor",
        "technical_summary": content[:300] + "..." if len(content) > 300 else content, # 增加摘要长度
        "fundamental_summary": "基本面分析需要更多数据或结果被截断。",
        "sentiment_summary": "市场情绪分析可能不完整或结果被截断。",
        "key_reasons": [message, "部分结果可能无法正常显示。"],
        "confidence_level": "Low",
        "raw_response": content
    }

def _format_fundamental_data(fundamental_data: dict | None) -> str:
    """
    格式化基本面数据为可读文本
    
    参数:
    fundamental_data: 基本面数据字典或None
    
    返回:
    str: 格式化的基本面数据文本
    """
    if not fundamental_data:
        return """基本面数据暂时无法获取。

**请AI主动进行以下基本面分析：**
1. **估值指标分析**：基于你的知识库，估算该股票的合理市盈率(PE)、市净率(PB)范围，并与行业平均水平对比
2. **盈利能力分析**：分析该公司的净资产收益率(ROE)、净利率水平，结合行业特点进行评估
3. **成长性分析**：基于对该公司/行业的了解，分析营收增长率、净利润增长率的合理预期
4. **财务健康度**：评估资产负债率、现金流状况等财务安全指标
5. **分红能力**：分析股息率水平和分红政策的可持续性
6. **行业对比**：与同行业龙头企业进行估值和财务指标对比
7. **市场地位**：分析公司在行业中的竞争地位和市场份额

**分析要求：**
- 运用你的知识库中该公司的历史财务数据和行业信息
- 结合当前市场环境和行业发展趋势
- 提供基于常识和经验的合理估值判断
- 明确指出投资价值和主要风险点"""
    
    # 定义指标的中文名称和格式化规则
    indicators = [
        ('pe_ttm', '市盈率 (PE TTM)', lambda x: f"{x:.2f}" if x is not None else "N/A"),
        ('pb', '市净率 (PB)', lambda x: f"{x:.2f}" if x is not None else "N/A"),
        ('eps_ttm', '每股收益 (EPS TTM)', lambda x: f"{x:.2f} 元" if x is not None else "N/A"),
        ('roe_ttm', '净资产收益率 (ROE TTM)', lambda x: f"{x*100:.2f}%" if x is not None else "N/A"),
        ('total_mv', '总市值', lambda x: f"{x:.0f} 万元" if x is not None else "N/A"),
        ('circulation_mv', '流通市值', lambda x: f"{x:.0f} 万元" if x is not None else "N/A"),
        ('revenue_yoy_growth', '营收同比增长率', lambda x: f"{x*100:.2f}%" if x is not None else "N/A"),
        ('net_profit_yoy_growth', '净利润同比增长率', lambda x: f"{x*100:.2f}%" if x is not None else "N/A"),
        ('dividend_yield', '股息率', lambda x: f"{x*100:.2f}%" if x is not None else "N/A"),
        ('gross_profit_margin', '毛利率', lambda x: f"{x*100:.2f}%" if x is not None else "N/A"),
        ('net_profit_margin', '净利率', lambda x: f"{x*100:.2f}%" if x is not None else "N/A"),
    ]
    
    # 构建格式化文本
    formatted_lines = []
    available_count = 0
    missing_indicators = []
    
    for key, name, formatter in indicators:
        value = fundamental_data.get(key)
        formatted_value = formatter(value)
        formatted_lines.append(f"- {name}: {formatted_value}")
        if value is not None:
            available_count += 1
        else:
            missing_indicators.append(name)
    
    if available_count == 0:
        return """基本面数据暂时无法获取。

**请AI主动进行以下基本面分析：**
1. **估值指标分析**：基于你的知识库，估算该股票的合理市盈率(PE)、市净率(PB)范围，并与行业平均水平对比
2. **盈利能力分析**：分析该公司的净资产收益率(ROE)、净利率水平，结合行业特点进行评估
3. **成长性分析**：基于对该公司/行业的了解，分析营收增长率、净利润增长率的合理预期
4. **财务健康度**：评估资产负债率、现金流状况等财务安全指标
5. **分红能力**：分析股息率水平和分红政策的可持续性
6. **行业对比**：与同行业龙头企业进行估值和财务指标对比
7. **市场地位**：分析公司在行业中的竞争地位和市场份额

**分析要求：**
- 运用你的知识库中该公司的历史财务数据和行业信息
- 结合当前市场环境和行业发展趋势
- 提供基于常识和经验的合理估值判断
- 明确指出投资价值和主要风险点"""
    
    # 添加数据状态说明
    header = f"以下是从AkShare获取的基本面数据（共获得 {available_count}/{len(indicators)} 项指标）："
    
    result = header + "\n" + "\n".join(formatted_lines)
    
    if available_count < len(indicators) // 2:
        result += f"\n\n**缺失指标需要AI主动分析：**\n缺失的关键指标包括：{', '.join(missing_indicators[:5])}等"
        result += "\n\n**请基于你的知识库主动补充以下分析：**"
        result += "\n- 对缺失指标进行合理估算和行业对比"
        result += "\n- 结合公司历史表现和行业特点进行综合评估"
        result += "\n- 提供基于市场常识的投资价值判断"
        result += "\n- 明确指出主要投资风险和机会"
    
    return result

def _format_technical_data(stock_code: str, current_price: float, additional_data: Optional[Dict[str, Any]] = None) -> str:
    """
    格式化技术面数据为可读文本，为AI提供技术分析指导
    
    参数:
    stock_code: 股票代码
    current_price: 当前价格
    additional_data: 额外数据
    
    返回:
    str: 格式化的技术面分析指导文本
    """
    # 获取价格变动信息
    breakout_direction = additional_data.get('breakout_direction') if additional_data else None
    price_change_info = additional_data.get('price_change_info') if additional_data else None
    
    # 构建技术面分析指导
    technical_info = f"当前股价：¥{current_price}"
    
    if breakout_direction:
        if breakout_direction.upper() == 'UP':
            technical_info += f"\n💹 价格突破上涨信号"
            action_guidance = "分析上涨动力、成交量配合情况、上方阻力位"
        elif breakout_direction.upper() == 'DOWN':
            technical_info += f"\n📉 价格突破下跌信号"
            action_guidance = "分析下跌原因、寻找支撑位、判断止跌信号"
        else:
            action_guidance = "综合分析技术面走势和关键价位"
    else:
        action_guidance = "基于历史走势分析当前技术面状况"
    
    if price_change_info:
        technical_info += f"\n价格变动：{price_change_info}"
    
    # 添加技术面分析的详细指导
    guidance_text = f"""
{technical_info}

**技术面数据严重不足，请AI主动补充以下分析：**

🔍 **缺失数据需要AI主动分析：**
- K线数据：开盘价、最高价、最低价、收盘价走势
- 成交量：成交量变化和量价关系分析
- 技术指标：MACD、RSI、KDJ、BOLL等指标状态推测
- 移动平均线：5日、10日、20日、60日均线位置关系
- 支撑阻力：关键支撑位和阻力位识别
- 技术形态：可能的K线形态和图表模式

📊 **请基于技术分析知识主动补充：**
- 运用你对该股票历史走势的了解进行趋势分析
- 基于当前价格推测可能的技术指标状态
- 提供合理的支撑位和阻力位估算
- 分析短期（1-5日）和中期（1-4周）走势可能性
- {action_guidance}
- 明确说明采用的技术分析方法和推理依据

💡 **技术分析要求：**
- 结合该股票的历史价格表现和波动特征
- 考虑当前市场环境对技术面的影响
- 提供具体的买卖点位建议
- 给出风险控制和止损建议"""
    
    return guidance_text

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