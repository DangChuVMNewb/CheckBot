# 🔥 Free Fire Info Bot

**Telegram bot tra cứu thông tin game thủ Free Fire** - Nhanh chóng, chính xác và dễ sử dụng!

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)](https://www.python.org/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot_API-26A5E4?logo=telegram)](https://core.telegram.org/bots/api)

## 📋 Giới thiệu

Bot Telegram này giúp bạn tra cứu thông tin chi tiết của game thủ Free Fire chỉ với vài cú click. Bot hỗ trợ cả tin nhắn riêng và group chat, tự động chuyển đổi múi giờ sang giờ Việt Nam (UTC+7) và hiển thị thông tin dưới dạng dễ đọc.

## ✨ Tính năng chính

- **Tra cứu thông tin game thủ** bằng UID và vùng
- **Hiển thị thời gian theo múi giờ Việt Nam** (ngày tạo tài khoản, đăng nhập gần nhất)
- **Hỗ trợ cả tin nhắn riêng và group chat**
- **Tự động hiển thị hướng dẫn sử dụng** khi cần
- **Gửi ảnh đại diện kèm thông tin chi tiết** (có thể tắt trong cấu hình)
- **Xử lý lỗi thông minh** với thông báo hướng dẫn cụ thể
- **Kiểm tra quyền tự động** trong group chat
- **Chống spam hiệu quả** trong môi trường group

## 🛠 Cài đặt và cấu hình

### Yêu cầu hệ thống
- Python 3.12+
- Thư viện: `requests`

### Bước 1: Clone repository
```bash
git clone git@github.com:DangChuVMNewb/CheckBot.git
cd CheckBot
```

### Bước 2: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình biến môi trường
Tạo file `.env` hoặc thiết lập biến môi trường:

```bash
BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
ADMIN_IDS="123456789"  # ID Telegram của admin, cách nhau bằng dấu phẩy nếu có nhiều
DEFAULT_REGION="SG"    # Vùng mặc định (SG, VN, ID, TH...)
ENABLE_PHOTOS="true"   # Bật/tắt tính năng gửi ảnh đại diện
```

#### Cách lấy BOT_TOKEN:
1. Tạo bot mới qua [@BotFather](https://t.me/BotFather) trên Telegram
2. Làm theo hướng dẫn để tạo bot mới
3. Copy token được cung cấp và dán vào file cấu hình

#### Cách lấy USER_ID:
- Sử dụng bot [@userinfobot](https://t.me/userinfobot) để lấy ID Telegram của bạn

## ▶️ Chạy bot

```bash
python app.py
```

## 📱 Cách sử dụng

### Trong tin nhắn riêng với bot:
```
/ff 5498571579
/ff 5498571579 VN
```

### Trong group chat:
```
/ff 5498571579
/ff@ten_bot_cua_ban 5498571579 VN
```

### Lệnh hỗ trợ:
- `/start` - Hiển thị thông tin giới thiệu và hướng dẫn
- `/ff` (không có UID) - Hiển thị hướng dẫn sử dụng chi tiết
- `/status` (chỉ admin) - Xem trạng thái hoạt động của bot

## 🎨 Ví dụ kết quả

Khi tra cứu thành công, bot sẽ trả về thông tin dạng:

```
🔥 THÔNG TIN GAME THỦ FREE FIRE

👤 Nickname: GameThuVIP
🆔 UID: 5498571579
🎮 Level: 50
❤️ Lượt thích: 1250
🏆 Rank: 350
📆 Ngày tạo: 15/06/2023 08:30:45 (Giờ VN)
⏰ Đăng nhập gần nhất: 25/12/2025 10:15:22 (Giờ VN)
```

## 🚀 Triển khai trên server

### Triển khai với Systemd (Linux)
Tạo file service: `/etc/systemd/system/freefire-bot.service`

```ini
[Unit]
Description=Free Fire Info Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/CheckBot
Environment="BOT_TOKEN=your_token_here"
Environment="ADMIN_IDS=123456789"
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Sau đó chạy:
```bash
sudo systemctl daemon-reload
sudo systemctl start freefire-bot
sudo systemctl enable freefire-bot
```

## 🔧 Cấu hình nâng cao

| Biến môi trường | Giá trị mặc định | Mô tả |
|----------------|------------------|-------|
| `BOT_TOKEN` | Bắt buộc | Token của Telegram bot |
| `ADMIN_IDS` | "" | Danh sách ID admin (cách nhau bằng dấu phẩy) |
| `DEFAULT_REGION` | "SG" | Vùng mặc định khi không chỉ định |
| `ENABLE_PHOTOS` | "true" | Bật/tắt tính năng gửi ảnh đại diện |
| `POLL_TIMEOUT` | "20" | Thời gian chờ khi lấy cập nhật từ Telegram |
| `REQUEST_TIMEOUT` | "10.0" | Timeout cho các yêu cầu API |
| `TIMEZONE_OFFSET` | "7" | Múi giờ (UTC+7 cho Việt Nam) |

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo Pull Request hoặc báo cáo issues nếu bạn tìm thấy lỗi hoặc có ý tưởng cải tiến.

## 📄 Giấy phép

Dự án này được cấp phép theo [MIT License](LICENSE).

---

**💡 Lưu ý:** Bot sử dụng API bên thứ ba để lấy thông tin game thủ. Nếu gặp lỗi, vui lòng kiểm tra lại UID và vùng đã chọn, hoặc thử lại sau vài phút.

**📞 Hỗ trợ:** Liên hệ admin nếu bạn gặp bất kỳ vấn đề nào trong quá trình sử dụng bot.

**🎉 Chúc bạn có trải nghiệm tuyệt vời với Free Fire Info Bot!** 🔥
