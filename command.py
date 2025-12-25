"""
Xử lý các lệnh và tin nhắn từ người dùng - chỉ tập trung vào lệnh /ff với hướng dẫn tích hợp
"""

import re
import time
import requests
from requests.exceptions import RequestException
from datetime import datetime as _dt

def phan_tich_lenh(text: str, bot_username: str = "") -> tuple:
    """
    Phân tích lệnh và đối số từ văn bản tin nhắn
    Xử lý cả trường hợp có mention bot trong group chat
    """
    if not text or not text.startswith('/'):
        return "", []
    
    # Xử lý lệnh có tên bot: /command@botname
    command_part = text.split('@')[0] if '@' in text else text
    parts = command_part.split()
    command = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    # Xử lý trường hợp bot được mention trong group
    if bot_username and f"@{bot_username}" in text:
        return command, args
    
    return command, args

def xac_thuc_uid(uid_str: str) -> str:
    """Xác thực và làm sạch UID đầu vào"""
    uid = uid_str.strip()
    return uid if uid.isdigit() else ""

def lay_thong_tin_game_thu(uid: str, region: str = "SG") -> dict:
    """Lấy thông tin game thủ từ API Free Fire"""
    url = "https://free-fire-info-site-oe7p.vercel.app/player-info"
    params = {"region": region.upper(), "uid": uid.strip()}
    
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "FreeFireInfoBot/2.0"})
        
        resp = session.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Lỗi khi lấy thông tin: {str(e)}")
        return None

def tao_tin_nhan_game_thu(data, timezone_converter) -> tuple:
    """Tạo tin nhắn định dạng từ dữ liệu game thủ"""
    if not data or not isinstance(data, dict):
        return "❌ Không có dữ liệu hợp lệ", ""
        
    basic = data.get("basicInfo", {})
    if not basic:
        return "❌ Không tìm thấy thông tin cơ bản", ""
        
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

def xu_ly_lenh_ff(bot, chat_id: int, chat_type: str, args: list, reply_id: int, user_id: int, username: str = ""):
    """Xử lý lệnh /ff để lấy thông tin game thủ - tích hợp hướng dẫn khi cần"""
    # Nếu không có đối số, hiển thị hướng dẫn sử dụng
    if len(args) < 1:
        if getattr(bot, 'la_tin_nhan_rieng', lambda x: x == "private")(chat_type):
            huong_dan = (
                "<b>🔥 HƯỚNG DẪN SỬ DỤNG BOT</b>\n\n"
                "📝 <b>Cách tra cứu thông tin game thủ:</b>\n"
                "<code>/ff &lt;uid&gt; [vùng]</code>\n\n"
                "<b>• &lt;uid&gt;:</b> ID game thủ Free Fire (bắt buộc)\n"
                "<b>• [vùng]:</b> Mã vùng (tùy chọn, mặc định là SG)\n\n"
                "<b>🌏 Các vùng hỗ trợ:</b>\n"
                "SG (Singapore), VN (Việt Nam), ID (Indonesia), TH (Thái Lan),...\n\n"
                "<b>💡 Ví dụ:</b>\n"
                "/ff 5498571579\n"
                "/ff 5498571579 VN\n\n"
                "<i>⚠️ Lưu ý: UID phải chỉ chứa chữ số</i>"
            )
        else:
            huong_dan = (
                "<b>🔥 HƯỚNG DẪN SỬ DỤNG</b>\n\n"
                "📝 <b>Cách tra cứu trong group:</b>\n"
                "<code>/ff &lt;uid&gt; [vùng]</code>\n\n"
                "<b>Ví dụ:</b>\n"
                "/ff 5498571579\n"
                "/ff@chuong2k8_bot 5498571579 VN\n\n"
                "<i>💡 Để trải nghiệm đầy đủ, hãy nhắn tin riêng với bot!</i>"
            )
        bot.gui_tin_nhan(chat_id, huong_dan, reply_id)
        return
    
    uid = xac_thuc_uid(args[0])
    region = args[1].upper() if len(args) > 1 else bot.cau_hinh.default_region
    
    if not uid:
        error_msg = (
            "❌ <b>UID không hợp lệ</b>\n\n"
            "UID phải chỉ chứa chữ số.\n"
            "Vui lòng kiểm tra lại và thử lại.\n\n"
            "<b>Ví dụ đúng:</b> /ff 5498571579"
        )
        bot.gui_tin_nhan(chat_id, error_msg, reply_id)
        return
    
    # Hiển thị thông báo đang xử lý trong tin nhắn riêng
    if getattr(bot, 'la_tin_nhan_rieng', lambda x: x == "private")(chat_type):
        bot.gui_tin_nhan(chat_id, "🔍 <b>Đang tra cứu thông tin...</b>", reply_id)
    
    data = lay_thong_tin_game_thu(uid, region)
    
    if not data:
        error_msg = (
            "❌ <b>Không tìm thấy thông tin game thủ</b>\n\n"
            "Vui lòng kiểm tra:\n"
            "• UID có chính xác không\n"
            "• Vùng có đúng không (SG, VN, ID...)\n\n"
            "<b>Ví dụ:</b> /ff 5498571579 VN"
        )
        bot.gui_tin_nhan(chat_id, error_msg, reply_id)
        return
    
    msg, player_uid = tao_tin_nhan_game_thu(data, bot.doi_thoi_gian)
    
    # Thêm thông tin người dùng trong group chat
    if chat_type != "private":
        user_info = f"@{username}" if username else f"Người dùng ID {user_id}"
        msg = f"<i>Yêu cầu từ {user_info}:</i>\n\n{msg}"
    
    # Gửi kết quả
    if bot.cau_hinh.enable_photos:
        bot.gui_anh_dai_dien(chat_id, player_uid, msg, reply_id)
    else:
        bot.gui_tin_nhan(chat_id, msg, reply_id)

