import argparse
import logging
import os

# Set up logging for the controller
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Controller] %(message)s",
    handlers=[logging.FileHandler("storm_control.log", encoding="utf-8"), logging.StreamHandler()]
)

def main():
    """
    主控登機系統 (Main Control Boarding System)
    - 負責解析指令並調度相應的模組。
    """
    parser = argparse.ArgumentParser(description="Storm AI 主控登機系統")
    subparsers = parser.add_subparsers(dest="command", required=True, help="可執行的指令")

    # 'run' command
    run_parser = subparsers.add_parser("run", help="執行一個自動化模組")
    run_parser.add_argument("module", choices=["dispatch"], help="要執行的模組名稱")

    # 'report' command
    report_parser = subparsers.add_parser("report", help="生成一份報告")
    report_parser.add_argument("type", choices=["finance"], help="要生成的報告類型")

    args = parser.parse_args()

    # Get the directory of the current script to build absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if args.command == "run":
        if args.module == "dispatch":
            logging.info("收到指令：執行 'dispatch' 模組...")
            try:
                from dispatch_module import DispatchBot
                config_path = os.path.join(base_dir, "config.json")
                bot = DispatchBot(config_path=config_path)
                bot.run()
            except ImportError:
                logging.critical("錯誤：無法導入 dispatch_module。請確保檔案存在且無語法錯誤。")
            except Exception as e:
                logging.critical(f"執行 'dispatch' 模組時發生未預期的錯誤: {e}", exc_info=True)
        else:
            logging.error(f"未知的模組: {args.module}")

    elif args.command == "report":
        if args.type == "finance":
            logging.info("收到指令：生成 'finance' 報告...")
            try:
                from finance_module import generate_financial_report
                ledger_path = os.path.join(base_dir, "financial_ledger.csv")
                generate_financial_report(ledger_path=ledger_path)
            except ImportError:
                logging.critical("錯誤：無法導入 finance_module。請確保檔案存在且無語法錯誤。")
            except Exception as e:
                logging.critical(f"生成 'finance' 報告時發生未預期的錯誤: {e}", exc_info=True)
        else:
            logging.error(f"未知的報告類型: {args.type}")

if __name__ == "__main__":
    main()
