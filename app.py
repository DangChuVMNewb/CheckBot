#!/usr/bin/env python3
"""
File chính khởi chạy bot với cấu hình tập trung
"""

import os
import time
import signal
import sys
from datetime import datetime as _dt, timezone, timedelta
import requests
from requests.exceptions import RequestException
import logging

# ===== CẤU HÌNH =====
class CauHinh:
    """Quản lý cấu hình tập trung"""
    def __init__(self):
        self.token = os.getenv("BOT_TOKEN")
        self.poll_timeout = int(os.getenv("POLL_TIMEOUT", "20"))
        self.request_timeout = float(os.getenv("REQUEST_TIMEOUT", "10.0"))
        self.default_region = os.getenv("DEFAULT_REGION", "SG")
        self.admin_ids = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
        self.timezone_offset = int(os.getenv("TIMEZONE_OFFSET", "7"))  # Múi giờ Việt Nam (UTC+7)
        self.enable_photos = os.getenv("ENABLE_PHOTOS", "true").lower() == "true"
        
        # Kiểm tra cấu hình quan trọng
        if not self.token:
            self._log_and_exit("❌ BOT_TOKEN chưa được thiết lập trong biến môi trường")

    def _log_and_exit(self, message: str):
        print(message)
        sys.exit(1)
    
    @property
    def timezone(self):
        return timezone(timedelta(hours=self.timezone_offset))

# ===== THIẾT LẬP LOGGER =====
def thiet_lap_logger(log_level: str = "INFO"):
    """Cấu hình hệ thống ghi log"""
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        level=getattr(logging, log_level),
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger("FreeFireBot")

# ===== LỚP BOT CHÍNH =====
class FreeFireBot:
    """Lớp chính của bot xử lý tất cả các chức năng"""
    def __init__(self, cau_hinh: CauHinh):
        self.cau_hinh = cau_hinh
        self.logger = thiet_lap_logger()
        self.api_url = f"https://api.telegram.org/bot{cau_hinh.token}"
        self.session = self._tao_session()
        self.update_offset = 0
        self.running = True
        self.start_time = time.time()
        
        # Đăng ký xử lý tắt bot an toàn
        signal.signal(signal.SIGINT, self._tat_an_toan)
        signal.signal(signal.SIGTERM, self._tat_an_toan)
    
    def _tao_session(self) -> requests.Session:
        """Tạo và cấu hình session requests"""
        session = requests.Session()
        session.headers.update({
            "User-Agent": "FreeFireInfoBot/2.0",
            "Accept": "application/json",
            "Connection": "keep-alive"
        })
        return session
    
    def _tat_an_toan(self, signum, frame):
        """Xử lý tắt bot an toàn khi nhận tín hiệu"""
        self.logger.info(f"Nhận tín hiệu {signum}, đang tắt bot một cách an toàn...")
        self.running = False
    
    # ===== TIỆN ÍCH THỜI GIAN =====
    def doi_thoi_gian(self, ts) -> str:
        """Chuyển đổi timestamp sang múi giờ được cấu hình"""
        try:
            if ts is None or ts == "" or ts == "0":
                return "Không rõ"
            
            t = int(str(ts))
            if t > 10**12:  # Xử lý milliseconds
                t = t // 1000
            if t <= 0:
                return "Không rõ"
            
            return _dt.fromtimestamp(t, timezone.utc).astimezone(self.cau_hinh.timezone).strftime("%d/%m/%Y %H:%M:%S")
        except Exception as e:
            self.logger.error(f"Lỗi chuyển đổi thời gian: {str(e)}")
            return "Không rõ"

    # ===== API TELEGRAM =====
    def gui_tin_nhan(self, chat_id: int, text: str, reply_to: int = None):
        """Gửi tin nhắn văn bản"""
        try:
            data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            if reply_to:
                data["reply_to_message_id"] = reply_to
            
            self.session.post(f"{self.api_url}/sendMessage", data=data, timeout=self.cau_hinh.request_timeout)
            self.logger.info(f"Đã gửi tin nhắn đến chat {chat_id}")
        except Exception as e:
            self.logger.error(f"Gửi tin nhắn thất bại đến {chat_id}: {str(e)}")
    
    def gui_anh_dai_dien(self, chat_id: int, uid: str, caption: str, reply_to: int = None):
        """Gửi ảnh đại diện kèm chú thích"""
        if not self.cau_hinh.enable_photos:
            self.gui_tin_nhan(chat_id, caption, reply_to)
            return False
        
        photo_url = f"https://profile.thug4ff.com/api/profile?uid={uid}"
        
        try:
            data = {
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": "HTML"
            }
            if reply_to:
                data["reply_to_message_id"] = reply_to
            
            resp = self.session.post(
                f"{self.api_url}/sendPhoto", 
                data=data, 
                timeout=self.cau_hinh.request_timeout
            )
            
            if resp.status_code == 200 and resp.json().get("ok"):
                self.logger.info(f"Đã gửi ảnh đại diện đến chat {chat_id}")
                return True
        except Exception as e:
            self.logger.warning(f"Gửi ảnh thất bại: {str(e)}")
        
        # Chuyển sang tin nhắn văn bản nếu gặp lỗi
        self.gui_tin_nhan(chat_id, caption, reply_to)
        return False
    
    # ===== VÒNG LẶP CHÍNH =====
    def chay(self):
        """Vòng lặp chính của bot"""
        self.logger.info("Bot đã khởi động thành công")
        self.logger.info(f"Môi trường: {os.getenv('VERCEL', 'LOCAL')}")
        self.logger.info(f"Python version: {os.getenv('PYTHON_VERSION', sys.version)}")
        self.logger.info(f"Sử dụng múi giờ UTC{self.cau_hinh.timezone_offset:+d} (Việt Nam)")
        
        # Import ở đây để tránh vòng lặp import
        from command import xu_ly_lenh
        
        while self.running:
            try:
                resp = self.session.get(
                    f"{self.api_url}/getUpdates",
                    params={"offset": self.update_offset, "timeout": self.cau_hinh.poll_timeout},
                    timeout=self.cau_hinh.poll_timeout + 5
                )
                
                if resp.status_code != 200:
                    self.logger.error(f"Lỗi khi lấy cập nhật: HTTP {resp.status_code}")
                    time.sleep(1)
                    continue
                
                updates = resp.json().get("result", [])
                
                for update in updates:
                    if not self.running:
                        break
                    
                    self.update_offset = update.get("update_id", self.update_offset) + 1
                    xu_ly_lenh(update, self)
                
                time.sleep(0.1)
                
            except RequestException as e:
                self.logger.error(f"Lỗi kết nối: {str(e)}")
                time.sleep(2)
            except Exception as e:
                self.logger.exception(f"Lỗi không mong đợi: {str(e)}")
                time.sleep(1)
        
        self.logger.info("Bot đã dừng hoạt động")

# ===== THỰC THI CHÍNH =====
if __name__ == "__main__":
    try:
        cau_hinh = CauHinh()
        bot = FreeFireBot(cau_hinh)
        bot.chay()
    except Exception as e:
        print(f"Lỗi nghiêm trọng: {str(e)}")
        sys.exit(1)
