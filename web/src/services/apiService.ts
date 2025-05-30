import { Stock, NewStockData, AlertInfo } from '../types/types';

const API_BASE_URL = 'http://127.0.0.1:5000';

/**
 * 获取关注列表
 * @returns 股票列表 Promise
 */
export const fetchWatchlist = async (): Promise<Stock[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/watchlist`);
    
    if (!response.ok) {
      throw new Error(`获取关注列表失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    return data as Stock[];
  } catch (error) {
    console.error('获取关注列表出错:', error);
    throw error;
  }
};

/**
 * 添加股票到关注列表
 * @param stockData 股票数据
 * @returns 添加结果 Promise
 */
export const addStock = async (stockData: NewStockData): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/add_stock`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(stockData),
    });
    
    if (!response.ok) {
      throw new Error(`添加股票失败: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('添加股票出错:', error);
    throw error;
  }
};

/**
 * 检查告警状态
 * @returns 告警信息 Promise，如无告警则返回null
 */
export const checkAlertsStatus = async (): Promise<AlertInfo | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/check_alerts_status`);
    
    if (!response.ok) {
      throw new Error(`检查告警状态失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // 如果没有告警，后端可能返回空对象或特定标识
    if (!data || Object.keys(data).length === 0) {
      return null;
    }
    
    return data as AlertInfo;
  } catch (error) {
    console.error('检查告警状态出错:', error);
    throw error;
  }
}; 