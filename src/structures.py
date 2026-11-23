import time


class Book:
    """教科書資料實體"""
    def __init__(self, isbn, title, course, price, condition, seller, status="Available"):
        self.isbn = isbn
        self.title = title
        self.course = course
        self.price = int(price)
        self.condition = condition
        self.seller = seller
        self.status = status
        # 每本書自帶一個優先佇列，管理預約排隊的買家
        self.waitlist = MinHeap()

    def __str__(self):
        return "[{}] {} | 課程:{} | ${} | {} | 賣家:{} | 狀態:{} (候補:{}人)".format(
            self.isbn, self.title, self.course, self.price,
            self.condition, self.seller, self.status, self.waitlist.size()
        )


# ==========================================
# 1. Hash Table (Separate Chaining) -> ISBN 查詢與刪除 O(1)
# ==========================================
class HashNode:
    def __init__(self, key, book):
        self.key = key
        self.book = book
        self.next = None


class HashTable:
    def __init__(self, capacity=128):
        self.capacity = capacity
        self.buckets = [None] * self.capacity
        self.count = 0

    def _hash(self, key):
        hash_val = 0
        for ch in str(key):
            hash_val = (hash_val * 31 + ord(ch)) % self.capacity
        return hash_val

    def insert(self, book):
        index = self._hash(book.isbn)
        head = self.buckets[index]
        curr = head
        while curr:
            if curr.key == book.isbn:
                curr.book = book
                return
            curr = curr.next
        new_node = HashNode(book.isbn, book)
        new_node.next = head
        self.buckets[index] = new_node
        self.count += 1

    def search(self, isbn):
        index = self._hash(isbn)
        curr = self.buckets[index]
        while curr:
            if curr.key == isbn:
                return curr.book
            curr = curr.next
        return None

    def delete(self, isbn):
        index = self._hash(isbn)
        curr = self.buckets[index]
        prev = None
        while curr:
            if curr.key == isbn:
                if prev is None:
                    self.buckets[index] = curr.next
                else:
                    prev.next = curr.next
                self.count -= 1
                return curr.book
            prev = curr
            curr = curr.next
        return None

    def get_all_books(self):
        result = []
        for head in self.buckets:
            curr = head
            while curr:
                result.append(curr.book)
                curr = curr.next
        return result


# ==========================================
# 2. Trie (Prefix Tree) -> 書名關鍵字前綴搜尋與刪除 O(L)
# ==========================================
class TrieNode:
    def __init__(self):
        self.children = {}
        self.books = []


class BookTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, book):
        node = self.root
        for ch in book.title.lower():
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.books.append(book)

    def search_prefix(self, prefix):
        node = self.root
        for ch in prefix.lower():
            if ch not in node.children:
                return []
            node = node.children[ch]
        results = []
        self._dfs_collect(node, results)
        return results

    def delete(self, book):
        node = self.root
        for ch in book.title.lower():
            if ch not in node.children:
                return False
            node = node.children[ch]
        original_len = len(node.books)
        node.books = [b for b in node.books if b.isbn != book.isbn]
        return len(node.books) < original_len

    def _dfs_collect(self, node, results):
        results.extend(node.books)
        for child in node.children.values():
            self._dfs_collect(child, results)


# ==========================================
# 3. Binary Search Tree (BST) -> 價格區間篩選與節點刪除 O(log n)
# ==========================================
class BSTNode:
    def __init__(self, book):
        self.price = book.price
        self.books = [book]
        self.left = None
        self.right = None


class PriceBST:
    def __init__(self):
        self.root = None

    def insert(self, book):
        if not self.root:
            self.root = BSTNode(book)
        else:
            self._insert_recursive(self.root, book)

    def _insert_recursive(self, node, book):
        if book.price == node.price:
            node.books.append(book)
        elif book.price < node.price:
            if node.left is None:
                node.left = BSTNode(book)
            else:
                self._insert_recursive(node.left, book)
        else:
            if node.right is None:
                node.right = BSTNode(book)
            else:
                self._insert_recursive(node.right, book)

    def delete(self, book):
        self.root = self._delete_recursive(self.root, book)

    def _delete_recursive(self, node, book):
        if not node:
            return None
        if book.price < node.price:
            node.left = self._delete_recursive(node.left, book)
        elif book.price > node.price:
            node.right = self._delete_recursive(node.right, book)
        else:
            node.books = [b for b in node.books if b.isbn != book.isbn]
            # 若該價格節點已無任何書籍，執行標準 BST 節點刪除
            if not node.books:
                if not node.left:
                    return node.right
                if not node.right:
                    return node.left
                # 尋找右子樹最小節點 (In-order Successor) 替換
                successor = node.right
                while successor.left:
                    successor = successor.left
                node.price = successor.price
                node.books = successor.books
                successor.books = []
                node.right = self._remove_empty_min(node.right)
        return node

    def _remove_empty_min(self, node):
        if not node.left:
            return node.right
        node.left = self._remove_empty_min(node.left)
        return node

    def range_search(self, min_price, max_price):
        results = []
        self._inorder_range(self.root, min_price, max_price, results)
        return results

    def _inorder_range(self, node, min_price, max_price, results):
        if not node:
            return
        if node.price > min_price:
            self._inorder_range(node.left, min_price, max_price, results)
        if min_price <= node.price <= max_price:
            results.extend(node.books)
        if node.price < max_price:
            self._inorder_range(node.right, min_price, max_price, results)


# ==========================================
# 4. Min-Heap (Priority Queue) -> 買家候補排隊 O(log n)
# ==========================================
class MinHeap:
    def __init__(self):
        self.heap = []

    def size(self):
        return len(self.heap)

    def push(self, buyer_name, offer_price):
        item = (-int(offer_price), time.time(), buyer_name, int(offer_price))
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        top = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return top

    def peek(self):
        return self.heap[0] if self.heap else None

    def _sift_up(self, idx):
        parent = (idx - 1) // 2
        while idx > 0 and self.heap[idx] < self.heap[parent]:
            self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
            idx = parent
            parent = (idx - 1) // 2

    def _sift_down(self, idx):
        n = len(self.heap)
        while True:
            smallest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2
            if left < n and self.heap[left] < self.heap[smallest]:
                smallest = left
            if right < n and self.heap[right] < self.heap[smallest]:
                smallest = right
            if smallest != idx:
                self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
                idx = smallest
            else:
                break