import time
import random
import matplotlib.pyplot as plt
import sys

sys.setrecursionlimit(5000)


def generate_euler_hamilton_graph(n, target_density):
    """Generuje spójny graf nieskierowany z zadanym nasyceniem krawędziami."""
    adj = {i: set() for i in range(n)}

    permutation = list(range(n))
    random.shuffle(permutation)
    for i in range(n):
        u = permutation[i]
        v = permutation[(i + 1) % n]
        adj[u].add(v)
        adj[v].add(u)

    max_edges = n * (n - 1) // 2
    target_edges = int(target_density * max_edges)
    current_edges = n

    attempts = 0
    while current_edges < target_edges and attempts < n * n:
        attempts += 1
        u, v = random.randint(0, n - 1), random.randint(0, n - 1)
        if u == v or v in adj[u]:
            continue

        x, y = random.randint(0, n - 1), random.randint(0, n - 1)
        if len({u, v, x, y}) != 4:
            continue

        if (v not in adj[u]) and (x not in adj[v]) and (y not in adj[x]) and (u not in adj[y]):
            adj[u].add(v);
            adj[v].add(u)
            adj[v].add(x);
            adj[x].add(v)
            adj[x].add(y);
            adj[y].add(x)
            adj[y].add(u);
            adj[u].add(y)
            current_edges += 4

    return adj


def find_all_hamilton_cycles_main(adj):
    n = len(adj)
    V = []
    V_set = set()
    source = 0
    cycle_count = 0

    def Hamilton(v):
        nonlocal cycle_count
        # V.Add(v);
        V.append(v)
        V_set.add(v)

        for w in adj[v]:
            if w not in V_set:
                Hamilton(w)

        if len(V) == n and source in adj[v]:
            cycle_count += 1

        V_set.remove(v)
        V.pop()

    Hamilton(source)
    return cycle_count


# --- URUCHOMIENIE EKSPERYMENTU DLA ZADANIA II ---
NUM_TESTS = 10

n_values_II = list(range(8, 18))
times_Zad2 = []

print("Rozpoczynam pomiary dla Zadania II (Wszystkie cykle Hamiltona)...")

for n in n_values_II:
    t_sum = 0
    for _ in range(NUM_TESTS):
        g50 = generate_euler_hamilton_graph(n, 0.50)  # Nasycenie krawędziami 50%

        t0 = time.perf_counter()
        total_cycles = find_all_hamilton_cycles_main(g50)
        t_sum += (time.perf_counter() - t0)

    avg_time_ms = (t_sum / NUM_TESTS) * 1000
    times_Zad2.append(avg_time_ms)
    print(f"Zakończono pomiar dla n = {n} (Średni czas: {avg_time_ms:.3f} ms)")

# Generowanie Wykresu dla Zadania II
plt.figure(figsize=(10, 5))
plt.plot(n_values_II, times_Zad2, label='Wszystkie cykle Hamiltona - 50%', marker='^', color='purple')
plt.title('Zadanie II: Czas znajdowania wszystkich cykli Hamiltona (Nasycenie 50%)')
plt.xlabel('Liczba wierzchołków (n)')
plt.ylabel('Średni czas t [ms]')  # Zmiana jednostki na milisekundy
plt.grid(True, ls="--")
plt.legend()
plt.tight_layout()
plt.savefig('wykres_zad_4_3_wszystkie_cykle.png', dpi=300)
plt.close()
print("\nWykres został pomyślnie zapisany jako 'wykres_zad2_wszystkie_cykle.png'")