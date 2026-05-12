import random
import time
import matplotlib.pyplot as plt
import csv
import heapq


def generate_connected_graph(n, density, max_w=1000):
    matrix = [[0] * n for _ in range(n)]
    adj_list = [[] for _ in range(n)]
    edges = set()
    # Budowa szkieletu spójnego
    nodes = [0];
    remaining = list(range(1, n));
    random.shuffle(remaining)
    for v in remaining:
        u = random.choice(nodes);
        w = random.randint(1, max_w)
        edges.add(tuple(sorted((u, v)) + [w]));
        nodes.append(v)
    # Dopełnienie krawędziami
    max_edges = n * (n - 1) // 2
    target = int(max_edges * density)
    while len(edges) < target:
        u, v = random.sample(range(n), 2);
        w = random.randint(1, max_w)
        edges.add(tuple(sorted((u, v)) + [w]))
    for u, v, w in edges:
        matrix[u][v] = matrix[v][u] = w
        adj_list[u].append((v, w));
        adj_list[v].append((u, w))
    return matrix, adj_list


# Ścisły pseudokod Prim (naiwne szukanie min krawędzi)
def prim_matrix_naive(n, matrix):
    TV = {0}
    T = []
    while len(T) < n - 1:
        min_w = float('inf');
        edge = None
        for u in TV:
            for v in range(n):
                if v not in TV and 0 < matrix[u][v] < min_w:
                    min_w = matrix[u][v];
                    edge = (u, v)
        if not edge: break
        TV.add(edge[1]);
        T.append(edge)


# Optymalizacja listowa (Kopiec) dla porównania
def prim_list_optimized(n, adj_list):
    TV = [False] * n;
    TV[0] = True;
    T_count = 0;
    pq = []
    for v, w in adj_list[0]: heapq.heappush(pq, (w, 0, v))
    while pq and T_count < n - 1:
        w, u, v = heapq.heappop(pq)
        if not TV[v]:
            TV[v] = True;
            T_count += 1
            for neighbor, weight in adj_list[v]:
                if not TV[neighbor]: heapq.heappush(pq, (weight, v, neighbor))


def run_experiment():
    # 15 punktów pomiarowych
    n_values = [n for n in range(100, 1600, 100)]

    for density in [0.3, 0.7]:
        results = []
        d_name = int(density * 100)
        print(f"\n--- Zadanie II: Algorytm Prima (Nasycenie {d_name}%) ---")

        for n in n_values:
            m, l = generate_connected_graph(n, density)

            # Macierz
            start = time.perf_counter()
            prim_matrix_naive(n, m)
            t_m = time.perf_counter() - start

            # Lista
            start = time.perf_counter()
            prim_list_optimized(n, l)
            t_l = time.perf_counter() - start

            results.append((n, t_m, t_l))
            print(f"N = {n} | Macierz: {t_m:.4f}s | Lista: {t_l:.4f}s")

        # Zapis CSV
        file_csv = f'wyniki_prim_{d_name}_15p.csv'
        with open(file_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['n', 'macierz', 'lista'])
            writer.writerows(results)

        # Wykres
        plt.figure(figsize=(12, 7))
        ns = [r[0] for r in results]
        plt.plot(ns, [r[1] for r in results], 'r-o', label='Macierz (Naiwny $O(V^3)$)')
        plt.plot(ns, [r[2] for r in results], 'b-s', label='Lista (Kopiec $O(E \log V)$)')
        plt.title(f'Algorytm Prima (Nasycenie {d_name}%)')
        plt.xlabel('Liczba wierzchołków (n)')
        plt.ylabel('Czas [s]')
        plt.legend();
        plt.grid(True, which="both", ls="-", alpha=0.5)
        plt.savefig(f'wykres_prim_{d_name}_15p.png')
        print(f"Zapisano {file_csv} oraz wykres_prim_{d_name}_15p.png")


if __name__ == "__main__":
    run_experiment()