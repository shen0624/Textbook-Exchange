import csv
import os
import time
import random
from structures import Book, HashTable, BookTrie, PriceBST


class TextbookPlatform:
    def __init__(self, csv_path="data/books.csv"):
        self.csv_path = csv_path
        self.hash_table = HashTable(capacity=256)
        self.trie = BookTrie()
        self.price_bst = PriceBST()
        self.load_from_csv()

    def load_from_csv(self):
        if not os.path.exists(self.csv_path):
            print("找不到資料檔 {}，請先執行 generate_data.py".format(self.csv_path))
            return
        with open(self.csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            count = 0
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
                self._index_book(book)
                count += 1
        print("系統初始化完成：已將 {} 筆書籍同步載入 Hash Table、Trie 與 BST。".format(count))

    def _index_book(self, book):
        self.hash_table.insert(book)
        self.trie.insert(book)
        self.price_bst.insert(book)

    def save_to_csv(self):
        books = self.hash_table.get_all_books()
        with open(self.csv_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["ISBN", "Title", "Course", "Price", "Condition", "Seller", "Status"])
            for b in books:
                writer.writerow([b.isbn, b.title, b.course, b.price, b.condition, b.seller, b.status])
        print("資料已成功儲存回 {}。".format(self.csv_path))

    def search_by_isbn(self):
        isbn = input("請輸入完整 13 碼 ISBN：").strip()
        t0 = time.perf_counter()
        book = self.hash_table.search(isbn)
        elapsed = (time.perf_counter() - t0) * 1000
        if book:
            print("\n[查詢成功] 耗時 {:.4f} ms".format(elapsed))
            print(book)
        else:
            print("\n查無此 ISBN 書籍。")

    def search_by_prefix(self):
        prefix = input("請輸入書名開頭關鍵字 (例如 Data 或 Cal)：").strip()
        t0 = time.perf_counter()
        results = self.trie.search_prefix(prefix)
        elapsed = (time.perf_counter() - t0) * 1000
        print("\n[Trie 前綴搜尋] 找到 {} 筆結果 (耗時 {:.4f} ms)：".format(len(results), elapsed))
        for b in results[:15]:
            print(" -", b)
        if len(results) > 15:
            print(" ... 僅顯示前 15 筆")

    def search_by_price_range(self):
        try:
            low = int(input("請輸入最低價格：").strip())
            high = int(input("請輸入最高價格：").strip())
        except ValueError:
            print("價格請輸入整數數字！")
            return
        t0 = time.perf_counter()
        results = self.price_bst.range_search(low, high)
        elapsed = (time.perf_counter() - t0) * 1000
        print("\n[BST 區間搜尋] 價格 ${} ~ ${} 共找到 {} 筆 (依價格由低到高，耗時 {:.4f} ms)：".format(
            low, high, len(results), elapsed))
        for b in results[:15]:
            print(" -", b)
        if len(results) > 15:
            print(" ... 僅顯示前 15 筆")

    def add_new_book(self):
        isbn = input("輸入 13 碼 ISBN：").strip()
        if self.hash_table.search(isbn):
            print("此 ISBN 已存在系統中！")
            return
        title = input("輸入書名：").strip()
        course = input("輸入適用課程：").strip()
        try:
            price = int(input("輸入二手售價：").strip())
        except ValueError:
            print("售價必須為整數！")
            return
        condition = input("輸入書況 (例如 九成新)：").strip()
        seller = input("輸入賣家系級姓名：").strip()

        new_book = Book(isbn, title, course, price, condition, seller)
        self._index_book(new_book)
        print("上架成功！已同步寫入三種資料結構。")

    def reserve_book(self):
        isbn = input("請輸入欲預約的書籍 ISBN：").strip()
        book = self.hash_table.search(isbn)
        if not book:
            print("查無此書籍！")
            return
        if book.status != "Available":
            print("此書目前已售出，無法預約。")
            return
        buyer = input("請輸入買家系級姓名：").strip()
        try:
            offer = int(input("請輸入願意出價金額 (定價為 ${}，出價高者優先)：".format(book.price)).strip())
        except ValueError:
            print("出價必須為整數！")
            return
        book.waitlist.push(buyer, offer)
        top = book.waitlist.peek()
        print("預約成功！目前共有 {} 人排隊，最高順位買家為：{} (出價 ${})".format(
            book.waitlist.size(), top[2], top[3]))

    def complete_transaction(self):
        isbn = input("請輸入欲結單的書籍 ISBN：").strip()
        book = self.hash_table.search(isbn)
        if not book:
            print("查無此書籍！")
            return
        winner = book.waitlist.pop()
        if not winner:
            print("目前無人預約此書。")
            return
        book.status = "Sold"
        print("成交！得標買家為：{}，最終成交價：${} (剩餘候補人數：{})".format(
            winner[2], winner[3], book.waitlist.size()))

    def run_benchmark(self):
        print("\n--- 開始執行資料結構效能實測 (10,000 筆資料) ---")
        n = 10000
        test_ht = HashTable(capacity=16384)
        test_list = []
        target_isbn = ""

        for i in range(n):
            isbn = "978{:010d}".format(i)
            b = Book(isbn, "Test Book {}".format(i), "CS", random.randint(100, 1000), "九成新", "測試員")
            test_ht.insert(b)
            test_list.append(b)
            if i == n - 1:
                target_isbn = isbn

        # 測試 1,000 次搜尋最後一筆資料 (Worst-case for Linear Search)
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

        print("查詢次數：{} 次 (資料規模 N = {})".format(iterations, n))
        print("1. 傳統陣列線性搜尋 O(n) ：{:.2f} ms".format(linear_ms))
        print("2. 手寫 Hash Table O(1)  ：{:.2f} ms".format(hash_ms))
        if hash_ms > 0:
            print("效能提升倍數：約 {:.1f} 倍".format(linear_ms / hash_ms))
        print("----------------------------------------------\n")


def main():
    platform = TextbookPlatform()
    while True:
        print("\n========== 校園二手教科書交換平台 ==========")
        print("1. ISBN 精準查詢        (Hash Table - O(1))")
        print("2. 書名關鍵字前綴搜尋   (Trie 字典樹 - O(L))")
        print("3. 價格區間篩選與排序   (BST 搜尋樹 - O(log n))")
        print("4. 上架新教科書         (同步更新索引)")
        print("5. 預約排隊 / 競標出價  (Min-Heap - O(log n))")
        print("6. 結單分配給最高順位   (Heap Pop)")
        print("7. 執行 10,000 筆效能實測對比 (報告數據用)")
        print("0. 儲存變更並離開")
        choice = input("請選擇功能編號：").strip()

        if choice == "1":
            platform.search_by_isbn()
        elif choice == "2":
            platform.search_by_prefix()
        elif choice == "3":
            platform.search_by_price_range()
        elif choice == "4":
            platform.add_new_book()
        elif choice == "5":
            platform.reserve_book()
        elif choice == "6":
            platform.complete_transaction()
        elif choice == "7":
            platform.run_benchmark()
        elif choice == "0":
            platform.save_to_csv()
            print("感謝使用，系統已安全關閉。")
            break
        else:
            print("無效的選項，請重新輸入。")


if __name__ == "__main__":
    main()