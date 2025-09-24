import argparse
import logging
import os
import sys

# Set up logging for the controller
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Controller] %(message)s",
    handlers=[logging.FileHandler("storm_control.log", encoding="utf-8"), logging.StreamHandler()]
)

def run_environment_check(base_dir: str) -> bool:
    """
    執行環境「紅綠燈」檢查，確保所有關鍵檔案都存在。
    """
    logging.info("⚡ 開始環境「紅綠燈」檢查...")

    # Define paths relative to the script's directory
    paths_to_check = [
        os.path.join(base_dir, "config.json"),
        os.path.join(base_dir, "dispatch_module.py"),
        os.path.join(base_dir, "finance_module.py")
    ]

    all_ok = True

    for path in paths_to_check:
        if not os.path.exists(path):
            logging.error(f"❌ 紅燈：找不到關鍵檔案 {path}")
            all_ok = False
        else:
            logging.info(f"✅ 綠燈：{os.path.basename(path)} 檔案存在")

    if all_ok:
        logging.info("✅ 環境檢查全部通過！系統準備就緒。")
    else:
        logging.critical("❌ 環境檢查失敗，存在「紅燈」項目。請先解決問題再執行。")

    return all_ok

def main():
    """
    主控登機系統 (Main Control Boarding System)
    - 負責解析指令並調度相應的模組。
    """
    # Get the directory of the current script to build absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # --- 環境檢查 ---
    if not run_environment_check(base_dir):
        sys.exit(1) # Exit if environment check fails

    # --- 指令解析 ---
    parser = argparse.ArgumentParser(description="Storm AI 主控登機系統")
    subparsers = parser.add_subparsers(dest="command", required=True, help="可執行的指令")

    # 'run' command
    run_parser = subparsers.add_parser("run", help="執行一個自動化模組")
    run_parser.add_argument("module", choices=["dispatch"], help="要執行的模組名稱")

    # 'report' command
    report_parser = subparsers.add_parser("report", help="生成一份報告")
    report_parser.add_argument("type", choices=["finance"], help="要生成的報告類型")

    args = parser.parse_args()

    # --- 指令執行 ---
    if args.command == "run":
        if args.module == "dispatch":
            logging.info("收到指令：執行 'dispatch' 模組...")
            try:
                from dispatch_module import DispatchBot
                config_path = os.path.join(base_dir, "config.json")
                bot = DispatchBot(config_path=config_path)
                bot.run()
            except ImportError:
                logging.critical("錯誤：無法導入 dispatch_module。")
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
                logging.critical("錯誤：無法導入 finance_module。")
            except Exception as e:
                logging.critical(f"生成 'finance' 報告時發生未預期的錯誤: {e}", exc_info=True)
        else:
            logging.error(f"未知的報告類型: {args.type}")

if __name__ == "__main__":
    main()
