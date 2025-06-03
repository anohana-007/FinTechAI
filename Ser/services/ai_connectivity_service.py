"""
AI连通性测试服务
用于测试各种AI API的连通性和配置是否正确
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

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
    """测试Google Gemini API连通性"""
    try:
        logger.info(f"开始测试Google Gemini API连通性: {model}")
        
        # Google Gemini API格式
        if not base_url:
            base_url = 'https://generativelanguage.googleapis.com/v1beta/models/'
        
        if not base_url.endswith('/'):
            base_url += '/'
        
        # 定义回退模型配置（如果用户配置的模型失败）
        fallback_models = [
            model,  # 用户配置的模型
            "gemini-pro",  # 稳定版
            "gemini-1.5-pro",  # 推荐版本
            "gemini-1.5-flash",  # 快速版本
        ]
        
        # 去重，保持顺序
        unique_models = []
        for m in fallback_models:
            if m not in unique_models:
                unique_models.append(m)
        
        last_error = None
        
        # 尝试不同的模型配置
        for test_model in unique_models:
            logger.info(f"尝试模型: {test_model}")
            
            url = f"{base_url}{test_model}:generateContent?key={api_key}"
            
            logger.info(f"构建的URL: {url}")
            logger.info(f"使用的模型: {test_model}")
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                'contents': [{
                    'parts': [{
                        'text': 'Hello, this is a connectivity test.'
                    }]
                }],
                'generationConfig': {
                    'maxOutputTokens': 10,
                    'temperature': 0.1
                }
            }
            
            try:
                response = requests.post(
                    url, 
                    headers=headers, 
                    json=payload, 
                    proxies=proxies,
                    timeout=30
                )
                
                logger.info(f"Google API响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Google Gemini API测试成功，使用模型: {test_model}")
                    
                    success_message = f'Google Gemini API连接成功，使用模型: {test_model}'
                    if test_model != model:
                        success_message += f' (原配置模型 {model} 不可用，已自动切换)'
                    
                    return {
                        'success': True,
                        'message': success_message,
                        'response_data': {
                            'model': test_model,
                            'original_model': model,
                            'candidates_count': len(result.get('candidates', []))
                        },
                        'provider': 'google',
                        'model': test_model,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    error_text = response.text
                    logger.error(f"Google API请求失败 (模型: {test_model}): {response.status_code}")
                    logger.error(f"错误响应: {error_text}")
                    
                    last_error = {
                        'status_code': response.status_code,
                        'error_text': error_text,
                        'model': test_model,
                        'url': url
                    }
                    
                    # 如果是404错误（模型不存在），尝试下一个模型
                    if response.status_code == 404:
                        logger.info(f"模型 {test_model} 不存在，尝试下一个模型")
                        continue
                    
                    # 如果是其他错误，也尝试下一个模型（除非是最后一个）
                    if test_model != unique_models[-1]:
                        logger.info(f"模型 {test_model} 失败，尝试下一个模型")
                        continue
                        
            except requests.exceptions.Timeout:
                logger.error(f"Google API请求超时 (模型: {test_model})")
                last_error = {
                    'error': f'请求超时（30秒） - 模型: {test_model}',
                    'model': test_model
                }
                if test_model != unique_models[-1]:
                    continue
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Google API连接错误 (模型: {test_model}): {e}")
                last_error = {
                    'error': f'连接失败 - 模型: {test_model}: {str(e)}',
                    'model': test_model
                }
                if test_model != unique_models[-1]:
                    continue
        
        # 所有模型都失败了，返回详细错误信息
        if last_error:
            if 'status_code' in last_error:
                # 提供更具体的错误信息
                status_code = last_error['status_code']
                error_text = last_error['error_text']
                
                if status_code == 400:
                    error_msg = f"请求格式错误 (HTTP 400)。常见原因：\n"
                    error_msg += f"• 模型名称不正确，已测试的模型: {', '.join(unique_models)}\n"
                    error_msg += f"• 建议使用稳定版本: gemini-pro 或 gemini-1.5-pro\n"
                    error_msg += f"• 检查API密钥是否有访问该模型的权限"
                elif status_code == 401:
                    error_msg = f"API密钥无效 (HTTP 401)，请检查密钥是否正确"
                elif status_code == 403:
                    error_msg = f"访问被禁止 (HTTP 403)，请检查API密钥权限和模型访问权限"
                elif status_code == 404:
                    error_msg = f"所有尝试的模型都不存在 (HTTP 404): {', '.join(unique_models)}"
                elif status_code == 429:
                    error_msg = f"请求过于频繁 (HTTP 429)，请稍后重试"
                else:
                    error_msg = f"API调用失败 (HTTP {status_code}): {error_text}"
                
                return {
                    'success': False,
                    'error': error_msg,
                    'provider': 'google',
                    'model': model,
                    'timestamp': datetime.now().isoformat(),
                    'debug_info': {
                        'tried_models': unique_models,
                        'last_error': last_error
                    }
                }
            else:
                return {
                    'success': False,
                    'error': last_error.get('error', 'Unknown error'),
                    'provider': 'google',
                    'model': model,
                    'timestamp': datetime.now().isoformat(),
                    'debug_info': {
                        'tried_models': unique_models,
                        'last_error': last_error
                    }
                }
        
        # 理论上不应该到达这里
        return {
            'success': False,
            'error': 'Unknown connectivity test failure',
            'provider': 'google',
            'model': model,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Google API连通性测试异常: {e}", exc_info=True)
        return {
            'success': False,
            'error': f'连通性测试异常: {str(e)}',
            'provider': 'google',
            'model': model,
            'timestamp': datetime.now().isoformat()
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