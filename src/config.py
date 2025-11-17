import yaml
from pathlib import Path
from pydantic import BaseModel, DirectoryPath, FilePath, HttpUrl, SecretStr
from pydantic_settings import BaseSettings

# --- GeoIP 配置模型 ---
class GeoIpLocalConfig(BaseModel):
    db_path: FilePath

class GeoIpApiConfig(BaseModel):
    endpoint: HttpUrl
    batch_size: int = 100
    timeout: int = 10

class GeoIpConfig(BaseModel):
    provider: str
    local: GeoIpLocalConfig | None = None
    api: GeoIpApiConfig | None = None

# --- AnalysisConfig 模型 ---
class AnalysisConfig(BaseModel):
    modules: list[str]
    top_n_count: int = 20
    geoip: GeoIpConfig | None = None

# --- Input API 配置模型 ---
class InputApiConfig(BaseModel):
    domain_name: str
    start_time: str
    end_time: str
    access_key: str
    secret_key: SecretStr
    # 华为云CDN API Endpoint, 可以设为默认值
    endpoint: str = "cdn.myhuaweicloud.com"

# --- InputConfig 模型 ---
class InputConfig(BaseModel):
    source_type: str = 'local'
    # path 和 file_pattern 在 api 模式下可以为空
    path: str | None = None
    file_pattern: str | None = None
    # api 配置
    api: InputApiConfig | None = None

# --- ParserConfig 模型 ---
class ParserConfig(BaseModel):
    format: str
    custom_regex: str | None = None
    time_format: str = "%d/%b/%Y:%H:%M:%S %z"

# --- OutputConfig 模型 ---
class OutputConfig(BaseModel):
    reporters: list[str]
    report_path: DirectoryPath

# --- 主配置模型 ---
class AppConfig(BaseSettings):
    input: InputConfig
    parser: ParserConfig
    analysis: AnalysisConfig
    output: OutputConfig

# --- 加载函数 ---
def load_config(config_path: str = 'config/config.yaml') -> AppConfig:
    """从指定的YAML文件路径加载配置"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    Path(config_data['output']['report_path']).mkdir(exist_ok=True)
    
    # 仅当 source_type 是 'local' 时，才确保日志目录存在
    if config_data.get('input', {}).get('source_type') == 'local':
        Path(config_data['input']['path']).mkdir(exist_ok=True)
        
    return AppConfig(**config_data)