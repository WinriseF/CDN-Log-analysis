import click
import logging
import pandas as pd
from tqdm import tqdm

from src.config import load_config
from src.input_handler import InputHandler
from src.log_parser import LogParser
from src.analysis_engine import AnalysisEngine
from src.reporters.cli_reporter import CliReporter
from src.reporters.excel_reporter import ExcelReporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@click.command()
@click.option(
    '--config-file',
    default='config/config.yaml',
    help='Path to the configuration file.',
    type=click.Path(exists=True)
)
def main(config_file: str):
    """一个模块化、可扩展的CDN日志分析工具"""
    try:
        logging.info("程序启动...")
        config = load_config(config_file)
        logging.info(f"成功加载配置: {config_file}")

        # 数据输入和解析
        input_handler = InputHandler(config)
        log_parser = LogParser(config)
        log_entries = [
            entry.model_dump() for line in tqdm(input_handler.get_lines(), desc="正在解析日志")
            if (entry := log_parser.parse_line(line))
        ]

        if not log_entries:
            logging.warning("未找到任何有效的日志条目，程序即将退出。")
            return
        logging.info(f"成功解析 {len(log_entries)} 条日志。")

        df = pd.DataFrame(log_entries)
        logging.info("日志数据已成功加载到DataFrame。")
        
        # 运行分析引擎
        engine = AnalysisEngine(df, config)
        analysis_results = engine.run()

        # 根据配置生成报告
        # 在这里注册所有可用的报告器
        available_reporters = {
            "cli": CliReporter,
            "excel": ExcelReporter,
        }
        
        enabled_reporters = config.output.reporters
        logging.info(f"将要生成的报告类型: {enabled_reporters}")

        for reporter_name in enabled_reporters:
            reporter_class = available_reporters.get(reporter_name)
            if reporter_class:
                reporter = reporter_class(analysis_results, config)
                reporter.generate()
            else:
                logging.warning(f"配置了未知的报告器 '{reporter_name}'，已跳过。")

        logging.info("所有报告生成完毕，程序正常结束。")

    except Exception as e:
        logging.error(f"发生未处理的错误: {e}", exc_info=True)
        exit(1)

if __name__ == '__main__':
    main()