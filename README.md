\# 校園二手教科書交換平台 (Campus Textbook Exchange)



本專案為「資料結構」課程期末專題，旨在解決大學生於學期初買賣與交換二手教科書時，面臨的搜尋效率低落、價格篩選不易及熱門書籍搶購混亂等問題。系統以 \*\*Python\*\* 手寫多種經典資料結構作為底層引擎，不依賴內建高級容器（如 `dict`、`heapq`）實作核心邏輯，並支援 CSV 資料持久化儲存。



\---



\## 一、 系統架構與目錄說明



```text

Textbook-Exchange/

├── src/

│   ├── generate\_data.py   # 自動生成 100 筆模擬大學教科書測試資料集

│   ├── structures.py      # 手寫核心資料結構 (HashTable, BookTrie, PriceBST, MinHeap)

│   └── main.py            # 互動式 CLI 平台主程式與效能對比測試

├── data/

│   └── books.csv          # 教科書庫存資料庫 (支援啟動載入與結束寫回)

├── docs/                  # 專題簡報與測試截圖

└── README.md              # 專案說明與複雜度分析報告

