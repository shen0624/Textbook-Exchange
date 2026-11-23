import csv
import os
import time
import random
import streamlit as st
from structures import Book, HashTable, BookTrie, PriceBST

st.set_page_config(page_title="校園二手教科書交換平台", page_icon="📚", layout="wide")

CSV_PATH = "data/books.csv"


def load_platform():
    ht = HashTable(capacity=256)
    trie = BookTrie()
    bst = PriceBST()
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                book = Book(
                    isbn=row["ISBN"],
                    title=row["Title"],
                    course=row["Course"],
                    price=row["Price"],
                    condition=row["Condition"],
                    seller=row["Seller"],
                    status=row["Status"]
                )
                ht.insert(book)
                trie.insert(book)
                bst.insert(book)
    return ht, trie, bst


def save_platform(ht):
    books = ht.get_all_books()
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["ISBN", "Title", "Course", "Price", "Condition", "Seller", "Status"])
        for b in books:
            writer.writerow([b.isbn, b.title, b.course, b.price, b.condition, b.seller, b.status])


def books_to_table(books):
    return [
        {
            "ISBN": b.isbn,
            "書名": b.title,
            "適用課程": b.course,
            "售價 ($)": b.price,
            "書況": b.condition,
            "賣家": b.seller,
            "狀態": b.status,
            "候補人數": b.waitlist.size()
        }
        for b in books
    ]


# 初始化 Session State（確保操作過程中資料結構狀態維持在記憶體）
if "initialized" not in st.session_state:
    ht, trie, bst = load_platform()
    st.session_state.ht = ht
    st.session_state.trie = trie
    st.session_state.bst = bst
    st.session_state.initialized = True

ht = st.session_state.ht
trie = st.session_state.trie
bst = st.session_state.bst

st.title("📚 校園二手教科書交換平台")
st.caption("底層引擎：手寫 Hash Table、Trie 字典樹、BST 二元搜尋樹、Min-Heap 優先佇列")

# 側邊欄：快速統計與存檔
with st.sidebar:
    st.header("📊 平台即時狀態")
    all_books = ht.get_all_books()
    avail_count = sum(1 for b in all_books if b.status == "Available")
    st.metric("館藏總書目", f"{len(all_books)} 本")
    st.metric("可交易書籍", f"{avail_count} 本")
    st.divider()
    if st.button("💾 儲存變更至 CSV", use_container_width=True):
        save_platform(ht)
        st.success("已成功寫回 data/books.csv！")

# 分頁選單
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 書籍搜尋 (Hash / Trie / BST)",
    "➕ 上架新教科書",
    "🔥 熱門預約排隊 (Min-Heap)",
    "⚡ 效能實測對比 (Benchmark)"
])

# ==========================================
# 分頁 1：三種資料結構搜尋
# ==========================================
with tab1:
    mode = st.radio(
        "選擇底層搜尋資料結構：",
        ["書名關鍵字前綴搜尋 (Trie - O(L))", "價格區間篩選排序 (BST - O(log n))", "ISBN 精準查詢 (Hash Table - O(1))"],
        horizontal=True
    )

    if mode.startswith("書名"):
        prefix = st.text_input("輸入書名開頭關鍵字（例如 Data、Cal、Linear，留空顯示全部）：", "")
        t0 = time.perf_counter()
        results = trie.search_prefix(prefix) if prefix else all_books
        elapsed = (time.perf_counter() - t0) * 1000
        st.info(f"Trie 搜尋完成：共找到 **{len(results)}** 筆結果（耗時 `{elapsed:.4f} ms`）")
        if results:
            st.dataframe(books_to_table(results), use_container_width=True, hide_index=True)

    elif mode.startswith("價格"):
        min_p, max_p = st.slider("拖曳選擇價格區間 ($)：", 100, 1200, (250, 550), step=10)
        t0 = time.perf_counter()
        results = bst.range_search(min_p, max_p)
        elapsed = (time.perf_counter() - t0) * 1000
        st.info(f"BST 中序走訪完成：`${min_p} ~ ${max_p}` 共 **{len(results)}** 筆，已依價格由低到高排序（耗時 `{elapsed:.4f} ms`）")
        if results:
            st.dataframe(books_to_table(results), use_container_width=True, hide_index=True)

    else:
        isbn_query = st.text_input("輸入完整 13 碼 ISBN：", "")
        if isbn_query:
            t0 = time.perf_counter()
            book = ht.search(isbn_query.strip())
            elapsed = (time.perf_counter() - t0) * 1000
            if book:
                st.success(f"Hash Table 查詢成功（耗時 `{elapsed:.4f} ms`）")
                st.dataframe(books_to_table([book]), use_container_width=True, hide_index=True)
            else:
                st.warning("查無此 ISBN 書籍。")

