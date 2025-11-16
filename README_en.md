**English** | [简体中文](./README.md)
# CDN Log Analyzer

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)

A modular, extensible, and configuration-driven CDN log analysis tool. It transforms raw, scattered CDN logs (`.gz` or `.log` files) into insightful analysis reports, with support for multiple output formats.

---

## 🌟 Core Features

*   **🔌 Modular Architecture**: Highly decoupled features. Analyzers and Reporters can be easily extended as plugins.
*   **⚙️ Configuration-Driven**: All core behaviors are controlled via a `config.yaml` file, adapting to different scenarios without any code modification.
*   **📊 Multi-dimensional Analysis**:
    *   **Basic Stats**: PV, status code distribution, requests per hour, and more.
    *   **Top N Analysis**: Easily identify the most active IPs, requested URLs, source countries, etc.
    *   **GeoIP Analysis**: Gain deep insights into your traffic's geographical origin with two modes:
        *   **Local Mode**: Utilizes the free GeoLite2 offline database for lightning-fast lookups.
        *   **API Mode**: Queries an online API (`ip-api.com`) for high-precision city and ISP data.
*   **📈 Multiple Report Formats**:
    *   **Command-Line (CLI)**: Get a quick overview of the core analysis results directly in your terminal.
    *   **Excel Reports**: Generate `.xlsx` files containing raw data, statistical summaries, and beautiful, interactive charts (bar, pie, line charts).

## 📸 Showcase

*CLI Output Summary:*

![CLI Demo](https://raw.githubusercontent.com/WinriseF/IMAGE/images/img/202511161546283.png)

*Excel Report Charts:*

![Status Code Distribution](https://raw.githubusercontent.com/WinriseF/IMAGE/images/img/202511161549378.png)
![Top IPs](https://raw.githubusercontent.com/WinriseF/IMAGE/images/img/202511161549432.png)
![Request Distribution by Country](https://raw.githubusercontent.com/WinriseF/IMAGE/images/img/202511161616330.png)
![Top ISP Distribution](https://raw.githubusercontent.com/WinriseF/IMAGE/images/img/202511161617314.png)


## 🛠️ Installation & Setup

**1. Clone the repository**
```bash
git clone https://github.com/WinriseF/CDN-Log-analysis.git
cd CDN-Log-analysis
```

**2. Create and activate a virtual environment**
```bash
# Create the virtual environment
python -m venv .venv

# Activate (macOS / Linux)
source .venv/bin/activate

# Activate (Windows)
.\.venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Prepare the GeoIP Database (for Local Mode only)**

*   Download the "**GeoLite2 City**" database from a source like [this repository](https://github.com/P3TERX/GeoLite.mmdb/releases).
*   Place the downloaded `GeoLite2-City.mmdb` file in the project's **root directory**.

## 🚀 Quick Start

**1. Place your log files**
Put your CDN log files (e.g., `*.gz` files) into the `logs/` directory.

**2. Configure `config.yaml`**
Open `config.yaml` and adjust it to your needs. The most important setting is `analysis.geoip.provider`. You can choose:
*   `provider: local` (Fast)
*   `provider: api` (Recommended for higher precision)

**3. Run the analysis**
From the project's root directory, execute the following command:
```bash
python -m src.main
```
After the analysis is complete, you will see a summary report in your terminal and find the generated Excel file in the `reports/` directory.

You can also specify a different configuration file:
```bash
python -m src.main --config-file /path/to/your/config.yaml
```

## ⚙️ Configuration Explained (`config.yaml`)

```yaml
# Input configuration
input:
  source_type: local
  path: ./logs/             # Directory containing your log files
  file_pattern: "*.gz"      # File name pattern to match, e.g., '*.gz' or '*.log'

# Parser configuration
parser:
  format: huawei_cdn
  time_format: "%d/%b/%Y:%H:%M:%S %z" # Timestamp format in your logs

# Core analysis configuration
analysis:
  modules:
    - basic_stats           # Enable basic statistical analysis
    - geo_ip                # Enable geographical analysis
  top_n_count: 20           # The 'N' for all Top N statistics

  # Detailed configuration for GeoIP analysis
  geoip:
    # provider: 'local' or 'api'
    provider: api

    # Configuration for local database mode
    local:
      db_path: ./GeoLite2-City.mmdb

    # Configuration for online API mode
    api:
      endpoint: "http://ip-api.com/batch?fields=status,message,country,city,isp,query"
      batch_size: 100
      timeout: 10

# Output configuration
output:
  reporters:
    - cli                   # Print a summary to the command line
    - excel                 # Generate an Excel report
  report_path: ./reports/   # Directory for output reports
```

## 🏗️ Project Architecture

This tool uses a highly modular pipeline architecture with a clear data flow:

`Input (InputHandler)` -> `Parse (LogParser)` -> `Analyze (AnalysisEngine)` -> `Report (Reporters)`

*   **`src/analyzers/`**: Contains all analysis logic modules. Each analyzer is an independent class responsible for a specific analysis dimension.
*   **`src/reporters/`**: Contains all report generation modules. Each reporter is responsible for a specific output format.

This design makes it extremely easy to add new analysis features or report formats.

## 🧩 How to Extend

### Adding a New Analyzer

1.  Create a new file in the `src/analyzers/` directory, e.g., `my_analyzer.py`.
2.  In the file, create a class that inherits from `BaseAnalyzer` and implements the `name` property and the `run` method.
3.  Register your new analyzer in the `_load_analyzers` method of `src/analysis_engine.py`.
4.  Enable it by adding its `name` to the `analysis.modules` list in `config.yaml`.

### Adding a New Reporter

1.  Create a new file in the `src/reporters/` directory, e.g., `my_reporter.py`.
2.  In the file, create a class that inherits from `BaseReporter` and implements the `generate` method.
3.  Register your new reporter in the `available_reporters` dictionary in `src/main.py`.
4.  Enable it by adding its name to the `output.reporters` list in `config.yaml`.

## 📜 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). See the `LICENSE` file for details.