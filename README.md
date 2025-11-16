# **CDN日志分析工具: 项目开发计划**

## 1. 项目愿景与目标

将现有的Python脚本重构并扩展为一个模块化、配置驱动、功能全面的CDN日志分析工具。该工具旨在为运维、开发和数据分析人员提供一个开箱即用的解决方案，用于快速进行性能分析、安全审计和业务洞察。

### **核心设计原则:**
*   **模块化 (Modular):** 功能高度解耦，易于维护和独立扩展（如新增解析器、分析器、报告器）。
*   **配置驱动 (Config-driven):** 核心行为由外部配置文件控制，用户无需修改代码即可适配不同场景。
*   **可扩展性 (Extensible):** 预留清晰的接口，方便社区或用户贡献新的功能模块。
*   **用户友好 (User-Friendly):** 提供清晰的命令行接口(CLI)、人类可读的报告和完善的文档。

---

## 2. 开发路线图 (Phased Development)

我们将项目分为四个主要阶段，循序渐进，确保每个阶段都有明确的可交付成果。

### **Phase 1: 基础重构与工程化 (Foundation & Refactoring)**

**目标:** 将现有脚本转化为一个结构良好、可维护的单一项目，实现配置与代码分离。此阶段不新增核心分析功能，重在打好基础。

**具体任务:**
1.  **创建标准项目结构:**
    *   建立清晰的目录结构 (`/src`, `/config`, `/logs`, `/reports`, `/tests`)。
    *   使用 `pyproject.toml` 或 `requirements.txt` 管理依赖。
2.  **实现命令行入口 (CLI):**
    *   使用 `Click` 或 `argparse` 库创建一个统一的命令行入口。
    *   实现基础命令，如 `cdn-analyzer analyze --config config.yaml`。
3.  **引入配置文件:**
    *   创建一个 `config.yaml` 模板，将所有硬编码的变量（如文件名、爬虫关键字、IP黑名单阈值、日志正则）移入其中。
4.  **面向对象(OOP)重构:**
    *   **`LogProcessor` 类:** 封装 `To-log.py` 的功能，负责日志的合并与预处理。
    *   **`AnalysisEngine` 类:** 封装 `Analysis.py` 的核心分析逻辑。
    *   **`Reporter` 类:** 将报告生成逻辑（如写Excel）抽象出来，为未来支持多种报告格式做准备。
5.  **引入日志系统:**
    *   使用 Python 内置的 `logging` 模块替换所有 `print()` 语句，实现不同级别的日志输出（DEBUG, INFO, WARNING, ERROR）。

**交付成果:**
*   一个可以通过命令行运行的、由YAML文件配置的、结构清晰的Python项目。
*   功能与原始脚本完全一致，但代码质量和可维护性大幅提升。

---

### **Phase 2: 核心功能增强 (Core Feature Enhancement)**

**目标:** 丰富分析维度，并提供更现代化的报告形式。

**具体任务:**
1.  **打造解析器工厂 (Parser Factory):**
    *   设计一个解析器基类，将现有的华为CDN日志解析器作为其第一个实现。
    *   允许用户在 `config.yaml` 中指定要使用的解析器（如 `parser: huawei_cdn`）。
    *   **扩展:** 新增对至少一种其他主流CDN日志格式的支持（如 `Cloudflare`, `AWS CloudFront`）。
2.  **扩充分析模块:**
    *   **URL分析:** 实现 Top N 访问路径、Top N 错误路径、Top N 大流量路径的分析。
    *   **User-Agent分析:** 实现客户端类型（PC/Mobile）、操作系统、浏览器分布的统计。
    *   **Referer分析:** 实现 Top N 流量来源域名的统计。
3.  **实现HTML报告器:**
    *   集成 `Jinja2` 模板引擎和 `Pyecharts` 或 `Plotly` 图表库。
    *   生成一个包含交互式图表（柱状图、饼图、折线图）的单文件HTML报告，使其比静态Excel更直观。

**交付成果:**
*   工具具备了更全面的分析能力。
*   能够生成交互式、美观的HTML分析报告。
*   支持至少两种不同格式的CDN日志。

---

### **Phase 3: 高级能力与安全审计 (Advanced Capabilities)**

**目标:** 引入安全检测和高级性能分析功能，使工具具备“专家级”能力。

