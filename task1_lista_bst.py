"""
Zadanie I – Porównanie posortowanej listy jednokierunkowej i drzewa BST
Mierzony czas: tworzenia, wyszukiwania (wg tablicy pomocniczej), usuwania
Autor: sprawozdanie AiSD
"""

import random
import time
import sys
from typing import Optional
import matplotlib.pyplot as plt
import numpy as np

sys.setrecursionlimit(200_000)

# ──────────────────────────────────────────────────────────
# 1. POSORTOWANA LISTA JEDNOKIERUNKOWA
# ──────────────────────────────────────────────────────────

class ListNode:
    """Węzeł listy jednokierunkowej."""
    __slots__ = ("info", "next")

    def __init__(self, info: int):
        self.info = info
        self.next = None


class SortedLinkedList:
    """
    Posortowana lista jednokierunkowa.
    Sortowanie odbywa się W TRAKCIE wstawiania (insertion sort online).
    Implementacja na podstawie pseudokodu z zajęć.
    """

    def __init__(self):
        self.head: ListNode | None = None

    # ---------- wstawianie (pseudokod z zajęć) ----------
    def insert(self, a: int) -> None:
        if self.head is None:
            node = ListNode(a)
            self.head = node  
        else:
            if self.head.info > a:          # wstaw przed głową
                tmp = ListNode(a)
                tmp.next = self.head
                self.head = tmp
            else:
                tmp = self.head
                # idź dopóki następnik istnieje I jest mniejszy od a
                while tmp.next is not None and tmp.next.info < a:
                    tmp = tmp.next
                tmp2 = ListNode(a)
                tmp2.next = tmp.next
                tmp.next = tmp2

    # ---------- wyszukiwanie ----------
    def search(self, x: int) -> Optional[ListNode]:
        tmp = self.head
        while tmp is not None:
            if tmp.info == x:
                return tmp
            if tmp.info > x:        # lista posortowana → dalej nie ma sensu szukać
                return None
            tmp = tmp.next
        return None

    # ---------- usuwanie pierwszego elementu ----------
    def delete_first(self) -> None:
        if self.head is not None:
            self.head = self.head.next

    def delete_all(self) -> None:
        """Usuwa całą listę, zawsze usuwając pierwszy element."""
        while self.head is not None:
            self.delete_first()


# ──────────────────────────────────────────────────────────
# 2. DRZEWO POSZUKIWAŃ BINARNYCH (BST)
# ──────────────────────────────────────────────────────────

class TreeNode:
    """Węzeł drzewa BST."""
    __slots__ = ("info", "left", "right")

    def __init__(self, info: int):
        self.info = info
        self.left: "TreeNode | None" = None
        self.right: "TreeNode | None" = None


class BST:
    """
    Drzewo poszukiwań binarnych.
    Wstawianie / wyszukiwanie / usuwanie zgodne z pseudokodem z zajęć.
    """

    def __init__(self):
        self.root: Optional[TreeNode] = None

    def insert(self, x: int) -> None:
        if self.root is None:
            self.root = TreeNode(x)
            return
        ptr = self.root
        while True:
            if x < ptr.info:
                if ptr.left is None:
                    ptr.left = TreeNode(x)
                    return
                ptr = ptr.left
            elif x > ptr.info:
                if ptr.right is None:
                    ptr.right = TreeNode(x)
                    return
                ptr = ptr.right
            else:
                return

    # ---------- wyszukiwanie (pseudokod z zajęć) ----------
    def search(self, x: int) -> Optional[TreeNode]:
        ptr = self.root
        while ptr:
            if x > ptr.info:
                ptr = ptr.right
            elif x < ptr.info:
                ptr = ptr.left
            else:
                break          # znaleziono
        return ptr

    # ---------- przechodzenie postorder ----------
    def _postorder(self, root: Optional[TreeNode], result: list) -> None:
        """Odczytuje węzły w porządku postorder (pseudokod z zajęć)."""
        if root is not None:
            self._postorder(root.left, result)
            self._postorder(root.right, result)
            result.append(root.info)

    def postorder_values(self) -> list[int]:
        result: list[int] = []
        self._postorder(self.root, result)
        return result

    # ---------- usuwanie węzła (standardowe BST) ----------
    def _delete(self, root: Optional[TreeNode], x: int) -> Optional[TreeNode]:
        if root is None:
            return None
        if x < root.info:
            root.left = self._delete(root.left, x)
        elif x > root.info:
            root.right = self._delete(root.right, x)
        else:
            # węzeł do usunięcia
            if root.left is None:
                return root.right
            if root.right is None:
                return root.left
            # dwa dzieci → następnik inorder (minimum prawego poddrzewa)
            successor = root.right
            while successor.left:
                successor = successor.left
            root.info = successor.info
            root.right = self._delete(root.right, successor.info)
        return root

    def delete(self, x: int) -> None:
        self.root = self._delete(self.root, x)

    def delete_all_postorder(self) -> None:
        """
        Usuwa wszystkie elementy drzewa w porządku wstecznym (postorder).
        Dzięki temu usuwamy najpierw liście, potem węzły wewnętrzne.
        """
        order = self.postorder_values()
        for val in order:
            self.delete(val)


# ──────────────────────────────────────────────────────────
# 3. POMIAR CZASU
# ──────────────────────────────────────────────────────────

