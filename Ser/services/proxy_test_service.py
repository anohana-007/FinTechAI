#!/usr/bin/env python3
"""
代理连通性测试服务
用于测试代理配置是否正确工作
"""

import requests
import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger('proxy_test_service')

def test_proxy_connectivity(proxy_settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    测试代理连通性
    
    参数:
    proxy_settings (dict): 代理配置
    
    返回:
    dict: 测试结果
    """
    try:
        logger.info("开始代理连通性测试")
        
        if not proxy_settings.get('enabled'):
            return {
                'success': False,
                'error': '代理未启用',
                'timestamp': datetime.now().isoformat()
            }
        
        # 验证代理配置
        validation_result = validate_proxy_settings(proxy_settings)
        if not validation_result['valid']:
            return {
                'success': False,
                'error': f"代理配置无效: {', '.join(validation_result['errors'])}",
                'timestamp': datetime.now().isoformat()
            }
        
        # 构建代理URL
        proxy_url = _build_proxy_url(proxy_settings)
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        logger.info(f"使用代理: {proxy_settings.get('host')}:{proxy_settings.get('port')}")
        
        # 执行各项测试
        test_results = []
        start_time = time.time()
        
        # 1. IP获取测试
        ip_test = _test_ip_check(proxies)
        test_results.append(ip_test)
        
        # 2. HTTPS连接测试
        https_test = _test_https_connection(proxies)
        test_results.append(https_test)
        
        # 3. 响应时间测试
        speed_test = _test_response_time(proxies)
        test_results.append(speed_test)
        
        total_time = time.time() - start_time
        
        # 统计结果
        successful_tests = sum(1 for test in test_results if test['success'])
        failed_tests = len(test_results) - successful_tests
        
        # 计算平均响应时间
        response_times = [test.get('response_time', 0) for test in test_results if test.get('response_time')]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        overall_success = successful_tests > 0  # 至少有一个测试成功
        
        result = {
            'success': overall_success,
            'message': f'代理连接{"成功" if overall_success else "失败"}，{successful_tests}/{len(test_results)} 项测试通过',
            'timestamp': datetime.now().isoformat(),
            'proxy_config': {
                'host': proxy_settings.get('host'),
                'port': proxy_settings.get('port'),
                'protocol': proxy_settings.get('protocol', 'http'),
                'has_auth': bool(proxy_settings.get('username') and proxy_settings.get('password'))
            },
            'test_results': test_results,
            'summary': {
                'total_tests': len(test_results),
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'average_response_time': round(avg_response_time),
                'total_test_time': round(total_time, 2)
            }
        }
        
        logger.info(f"代理测试完成: {successful_tests}/{len(test_results)} 项测试通过")
        return result
        
    except Exception as e:
        logger.error(f"代理连通性测试异常: {e}", exc_info=True)
        return {
            'success': False,
            'error': f'测试过程中发生异常: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }

def validate_proxy_settings(proxy_settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证代理设置
    
    参数:
    proxy_settings (dict): 代理配置
    
    返回:
    dict: 验证结果
    """
    errors = []
    
    # 检查必要字段
    if not proxy_settings.get('host'):
        errors.append('代理服务器地址不能为空')
    
    if not proxy_settings.get('port'):
        errors.append('代理端口不能为空')
    else:
        try:
            port = int(proxy_settings['port'])
            if not (1 <= port <= 65535):
                errors.append('代理端口必须在1-65535范围内')
        except (ValueError, TypeError):
            errors.append('代理端口必须是有效的数字')
    
    # 检查协议
    protocol = proxy_settings.get('protocol', 'http')
    if protocol not in ['http', 'https', 'socks5']:
        errors.append('代理协议必须是http、https或socks5')
    
    # 检查认证信息（如果有）
    username = proxy_settings.get('username')
    password = proxy_settings.get('password')
    if username and not password:
        errors.append('如果设置了用户名，密码不能为空')
    if password and not username:
        errors.append('如果设置了密码，用户名不能为空')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def _build_proxy_url(proxy_settings: Dict[str, Any]) -> str:
    """构建代理URL"""
    protocol = proxy_settings.get('protocol', 'http')
    host = proxy_settings.get('host')
    port = proxy_settings.get('port')
    username = proxy_settings.get('username')
    password = proxy_settings.get('password')
    
    if username and password:
        return f"{protocol}://{username}:{password}@{host}:{port}"
    else:
        return f"{protocol}://{host}:{port}"

def _test_ip_check(proxies: Dict[str, str]) -> Dict[str, Any]:
    """测试IP获取"""
    test_name = "IP获取测试"
    try:
        logger.info(f"执行{test_name}...")
        start_time = time.time()
        
        response = requests.get(
            'https://httpbin.org/ip',
            proxies=proxies,
            timeout=10,
            verify=False  # 对于测试，忽略SSL验证
        )
        
        response_time = round((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            data = response.json()
            ip = data.get('origin', 'unknown')
            logger.info(f"{test_name}成功: IP={ip}")
            return {
                'test': test_name,
                'success': True,
                'response_time': response_time,
                'data': {'ip': ip}
            }
        else:
            logger.error(f"{test_name}失败: HTTP {response.status_code}")
            return {
                'test': test_name,
                'success': False,
                'error': f'HTTP {response.status_code}',
                'response_time': response_time
            }
    
    except requests.exceptions.Timeout:
        return {
            'test': test_name,
            'success': False,
            'error': '请求超时'
        }
    except requests.exceptions.ConnectionError as e:
        return {
            'test': test_name,
            'success': False,
            'error': f'连接失败: {str(e)}'
        }
    except Exception as e:
        return {
            'test': test_name,
            'success': False,
            'error': f'测试异常: {str(e)}'
        }

def _test_https_connection(proxies: Dict[str, str]) -> Dict[str, Any]:
    """测试HTTPS连接"""
    test_name = "HTTPS连接测试"
    try:
        logger.info(f"执行{test_name}...")
        start_time = time.time()
        
        response = requests.get(
            'https://www.google.com',
            proxies=proxies,
            timeout=10,
            verify=False  # 对于测试，忽略SSL验证
        )
        
        response_time = round((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            logger.info(f"{test_name}成功")
            return {
                'test': test_name,
                'success': True,
                'response_time': response_time,
                'data': {'status': 'HTTPS连接正常'}
            }
        else:
            logger.error(f"{test_name}失败: HTTP {response.status_code}")
            return {
                'test': test_name,
                'success': False,
                'error': f'HTTP {response.status_code}',
                'response_time': response_time
            }
    
    except requests.exceptions.Timeout:
        return {
            'test': test_name,
            'success': False,
            'error': '请求超时'
        }
    except requests.exceptions.ConnectionError as e:
        return {
            'test': test_name,
            'success': False,
            'error': f'连接失败: {str(e)}'
        }
    except Exception as e:
        return {
            'test': test_name,
            'success': False,
            'error': f'测试异常: {str(e)}'
        }

def _test_response_time(proxies: Dict[str, str]) -> Dict[str, Any]:
    """测试响应时间"""
    test_name = "响应时间测试"
    try:
        logger.info(f"执行{test_name}...")
        
        # 进行3次测试取平均值
        response_times = []
        for i in range(3):
            start_time = time.time()
            
            response = requests.get(
                'https://httpbin.org/status/200',
                proxies=proxies,
                timeout=5,
                verify=False
            )
            
            if response.status_code == 200:
                response_time = round((time.time() - start_time) * 1000)
                response_times.append(response_time)
            else:
                # 如果有任何一次失败，返回失败
                return {
                    'test': test_name,
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
        
        avg_response_time = round(sum(response_times) / len(response_times))
        
        logger.info(f"{test_name}成功: 平均响应时间 {avg_response_time}ms")
        return {
            'test': test_name,
            'success': True,
            'response_time': avg_response_time,
            'data': {
                'average_time': avg_response_time,
                'individual_times': response_times
            }
        }
    
    except requests.exceptions.Timeout:
        return {
            'test': test_name,
            'success': False,
            'error': '请求超时'
        }
    except requests.exceptions.ConnectionError as e:
        return {
            'test': test_name,
            'success': False,
            'error': f'连接失败: {str(e)}'
        }
    except Exception as e:
        return {
            'test': test_name,
            'success': False,
            'error': f'测试异常: {str(e)}'
        } 