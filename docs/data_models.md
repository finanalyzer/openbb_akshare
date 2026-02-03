# OpenBB 数据模型分析文档

## 概述

`openbb_akshare` 项目实现了 21 个 OpenBB 标准数据模型，通过 AKShare 提供中国金融市场的数据接口。本文档详细分析每个数据模型的实现细节、数据来源和特性。

## 数据模型分类

### 1. 股票相关模型 (Equity Models)

#### 1.1 Equity Historical Price (股票历史价格)

**文件**: `equity_historical.py`

**数据源**: AKShare

**查询参数**:
- `symbol`: 股票代码（支持多个）
- `start_date`: 开始日期（默认为一年前）
- `end_date`: 结束日期（默认为今天）
- `period`: 周期（daily/weekly/monthly，默认 daily）
- `use_cache`: 是否使用缓存（默认 True）

**数据字段**:
- `date`: 日期
- `open`: 开盘价
- `close`: 收盘价
- `high`: 最高价
- `low`: 最低价
- `volume`: 成交量
- `change`: 涨跌额
- `change_percent`: 涨跌幅
- `amount`: 成交额

**特性**:
- 支持 A 股和港股
- 使用缓存机制优化性能
- 通过 `ak_download` 辅助函数获取数据

---

#### 1.2 Equity Quote (股票实时报价)

**文件**: `equity_quote.py`

**数据源**: AKShare（通过缓存）

**查询参数**:
- `symbol`: 股票代码（支持多个，逗号分隔）
- `use_cache`: 是否使用缓存（默认 True）

**数据字段**:
- `symbol`: 代码
- `name`: 名称
- `last_price`: 最新价
- `open`: 今开
- `high`: 最高
- `low`: 最低
- `prev_close`: 昨收
- `volume`: 成交量
- `change`: 涨跌额
- `change_percent`: 涨跌幅

**特性**:
- 使用 `normalize_symbol` 标准化股票代码
- 支持多市场（A股、港股）
- 从缓存加载实时报价数据

---

#### 1.3 Equity Profile (股票概况)

**文件**: `equity_profile.py`

**数据源**: AKShare

**查询参数**:
- `symbol`: 股票代码（支持多个）
- `use_cache`: 是否使用缓存（默认 True）

**数据字段**:
- `symbol`: 股票代码
- `name`: 公司名称（英文）
- `公司名称`: 公司名称（中文）
- `公司简介`: 公司简介
- `主要范围`: 主要经营范围
- `上市日期`: 上市日期
- `established_date`: 成立日期
- `ceo`: 董事长
- `company_url`: 公司网站
- `business_address`: 注册地址（中文）
- `mailing_address`: 办公地址（中文）
- `business_phone_no`: 联系电话
- `hq_address_postal_code`: 邮编
- `hq_state`: 省份
- `employees`: 员工人数
- `sector`: 所属行业
- `industry_category`: 经营范围
- `currency`: 交易货币

**特性**:
- 支持异步数据获取
- 包含中英文双语信息
- 日期字段经过验证和处理
- 使用 Pandas 验证器处理空值

---

#### 1.4 Equity Search (股票搜索)

**文件**: `equity_search.py`

**数据源**: AKShare

**查询参数**:
- `query`: 搜索关键词（可选）
- `use_cache`: 是否使用缓存（默认 True）
- `limit`: 返回数量限制（默认 10000）

**数据字段**:
- 继承自 `EquitySearchData` 标准字段

**特性**:
- 支持按名称或代码搜索
- 自动去除交易所后缀（.SS, .SH, .HK, .BJ, .SZ）
- 使用 `get_symbols` 工具函数获取股票列表

---

#### 1.5 Equity Screener (股票筛选器)

**文件**: `equity_screener.py`

**数据源**: AKShare（通过缓存）

**查询参数**:
- `exchange`: 交易所（可选）
- `sector`: 行业（可选）
- `use_cache`: 是否使用缓存（默认 True）
- `limit`: 返回数量限制（默认 1000）

**数据字段**:
- `symbol`: 代码
- `name`: 名称
- `sector`: 行业
- `exchange`: 交易所

**特性**:
- 支持按交易所和行业筛选
- 支持多个交易所（上海、深圳、北京）
- 从缓存加载市场数据

---

#### 1.6 Equity Ownership (股权结构)

**文件**: `equity_ownership.py`

**数据源**: AKShare（东方财富）

**查询参数**:
- `symbol`: 股票代码
- `date`: 日期（自动计算最近季度）

**数据字段**:
- 继承自 `EquityOwnershipData` 标准字段

