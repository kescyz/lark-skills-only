# Lark Skills v2.1.1 - Individual Skill Plugins

Skill plugins rieng le cho LarkSuite. Cai thu cong vao Claude Code, Claude Desktop, hoac upload len Claude.ai.

## Cach cai (Claude Code / Claude Desktop)

```bash
# Copy folder skill vao .claude/skills/ trong project
cp -r lark-calendar .claude/skills/lark-calendar
cp -r lark-token-manager .claude/skills/lark-token-manager  # bat buoc

# Hoac clone repo roi copy
git clone https://github.com/kescyz/lark-skills-only.git
cp -r lark-skills-only/lark-docs .claude/skills/lark-docs
```

## Upload len Claude.ai

Claude.ai chi nhan file **.zip**. Neu muon upload skill len Claude.ai:

```bash
# Buoc 1: Tai ve repo
git clone https://github.com/kescyz/lark-skills-only.git
cd lark-skills-only

# Buoc 2: Zip skill can dung
cd lark-docs && zip -r ../lark-docs.zip . && cd ..
cd lark-base && zip -r ../lark-base.zip . && cd ..
# ... tuong tu cho cac skill khac

# Buoc 3: Upload file .zip len Claude.ai > Skills
```

**Luu y:** Zip tu **ben trong** folder (ko zip folder cha). File zip phai chua `SKILL.md` o root.

## Yeu cau

- MCP server da ket noi ([huong dan](https://larkskills.kesflow.vn/setup/claude-code))
- Moi skill can MCP tools tu `lark-token-manager` de hoat dong
- Python 3.10+ (cac script dung `urllib.request`)

## Danh sach skills (12 plugins, 248 methods)

| Skill | Methods | Mo ta |
|-------|---------|-------|
| lark-calendar | 12 | Lich & cuoc hop |
| lark-task | 29 | Cong viec, subtasks, sections |
| lark-messenger | 34 | Tin nhan, cards, nhom chat, webhooks |
| lark-contacts | 16 | Danh ba to chuc |
| lark-docs | 25 | Tai lieu DocX, block editing, import markdown |
| lark-drive | 17 | Quan ly file, upload, download, chia se |
| lark-wiki | 15 | Wiki noi bo, knowledge base |
| lark-sheets | 23 | Bang tinh, formatting |
| lark-base | 36 | Co so du lieu Bitable |
| lark-base-formula | 13 | Cong thuc Base (tham khao) |
| lark-comment | 8 | Binh luan tren docs/sheets |
| lark-token-manager | 17 | Quan ly OAuth token (bat buoc) |

## Cach khac: Cai tu Marketplace (khuyen dung)

```bash
# Trong Claude Code - cai tat ca 12 skills mot luc
/plugin marketplace add kescyz/lark-skills-marketplace
/plugin install lark-skills@lark-skills-marketplace
```

## License

Proprietary. All rights reserved.
