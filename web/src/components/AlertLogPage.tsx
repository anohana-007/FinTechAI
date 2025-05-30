import React, { useState, useEffect } from 'react';
import { AlertLogEntry, AlertLogResponse, PaginationParams } from '../types/types';
import { fetchAlertLog } from '../services/apiService';

interface AlertLogPageProps {
  userEmail?: string;
  onBack?: () => void;
}

const AlertLogPage: React.FC<AlertLogPageProps> = ({ userEmail = 'user@example.com', onBack }) => {
  const [logs, setLogs] = useState<AlertLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 20,
    total_count: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false,
  });

  // 过滤参数
  const [filters, setFilters] = useState<PaginationParams>({
    page: 1,
    page_size: 20,
  });

  const [filterForm, setFilterForm] = useState({
    stock_code: '',
    start_date: '',
    end_date: '',
  });

  useEffect(() => {
    loadAlertLogs();
  }, [filters]);

  const loadAlertLogs = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params: PaginationParams = {
        ...filters,
        user_email: userEmail,
      };

      const response: AlertLogResponse = await fetchAlertLog(params);
      
      if (response.success) {
        setLogs(response.data);
        setPagination(response.pagination);
      } else {
        setError('获取告警日志失败');
      }
    } catch (err) {
      console.error('加载告警日志出错:', err);
      setError('加载告警日志失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage: number) => {
    setFilters(prev => ({ ...prev, page: newPage }));
  };

  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters(prev => ({
      ...prev,
      page: 1, // 重置到第一页
      stock_code: filterForm.stock_code || undefined,
      start_date: filterForm.start_date || undefined,
      end_date: filterForm.end_date || undefined,
    }));
  };

  const handleResetFilters = () => {
    setFilterForm({
      stock_code: '',
      start_date: '',
      end_date: '',
    });
    setFilters({
      page: 1,
      page_size: 20,
    });
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const getDirectionText = (direction: 'UP' | 'DOWN') => {
    return direction === 'UP' ? '突破上限' : '跌破下限';
  };

  const getDirectionColor = (direction: 'UP' | 'DOWN') => {
    return direction === 'UP' ? 'text-red-600 bg-red-100' : 'text-green-600 bg-green-100';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          {onBack && (
            <button
              onClick={onBack}
              className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              返回仪表盘
            </button>
          )}
          <div>
            <h1 className="text-3xl font-bold text-gray-900">历史告警日志</h1>
            <p className="mt-2 text-sm text-gray-600">
              查看所有股票价格突破阈值的历史记录
            </p>
          </div>
        </div>
      </div>

      {/* 过滤器 */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium text-gray-900">筛选条件</h2>
          {onBack && (
            <button
              onClick={onBack}
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              返回
            </button>
          )}
        </div>
        
        <form onSubmit={handleFilterSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                股票代码
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                placeholder="如：600036.SH"
                value={filterForm.stock_code}
                onChange={(e) => setFilterForm(prev => ({ ...prev, stock_code: e.target.value }))}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                开始日期
              </label>
              <input
                type="date"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                value={filterForm.start_date}
                onChange={(e) => setFilterForm(prev => ({ ...prev, start_date: e.target.value }))}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                结束日期
              </label>
              <input
                type="date"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                value={filterForm.end_date}
                onChange={(e) => setFilterForm(prev => ({ ...prev, end_date: e.target.value }))}
              />
            </div>
          </div>
          
          <div className="flex space-x-4">
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              搜索
            </button>
            <button
              type="button"
              onClick={handleResetFilters}
              className="px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              重置
            </button>
          </div>
        </form>
      </div>

      {/* 错误信息 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
          <div className="flex">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* 告警日志列表 */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        {logs.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">暂无告警记录</h3>
            <p className="mt-1 text-sm text-gray-500">当股票价格突破阈值时会产生告警记录</p>
          </div>
        ) : (
          <>
            {/* 表头 */}
            <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
              <div className="grid grid-cols-7 gap-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
                <div>股票信息</div>
                <div>告警时间</div>
                <div>触发价格</div>
                <div>阈值价格</div>
                <div>突破方向</div>
                <div>AI分析</div>
                <div>创建时间</div>
              </div>
            </div>

            {/* 表格内容 */}
            <div className="divide-y divide-gray-200">
              {logs.map((log) => (
                <div key={log.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="grid grid-cols-7 gap-4">
                    {/* 股票信息 */}
                    <div className="flex flex-col">
                      <div className="text-sm font-medium text-gray-900">
                        {log.stock_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {log.stock_code}
                      </div>
                    </div>

                    {/* 告警时间 */}
                    <div className="text-sm text-gray-900">
                      {formatDateTime(log.alert_timestamp)}
                    </div>

                    {/* 触发价格 */}
                    <div className="text-sm font-medium text-gray-900">
                      ¥{log.triggered_price.toFixed(2)}
                    </div>

                    {/* 阈值价格 */}
                    <div className="text-sm text-gray-500">
                      ¥{log.threshold_price.toFixed(2)}
                    </div>

                    {/* 突破方向 */}
                    <div>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getDirectionColor(log.direction)}`}>
                        {getDirectionText(log.direction)}
                      </span>
                    </div>

                    {/* AI分析 */}
                    <div className="text-sm text-gray-500">
                      {log.ai_analysis ? (
                        <div title={log.ai_analysis} className="truncate max-w-xs">
                          {log.ai_analysis}
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </div>

                    {/* 创建时间 */}
                    <div className="text-sm text-gray-500">
                      {formatDateTime(log.created_at)}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* 分页 */}
            {pagination.total_pages > 1 && (
              <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1 flex justify-between sm:hidden">
                    <button
                      onClick={() => handlePageChange(pagination.page - 1)}
                      disabled={!pagination.has_prev}
                      className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      上一页
                    </button>
                    <button
                      onClick={() => handlePageChange(pagination.page + 1)}
                      disabled={!pagination.has_next}
                      className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      下一页
                    </button>
                  </div>
                  <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm text-gray-700">
                        显示第 <span className="font-medium">{(pagination.page - 1) * pagination.page_size + 1}</span> 到{' '}
                        <span className="font-medium">{Math.min(pagination.page * pagination.page_size, pagination.total_count)}</span> 条，
                        共 <span className="font-medium">{pagination.total_count}</span> 条记录
                      </p>
                    </div>
                    <div>
                      <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                        <button
                          onClick={() => handlePageChange(pagination.page - 1)}
                          disabled={!pagination.has_prev}
                          className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          上一页
                        </button>
                        
                        {/* 页码按钮 */}
                        {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                          const page = Math.max(1, pagination.page - 2) + i;
                          if (page > pagination.total_pages) return null;
                          
                          return (
                            <button
                              key={page}
                              onClick={() => handlePageChange(page)}
                              className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                                page === pagination.page
                                  ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                                  : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                              }`}
                            >
                              {page}
                            </button>
                          );
                        })}
                        
                        <button
                          onClick={() => handlePageChange(pagination.page + 1)}
                          disabled={!pagination.has_next}
                          className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          下一页
                        </button>
                      </nav>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default AlertLogPage; 