# ==========================================
# 分頁 2：上架新教科書
# ==========================================
with tab2:
    st.subheader("上架二手教科書（同步寫入 Hash Table、Trie 與 BST）")
    with st.form("add_book_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_isbn = st.text_input("13 碼 ISBN", placeholder="例如 9781234567890")
            new_title = st.text_input("書名", placeholder="例如 Data Structures in Python")
            new_course = st.text_input("適用課程", placeholder="例如 資料結構")
        with col2:
            new_price = st.number_input("二手售價 ($)", min_value=50, max_value=3000, value=400, step=10)
            new_cond = st.selectbox("書況", ["全新未拆", "九成新(無筆記)", "八成新(少許劃記)", "七成新(含重點筆記)"])
            new_seller = st.text_input("賣家系級姓名", placeholder="例如 電機二_王小明")

        submitted = st.form_submit_button("確認上架")
        if submitted:
            if not new_isbn or not new_title or not new_seller:
                st.error("請填寫完整 ISBN、書名與賣家資訊！")
            elif ht.search(new_isbn.strip()):
                st.error("此 ISBN 已存在系統中！")
            else:
                b = Book(new_isbn.strip(), new_title.strip(), new_course.strip(), new_price, new_cond, new_seller.strip())
                ht.insert(b)
                trie.insert(b)
                bst.insert(b)
                save_platform(ht)
                st.success(f"《{new_title}》上架成功並已存入資料庫！")

# ==========================================
# 分頁 3：Min-Heap 預約排隊與結單
# ==========================================
with tab3:
    st.subheader("熱門書籍競標排隊系統（Min-Heap 優先佇列）")
    st.write("出價越高者排在堆積頂端（優先成交）；若出價相同，則依預約時間先後決定。")

    avail_books = [b for b in all_books if b.status == "Available"]
    if not avail_books:
        st.warning("目前沒有可預約的書籍。")
    else:
        book_options = {f"[{b.isbn}] {b.title} (${b.price}) - 候補:{b.waitlist.size()}人": b for b in avail_books}
        selected_label = st.selectbox("選擇要預約或結單的書籍：", list(book_options.keys()))
        target_book = book_options[selected_label]

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### 1️⃣ 買家加入候補排隊")
            buyer_name = st.text_input("買家系級姓名", placeholder="例如 資工二_林怡君")
            offer_price = st.number_input("出價金額 ($)", min_value=50, max_value=5000, value=target_book.price, step=10)
            if st.button("送出預約 (Heap Push)"):
                if not buyer_name.strip():
                    st.error("請輸入買家姓名！")
                else:
                    target_book.waitlist.push(buyer_name.strip(), offer_price)
                    st.success(f"預約成功！目前最高順位：{target_book.waitlist.peek()[2]} (出價 ${target_book.waitlist.peek()[3]})")
                    st.rerun()

        with col_b:
            st.markdown("#### 2️⃣ 賣家結單分配")
            top = target_book.waitlist.peek()
            if top:
                st.info(f"目前排隊人數：**{target_book.waitlist.size()} 人**\n\n最高順位買家：**{top[2]}**（出價 **${top[3]}**）")
                if st.button("確認結單給最高順位 (Heap Pop)", type="primary"):
                    winner = target_book.waitlist.pop()
                    target_book.status = "Sold"
                    save_platform(ht)
                    st.success(f"🎉 成交！得標買家：{winner[2]}，成交價：${winner[3]}")
                    st.rerun()
            else:
                st.write("目前尚無人預約此書籍。")

# ==========================================
# 分頁 4：10,000 筆效能對比測試
# ==========================================
with tab4:
    st.subheader("10,000 筆資料搜尋效能實測 (Complexity Benchmark)")
    st.write("模擬 10,000 筆教科書資料，重複執行 1,000 次最壞情況（Worst-Case）搜尋，比較線性掃描與手寫雜湊表的速度差異。")

    if st.button("🚀 開始執行效能實測", type="primary"):
        n = 10000
        test_ht = HashTable(capacity=16384)
        test_list = []
        target_isbn = ""

        for i in range(n):
            isbn = f"978{i:010d}"
            b = Book(isbn, f"Test Book {i}", "CS", random.randint(100, 1000), "九成新", "測試員")
            test_ht.insert(b)
            test_list.append(b)
            if i == n - 1:
                target_isbn = isbn

        iterations = 1000
        t0 = time.perf_counter()
        for _ in range(iterations):
            for item in test_list:
                if item.isbn == target_isbn:
                    break
        linear_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        for _ in range(iterations):
            test_ht.search(target_isbn)
        hash_ms = (time.perf_counter() - t0) * 1000

        speedup = linear_ms / hash_ms if hash_ms > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("傳統陣列線性搜尋 O(n)", f"{linear_ms:.2f} ms")
        c2.metric("手寫 Hash Table O(1)", f"{hash_ms:.2f} ms")
        c3.metric("效能提升倍數", f"{speedup:.1f} 倍")