**特性**:
- 使用 `most_recent_quarter` 自动计算最近季度
- 获取前十大股东信息
- 按 filing_date 降序排列

---

#### 1.7 Historical Dividends (历史分红)

**文件**: `historical_dividends.py`

**数据源**: AKShare

**查询参数**:
- `symbol`: 股票代码

**数据字段**:
- `symbol`: 股票代码
- `amount`: 分红金额
- `ex_dividend_date`: 除权除息日
- `record_date`: 股权登记日
- `declaration_date`: 公告日期
- `reported_date`: 公告日期
- `description`: 描述

**特性**:
- 支持 A 股和港股
- 使用 `normalize_symbol` 识别市场
- 日期字段经过验证

---

### 2. 财务报表模型 (Financial Statement Models)

#### 2.1 Balance Sheet (资产负债表)

**文件**: `balance_sheet.py`

**数据源**: AKShare（东方财富）

**查询参数**:
- `symbol`: 股票代码
- `period`: 周期（annual/quarter，默认 annual）
- `limit`: 返回数量限制（默认 5）
- `use_cache`: 是否使用缓存（默认 True）

**数据字段**:
- `period_ending`: 报告日期
- `fiscal_period`: 报告类型
- `reported_currency`: 报告货币
- `总资产`: 总资产
- `总负债`: 总负债
- `总权益`: 总权益

**特性**:
- 使用 BlobCache 实现缓存
- 支持年度和季度数据
- 日期格式转换（字符串 → datetime）

---

#### 2.2 Income Statement (利润表)

**文件**: `income_statement.py`

**数据源**: AKShare（东方财富）

**查询参数**:
- `symbol`: 股票代码
- `period`: 周期（annual/quarter，默认 annual）
- `limit`: 返回数量限制（默认 5）
- `use_cache`: 是否使用缓存（默认 True）

**数据字段**:
- `period_ending`: 报告日期
- `fiscal_period`: 报告类型
- `reported_currency`: 报告货币
- `总营收`: 总营业收入
- `净利润`: 净利润

**特性**:
- 使用 BlobCache 实现缓存
- 零值替换为 None
- 移除 symbol 和 cik 字段

---

#### 2.3 Cash Flow Statement (现金流量表)

**文件**: `cash_flow.py`

**数据源**: AKShare（东方财富）

**查询参数**:
- `symbol`: 股票代码
- `period`: 周期（annual/quarter，默认 annual）
- `limit`: 返回数量限制（默认 5）
- `use_cache`: 是否使用缓存（默认 True）

**数据字段**:
- `period_ending`: 报告日期
- `fiscal_period`: 报告类型
- `reported_currency`: 报告货币
- `营业性现金流`: 经营活动现金流
- `投资性现金流`: 投资活动现金流
- `融资性现金流`: 筹资活动现金流

**特性**:
- 使用 BlobCache 实现缓存
- 日期格式转换
- 支持年度和季度数据

---

#### 2.4 Key Metrics (关键指标)

**文件**: `key_metrics.py`

**数据源**: AKShare（东方财富）

**查询参数**:
- `symbol`: 股票代码（支持多个）
- `period`: 周期（annual/quarter，默认 quarter）
- `use_cache`: 是否使用缓存（默认 True）

**数据字段**:
- `symbol`: 证券代码
- `fiscal_period`: 报告类型
- `period_ending`: 报告日期
- `market_cap`: 流通市值
- `pe_ratio`: 市盈率（动态）

**特性**:
- 支持异步数据获取
- 使用 `fetch_key_metrics` 工具函数
- 返回字典格式的指标数据

---

### 3. 市场分析模型 (Market Analysis Models)

#### 3.1 Company News (公司新闻)

**文件**: `company_news.py`

**数据源**: 
- A 股：东方财富（stock_info_em）
- 港股：新浪（scrape_hk_stock_news）

**查询参数**:
- `symbol`: 股票代码（支持多个，逗号分隔）

**数据字段**:
- `date`: 日期
- `title`: 标题
- `url`: 链接
- `source`: 来源

**特性**:
- 支持别名（query, symbols, ticker, tickers）
- 自动识别市场（A股/港股）
- 异步获取多个股票的新闻
- 使用 EmptyDataError 处理无数据情况

---

#### 3.2 Business Analysis (业务分析)

**文件**: `business_analysis.py`

**数据源**: AKShare（东方财富）

**查询参数**:
- `symbol`: 股票代码

