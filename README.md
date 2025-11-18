[English](./README_en.md) | **简体中文**
# CDN 日志分析工具 (CDN Log Analyzer)

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)

一个模块化、可扩展、配置驱动的 CDN 日志分析工具。它可以将原始、分散的 CDN 日志 (`.gz` 或 `.log` 文件) 转化为富有洞察力的分析报告，并支持多种输出格式。

---



## 🌟 核心特性

*   **🔌 灵活的数据源**:
    *   **本地模式**: 支持分析本地存储的 `.gz` 或 `.log` 日志文件。
    *   **API 模式**: 可直接对接**华为云CDN API**，根据指定的时间范围自动拉取、分析日志，并支持智能缓存，避免重复下载。
*   **⚙️ 配置驱动**: 所有核心行为均由 `config.yaml` 文件控制，无需修改任何代码即可适配不同场景。
*   **📊 多维分析**:
    *   **基础统计**: PV、状态码分布、每小时请求数等。
    *   **Top N 分析**: 轻松获取访问量最高的 IP、来源国家/地区和运营商。
    *   **地理位置分析 (GeoIP)**: 深入了解流量来源，支持两种模式：
        *   **本地模式**: 使用免费的 GeoLite2 离线数据库，速度极快。
        *   **API 模式**: 调用在线 API (`ip-api.com`)，获取高精度的城市和运营商信息。
*   **📈 多种报告格式**:
    *   **命令行 (CLI)**: 在终端快速预览核心分析结果。
    *   **Excel 报告**: 生成包含原始数据样本、统计结果和可视化图表 (`柱状图`, `饼图`, `折线图`) 的 `.xlsx` 文件。
*   **🧩 模块化架构**: 功能高度解耦，分析器 (Analyzers) 与报告器 (Reporters) 均可作为插件轻松扩展。

## 📸 效果演示

*CLI 输出摘要:*

