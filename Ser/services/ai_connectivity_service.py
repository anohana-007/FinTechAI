"""
AI连通性测试服务
用于测试各种AI API的连通性和配置是否正确
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import google.generativeai as genai
import os

logger = logging.getLogger('ai_connectivity_service')

def test_ai_connectivity(
    provider: str, 
    model: str, 
    base_url: str, 
    api_key: str, 
    proxy_settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    测试AI服务的连通性
    
    参数:
    provider (str): 服务提供商 ('openai', 'deepseek', 'google', 'anthropic', 'custom')
    model (str): 模型名称
    base_url (str): API基础URL
    api_key (str): API密钥
    proxy_settings (dict): 代理设置
    
    返回:
    dict: 测试结果
    """
    try:
        logger.info(f"开始测试AI连通性: {provider} - {model}")
        
        # 准备代理设置
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
                logger.info(f"使用代理: {proxy_host}:{proxy_port}")
        
        # 根据提供商测试连通性
        if provider.lower() == 'openai':
            return _test_openai_connectivity(model, base_url, api_key, proxies)
        elif provider.lower() == 'deepseek':
            return _test_deepseek_connectivity(model, base_url, api_key, proxies)
        elif provider.lower() == 'google':
            return _test_google_connectivity(model, base_url, api_key, proxies)
        elif provider.lower() == 'anthropic':
            return _test_anthropic_connectivity(model, base_url, api_key, proxies)
        elif provider.lower() == 'custom':
            return _test_custom_connectivity(model, base_url, api_key, proxies)
        else:
            logger.error(f"不支持的服务提供商: {provider}")
            return {
                'success': False,
                'error': f'不支持的服务提供商: {provider}',
                'provider': provider,
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"AI连通性测试失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': f'连通性测试异常: {str(e)}',
            'provider': provider,
            'model': model,
            'timestamp': datetime.now().isoformat()
        }

