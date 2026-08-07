import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

class AccountManager:
    def __init__(self):
        self.accounts = []
        self.active_account_index = 0
        self.exhausted_accounts = set()
        self.load_config()

    def load_config(self):
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError(f"Không tìm thấy file cấu hình {CONFIG_PATH}")
            
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.accounts = data.get("accounts", [])
        if not self.accounts:
            raise ValueError("Không có tài khoản nào được cấu hình trong config.json")
            
        self.active_account_index = 0
        self.exhausted_accounts = set()

    def get_current_account(self):
        if self.is_all_exhausted():
            return None
            
        # Tìm account đầu tiên chưa bị exhausted (Quét từ active index)
        start_index = self.active_account_index
        for i in range(len(self.accounts)):
            idx = (start_index + i) % len(self.accounts)
            acc = self.accounts[idx]
            if acc["id"] not in self.exhausted_accounts:
                self.active_account_index = idx
                return acc
                
        return None

    def get_current_profile_dir(self):
        acc = self.get_current_account()
        return acc["profile_dir"] if acc else None

    def get_current_project_url(self):
        acc = self.get_current_account()
        if acc and acc.get("projects"):
            # Lấy project đầu tiên. Ở phiên bản này 1 account = 1 project
            return acc["projects"][0]
        return None

    def mark_exhausted(self):
        acc = self.get_current_account()
        if acc:
            print(f"[*] Account Manager: Đánh dấu tài khoản '{acc['id']}' là Exhausted (Hết Quota).")
            self.exhausted_accounts.add(acc["id"])
            # Xoay sang tài khoản kế tiếp luôn
            self.get_current_account()

    def is_all_exhausted(self):
        return len(self.exhausted_accounts) >= len(self.accounts)

# Singleton instance
account_manager = AccountManager()
