"""
Xử lý các lệnh và tin nhắn từ người dùng
"""

import re
import time
import requests
from requests.exceptions import RequestException
from datetime import datetime as _dt

def phan_tich_lenh(text: str) -> tuple:
    """Phân tích lệnh và đối số từ văn bản tin nhắn"""
    if not text or not text.startswith('/'):
        return "", []
    
    # Xử lý lệnh có tên bot: /command@botname
    if '@' in text:
        text = text.split('@')[0]
    
    parts = text.split()
    command = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    return command, args

def xac_thuc_uid(uid_str: str) -> str:
    """Xác thực và làm sạch UID đầu vào"""
    uid = uid_str.strip()
    return uid if uid.isdigit() else ""

def lay_thong_tin_game_thu(uid: str, region: str = "SG") -> dict:
    """Lấy thông tin game thủ từ API Free Fire"""
    url = "https://free-fire-info-site-oe7p.vercel.app/player-info"
    params = [("region", region.upper()), ("uid", uid.strip())]
    
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "FreeFireInfoBot/2.0"})
        
        resp = session.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return None

def tao_tin_nhan_game_thu(data: dict, timezone_converter) -> tuple:
    """Tạo tin nhắn định dạng từ dữ liệu game thủ"""
    basic = data.get("basicInfo", {})
    uid = basic.get("accountId") or basic.get("uid", "Không rõ")
    nickname = basic.get("nickname", "Không rõ")
    level = basic.get("level", "?")
    liked = basic.get("liked", "?")
    rank = basic.get("rank", "?")
    
    # Lấy thời gian và chuyển đổi múi giờ
    create_at = basic.get("createAt")
    last_login_at = basic.get("lastLoginAt")
    create_at_vn = timezone_converter(create_at)
    last_login_vn = timezone_converter(last_login_at)
    
    msg = (
        "<b>🔥 THÔNG TIN GAME THỦ FREE FIRE</b>\n\n"
        f"<b>👤 Nickname:</b> {nickname}\n"
        f"<b>🆔 UID:</b> <code>{uid}</code>\n"
        f"<b>🎮 Level:</b> {level}\n"
        f"<b>❤️ Lượt thích:</b> {liked}\n"
        f"<b>🏆 Rank:</b> {rank}\n"
        f"<b>📆 Ngày tạo:</b> {create_at_vn} (Giờ VN)\n"
        f"<b>⏰ Đăng nhập gần nhất:</b> {last_login_vn} (Giờ VN)"
    )
    
    return msg, uid

def xu_ly_lenh_ff(bot, chat_id: int, args: list, reply_id: int):
    """Xử lý lệnh /ff để lấy thông tin game thủ"""
    if len(args) < 1:
        bot.gui_tin_nhan(chat_id, "❓ Cách sử dụng: /ff <uid> [vùng]", reply_id)
        return
    
    uid = xac_thuc_uid(args[0])
    region = args[1].upper() if len(args) > 1 else bot.cau_hinh.default_region
    
    if not uid:
        bot.gui_tin_nhan(chat_id, "❌ Định dạng UID không hợp lệ. UID chỉ được chứa chữ số.", reply_id)
        return
    
    data = lay_thong_tin_game_thu(uid, region)
    
    if not data:
        error_msg = "❌ Không thể lấy thông tin game thủ. Vui lòng kiểm tra UID và vùng đã chọn."
        bot.gui_tin_nhan(chat_id, error_msg, reply_id)
        return
    
    msg, player_uid = tao_tin_nhan_game_thu(data, bot.doi_thoi_gian)
    
    if bot.cau_hinh.enable_photos:
        bot.gui_anh_dai_dien(chat_id, player_uid, msg, reply_id)
    else:
        bot.gui_tin_nhan(chat_id, msg, reply_id)

def xu_ly_lenh_help(bot, chat_id: int):
    """Xử lý lệnh /help"""
    help_text = (
        "<b>🔥 Bot Tra Cứu Thông Tin Free Fire</b>\n\n"
        "<b>Các lệnh:</b>\n"
        "/ff &lt;uid&gt; [vùng] - Xem thông tin game thủ (mặc định: SG)\n"
        "/help - Hiển thị hướng dẫn này"
    )
    bot.gui_tin_nhan(chat_id, help_text)

def xu_ly_lenh_time(bot, chat_id: int):
    """Xử lý lệnh /time"""
    now = _dt.now(bot.cau_hinh.timezone)
    time_text = (
        f"<b>⏰ Thời Gian Hiện Tại</b>\n"
        f"Múi giờ: UTC{bot.cau_hinh.timezone_offset:+d} (Việt Nam)\n"
        f"Thời gian: {now.strftime('%d/%m/%Y %H:%M:%S')}"
    )
    bot.gui_tin_nhan(chat_id, time_text)

def xu_ly_lenh_start(bot, chat_id: int):
    """Xử lý lệnh /start"""
    welcome = "<b>🎉 Chào mừng bạn đến với Bot Tra Cứu Free Fire!</b>\n\nGõ /help để xem các lệnh có sẵn."
    bot.gui_tin_nhan(chat_id, welcome)

def xu_ly_lenh_status(bot, chat_id: int, user_id: int):
    """Xử lý lệnh /status (chỉ admin)"""
    if user_id not in bot.cau_hinh.admin_ids:
        bot.gui_tin_nhan(chat_id, "❌ Bạn không có quyền sử dụng lệnh này!")
        return
    
    uptime = time.time() - bot.start_time
    days, remainder = divmod(uptime, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    uptime_str = f"{int(days)} ngày, {int(hours)} giờ, {int(minutes)} phút, {int(seconds)} giây"
    
    status = (
        "<b>📊 THÔNG TIN TRẠNG THÁI BOT</b>\n\n"
        f"⏱ Thời gian hoạt động: {uptime_str}\n"
        f"🌍 Múi giờ: UTC{bot.cau_hinh.timezone_offset:+d} (Việt Nam)\n"
        f"📍 Vùng mặc định: {bot.cau_hinh.default_region}"
    )
    bot.gui_tin_nhan(chat_id, status)

def xu_ly_tin_nhan(bot, update: dict):
    """Xử lý tin nhắn/update nhận được"""
    message = update.get("message") or update.get("edited_message")
    if not message:
        return
    
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    msg_id = message.get("message_id")
    text = message.get("text", "")
    user = message.get("from", {})
    user_id = user.get("id")
    
    bot.logger.info(f"Nhận tin nhắn từ người dùng {user_id} trong chat {chat_id}: {text}")
    
    command, args = phan_tich_lenh(text)
    
    # Xử lý các lệnh
    if command == "/ff":
        xu_ly_lenh_ff(bot, chat_id, args, msg_id)
    elif command == "/help":
        xu_ly_lenh_help(bot, chat_id)
    elif command == "/time":
        xu_ly_lenh_time(bot, chat_id)
    elif command == "/start":
        xu_ly_lenh_start(bot, chat_id)
    elif command == "/status":
        xu_ly_lenh_status(bot, chat_id, user_id)

def xu_ly_lenh(update: dict, bot):
    """Hàm điểm vào để xử lý lệnh"""
    xu_ly_tin_nhan(bot, update)