**具体任务:**
1.  **构建安全分析模块:**
    *   **Web攻击特征识别:** 通过正则表达式匹配URL和UA中的常见攻击载荷（如SQL注入、XSS、目录遍历）。
    *   **CC攻击检测:** 基于“单IP在单位时间内的请求频率”进行阈值判断和告警。
2.  **集成IP情报库:**
    *   集成离线的GeoIP数据库（如 `GeoLite2`），在报告中展示IP的地理位置分布图。
    *   （可选）提供API接口，对接第三方威胁情报平台，查询Top IP是否为恶意IP。
3.  **深化性能分析模块:**
    *   **缓存命中率(CHR)分析:** 精确计算全局缓存命中率，并分析Top N低命中率的URL。
    *   **响应耗时分析:** 计算P90/P95/P99响应时间，识别慢速请求。
4.  **实现告警模块:**
    *   当触发特定条件（如错误率激增、检测到CC攻击）时，通过Webhook向钉钉、企业微信或Slack发送通知。

**交付成果:**
*   工具不仅能做统计，还能主动发现安全威胁和性能瓶颈。
*   报告中包含IP地理位置信息，分析更具深度。
*   具备初步的自动化告警能力。

---

### **Phase 4: 产品化与生态集成 (Productization & Integration)**

**目标:** 将工具打磨成一个成熟的产品，易于分发和集成到自动化流程中。

**具体任务:**
1.  **扩展数据输入源:**
    *   除了本地文件，增加对云存储的支持（如通过`boto3`读取AWS S3，`oss2`读取阿里云OSS）。
2.  **增加数据持久化选项:**
    *   支持将每日的核心分析结果（如PV、UV、CHR、Top IP）存入一个轻量级数据库（如 `SQLite`），用于长期趋势分析。
3.  **打包与分发:**
    *   使用 `setuptools` 或 `poetry` 将项目打包，使其可以通过 `pip install` 进行安装。
    *   （可选）发布到 PyPI，成为一个开源项目。
4.  **构建Web UI (可选但强烈推荐):**
    *   使用 `Streamlit` 或 `Gradio` 快速为工具构建一个简单的Web界面，允许用户通过浏览器上传日志、点击按钮进行分析并在线查看报告。
    *   对于更复杂的场景，可使用 `Flask` 或 `Django`。

**交付成果:**
*   一个可以通过pip安装的、成熟的Python库/工具。
*   能够无缝对接近代化的云基础设施。
*   （如果实现Web UI）一个拥有图形化界面的、非技术人员也能轻松使用的日志分析平台。

---

## 3. 技术栈选型 (Technology Stack)

*   **命令行接口:** `Click` / `argparse`
*   **数据处理:** `Pandas`
*   **配置文件:** `PyYAML`
*   **报告生成:**
    *   Excel: `openpyxl` / `xlsxwriter`
    *   HTML: `Jinja2` + `Pyecharts` / `Plotly`
*   **IP地理信息:** `geoip2`
*   **云存储SDK:** `boto3` (AWS S3), `oss2` (Aliyun OSS)
*   **Web UI (可选):** `Streamlit` / `Flask`

## 4. 示例 `config.yaml` 结构

```yaml
# config.yaml

# 1. 输入配置
input:
  type: local # 'local' or 's3' or 'oss'
  path: ./logs/ # 本地路径 or S3/OSS bucket
  # s3_credentials: ...

# 2. 解析器配置
parser:
  format: huawei_cdn # 使用哪种日志格式解析器
  log_pattern: '\[(?P<time>.*?)\]\s+(?P<ip>\S+)\s+...' # 当 format 为 custom 时生效

# 3. 分析模块开关
analysis_modules:
  - basic_stats    # 基础统计 (PV, UV, IP, Status Code)
  - top_n_urls     # Top N URL 分析
  - user_agent     # User-Agent 分析
  - performance    # 性能分析 (CHR, Response Time)
  - security       # 安全审计 (WAF, CC)
  - geo_ip         # IP地理位置分析

# 4. 输出/报告配置
output:
  reporters:
    - excel        # 生成Excel报告
    - html         # 生成HTML报告
  report_path: ./reports/
  top_n_count: 20  # 各类Top N统计的数量

# 5. 告警配置
alerts:
  enable: true
  webhook_url: 'https://oapi.dingtalk.com/robot/send?access_token=xxx'
  rules:
    - metric: status_5xx_rate # 5xx错误率
      threshold: 0.05         # 阈值 5%
      window: 60              # 检查窗口 60秒
```