SIZES = list(range(3_000, 46_000, 3_000))  # 3000, 6000, ..., 45000 (15 punktów)
REPEATS = 3     # uśrednianie pomiarów


def measure(sizes: list[int], repeats: int = REPEATS):
    """
    Dla każdego rozmiaru N mierzy:
      - czas budowania listy i BST
      - czas wyszukiwania wszystkich elementów (tablica pomocnicza)
      - czas usuwania całej struktury
    Zwraca słownik z listami wyników.
    """
    results = {
        "n":            [],
        "list_build":   [],
        "bst_build":    [],
        "list_search":  [],
        "bst_search":   [],
        "list_delete":  [],
        "bst_delete":   [],
    }

    for n in sizes:
        print(f"  N = {n} ...", end=" ", flush=True)

        t_list_build  = t_bst_build  = 0.0
        t_list_search = t_bst_search = 0.0
        t_list_del    = t_bst_del    = 0.0

        for _ in range(repeats):
            # losowy ciąg bez powtórzeń
            data = random.sample(range(n * 10), n)
            aux  = data[:]          # tablica pomocnicza do wyszukiwania
            random.shuffle(aux)     # kolejność wyszukiwania różna od kolejności wstawiania

            # ── TWORZENIE ──
            lst = SortedLinkedList()
            t0 = time.perf_counter()
            for val in data:
                lst.insert(val)
            t_list_build += time.perf_counter() - t0

            bst = BST()
            t0 = time.perf_counter()
            for val in data:
                bst.insert(val)
            t_bst_build += time.perf_counter() - t0

            # ── WYSZUKIWANIE (przez tablicę pomocniczą) ──
            t0 = time.perf_counter()
            for val in aux:
                lst.search(val)
            t_list_search += time.perf_counter() - t0

            t0 = time.perf_counter()
            for val in aux:
                bst.search(val)
            t_bst_search += time.perf_counter() - t0

            # ── USUWANIE ──
            t0 = time.perf_counter()
            lst.delete_all()        # zawsze usuwa pierwszy element
            t_list_del += time.perf_counter() - t0

            t0 = time.perf_counter()
            bst.delete_all_postorder()    # elementy w porządku wstecznym (postorder)
            t_bst_del += time.perf_counter() - t0

        # uśrednianie
        results["n"].append(n)
        results["list_build"].append(t_list_build   / repeats)
        results["bst_build"].append(t_bst_build    / repeats)
        results["list_search"].append(t_list_search  / repeats)
        results["bst_search"].append(t_bst_search   / repeats)
        results["list_delete"].append(t_list_del     / repeats)
        results["bst_delete"].append(t_bst_del      / repeats)

        print("OK")

    return results


# ──────────────────────────────────────────────────────────
# 4. WYKRESY
# ──────────────────────────────────────────────────────────

def plot_results(results: dict, log_scale: bool = False) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(
        "Porównanie: Posortowana Lista jednokierunkowa vs BST\n"
        f"(skala {'logarytmiczna' if log_scale else 'liniowa'})",
        fontsize=13, fontweight="bold"
    )

    ns = results["n"]
    ops = [
        ("Tworzenie struktury",      "list_build",  "bst_build"),
        ("Wyszukiwanie (wszystkich)", "list_search", "bst_search"),
        ("Usuwanie struktury",        "list_delete", "bst_delete"),
    ]

    colors = {"Lista": "#e74c3c", "BST": "#2980b9"}
    markers = {"Lista": "o", "BST": "s"}

    for ax, (title, list_key, bst_key) in zip(axes, ops):
        ax.plot(ns, results[list_key], color=colors["Lista"],
                marker=markers["Lista"], label="Lista jednokierunkowa", linewidth=2)
        ax.plot(ns, results[bst_key],  color=colors["BST"],
                marker=markers["BST"],  label="BST",                   linewidth=2)

        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xlabel("Liczba elementów N", fontsize=10)
        ax.set_ylabel("Czas [s]", fontsize=10)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

        if log_scale:
            ax.set_yscale("log")

    plt.tight_layout()
    filename = "task1_wyniki_log.png" if log_scale else "task1_wyniki_liniowe.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    print(f"  Wykres zapisany: {filename}")
    plt.show()


def save_csv(results: dict, filename: str = "task1_dane.csv") -> None:
    """Zapisuje wyniki do pliku CSV."""
    import csv
    headers = ["N", "Lista_budowa[s]", "BST_budowa[s]",
               "Lista_szukanie[s]", "BST_szukanie[s]",
               "Lista_usuwanie[s]", "BST_usuwanie[s]"]
    rows = zip(
        results["n"],
        results["list_build"],  results["bst_build"],
        results["list_search"], results["bst_search"],
        results["list_delete"], results["bst_delete"],
    )
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(headers)
        for row in rows:
            w.writerow([f"{v:.8f}" if isinstance(v, float) else v for v in row])
    print(f"  Dane CSV zapisane: {filename}")



# ──────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  ZADANIE I – Lista jednokierunkowa vs BST")
    print("=" * 60)
    print(f"\nRozmiary N: {SIZES}")
    print(f"Powtórzenia (uśrednianie): {REPEATS}\n")

    print("Pomiar czasów...")
    results = measure(SIZES, REPEATS)

    print("\nZapis danych...")
    save_csv(results)

    print("\nGenerowanie wykresów...")
    plot_results(results, log_scale=False)
    plot_results(results, log_scale=True)


