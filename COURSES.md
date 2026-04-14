# 課程資料夾對照表

## 命名規範

- 資料夾名稱：全小寫英文，以連字號分隔（kebab-case）
- 以工具名稱或主題縮寫為主，不使用通用名稱（如 `course/`）
- 每門課根目錄放 `index.html`（課程總覽頁）

## 課程大綱資料夾

`_outlines/` 存放各課程的 Markdown 大綱文件（`{slug}.md`）。
建立新頁面時，Claude 會先讀取對應大綱，自動取得主題色、學員背景、章節結構，無需重複詢問。
範本：`_outlines/_template.md`

---

## 現有課程

| 資料夾 | 課程名稱（中文） | 狀態 | 備注 |
|--------|----------------|------|------|
| `ai-workshop/` | AI 實務全攻略（12h/18h） | 完成 | 4 Parts，12 CH + 4 PRAC + 4 WS + index，主色霧藍 --c-a4 |
| `gemini-ai/` | Gemini 零代碼 AI 實戰課 | 完成 | 4 Parts，12 單元，含 PRAC 頁 |
| `gtm/` | GTM 實務演練 | 完成 | 4 Parts，13 單元 |
| `office-ai/` | 辦公室 AI 工具實務應用 | 製作中 | 6 章，章節頁待建 |
| `n8n/` | n8n 自動化實戰課 | 完成 | 4 Modules，含 landing page |

---

## 各課程子結構

### ai-workshop/
```
ai-workshop/
├── index.html          課程總覽（12h/18h 版本切換）
├── part1/              CH1-1~3, PRAC1, WS1-A
├── part2/              CH2-1~3, PRAC2, WS2-A
├── part3/              CH3-1~3, PRAC3, WS3-A
└── part4/              CH4-1~3, PRAC4, WS4-A
```

### gemini-ai/
```
gemini-ai/
├── index.html          課程總覽
├── part1/
│   ├── CH1-1.html      單元頁
│   └── PRAC1-1.html    實例演練頁
├── part2/ … part4/
```

### gtm/
```
gtm/
├── index.html          課程總覽
├── part1/ … part4/
```

### office-ai/
```
office-ai/
├── index.html          課程總覽
├── course-outline.docx 課程大綱（個人參考用）
├── ch1/
│   └── CH1.html        單元頁
├── ch2/ … ch6/
```

### n8n/
```
n8n/
├── index.html          課程 Landing Page
└── lessons/
    ├── index.html      課程總覽
    ├── module1.html    模組總覽頁
    ├── m1-1-setup.html 單元頁
    └── …
```

---

## 檔案命名規則

| 類型 | 格式 | 範例 |
|------|------|------|
| 單元頁 | `CH[章]-[節].html` | `CH1-1.html` |
| 實例演練頁 | `PRAC[章]-[節].html` | `PRAC1-1.html` |
| 模組總覽頁 | `module[N].html` | `module1.html` |
| 課程總覽 | `index.html` | — |
| 課程大綱文件 | `course-outline.docx` | — |

---

## 待加入課程（預留位置）

| 資料夾 | 課程名稱 | 狀態 |
|--------|---------|------|
| `make-com/` | Make.com 自動化入門 | 規劃中 |

---

*最後更新：2026-04-14*
