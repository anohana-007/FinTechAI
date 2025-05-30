// 模拟的股票数据
const mockStocks = [
  {
    id: 1,
    code: 'SH600000',
    name: '浦发银行',
    price: 10.24,
    change: 0.34,
    upperLimit: 11.26,
    lowerLimit: 9.22
  },
  {
    id: 2,
    code: 'SZ000001',
    name: '平安银行',
    price: 15.78,
    change: -0.42,
    upperLimit: 17.36,
    lowerLimit: 14.20
  },
  {
    id: 3,
    code: 'SH601398',
    name: '工商银行',
    price: 5.43,
    change: 0.12,
    upperLimit: 5.97,
    lowerLimit: 4.89
  },
  {
    id: 4,
    code: 'SH601988',
    name: '中国银行',
    price: 3.67,
    change: 0.05,
    upperLimit: 4.04,
    lowerLimit: 3.30
  },
  {
    id: 5,
    code: 'SZ000063',
    name: '中兴通讯',
    price: 34.56,
    change: -1.23,
    upperLimit: 38.02,
    lowerLimit: 31.10
  }
];

// 获取所有股票
export const getAllStocks = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(mockStocks);
    }, 500);
  });
};

// 根据代码获取单个股票
export const getStockByCode = (code: string) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const stock = mockStocks.find(s => s.code === code);
      if (stock) {
        resolve(stock);
      } else {
        reject(new Error('股票未找到'));
      }
    }, 300);
  });
};

// 模拟搜索股票
export const searchStocks = (query: string) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const results = mockStocks.filter(
        s => s.code.includes(query) || s.name.includes(query)
      );
      resolve(results);
    }, 300);
  });
}; 