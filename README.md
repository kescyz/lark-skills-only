# Lark Skills — Cài đặt thủ công

Các file zip chứa skill plugins cho Claude Code / Claude Desktop.

## Cách cài

1. Tải file zip skill bạn muốn
2. Giải nén vào thư mục `.claude/skills/` trong project:
   ```bash
   # Ví dụ: cài lark-calendar
   mkdir -p .claude/skills/lark-calendar
   unzip lark-calendar.zip -d .claude/skills/lark-calendar/
   ```
3. Khởi động lại Claude Code

## Yêu cầu
- Phải có MCP server đã kết nối ([hướng dẫn](https://larkskills.kesflow.vn/setup/claude-code))
- Mỗi skill cần MCP tools từ lark-token-manager để hoạt động

## Danh sách skills
| Skill | Mô tả |
|-------|-------|
| lark-calendar | Lịch & cuộc họp |
| lark-task | Công việc & dự án |
| lark-messenger | Tin nhắn & nhóm chat |
| lark-contacts | Danh bạ tổ chức |
| lark-docs | Tài liệu |
| lark-drive | Quản lý file |
| lark-wiki | Wiki nội bộ |
| lark-sheets | Bảng tính |
| lark-base | Cơ sở dữ liệu Bitable |
| lark-base-formula | Công thức Base (tham khảo) |
| lark-comment | Bình luận |
| lark-token-manager | Quản lý token (bắt buộc) |