![image-20251116154615991](https://raw.githubusercontent.com/WinriseF/IMAGE/images/img/202511161546283.png)

*Excel 报告图表:*

![image-20251116154918915](https://raw.githubusercontent.com/WinriseF/IMAGE/images/img/202511161549378.png)

![image-20251116154946296](https://raw.githubusercontent.com/WinriseF/IMAGE/images/img/202511161549432.png)

![image-20251116161523107](https://raw.githubusercontent.com/WinriseF/IMAGE/images/img/202511161616330.png)

![image-20251116161756137](https://raw.githubusercontent.com/WinriseF/IMAGE/images/img/202511161617314.png)


## 🛠️ 安装与准备

**1. 克隆项目**
```bash
git clone https://github.com/WinriseF/CDN-Log-analysis
cd CDN-Log-analysis
```

**2. 创建并激活虚拟环境**
```bash
# 创建虚拟环境
python -m venv .venv

# 激活 (macOS / Linux)
source .venv/bin/activate

# 激活 (Windows)
.\.venv\Scripts\activate
```

**3. 安装依赖**
```bash
pip install -r requirements.txt
```

**4. 准备 GeoIP 数据库 (仅本地模式需要)**

*   下载 “**GeoLite2 City**” 数据库，参考[https://github.com/P3TERX/GeoLite.mmdb/releases](https://github.com/P3TERX/GeoLite.mmdb/releases)。
*   将下载得到的 `GeoLite2-City.mmdb` 文件放置到本项目的**根目录**下。

## 🚀 快速开始

本工具支持两种工作模式，由 `config.yaml` 中的 `input.source_type` 控制。

---

### **模式一：本地文件分析 (Local Mode)**

**1. 放置日志文件**
将您的 CDN 日志文件 (例如 `*.gz` 文件) 放入 `logs/` 目录下。

**2. 修改配置**
打开 `config/config.yaml`，确保配置如下，此配置下会分析所有在logs下面的日志：
```yaml
input:
  source_type: local
  path: ./logs/
  file_pattern: "*.gz"
```

**3. 运行分析**

```bash
python -m src.main
```

---

### **模式二：API 自动拉取 (API Mode)**

**1. 修改配置**
打开 `config/config.yaml`，进行如下配置，此配置下只会分析在start_time-end_time之间的日志：

```yaml
input:
  source_type: api
  path: ./logs/ # 在API模式下，此路径用作日志的本地缓存目录

  api:
    domain_name: "your.cdn.domain.com"      # 替换为您的CDN加速域名
    start_time: "2025-11-16T10:00:00Z"    # 设置分析的开始时间 (UTC)
    end_time: "2025-11-16T12:00:00Z"      # 设置分析的结束时间 (UTC)
    access_key: "YOUR_HUAWEI_CLOUD_AK"      # 替换为您的华为云 Access Key
    secret_key: "YOUR_HUAWEI_CLOUD_SK"      # 替换为您的华为云 Secret Key
    skip_existing_logs: true              # 推荐：智能跳过已缓存的日志
    download_new_logs: true               # 推荐：将新日志下载到缓存目录
```

**2. 运行分析**

```bash
python -m src.main
```

程序将自动从华为云API拉取指定时间范围的日志。如果日志已存在于本地缓存 (`./logs` 目录)，将直接使用缓存进行分析，避免重复下载。

---

分析完成后，您将在终端看到摘要报告，并在 `reports/` 目录下找到生成的 Excel 文件。

您也可以指定一个不同的配置文件：
```bash
python -m src.main --config-file /path/to/your/config.yaml
```

## ⚙️ 配置文件详解 (`config.yaml`)

```yaml
# 输入配置
input:
  # 'local' (从本地文件夹读取) 或 'api' (从华为云API拉取)
  source_type: api
  
  # 本地模式配置 (或 API 模式下的缓存目录)
  path: ./logs/
  file_pattern: "*.gz"      #要匹配的本地文件名模式

  # API 模式专属配置
  api:
    domain_name: "your.cdn.domain.com"	# CDN分析域名，比如img.XXX.cn
    start_time: "YYYY-MM-DDTHH:MM:SSZ"  # 分析开始时间 (ISO 8601 UTC格式)，例如："2025-11-12T00:00:00Z"
    end_time: "YYYY-MM-DDTHH:MM:SSZ"    # 分析结束时间 (ISO 8601 UTC格式)，例如："2025-11-16T16:00:00Z"
    access_key: "YOUR_AK"			   # 华为云具有读取日志权限的access_key
    secret_key: "YOUR_SK"			   # secret_key
    skip_existing_logs: true            # 是否跳过本地已存在的同名日志，推荐true
    download_new_logs: true             # 是否将新拉取的日志保存到本地，推荐true

# 解析器配置
parser:
  format: huawei_cdn
  time_format: "%d/%b/%Y:%H:M:%S %z" # 日志中的时间格式，默认符合华为云日志格式

# 核心分析配置
analysis:
  modules:
    - basic_stats           # 基础统计分析
    - geo_ip                # 地理位置分析
  top_n_count: 50           # 各类 Top N 统计的数量
  
  # 控制报告中原始日志样本的数量。-1 表示显示全部。
  raw_logs_sample_limit: 1000

  # 地理位置分析的详细配置，分析IP属地
  geoip:
    # provider: 'local' (离线数据库) 或 'api' (在线API)
    provider: api
    # local:
    #   db_path: ./GeoLite2-City.mmdb # 本地数据库路径
    api:
      endpoint: "http://ip-api.com/batch"
      batch_size: 100

# 输出配置
output:
  reporters:
    - cli                   # 在命令行打印摘要
    - excel                 # 生成 Excel 报告
  report_path: ./reports/   # 报告输出目录
```

## 🏗️ 项目架构

本工具采用高度模块化的管道式架构，数据流清晰：

`输入 (InputHandler)` -> `解析 (LogParser)` -> `分析 (AnalysisEngine)` -> `报告 (Reporters)`

*   **`src/analyzers/`**: 存放所有的分析逻辑模块。每个分析器都是一个独立的类，负责一个特定的分析维度。
*   **`src/reporters/`**: 存放所有的报告生成模块。每个报告器负责一种输出格式。

这种设计使得添加新的分析功能或报告格式变得异常简单。

## 🧩 如何扩展

### 添加一个新的分析器 (Analyzer)

1.  在 `src/analyzers/` 目录下创建一个新文件，例如 `my_analyzer.py`。
2.  在文件中创建一个类，继承自 `BaseAnalyzer`，并实现 `name` 属性和 `run` 方法。
3.  在 `src/analysis_engine.py` 的 `_load_analyzers` 方法中注册您的新分析器。
4.  在 `config.yaml` 的 `analysis.modules` 列表中加入您的分析器 `name` 来启用它。

### 添加一个新的报告器 (Reporter)

1.  在 `src/reporters/` 目录下创建一个新文件，例如 `my_reporter.py`。
2.  在文件中创建一个类，继承自 `BaseReporter`，并实现 `generate` 方法。
3.  在 `src/main.py` 的 `available_reporters` 字典中注册您的新报告器。
4.  在 `config.yaml` 的 `output.reporters` 列表中加入您的报告器名称来启用它。

## 📜 许可证

本项目采用 [MIT](https://opensource.org/licenses/MIT) 许可证。详情请见 `LICENSE` 文件。