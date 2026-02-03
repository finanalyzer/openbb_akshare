# openbb_akshare 项目上下文

## 项目概述

**openbb_akshare** 是 OpenBB Platform 的数据源扩展插件，将中国金融数据聚合库 AKShare 集成到 OpenBB 平台中。该项目解决了中国内地用户访问 OpenBB 时需要 VPN 的痛点，通过 AKShare 提供本地化的 A 股、港股等市场数据接口。

### 核心功能

- **股票数据**: A 股和港股的历史价格、实时报价、公司概况、股票搜索、股权结构等
- **财务数据**: 资产负债表、现金流量表、利润表、关键指标等
- **市场分析**: 公司新闻、价格表现、业务分析等
- **基金数据**: ETF 持仓、基金持仓、ETF 搜索等
- **货币数据**: 货币历史价格、货币快照等
- **指数数据**: 可用指数列表

### 技术栈

- **Python**: 3.11 - 3.12
- **核心依赖**:
  - `akshare` (1.18.19): 中国金融数据聚合库
  - `openbb` (4.6.0): OpenBB Platform 核心库
  - `openbb-core` (^1.5.8): OpenBB 核心接口
  - `mysharelib` (^1.0.4): 自定义工具库
- **开发依赖**:
  - `pytest` (9.0.1): 测试框架
  - `ipykernel` (6.30.1): Jupyter 内核
  - `uvicorn` (0.40.0): ASGI 服务器

### 项目架构

```
openbb_akshare/
├── openbb_akshare/          # 主包目录
│   ├── __init__.py          # Provider 定义和导出
│   ├── openbb.py            # 应用工厂和扩展构建
│   ├── router.py            # 路由命令定义
│   ├── models/              # 数据获取器 (Fetchers)
│   │   ├── available_indices.py
│   │   ├── balance_sheet.py
│   │   ├── business_analysis.py
│   │   ├── cash_flow.py
│   │   ├── company_news.py
│   │   ├── currency_historical.py
│   │   ├── currency_snapshots.py
│   │   ├── equity_historical.py
│   │   ├── equity_ownership.py
│   │   ├── equity_profile.py
│   │   ├── equity_quote.py
│   │   ├── equity_screener.py
│   │   ├── equity_search.py
│   │   ├── etf_holdings.py
│   │   ├── etf_search.py
│   │   ├── fund_holdings.py
│   │   ├── historical_dividends.py
│   │   ├── income_statement.py
│   │   ├── key_metrics.py
│   │   └── price_performance.py
│   ├── standard_models/     # 标准模型定义
│   │   ├── business_analysis.py
│   │   └── fund_holdings.py
│   └── utils/               # 工具函数和辅助模块
│       ├── ak_balance_sheet.py
│       ├── ak_cash_flow.py
│       ├── ak_compare_company_facts.py
│       ├── ak_equity_ownership.py
│       ├── ak_equity_search.py
│       ├── ak_income_statement.py
│       ├── ak_key_metrics.py
│       ├── fetch_equity_info.py
│       ├── fetch_quote.py
│       ├── helpers.py
│       └── references.py
├── tests/                   # 测试文件
│   ├── conftest.py          # Pytest 配置和 fixtures
│   ├── test_*.py            # 各功能模块测试
│   └── debug_*.py           # 调试脚本
└── docs/                    # 文档和图片
```

## 构建和运行

### 环境设置

项目使用 Poetry 进行依赖管理，但也可以使用 pip 安装。

**方法 1: 使用 Poetry**

```bash
# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

**方法 2: 使用 pip**

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source .venv/bin/activate

# 安装依赖
pip install -e .
```

### 构建项目

```bash
# 构建所有模块
python -c "from openbb_akshare import build; build()"

# 或者使用 OpenBB 的构建命令
python -c "import openbb; openbb.build()"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest test_company_news.py

# 运行特定测试函数
pytest test_company_news.py::test_company_news_fetcher

# 显示详细输出
pytest -v

# 显示打印输出
pytest -s
```

### 使用 OpenBB CLI

```bash
# 启动 OpenBB CLI
openbb

# 在 CLI 中使用 akshare 提供商
/news/company --symbol 000002 --provider akshare
/equity/price/historical --symbol 06823 --provider akshare
```

### 在 Python 代码中使用

```python
from openbb import obb

# 获取公司新闻
news = obb.news.company("000002", provider="akshare")

# 获取历史股价
prices = obb.equity.price.historical(
    symbol="06823",
    start_date="2025-06-01",
    end_date="2025-06-10",
    provider="akshare"
)

# 获取财务数据
balance_sheet = obb.equity.fundamental.balance_sheet("000002", provider="akshare")
```

## 开发约定

### 代码风格