def xu_ly_lenh_start(bot, chat_id: int, chat_type: str):
    """Xử lý lệnh /start - giới thiệu bot và hướng dẫn sử dụng"""
    if getattr(bot, 'la_tin_nhan_rieng', lambda x: x == "private")(chat_type):
        welcome = (
            "<b>🎉 Chào mừng đến với Bot Tra Cứu Free Fire!</b>\n\n"
            "✨ <b>Tính năng chính:</b>\n"
            "• Tra cứu thông tin game thủ nhanh chóng\n"
            "• Hiển thị chi tiết cấp độ, rank, lượt thích\n"
            "• Xem thời gian tạo tài khoản và đăng nhập gần nhất\n\n"
            "📝 <b>Cách sử dụng:</b>\n"
            "Gõ <code>/ff &lt;uid&gt; [vùng]</code>\n\n"
            "<b>Ví dụ:</b>\n"
            "/ff 5498571579\n"
            "/ff 5498571579 VN\n\n"
            "<i>💡 UID là dãy số bạn thấy trong game khi vào profile của người chơi</i>"
        )
    else:
        welcome = (
            "<b>🎉 Xin chào group!</b>\n\n"
            "Tôi là bot tra cứu thông tin Free Fire.\n\n"
            "📝 <b>Cách sử dụng:</b>\n"
            "/ff &lt;uid&gt; - Tra cứu thông tin game thủ\n\n"
            "<b>Ví dụ:</b> /ff 5498571579\n\n"
            "<i>💡 Nhắn tin riêng với bot để được hỗ trợ đầy đủ hơn!</i>"
        )
    
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
        f"⏱ <b>Thời gian hoạt động:</b> {uptime_str}\n"
        f"🤖 <b>Bot ID:</b> {bot.bot_id}\n"
        f"🌍 <b>Múi giờ:</b> UTC{bot.cau_hinh.timezone_offset:+d} (Việt Nam)"
    )
    bot.gui_tin_nhan(chat_id, status)

def xu_ly_tin_nhan(bot, update: dict):
    """Xử lý tin nhắn/update nhận được - chỉ tập trung vào lệnh /ff"""
    message = update.get("message") or update.get("edited_message")
    if not message:
        return
    
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    chat_type = chat.get("type", "private")  # private, group, supergroup, channel
    msg_id = message.get("message_id")
    text = message.get("text", "")
    user = message.get("from", {})
    user_id = user.get("id")
    username = user.get("username", "")
    first_name = user.get("first_name", "")
    
    # Log thông tin tin nhắn
    chat_info = f"{'💬 Group' if chat_type != 'private' else '👤 Private'} (ID: {chat_id})"
    user_info = f"{first_name} (@{username})" if username else first_name
    bot.logger.info(f"📩 Nhận tin nhắn từ {user_info} (ID: {user_id}) trong {chat_info}: {text}")
    
    # Chỉ xử lý tin nhắn có text
    if not text:
        return
    
    command, args = phan_tich_lenh(text, bot.cau_hinh.bot_username)
    
    # Xử lý các lệnh
    if command == "/ff":
        xu_ly_lenh_ff(bot, chat_id, chat_type, args, msg_id, user_id, username)
    elif command == "/start":
        xu_ly_lenh_start(bot, chat_id, chat_type)
    elif command == "/status":
        xu_ly_lenh_status(bot, chat_id, user_id)
    # Không phản hồi các tin nhắn khác trong group để tránh spam
    elif chat_type == "private":
        # Trong tin nhắn riêng, hiển thị hướng dẫn sử dụng lệnh /ff
        huong_dan_chung = (
            "❓ <b>Tôi chỉ hỗ trợ tra cứu thông tin Free Fire</b>\n\n"
            "📝 <b>Cách sử dụng:</b>\n"
            "<code>/ff &lt;uid&gt; [vùng]</code>\n\n"
            "<b>Ví dụ:</b>\n"
            "/ff 5498571579\n"
            "/ff 5498571579 VN\n\n"
            "<i>UID là dãy số ID game thủ bạn muốn tra cứu</i>"
        )
        bot.gui_tin_nhan(chat_id, huong_dan_chung, msg_id)

def xu_ly_lenh(update: dict, bot):
    """Hàm điểm vào để xử lý lệnh"""
    xu_ly_tin_nhan(bot, update)