**数据字段**:
- `symbol`: 股票代码
- `report_date`: 报告日期
- `category_type`: 分类类型（按产品分类/按行业分类）
- `main_composition`: 主营构成
- `main_revenue`: 主营收入
- `revenue_ratio`: 收入比例
- `main_cost`: 主营成本
- `cost_ratio`: 成本比例
- `main_profit`: 主营利润
- `profit_ratio`: 利润比例
- `gross_margin`: 毛利率

**特性**:
- 使用 `convert_stock_code_format` 转换代码格式
- 自动填充缺失的分类类型
- 将 NaN 替换为 None
- 标准化股票代码格式

---

#### 3.3 Price Performance (价格表现)

**文件**: `price_performance.py`

**数据源**: AKShare + 自定义计算

**查询参数**:
- `symbol`: 股票代码（支持多个）

**数据字段**:
- `symbol`: 股票代码
- `one_day`: 1日涨跌幅
- `one_week`: 5日涨跌幅
- `one_month`: 1月涨跌幅
- `three_month`: 3月涨跌幅
- `six_month`: 6月涨跌幅
- `one_year`: 1年涨跌幅
- `three_year`: 3年涨跌幅
- `five_year`: 5年涨跌幅
- `ten_year`: 10年涨跌幅

**特性**:
- 使用 `calculate_price_performance` 计算各周期涨跌幅
- 零值替换为 None
- 百分比转换为标准化值（除以 100）
- 异步获取多个股票数据

---

### 4. 基金相关模型 (Fund Models)

#### 4.1 ETF Holdings (ETF 持仓)

**文件**: `etf_holdings.py`

**数据源**: AKShare（东方财富）

**查询参数**:
- `symbol`: ETF 代码（支持 Yahoo 格式）
- `year`: 年份（默认 2024）
- `quarter`: 季度（默认 4）
- `use_cache`: 是否使用缓存（默认 True）

**数据字段**:
- `symbol`: 股票代码
- `name`: 股票名称
- `balance`: 持股数
- `value`: 持仓市值
- `weight`: 占净值比例
- `acceptance_datetime`: 季度

**特性**:
- 支持多种代码格式（510300.SS, SH510300, 510300）
- 使用正则表达式验证代码格式
- 按季度筛选数据
- 权重百分比标准化
- 空值处理（空字符串、0、"-" 替换为 None）

---

#### 4.2 ETF Search (ETF 搜索)

**文件**: `etf_search.py`

**数据源**: AKShare（多种 API）

**查询参数**:
- `query`: 搜索关键词（可选）
- `use_cache`: 是否使用缓存（默认 True）
- `limit`: 返回数量限制（默认 10000）

**数据字段**:
- `symbol`: 代码
- `name`: 名称

**特性**:
- 多 API 备用策略：
  1. `fund_name_em` - 基金名称列表
  2. `fund_etf_spot_em` - ETF 实时数据
  3. `fund_etf_category_sina` - 新浪 ETF 分类
  4. `fund_etf_fund_info_em` - ETF 基金信息
- 列名智能映射（支持多种列名变体）
- 支持按代码或名称搜索
- 详细的日志记录用于调试

---

#### 4.3 Fund Holdings (基金持仓)

**文件**: `fund_holdings.py`

**数据源**: AKShare（东方财富）

**查询参数**:
- `symbol`: 基金代码（支持 Yahoo 格式）
- `date`: 日期（格式 YYYY-MM-DD，默认 2024-01-01）
- `use_cache`: 是否使用缓存（默认 True）

**数据字段**:
- `symbol`: 股票代码
- `name`: 股票名称
- `balance`: 持股数
- `value`: 持仓市值
- `weight`: 占净值比例
- `acceptance_datetime`: 季度

**特性**:
- 日期格式验证（YYYY-MM-DD）
- 代码格式规范化
- 使用年份提取季度数据
- 与 ETF Holdings 类似的空值处理逻辑

---

### 5. 货币相关模型 (Currency Models)

#### 5.1 Currency Historical (货币历史价格)

**文件**: `currency_historical.py`

**数据源**: AKShare（东方财富）

**查询参数**:
- `symbol`: 货币对代码
- `start_date`: 开始日期（默认一年前）
- `end_date`: 结束日期（默认今天）
- `interval`: 时间间隔（1m/5m/15m/30m/1h/4h/1d，默认 1d）

**数据字段**:
- `date`: 日期
- `open`: 今开
- `high`: 最高
- `low`: 最低
- `close`: 最新价
- `change`: 振幅
- `symbol`: 代码
- `name`: 名称

**特性**:
- 使用 `forex_hist_em` 获取外汇历史数据
- 自动设置默认日期范围（一年）
- 支持多种时间间隔

---

#### 5.2 Currency Snapshots (货币快照)

