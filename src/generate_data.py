import csv
import os
import random

# 模擬大學常見教科書清單 (書名, 對應課程, 原價範圍)
TEXTBOOKS = [
    ("Data Structures and Algorithm Analysis", "資料結構", 850),
    ("Introduction to Algorithms (CLRS)", "演算法", 1200),
    ("Calculus: Early Transcendentals", "微積分", 1100),
    ("Linear Algebra and Its Applications", "線性代數", 900),
    ("Differential Equations", "微分方程", 880),
    ("Microelectronic Circuits (Sedra/Smith)", "電子學", 1250),
    ("Fundamentals of Electric Circuits", "電路學", 980),
    ("Digital Design (Morris Mano)", "數位邏輯設計", 820),
    ("Electric Machinery Fundamentals", "電機機械", 950),
    ("Computer Organization and Design", "計算機組織", 1050),
    ("Operating System Concepts", "作業系統", 990),
    ("Computer Networking: A Top-Down Approach", "計算機網路", 960),
    ("Python Crash Course", "程式設計", 650),
    ("C++ Primer", "物件導向程式設計", 890),
    ("Discrete Mathematics and Its Applications", "離散數學", 920),
]

CONDITIONS = ["全新未拆", "九成新(無筆記)", "八成新(少許劃記)", "七成新(含重點筆記)", "六成新(書角微損)"]
SELLERS = ["資工一_王小明", "電機二_陳大華", "資工二_林怡君", "電機三_張志豪", "應數二_李雅婷", "資工三_黃冠宇", "電機一_吳宗憲", "通訊二_劉佳穎"]

def generate_csv(filename="data/books.csv", count=100):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    used_isbns = set()

    with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["ISBN", "Title", "Course", "Price", "Condition", "Seller", "Status"])

        for i in range(1, count + 1):
            # 生成不重複的 13 碼模擬 ISBN
            while True:
                isbn = "978" + "".join([str(random.randint(0, 9)) for _ in range(10)])
                if isbn not in used_isbns:
                    used_isbns.add(isbn)
                    break

            title, course, base_price = random.choice(TEXTBOOKS)
            # 加上版次變化讓書名更多樣
            edition = random.choice(["3rd Ed.", "4th Ed.", "5th Ed.", "7th Ed.", "8th Ed."])
            full_title = "{} ({})".format(title, edition)

            # 二手價約為原價的 3 折到 7 折，取 10 的倍數
            price = int((base_price * random.uniform(0.3, 0.7)) // 10) * 10
            condition = random.choice(CONDITIONS)
            seller = random.choice(SELLERS)
            status = "Available"

            writer.writerow([isbn, full_title, course, price, condition, seller, status])

    print("成功生成 {} 筆模擬教科書資料至 {}".format(count, filename))

if __name__ == "__main__":
    generate_csv()