好的，遵命。这是一份详尽的、旨在将您的项目产品化的详细设计指南。

本指南将涵盖系统架构、核心模块设计、数据流、关键数据结构以及扩展性设计，为您提供一份可以直接用于指导编码的蓝图。

---

# **CDN日志分析工具 - 详细设计指南 (Detailed Design Guide)**

## 1. 系统架构 (System Architecture)

我们将采用一个基于**管道 (Pipeline)** 和**策略模式 (Strategy Pattern)** 的模块化架构。数据从输入源流经一系列处理单元，最终生成报告。每个处理单元都是可替换和可配置的。

**核心流程图:**

```
[输入源] -> [Input Handler] -> [原始日志流 (Raw Log Stream)] -> [Log Parser] -> [结构化数据 (Parsed Data)] -> [Analysis Engine] -> [分析结果 (Analysis Results)] -> [Report Generator] -> [分析报告 (Report)]
    ^                  ^                      ^                    ^                        ^
    |                  |                      |                    |                        |
[config.yaml] ----> [Orchestrator (main.py)] --- (控制所有模块) ---------------------------->
```

*   **Orchestrator (协调器):** 即主程序入口 `main.py`。它负责读取 `config.yaml`，并根据配置来初始化和串联所有其他模块。
*   **Config-Driven:** 所有模块的行为都由 `config.yaml` 决定，实现了逻辑与配置的彻底分离。

## 2. 配置文件设计 (`config.yaml`)

配置文件是整个工具的“控制面板”，其设计的优劣直接影响工具的灵活性。

```yaml
# -------------------- #
#  输入模块配置 (Input) #
# -------------------- #
input:
  # 'local' (本地文件), 's3' (AWS S3), 'oss' (阿里云 OSS)
  source_type: local
  path: ./logs/  # 本地文件夹路径 或 云存储的 Bucket/Path
  # 当 source_type 为 local 时，指定文件匹配模式
  file_pattern: "*.gz"
  # 云存储访问凭证 (可选, 建议使用环境变量)
  # credentials:
  #   aws_access_key_id: 'KEY'
  #   aws_secret_access_key: 'SECRET'

# -------------------- #
#  解析器模块配置 (Parser) #
# -------------------- #
parser:
  # 内置格式: 'huawei_cdn', 'cloudflare_json', 'aws_cloudfront'
  # 或 'custom' 使用自定义正则
  format: huawei_cdn
  # 当 format 为 'custom' 时，必须提供以下正则
  # custom_regex: '...'
  # 日志时间格式，用于精确解析
  time_format: "%d/%b/%Y:%H:%M:%S %z"

# -------------------- #
#  分析引擎配置 (Analysis) #
# -------------------- #
analysis:
  # 启用哪些分析模块
  modules:
    - basic_stats    # 基础统计 (PV, UV, 独立IP, 状态码)
    - top_n          # 所有Top N分析
    - performance    # 性能分析 (缓存命中率, 响应时间)
    - security       # 安全审计 (Web攻击, CC攻击检测)
    - geo_ip         # IP地理位置分析
  
  # Top N 统计的数量
  top_n_count: 20
  
  # 性能分析相关阈值
  performance_thresholds:
    slow_request_ms: 1000 # 超过此毫秒数的请求被认为是慢请求

  # 安全审计相关配置
  security_rules:
    cc_attack:
      # 1个IP在10秒内请求超过100次，则标记为疑似CC攻击
      requests: 100
      time_window_seconds: 10
    # GeoIP数据库文件路径
    geoip_db_path: ./GeoLite2-City.mmdb

# -------------------- #
#  输出报告配置 (Output) #
# -------------------- #
output:
  # 可同时生成多种报告: 'cli', 'excel', 'html'
  reporters:
    - cli
    - html
  # 输出报告的存放目录
  report_path: ./reports/
  # 报告文件名前缀，最终文件名会加上时间戳
  report_filename_prefix: cdn_analysis_report

# -------------------- #
#  告警模块配置 (Alerting) #
# -------------------- #
alerting:
  enable: false
  # 支持 'dingtalk', 'wechat_webhook', 'slack'
  provider: dingtalk
  webhook_url: 'YOUR_WEBHOOK_URL'
  # 告警触发规则
  rules:
    - metric: status_5xx_rate # 5xx错误率
      operator: ">"
      threshold: 0.05         # 阈值 5%
      # ... 更多规则
```

## 3. 核心组件详细设计

