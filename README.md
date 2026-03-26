# Lark Skills v2.1.1 - Skill Plugins riêng lẻ

Skill plugins riêng lẻ cho LarkSuite. Cài thủ công vào Claude Code, Claude Desktop, hoặc upload lên Claude.ai.

## Cách cài (Claude Code / Claude Desktop)

```bash
# Copy folder skill vào .claude/skills/ trong project
cp -r lark-calendar .claude/skills/lark-calendar
cp -r lark-token-manager .claude/skills/lark-token-manager  # bắt buộc

# Hoặc clone repo rồi copy
git clone https://github.com/kescyz/lark-skills-only.git
cp -r lark-skills-only/lark-docs .claude/skills/lark-docs
```

## Upload lên Claude.ai

Claude.ai chỉ nhận file **.zip**. Nếu muốn upload skill lên Claude.ai:

```bash
# Bước 1: Tải về repo
git clone https://github.com/kescyz/lark-skills-only.git
cd lark-skills-only

# Bước 2: Zip skill cần dùng
cd lark-docs && zip -r ../lark-docs.zip . && cd ..
cd lark-base && zip -r ../lark-base.zip . && cd ..
# ... tương tự cho các skill khác

# Bước 3: Upload file .zip lên Claude.ai > Skills
```

**Lưu ý:** Zip từ **bên trong** folder (không zip folder cha). File zip phải chứa `SKILL.md` ở root.

## Yêu cầu

- MCP server đã kết nối ([hướng dẫn](https://larkskills.kesflow.vn/setup/claude-code))
- Mỗi skill cần MCP tools từ `lark-token-manager` để hoạt động
- Python 3.10+ (các script dùng `urllib.request`)

## Danh sách skills (12 plugins, 248 methods)

| Skill | Methods | Mô tả |
|-------|---------|-------|
| lark-calendar | 12 | Lịch & cuộc họp |
| lark-task | 29 | Công việc, subtasks, sections |
| lark-messenger | 34 | Tin nhắn, cards, nhóm chat, webhooks |
| lark-contacts | 16 | Danh bạ tổ chức |
| lark-docs | 25 | Tài liệu DocX, block editing, import markdown |
| lark-drive | 17 | Quản lý file, upload, download, chia sẻ |
| lark-wiki | 15 | Wiki nội bộ, knowledge base |
| lark-sheets | 23 | Bảng tính, formatting |
| lark-base | 36 | Cơ sở dữ liệu Bitable |
| lark-base-formula | 13 | Công thức Base (tham khảo) |
| lark-comment | 8 | Bình luận trên docs/sheets |
| lark-token-manager | 17 | Quản lý OAuth token (bắt buộc) |

## Cách khác: Cài từ Marketplace (khuyên dùng)

```bash
# Trong Claude Code - cài tất cả 12 skills một lúc
/plugin marketplace add kescyz/lark-skills-marketplace
/plugin install lark-skills@lark-skills-marketplace
```

## License

Proprietary. All rights reserved.
