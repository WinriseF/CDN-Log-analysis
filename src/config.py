import yaml
from pathlib import Path
from pydantic import BaseModel, DirectoryPath, FilePath
from pydantic_settings import BaseSettings

# 定义嵌套的配置模型
class InputConfig(BaseModel):
    source_type: str = 'local'
    path: str
    file_pattern: str = "*.log"

class ParserConfig(BaseModel):
    format: str
    custom_regex: str | None = None
    time_format: str = "%d/%b/%Y:%H:%M:%S %z"

class AnalysisConfig(BaseModel):
    modules: list[str]
    top_n_count: int = 20
    geoip_db_path: FilePath | None = None

class OutputConfig(BaseModel):
    reporters: list[str]
    report_path: DirectoryPath

# 主配置模型
class AppConfig(BaseSettings):
    input: InputConfig
    parser: ParserConfig
    analysis: AnalysisConfig
    output: OutputConfig

# 全局配置加载函数
def load_config(config_path: str = 'config/config.yaml') -> AppConfig:
    """从指定的YAML文件路径加载配置"""
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    # 报告和日志目录存在
    Path(config_data['output']['report_path']).mkdir(exist_ok=True)
    Path(config_data['input']['path']).mkdir(exist_ok=True)
    return AppConfig(**config_data)