### 3.1. 配置管理器 (`/src/config.py`)

**职责:** 安全地加载和验证`config.yaml`，并提供全局唯一的配置访问点。

```python
# src/config.py

import yaml

class ConfigManager:
    """提供一个单例模式或全局实例来管理配置"""
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        # 在此可以添加配置验证逻辑

    def get(self, key_path: str, default=None):
        # 支持点分路径访问, 如 'input.source_type'
        keys = key_path.split('.')
        value = self._config
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return default
            value = value[key]
        return value

# 全局实例
# config = ConfigManager('config.yaml')
```

### 3.2. 输入处理器 (`/src/input_handlers.py`)

**设计模式:** 工厂模式 (Factory Pattern)。主程序根据配置决定创建哪个具体的Handler实例。

```python
# src/input_handlers.py

from abc import ABC, abstractmethod
from typing import Iterator

class BaseInputHandler(ABC):
    """输入处理器的抽象基类"""
    @abstractmethod
    def read_logs(self) -> Iterator[str]:
        """以迭代器方式逐行返回日志，以支持大文件流式处理"""
        pass

class LocalFileInputHandler(BaseInputHandler):
    """处理本地日志文件"""
    def __init__(self, path: str, pattern: str):
        # ... 初始化逻辑 ...
    
    def read_logs(self) -> Iterator[str]:
        # ... 实现逻辑：找到文件，解压(如果需要)，逐行yield ...
        pass

class S3InputHandler(BaseInputHandler):
    """处理来自AWS S3的日志"""
    def __init__(self, bucket: str, prefix: str, credentials: dict):
        # ... 初始化boto3客户端 ...
    
    def read_logs(self) -> Iterator[str]:
        # ... 实现逻辑：列出S3对象，下载，流式解压，逐行yield ...
        pass

def get_input_handler(config: ConfigManager) -> BaseInputHandler:
    """工厂函数"""
    source_type = config.get('input.source_type')
    if source_type == 'local':
        return LocalFileInputHandler(...)
    elif source_type == 's3':
        return S3InputHandler(...)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")

```

### 3.3. 日志解析器 (`/src/log_parser.py`)

**设计模式:** 策略模式 (Strategy Pattern)。`LogParser`持有一个解析策略（即正则表达式），使得解析逻辑可以轻松切换。

```python
# src/log_parser.py

import re
from typing import Optional, Dict, Any

class LogParser:
    """日志解析器，使用指定的策略来解析日志行"""
    def __init__(self, config: ConfigManager):
        parser_format = config.get('parser.format')
        if parser_format == 'custom':
            self._pattern = re.compile(config.get('parser.custom_regex'))
        else:
            # 从预设模板中获取正则表达式
            self._pattern = self._get_predefined_pattern(parser_format)
        # ... 其他初始化 ...

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """解析单行日志"""
        match = self._pattern.match(line)
        if match:
            return match.groupdict()
        return None

    def _get_predefined_pattern(self, format_name: str) -> re.Pattern:
        # ... 返回内置的华为云、Cloudflare等日志格式的正则表达式 ...
        pass
```

### 3.4. 分析引擎 (`/src/analysis_engine.py`)

**职责:** 接收一个包含所有结构化日志的Pandas DataFrame，并根据配置执行不同的分析任务。

```python
# src/analysis_engine.py

import pandas as pd

class AnalysisEngine:
    """核心分析引擎，所有分析方法在此实现"""
    def __init__(self, df: pd.DataFrame, config: ConfigManager):
        self.df = df
        self.config = config
        self.results = {}

    def run(self):
        """根据配置，运行所有启用的分析模块"""
        enabled_modules = self.config.get('analysis.modules', [])
        
        if 'basic_stats' in enabled_modules:
            self.results['basic_stats'] = self._analyze_basic_stats()
        if 'top_n' in enabled_modules:
            self.results['top_n'] = self._analyze_top_n()
        if 'performance' in enabled_modules:
            self.results['performance'] = self._analyze_performance()
        # ... 依次调用其他分析模块 ...

        return self.results

    def _analyze_basic_stats(self) -> Dict[str, Any]:
        # ... 实现PV, UV, 状态码分布等计算 ...
        pass

    def _analyze_top_n(self) -> Dict[str, pd.DataFrame]:
        # ... 实现Top IP, Top URL, Top UA, Top Referer的计算 ...
        pass

    def _analyze_performance(self) -> Dict[str, Any]:
        # ... 实现缓存命中率, P95/P99响应时间, 慢请求列表的计算 ...
        pass

    def _analyze_security(self) -> Dict[str, Any]:
        # ... 实现Web攻击检测和CC攻击检测 ...
        pass

    def _analyze_geo_ip(self) -> pd.DataFrame:
        # ... 实现IP地理位置分析 ...
        pass
```

