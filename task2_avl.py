"""
Zadanie II – Porównanie wysokości drzewa BST i wyważonego drzewa AVL
Metoda wyważania: odczytaj BST inorder → posortowana tablica → połowienie binarne
Autor: sprawozdanie AiSD
"""

import random
import sys
from typing import Optional
import matplotlib.pyplot as plt
import numpy as np

sys.setrecursionlimit(200_000)

# ──────────────────────────────────────────────────────────
# 1. DRZEWO BST
# ──────────────────────────────────────────────────────────

class TreeNode:
    """Węzeł drzewa."""
    __slots__ = ("info", "left", "right")

    def __init__(self, info: int):
        self.info  = info
        self.left  = None
        self.right = None


class BST:
    """
    Drzewo poszukiwań binarnych – zgodne z pseudokodem z zajęć.
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
                return  # duplikat – ignoruj

    def inorder_values(self) -> list:
        """Zwraca posortowaną listę wartości (inorder) – wersja iteracyjna."""
        result = []
        stack  = []
        ptr    = self.root
        while ptr or stack:
            while ptr:
                stack.append(ptr)
                ptr = ptr.left
            ptr = stack.pop()
            result.append(ptr.info)
            ptr = ptr.right
        return result

    # ---------- wysokość ----------
    def _height(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0
        return 1 + max(self._height(root.left), self._height(root.right))

    def height(self) -> int:
        return self._height(self.root)


# ──────────────────────────────────────────────────────────
# 2. WYWAŻONE DRZEWO (metoda połowienia binarnego)
# ──────────────────────────────────────────────────────────

class BalancedBST:
    """
    Wyważone drzewo BST zbudowane metodą połowienia binarnego.
    Algorytm:
      1. Odczytaj elementy BST w porządku inorder → posortowana tablica
      2. Rekurencyjnie wybieraj środkowy element jako korzeń (połowienie binarne)
      3. Lewe poddrzewo  ← lewa połowa tablicy
         Prawe poddrzewo ← prawa połowa tablicy
    Wynikowe drzewo ma minimalną możliwą wysokość ⌈log₂(N+1)⌉.
    """

    def __init__(self):
        self.root: Optional[TreeNode] = None

    def build_from_sorted(self, sorted_arr: list) -> None:
        """
        Buduje wyważone drzewo z posortowanej tablicy
        metodą połowienia binarnego.
        """
        self.root = self._build(sorted_arr, 0, len(sorted_arr) - 1)

    def _build(self, arr: list, lo: int, hi: int) -> Optional[TreeNode]:
        """
        Rekurencja:
          - środkowy element → bieżący korzeń
          - lewa  połowa → lewe  poddrzewo
          - prawa połowa → prawe poddrzewo
        """
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        node = TreeNode(arr[mid])
        node.left  = self._build(arr, lo,      mid - 1)
        node.right = self._build(arr, mid + 1, hi)
        return node

    # ---------- wysokość ----------
    def _height(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0
        return 1 + max(self._height(root.left), self._height(root.right))

    def height(self) -> int:
        return self._height(self.root)

    # ---------- weryfikacja: czy jest BST i czy jest zbalansowany ----------
    def _is_balanced(self, root: Optional[TreeNode]) -> tuple:
        """Zwraca (jest_zbalansowane, wysokość)."""
        if root is None:
            return True, 0
        bal_l, h_l = self._is_balanced(root.left)
        bal_r, h_r = self._is_balanced(root.right)
        balanced = bal_l and bal_r and abs(h_l - h_r) <= 1
        return balanced, 1 + max(h_l, h_r)

    def is_balanced(self) -> bool:
        ok, _ = self._is_balanced(self.root)
        return ok


# ──────────────────────────────────────────────────────────
# 3. POMIAR WYSOKOŚCI DLA RÓŻNYCH N
# ──────────────────────────────────────────────────────────

SIZES   = list(range(10_000, 160_000, 10_000))  # 10000, 20000, ..., 150000 (15 punktów)
REPEATS = 3   # uśrednianie (BST jest wrażliwy na kolejność wstawień)


def measure_heights(sizes: list, repeats: int = REPEATS) -> dict:
    """
    Dla każdego N buduje BST z losowych danych, wyważa go,
    i zapisuje obie wysokości.
    """
    results = {
        "n":          [],
        "bst_height": [],
        "avl_height": [],
        "log2_N":     [],   # teoretyczne minimum ⌈log₂(N+1)⌉
    }

    for n in sizes:
        print(f"  N = {n:>6} ...", end=" ", flush=True)

        h_bst_sum = 0
        h_avl_sum = 0

        for _ in range(repeats):
            data = random.sample(range(n * 10), n)

            # Buduj BST
            bst = BST()
            for val in data:
                bst.insert(val)

            # Odczytaj inorder → posortowana tablica
            sorted_vals = bst.inorder_values()

            # Zbuduj wyważone drzewo metodą połowienia binarnego
            avl = BalancedBST()
            avl.build_from_sorted(sorted_vals)

            h_bst_sum += bst.height()
            h_avl_sum += avl.height()

        results["n"].append(n)
        results["bst_height"].append(h_bst_sum / repeats)
        results["avl_height"].append(h_avl_sum / repeats)
        results["log2_N"].append(np.ceil(np.log2(n + 1)))

        print(f"BST śr.={h_bst_sum/repeats:.1f}  AVL={h_avl_sum/repeats:.1f}  "
              f"⌈log₂(N+1)⌉={int(np.ceil(np.log2(n+1)))}")

    return results


# ──────────────────────────────────────────────────────────
# 4. DEMO JEDNEGO KONKRETNEGO DRZEWA (wydruk tekstowy)
# ──────────────────────────────────────────────────────────

def demo_single(n: int = 15) -> None:
    """Pokazuje konkretny przykład dla małego N."""
    data = random.sample(range(n * 5), n)
    print(f"\n  Przykładowe dane (N={n}): {data}")

    bst = BST()
    for val in data:
        bst.insert(val)

    sorted_vals = bst.inorder_values()
    print(f"  Inorder BST (posortowane): {sorted_vals}")

    avl = BalancedBST()
    avl.build_from_sorted(sorted_vals)

    print(f"  Wysokość BST             : {bst.height()}")
    print(f"  Wysokość po wyważeniu    : {avl.height()}")
    print(f"  ⌈log₂(N+1)⌉             : {int(np.ceil(np.log2(n+1)))}")
    print(f"  Wyważone? (AVL-property) : {avl.is_balanced()}")


# ──────────────────────────────────────────────────────────
# 5. WYKRESY
# ──────────────────────────────────────────────────────────

def plot_heights(results: dict) -> None:
    ns  = results["n"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "Porównanie wysokości drzewa BST i wyważonego drzewa (połowienie binarne)",
        fontsize=13, fontweight="bold"
    )

    # ── wykres 1: skala liniowa ──
    ax = axes[0]
    ax.plot(ns, results["bst_height"], color="#e74c3c", marker="o",
            linewidth=2, label="BST (losowe dane, śr.)")
    ax.plot(ns, results["avl_height"], color="#27ae60", marker="s",
            linewidth=2, label="Wyważone BST (połowienie)")
    ax.plot(ns, results["log2_N"],     color="#7f8c8d", marker="^",
            linewidth=1.5, linestyle="--", label="⌈log₂(N+1)⌉ – minimum teoret.")
    ax.set_title("Skala liniowa")
    ax.set_xlabel("Liczba elementów N")
    ax.set_ylabel("Wysokość drzewa")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # ── wykres 2: skala logarytmiczna (oś X) ──
    ax = axes[1]
    ax.semilogx(ns, results["bst_height"], color="#e74c3c", marker="o",
                linewidth=2, label="BST (losowe dane, śr.)")
    ax.semilogx(ns, results["avl_height"], color="#27ae60", marker="s",
                linewidth=2, label="Wyważone BST (połowienie)")
    ax.semilogx(ns, results["log2_N"],     color="#7f8c8d", marker="^",
                linewidth=1.5, linestyle="--", label="⌈log₂(N+1)⌉ – minimum teoret.")
    ax.set_title("Skala logarytmiczna (oś X)")
    ax.set_xlabel("Liczba elementów N (log)")
    ax.set_ylabel("Wysokość drzewa")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("task2_wysokosci.png", dpi=150, bbox_inches="tight")
    print("\n  Wykres zapisany: task2_wysokosci.png")
    plt.show()


def plot_height_ratio(results: dict) -> None:
    """Dodatkowy wykres: stosunek H_BST / H_AVL."""
    ns    = results["n"]
    ratio = [b / a for b, a in zip(results["bst_height"], results["avl_height"])]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(ns, ratio, color="#8e44ad", marker="D", linewidth=2)
    ax.axhline(y=1.0, color="gray", linestyle="--", linewidth=1)
    ax.set_title("Stosunek wysokości BST / wyważone BST", fontsize=12, fontweight="bold")
    ax.set_xlabel("Liczba elementów N")
    ax.set_ylabel("H_BST / H_AVL")
    ax.fill_between(ns, 1.0, ratio, alpha=0.15, color="#8e44ad")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("task2_stosunek_wysokosci.png", dpi=150, bbox_inches="tight")
    print("  Wykres zapisany: task2_stosunek_wysokosci.png")
    plt.show()


def save_csv(results: dict, filename: str = "task2_dane.csv") -> None:
    import csv
    headers = ["N", "BST_wysokosc_sr", "AVL_wysokosc", "log2_N+1"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(headers)
        for i, n in enumerate(results["n"]):
            w.writerow([
                n,
                f"{results['bst_height'][i]:.2f}",
                f"{results['avl_height'][i]:.2f}",
                f"{results['log2_N'][i]:.2f}",
            ])
    print(f"  Dane CSV zapisane: {filename}")



# ──────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  ZADANIE II – Wysokość BST vs Wyważone BST")
    print("=" * 60)

    # Demo na małym przykładzie
    print("\n── Demo dla małego N ──")
    demo_single(n=15)

    # Pomiary
    print(f"\n── Pomiar wysokości (N ∈ {SIZES}) ──")
    results = measure_heights(SIZES, REPEATS)

    # Zapis i wykresy
    print("\nZapis danych...")
    save_csv(results)

    print("\nGenerowanie wykresów...")
    plot_heights(results)
    plot_height_ratio(results)