def _test_openai_connectivity(model: str, base_url: str, api_key: str, proxies: Optional[Dict[str, str]]) -> Dict[str, Any]:
    """测试OpenAI API连通性"""
    try:
        logger.info(f"测试OpenAI API: {model}")
        
        # 确保base_url以正确格式结尾
        if not base_url.endswith('/'):
            base_url += '/'
        
        # 如果URL还没有包含chat/completions端点，则添加
        if 'chat/completions' not in base_url:
            if base_url.endswith('v1/'):
                base_url += 'chat/completions'
            else:
                base_url += 'v1/chat/completions'
        
        logger.info(f"使用URL: {base_url}")
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [
                {'role': 'user', 'content': 'Hello, this is a connectivity test.'}
            ],
            'max_tokens': 5,  # 减少token数量
            'temperature': 0.1
        }
        
        logger.info(f"发送请求到OpenAI API...")
        
        response = requests.post(
            base_url, 
            headers=headers, 
            json=payload, 
            proxies=proxies,
            timeout=15  # 减少超时时间从30秒到15秒
        )
        
        logger.info(f"收到响应，状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                logger.info("OpenAI API测试成功")
                return {
                    'success': True,
                    'message': 'OpenAI API连接成功',
                    'response_data': {
                        'model': result.get('model'),
                        'usage': result.get('usage')
                    },
                    'provider': 'openai',
                    'model': model,
                    'timestamp': datetime.now().isoformat()
                }
            except json.JSONDecodeError as e:
                logger.error(f"OpenAI响应JSON解析失败: {e}")
                return {
                    'success': False,
                    'error': f'响应解析失败: {str(e)}',
                    'provider': 'openai',
                    'model': model,
                    'timestamp': datetime.now().isoformat()
                }
        else:
            logger.error(f"OpenAI API调用失败，状态码: {response.status_code}")
            try:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            except:
                error_data = response.text
            
            return {
                'success': False,
                'error': f'API调用失败 (HTTP {response.status_code}): {error_data}',
                'provider': 'openai',
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
    
    except requests.exceptions.Timeout as e:
        logger.error(f"OpenAI API请求超时: {e}")
        return {
            'success': False,
            'error': f'请求超时（15秒）: {str(e)}',
            'provider': 'openai',
            'model': model,
            'timestamp': datetime.now().isoformat()
        }
    except requests.exceptions.ConnectionError as e:
        logger.error(f"OpenAI API连接错误: {e}")
        return {
            'success': False,
            'error': f'连接失败: {str(e)}',
            'provider': 'openai',
            'model': model,
            'timestamp': datetime.now().isoformat()
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenAI API请求异常: {e}")
        return {
            'success': False,
            'error': f'网络请求失败: {str(e)}',
            'provider': 'openai',
            'model': model,
            'timestamp': datetime.now().isoformat()
        }

def _test_deepseek_connectivity(model: str, base_url: str, api_key: str, proxies: Optional[Dict[str, str]]) -> Dict[str, Any]:
    """测试DeepSeek API连通性"""
    try:
        logger.info(f"测试DeepSeek API: {model}")
        
        # DeepSeek使用类似OpenAI的API格式
        if not base_url.endswith('/'):
            base_url += '/'
        
        # 如果URL还没有包含chat/completions端点，则添加
        if 'chat/completions' not in base_url:
            if base_url.endswith('v1/'):
                base_url += 'chat/completions'
            else:
                base_url += 'v1/chat/completions'
        
        logger.info(f"使用URL: {base_url}")
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [
                {'role': 'user', 'content': 'Hello, this is a connectivity test.'}
            ],
            'max_tokens': 5,  # 减少token数量
            'temperature': 0.1
        }
        
        logger.info(f"发送请求到DeepSeek API...")
        
        response = requests.post(
            base_url, 
            headers=headers, 
            json=payload, 
            proxies=proxies,
            timeout=15  # 减少超时时间
        )
        
        logger.info(f"收到响应，状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                logger.info("DeepSeek API测试成功")
                return {
                    'success': True,
                    'message': 'DeepSeek API连接成功',
                    'response_data': {
                        'model': result.get('model'),
                        'usage': result.get('usage')
                    },
                    'provider': 'deepseek',
                    'model': model,
                    'timestamp': datetime.now().isoformat()
                }
            except json.JSONDecodeError as e:
                logger.error(f"DeepSeek响应JSON解析失败: {e}")
                return {
                    'success': False,
                    'error': f'响应解析失败: {str(e)}',
                    'provider': 'deepseek',
                    'model': model,
                    'timestamp': datetime.now().isoformat()
                }
        else:
            logger.error(f"DeepSeek API调用失败，状态码: {response.status_code}")
            try:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            except:
                error_data = response.text
            
            return {
                'success': False,
                'error': f'API调用失败 (HTTP {response.status_code}): {error_data}',
                'provider': 'deepseek',
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
    
    except requests.exceptions.Timeout as e:
        logger.error(f"DeepSeek API请求超时: {e}")
        return {
            'success': False,
            'error': f'请求超时（15秒）: {str(e)}',
            'provider': 'deepseek',
            'model': model,
            'timestamp': datetime.now().isoformat()
        }
    except requests.exceptions.ConnectionError as e:
        logger.error(f"DeepSeek API连接错误: {e}")
        return {
            'success': False,
            'error': f'连接失败: {str(e)}',
            'provider': 'deepseek',
            'model': model,
            'timestamp': datetime.now().isoformat()
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"DeepSeek API请求异常: {e}")
        return {
            'success': False,
            'error': f'网络请求失败: {str(e)}',
            'provider': 'deepseek',
            'model': model,
            'timestamp': datetime.now().isoformat()
        }

def _test_google_connectivity(model: str, base_url: str, api_key: str, proxies: Optional[Dict[str, str]]) -> Dict[str, Any]:
    """测试Google Gemini API连通性并获取可用模型列表"""
    if not api_key:
        return {
            'success': False,
            'error': 'Google API密钥未提供',
            'provider': 'google',
            'model': model,
            'timestamp': datetime.now().isoformat()
        }

    # 配置Gemini SDK
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        logger.error(f"Gemini SDK配置失败 (genai.configure): {e}")
        return {
            'success': False,
            'error': f'Gemini SDK配置API密钥失败: {str(e)}',
            'provider': 'google',
            'model': model,
            'timestamp': datetime.now().isoformat()
        }

    # 处理代理设置 (与ai_analysis_service.py中的逻辑一致)
    original_http_proxy = os.environ.get('HTTP_PROXY')
    original_https_proxy = os.environ.get('HTTPS_PROXY')
    proxy_configured_for_sdk = False

    if proxies and proxies.get('https'):
        os.environ['HTTPS_PROXY'] = proxies['https']
        os.environ['HTTP_PROXY'] = proxies.get('http', proxies['https'])
        logger.info(f"为Gemini SDK连通性测试设置代理: {proxies['https']}")
        proxy_configured_for_sdk = True
    elif proxies:
        logger.warning("代理已提供但缺少 'https' 键，Gemini SDK连通性测试代理可能未正确设置")

    # 定义测试模型列表 (与ai_analysis_service.py中的逻辑一致)
    # 优先使用用户配置的模型，然后是回退模型
    default_model = "gemini-pro" # 默认测试模型
    configured_model_name = default_model

    if user_config and user_config.get('ai_configurations'):
        ai_configurations = user_config['ai_configurations']
        google_config = None
        for provider_id, config_data in ai_configurations.items():
            if provider_id.lower() in ['google', 'gemini'] and config_data.get('enabled'):
                google_config = config_data
                break
        if google_config:
            model_from_config = google_config.get('model_name') or google_config.get('model_id')
            if model_from_config:
                configured_model_name = model_from_config.lower().replace(' ', '-')
                logger.info(f"连通性测试将优先尝试用户配置模型: {configured_model_name}")
    
    # 定义回退模型配置（移除已弃用的预览版模型，优先稳定版本）
    fallback_models = [
        configured_model_name, # 用户配置的模型或默认模型
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-pro",
        "gemini-1.5-pro-latest",
    ]
    unique_models_to_test = []
    for m in fallback_models:
        if m not in unique_models_to_test:
            unique_models_to_test.append(m)

    test_prompt = "你好，请做个简单的自我介绍。"
    available_models_details = []
    first_successful_model = None
    connection_successful = False
    last_error_message = "所有尝试的Gemini模型均连接失败或不可用。"

    for model_name_to_test in unique_models_to_test:
        logger.info(f"尝试通过SDK连接Gemini模型: {model_name_to_test}")
        try:
            model_sdk = genai.GenerativeModel(model_name=model_name_to_test)
            
            # 使用非常短的超时（如果SDK支持的话），或依赖SDK默认的快速失败机制
            # Python SDK的 `generate_content` 不直接接受timeout参数
            # 超时主要由底层的HTTP请求库控制，或者通过 genai.configure(transport=...) 自定义
            # 这里我们依赖SDK的默认行为，对于连通性测试，快速响应很重要
            response_sdk = model_sdk.generate_content(contents=test_prompt)

            if response_sdk and response_sdk.text:
                logger.info(f"Gemini SDK模型 {model_name_to_test} 连接成功并收到回复。")
                if not connection_successful: # 记录第一个成功的模型和消息
                    connection_successful = True
                    first_successful_model = model_name_to_test
                    last_error_message = f"通过模型 {model_name_to_test} 成功连接到Gemini API。"
                
                available_models_details.append({
                    "id": model_name_to_test,
                    "name": model_name_to_test,
                    "status": "available",
                    "message": "连接成功"
                })
            else:
                # SDK未能返回有效文本
                error_detail = "API未返回有效文本。"
                if response_sdk.prompt_feedback and response_sdk.prompt_feedback.block_reason:
                    error_detail = f"内容被阻止: {response_sdk.prompt_feedback.block_reason_message}"
                elif not response_sdk.candidates:
                     error_detail = "API未返回候选内容 (candidates is empty)"

                logger.warning(f"Gemini SDK模型 {model_name_to_test} 连接成功但未能生成有效内容: {error_detail}")
                available_models_details.append({
                    "id": model_name_to_test,
                    "name": model_name_to_test,
                    "status": "limited",
                    "message": f"连接成功但响应无效: {error_detail}"
                })
                if not connection_successful: # 即使响应无效，也算某种程度的连接
                    last_error_message = f"模型 {model_name_to_test} 连接成功但响应无效: {error_detail}"

        except Exception as e:
            error_str = str(e)
            logger.error(f"Gemini SDK模型 {model_name_to_test} 连接失败: {error_str}")
            status_message = f"连接失败: {error_str}"
            
            if "API key not valid" in error_str or "API_KEY_INVALID" in error_str:
                status_message = "API密钥无效或未配置。"
                # API密钥问题是致命的，不需要尝试其他模型
                last_error_message = status_message
                available_models_details.append({"id": model_name_to_test, "name": model_name_to_test, "status": "error", "message": status_message})
                connection_successful = False # 确保标记为失败
                break # 停止尝试其他模型
            elif "PermissionDenied" in error_str or "google.api_core.exceptions.PermissionDenied" in error_str:
                status_message = f"权限不足 (检查API密钥是否有权访问 {model_name_to_test})。"
            elif "Model not found" in error_str or "NotFound" in error_str:
                status_message = "模型不存在。"
            elif "DeadlineExceeded" in error_str or "timeout" in error_str.lower():
                status_message = "请求超时。"
            elif "ResourceExhausted" in error_str:
                status_message = "资源耗尽 (达到API配额)。"
            else:
                status_message = f"未知错误: {error_str}"
            
            available_models_details.append({"id": model_name_to_test, "name": model_name_to_test, "status": "error", "message": status_message})
            if not connection_successful: # 更新最后一个错误信息，直到有成功的连接
                last_error_message = f"模型 {model_name_to_test}: {status_message}"
    
    # 清理代理环境变量
    if proxy_configured_for_sdk:
        if original_http_proxy is not None:
            os.environ['HTTP_PROXY'] = original_http_proxy
        elif 'HTTP_PROXY' in os.environ:
            del os.environ['HTTP_PROXY']
        
        if original_https_proxy is not None:
            os.environ['HTTPS_PROXY'] = original_https_proxy
        elif 'HTTPS_PROXY' in os.environ:
            del os.environ['HTTPS_PROXY']
        logger.info("已恢复连通性测试的原始代理环境变量设置")

    if connection_successful and first_successful_model:
        # 如果至少有一个模型连接成功，整体状态视为成功
        # 可以在这里尝试列出所有可用模型 (genai.list_models())，但这需要额外权限，且可能较慢
        # 为了快速连通性测试，我们仅依赖于是否能用一个模型成功生成内容
        logger.info(f"Google Gemini API连通性测试成功 (通过模型: {first_successful_model})。")
        # 过滤掉完全出错的模型，除非所有模型都出错
        successful_or_limited_models = [m for m in available_models_details if m["status"] != "error"]
        if not successful_or_limited_models and available_models_details: # 如果全是error，就返回这些error信息
            return {
                'success': False,
                'error': last_error_message,
                'provider': 'google',
                'model': model,
                'timestamp': datetime.now().isoformat(),
                'debug_info': {
                    'tried_models': unique_models_to_test,
                    'last_error': last_error_message
                }
            }
        return {
            'success': True,
            'message': last_error_message,
            'response_data': {
                'model': first_successful_model,
                'original_model': model,
                'candidates_count': len(successful_or_limited_models)
            },
            'provider': 'google',
            'model': first_successful_model,
            'timestamp': datetime.now().isoformat(),
            'debug_info': {
                'tried_models': unique_models_to_test,
                'last_error': last_error_message
            }
        }
    else:
        logger.error(f"Google Gemini API连通性测试失败。最后错误: {last_error_message}")
        return {
            'success': False,
            'error': last_error_message,
            'provider': 'google',
            'model': model,
            'timestamp': datetime.now().isoformat(),
            'debug_info': {
                'tried_models': unique_models_to_test,
                'last_error': last_error_message
            }
        }

def _test_anthropic_connectivity(model: str, base_url: str, api_key: str, proxies: Optional[Dict[str, str]]) -> Dict[str, Any]:
    """测试Anthropic Claude API连通性"""
    try:
        if not base_url:
            base_url = 'https://api.anthropic.com/v1/messages'
        
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        payload = {
            'model': model,
            'max_tokens': 10,
            'messages': [
                {'role': 'user', 'content': 'Hello, this is a connectivity test.'}
            ]
        }
        
        response = requests.post(
            base_url, 
            headers=headers, 
            json=payload, 
            proxies=proxies,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'message': 'Anthropic Claude API连接成功',
                'response_data': {
                    'model': result.get('model'),
                    'usage': result.get('usage')
                },
                'provider': 'anthropic',
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            return {
                'success': False,
                'error': f'API调用失败 (HTTP {response.status_code}): {error_data}',
                'provider': 'anthropic',
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
    
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'网络请求失败: {str(e)}',
            'provider': 'anthropic',
            'model': model,
            'timestamp': datetime.now().isoformat()
        }

def _test_custom_connectivity(model: str, base_url: str, api_key: str, proxies: Optional[Dict[str, str]]) -> Dict[str, Any]:
    """测试自定义API连通性"""
    try:
        # 尝试使用OpenAI兼容格式
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [
                {'role': 'user', 'content': 'Hello, this is a connectivity test.'}
            ],
            'max_tokens': 10,
            'temperature': 0.1
        }
        
        response = requests.post(
            base_url, 
            headers=headers, 
            json=payload, 
            proxies=proxies,
            timeout=30
        )
        
        if response.status_code == 200:
            try:
                result = response.json()
                return {
                    'success': True,
                    'message': '自定义API连接成功',
                    'response_data': result,
                    'provider': 'custom',
                    'model': model,
                    'timestamp': datetime.now().isoformat()
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'message': '自定义API连接成功（非JSON响应）',
                    'response_data': {'response_text': response.text[:200]},
                    'provider': 'custom',
                    'model': model,
                    'timestamp': datetime.now().isoformat()
                }
        else:
            return {
                'success': False,
                'error': f'API调用失败 (HTTP {response.status_code}): {response.text[:200]}',
                'provider': 'custom',
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
    
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'网络请求失败: {str(e)}',
            'provider': 'custom',
            'model': model,
            'timestamp': datetime.now().isoformat()
        } 