### 3.5. 报告生成器 (`/src/reporters.py`)

**设计模式:** 工厂模式。与`InputHandler`类似，根据配置创建具体的报告生成器。

```python
# src/reporters.py

from abc import ABC, abstractmethod

class BaseReporter(ABC):
    """报告生成器的抽象基类"""
    def __init__(self, analysis_results: dict, config: ConfigManager):
        self.results = analysis_results
        self.config = config

    @abstractmethod
    def generate(self):
        """生成并保存报告"""
        pass

class HtmlReporter(BaseReporter):
    """生成交互式HTML报告"""
    def generate(self):
        # 使用Jinja2和Pyecharts生成HTML文件
        pass

class ExcelReporter(BaseReporter):
    """生成Excel报告"""
    def generate(self):
        # 使用Pandas和xlsxwriter生成带图表的Excel文件
        pass

class CliReporter(BaseReporter):
    """在命令行打印摘要报告"""
    def generate(self):
        # 使用rich或tabulate库格式化输出到控制台
        pass

def get_reporters(results: dict, config: ConfigManager) -> list[BaseReporter]:
    """工厂函数，返回一个包含所有已启用报告器的列表"""
    reporter_instances = []
    reporter_names = config.get('output.reporters', [])
    
    if 'html' in reporter_names:
        reporter_instances.append(HtmlReporter(results, config))
    if 'excel' in reporter_names:
        reporter_instances.append(ExcelReporter(results, config))
    if 'cli' in reporter_names:
        reporter_instances.append(CliReporter(results, config))
        
    return reporter_instances
```

## 4. 主程序工作流 (`main.py`)

```python
# main.py

import click
import pandas as pd
from tqdm import tqdm # 用于显示进度条

# 导入所有模块
from src.config import ConfigManager
from src.input_handlers import get_input_handler
from src.log_parser import LogParser
from src.analysis_engine import AnalysisEngine
from src.reporters import get_reporters

@click.command()
@click.option('--config', default='config.yaml', help='Path to config file.')
def main(config_path: str):
    """CDN Log Analysis Tool"""
    # 1. 初始化配置
    config = ConfigManager(config_path)

    # 2. 获取输入处理器并读取日志
    input_handler = get_input_handler(config)
    log_iterator = input_handler.read_logs()

    # 3. 初始化解析器并解析日志流
    parser = LogParser(config)
    parsed_data = [
        data for line in tqdm(log_iterator, desc="Parsing logs") 
        if (data := parser.parse_line(line)) is not None
    ]
    if not parsed_data:
        print("No valid log entries found.")
        return

    # 4. 转换为Pandas DataFrame进行分析
    df = pd.DataFrame(parsed_data)
    # 在此进行数据类型转换和预处理（如时间转换）

    # 5. 运行分析引擎
    engine = AnalysisEngine(df, config)
    results = engine.run()

    # 6. 生成所有配置的报告
    reporters = get_reporters(results, config)
    for reporter in reporters:
        reporter.generate()

    # 7. (可选) 触发告警
    # alerter = Alerter(results, config)
    # alerter.check_and_alert()
    
    print("Analysis complete.")

if __name__ == '__main__':
    main()
```

## 5. 项目目录结构

```
cdn-log-analyzer/
├── .gitignore
├── pyproject.toml         # 或 requirements.txt
├── README.md
├── config.yaml            # 默认配置文件
├── GeoLite2-City.mmdb     # GeoIP数据库
├── logs/                  # 存放日志文件的示例目录
│   └── cdn.log.gz
├── reports/               # 存放输出报告的目录
└── src/
    ├── __init__.py
    ├── config.py
    ├── input_handlers.py
    ├── log_parser.py
    ├── analysis_engine.py
    ├── reporters.py
    ├── alerting.py
    └── utils/             # 存放通用函数，如时间处理
        ├── __init__.py
        └── time_utils.py
```

---

这份设计指南为您提供了一个清晰、可执行的框架。按照这个设计，您可以逐步构建出一个功能强大且易于扩展的专业级日志分析工具。