- **类型提示**: 使用 Python 类型提示，特别是在函数签名中
- **文档字符串**: 使用 Google 风格的 docstring
- **导入顺序**: 遵循 PEP 8 标准导入顺序
- **命名约定**:
  - Fetcher 类: `AKShare<Name>Fetcher` 或 `Akshare<Name>Fetcher`
  - 模块函数: 使用 snake_case
  - 常量: 使用 UPPER_CASE

### Fetcher 实现

每个数据获取器 (Fetcher) 需要遵循以下模式：

```python
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.<model_name> import <ModelName>QueryParams

class AKShare<Name>Fetcher(Fetcher[<ModelName>QueryParams, List[<ModelName>Data]]):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> <ModelName>QueryParams:
        """转换查询参数。"""
        # 转换逻辑
        return params

    @staticmethod
    def extract_data(query: <ModelName>QueryParams, credentials: Optional[Dict[str, str]], **kwargs) -> List[Dict]:
        """从 AKShare 获取原始数据。"""
        # 调用 akshare 函数
        return raw_data

    @staticmethod
    def transform_data(data: List[Dict], **kwargs) -> List[<ModelName>Data]:
        """转换数据为标准格式。"""
        # 数据转换逻辑
        return transformed_data
```

### Provider 注册

在 `openbb_akshare/__init__.py` 中注册所有 Fetcher：

```python
provider = Provider(
    name="akshare",
    description="Data provider for openbb-akshare.",
    credentials=["api_key"],
    website="https://akshare.akfamily.xyz/",
    fetcher_dict={
        "FetcherName": AKShareFetcherName,
        # ... 其他 fetchers
    }
)
```

### 环境变量

- `AKSHARE_API_KEY`: AKShare API 密钥（某些功能可能需要）
- `PIP_INDEX_URL`: pip 镜像地址（可选，用于国内加速）

### 测试约定

- 使用 pytest 作为测试框架
- 测试文件命名: `test_*.py`
- 使用 fixtures 提供共享资源（在 `conftest.py` 中定义）
- 每个 Fetcher 应有对应的测试文件
- 调试脚本命名: `debug_*.py`

### 工具函数

工具函数位于 `openbb_akshare/utils/` 目录：

- `helpers.py`: 通用辅助函数
- `fetch_quote.py`: 股票报价获取
- `fetch_equity_info.py`: 股票信息获取
- `ak_*.py`: 各类数据格式转换函数
- `references.py`: 参考数据映射表

### 插件配置

插件通过 Poetry 插件系统注册：

```toml
[tool.poetry.plugins."openbb_core_extension"]
akshare = "openbb_akshare.router:router"

[tool.poetry.plugins."openbb_provider_extension"]
akshare = "openbb_akshare:provider"
```

### 版本控制

- 主版本: 1.0.x
- 当前版本: 1.0.9
- 使用 Semantic Versioning
- 依赖 Poetry.lock 确保可重复构建

### 文档

- 主文档: `README.md` (英文)
- 中文文档: `README.zh-CN.md`
- 图片资源: `docs/images/`

### 注意事项

1. **数据标准化**: 所有数据必须转换为 OpenBB 标准模型格式
2. **错误处理**: 添加适当的异常处理和日志记录
3. **缓存机制**: 考虑实现数据缓存以提高性能
4. **API 限制**: 注意 AKShare API 的调用频率限制
5. **符号规范化**: 使用 `normalize_symbol` 工具函数处理股票代码
6. **日志记录**: 使用 `setup_logger` 配置项目日志

### 依赖管理

- 优先使用 Poetry 管理依赖
- 锁定具体版本号确保稳定性
- 定期更新依赖以获取安全和功能更新

### 持续集成

项目支持标准 CI/CD 流程：
- 运行测试套件
- 代码质量检查
- 类型检查
- 构建验证

## 常见任务

### 添加新的数据获取器

1. 在 `openbb_akshare/models/` 创建新的 Fetcher 文件
2. 实现标准的 Fetcher 接口
3. 在 `__init__.py` 中注册 Fetcher
4. 创建对应的测试文件
5. 添加必要的工具函数到 `utils/`

### 调试数据问题

1. 使用 `debug_*.py` 脚本进行单独测试
2. 检查 AKShare API 返回的原始数据
3. 验证数据转换逻辑
4. 查看日志输出定位问题

### 更新依赖

```bash
# 使用 Poetry
poetry update

# 或手动更新特定包
poetry add akshare@latest
```

### 构建 Distribution

```bash
# 构建 wheel 和 source distribution
poetry build

# 或使用 Python
python setup.py sdist bdist_wheel
```

## 相关链接

- **项目主页**: https://github.com/finanalyzer/openbb_akshare
- **国内镜像**: https://gitcode.com/finanalyzer/openbb_akshare
- **AKShare 文档**: https://akshare.akfamily.xyz/
- **OpenBB 文档**: https://docs.openbb.co/

## 许可证

AGPL-3.0-only

## 联系方式

- 作者: Roger Ye <shugaoye@yahoo.com>