**文件**: `currency_snapshots.py`

**数据源**: AKShare（东方财富）

**查询参数**:
- `base`: 基础货币（支持多个）

**数据字段**:
- `last_rate`: 最新价
- `open`: 今开
- `high`: 最高
- `low`: 最低
- `base_currency`: 代码
- `counter_currency`: 名称
- `prev_close`: 昨收
- `change`: 涨跌额
- `change_percent`: 涨跌幅

**特性**:
- 使用 `forex_spot_em` 获取实时外汇数据
- 移除"序号"列
- 涨跌幅百分比标准化（除以 100）

---

### 6. 指数相关模型 (Index Models)

#### 6.1 Available Indices (可用指数)

**文件**: `available_indices.py`

**数据源**: AKShare

**查询参数**:
- 无特定参数

**数据字段**:
- `symbol`: 指数代码
- `name`: 指数名称
- `publish_date`: 发布日期

**特性**:
- 使用 `index_stock_info` 获取指数信息
- 自动添加货币字段（CNY）
- 字段别名映射（display_name → name, index_code → symbol）

---

### 7. 标准模型 (Standard Models)

#### 7.1 Business Analysis (业务分析标准模型)

**文件**: `standard_models/business_analysis.py`

**查询参数**:
- `symbol`: 股票代码（自动转大写）

**数据字段**:
- `symbol`: 股票代码
- `report_date`: 报告日期
- `main_composition`: 主营构成

**特性**:
- 使用 `field_validator` 自动转大写
- 作为基础数据模型被 `AkshareBusinessAnalysisData` 继承

---

#### 7.2 Fund Holdings (基金持仓标准模型)

**文件**: `standard_models/fund_holdings.py`

**查询参数**:
- `symbol`: 基金代码（自动转大写）

**数据字段**:
- `symbol`: 基金代码
- `name`: 基金持仓名称

**特性**:
- 使用 `field_validator` 自动转大写
- 作为基础数据模型被 `AkshareFundHoldingsData` 继承

---

## 通用特性分析

### 1. 缓存机制

多数模型实现了缓存功能，使用：
- `BlobCache`: 用于财务报表数据（balance_sheet, cash_flow, income_statement）
- `load_cached_data`: 用于股票报价和筛选器数据
- `use_cache` 参数：控制是否使用缓存

### 2. 代码规范化

使用 `normalize_symbol` 工具函数处理：
- 支持多种代码格式（000002, 000002.SZ, SZ000002）
- 自动识别市场（A股/港股）
- 统一输出标准格式

### 3. 异步支持

部分 Fetcher 实现了异步方法：
- `aextract_data`: 异步数据提取
- `asyncio.gather`: 并发获取多个数据源
- 主要用于需要多次 API 调用的场景

### 4. 数据验证

使用 Pydantic 验证器：
- `field_validator`: 字段级验证（日期格式、代码格式等）
- `model_validator`: 模型级验证（零值替换、百分比转换等）
- 类型提示和 Optional 处理

### 5. 错误处理

统一的错误处理策略：
- `EmptyDataError`: 无数据时抛出
- `OpenBBError`: 通用错误
- `RuntimeError`: 运行时错误
- `ValueError`: 参数验证错误

### 6. 字段别名

使用 `__alias_dict__` 实现字段映射：
- 中文列名映射到英文字段名
- 支持多种数据源的列名变体
- 保持数据模型的一致性

### 7. 数据来源

主要数据源：
- **东方财富**：财务报表、股票信息、基金持仓
- **新浪**：港股新闻
- **AKShare API**：市场数据、指数数据
- **自定义计算**：价格表现、关键指标

## 性能优化建议

1. **缓存策略**：财务报表数据使用 BlobCache，有效期可配置
2. **批量请求**：支持多个股票代码的批量查询
3. **异步处理**：新闻搜索等耗时操作使用异步方法
4. **数据预处理**：在 `transform_data` 中统一处理数据格式

## 扩展性设计

1. **模块化结构**：每个模型独立文件，易于维护
2. **标准接口**：遵循 OpenBB Provider 规范
3. **工具函数分离**：utils 目录存放可复用逻辑
4. **配置灵活**：通过参数控制缓存、限制等行为

## 数据质量保障

1. **空值处理**：统一使用 None 替代空字符串和零值
2. **日期验证**：确保日期格式正确且有效
3. **类型转换**：自动处理数值和百分比转换
4. **异常捕获**：完善的错误处理和日志记录

---

**文档版本**: 1.0  
**最后更新**: 2026-02-02  
**维护者**: openbb_akshare 项目团队