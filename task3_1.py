import random
import time
import matplotlib.pyplot as plt
import csv
import sys

# Zwiększenie limitu rekurencji dla głębokiego DFS na M4 Pro
sys.setrecursionlimit(10000)


class TopoSortTask:
    def __init__(self, n):
        self.krok = 1
        self.visited = [False] * n
        self.IN = [0] * n
        self.OUT = [0] * n

    # Pseudokod TS(v)
    def TS_matrix(self, v, n, matrix):
        self.visited[v] = True
        self.IN[v] = self.krok
        self.krok += 1
        for w in range(n):
            if matrix[v][w] == 1 and not self.visited[w]:
                self.TS_matrix(w, n, matrix)
        self.OUT[v] = self.krok
        self.krok += 1

    def TS_list(self, v, adj_list):
        self.visited[v] = True
        self.IN[v] = self.krok
        self.krok += 1
        for w in adj_list[v]:
            if not self.visited[w]:
                self.TS_list(w, adj_list)
        self.OUT[v] = self.krok
        self.krok += 1


def generate_dag(n, density=0.6):
    max_edges = n * (n - 1) // 2
    target_edges = int(max_edges * density)
    matrix = [[0] * n for _ in range(n)]
    adj_list = [[] for _ in range(n)]
    # Zapewnienie acykliczności (i < j)
    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    selected_edges = random.sample(possible_edges, target_edges)
    for u, v in selected_edges:
        matrix[u][v] = 1
        adj_list[u].append(v)
    return matrix, adj_list


def run_experiment():
    # 15 punktów pomiarowych
    n_values = [n for n in range(200, 3200, 200)]
    results = []

    print("--- Zadanie I: Sortowanie Topologiczne (Pomiary: 15 punktów) ---")
    for n in n_values:
        m, l = generate_dag(n, 0.6)

        # Pomiar Macierz
        ts_m = TopoSortTask(n)
        start = time.perf_counter()
        for i in range(n):
            if not ts_m.visited[i]: ts_m.TS_matrix(i, n, m)
        t_matrix = time.perf_counter() - start

        # Pomiar Lista
        ts_l = TopoSortTask(n)
        start = time.perf_counter()
        for i in range(n):
            if not ts_l.visited[i]: ts_l.TS_list(i, l)
        t_list = time.perf_counter() - start

        results.append((n, t_matrix, t_list))
        print(f"N = {n} | Macierz: {t_matrix:.4f}s | Lista: {t_list:.4f}s")

    # Zapis do CSV
    with open('wyniki_toposort_15p.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['n', 'czas_macierz', 'czas_lista'])
        writer.writerows(results)

    # Wykres
    plt.figure(figsize=(12, 7))
    ns = [r[0] for r in results]
    plt.plot(ns, [r[1] for r in results], 'r-o', label='Macierz sąsiedztwa $O(V^2)$')
    plt.plot(ns, [r[2] for r in results], 'b-s', label='Lista incydencji $O(V+E)$')
    plt.title('Sortowanie Topologiczne (Nasycenie 60%)')
    plt.xlabel('Liczba wierzchołków (n)')
    plt.ylabel('Czas [s]')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.savefig('wykres_toposort_15p.png')
    print("\nGotowe! Wygenerowano wyniki_toposort_15p.csv i wykres_toposort_15p.png")


if __name__ == "__main__":
    run_experiment()