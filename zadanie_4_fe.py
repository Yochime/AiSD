import time
import random
import matplotlib.pyplot as plt
import sys

# Zwiększenie limitu rekurencji dla głębokiego backtrackingu
sys.setrecursionlimit(5000)


# ==============================================================================
# GENERATOR GRAFÓW (Euler + Hamilton + Spójność, Indeksowanie od 1)
# ==============================================================================
def generate_euler_hamilton_graph(n, target_density):
    """
    Generuje spójny graf nieskierowany będący jednocześnie Eulerowskim i Hamiltonowskim.
    Wierzchołki są indeksowane od 1 do n, a listy sąsiadów są posortowane.
    """
    adj = {i: set() for i in range(1, n + 1)}

    # 1. Bazowy cykl Hamiltona (gwarantuje spójność i parzystość stopni na start)
    permutation = list(range(1, n + 1))
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
        u, v = random.randint(1, n), random.randint(1, n)
        if u == v or v in adj[u]:
            continue

        x, y = random.randint(1, n), random.randint(1, n)
        if len({u, v, x, y}) != 4:
            continue

        # Dodajemy krawędzie czwórkami, zachowując parzystość stopni wierzchołków
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

    # Konwersja na listy posortowane (zgodnie z logiką sprawdzania od najmniejszego sąsiada)
    return {i: sorted(list(adj[i])) for i in range(1, n + 1)}


# ==============================================================================
# IMPLEMENTACJA (CYKL EULERA) - ZGODNA Z PSEUDOKODEM (START OD 1, BEZ ODWRACANIA)
# ==============================================================================
def find_euler_cycle_main(graph_dict):
    unvisited_edges = set()
    for u, neighbors in graph_dict.items():
        for w in neighbors:
            if (w, u) not in unvisited_edges:
                unvisited_edges.add((u, w))

    C = []  # stwórz listę C;

    def Euler(v):
        # dla każdego wierzchołka w takiego, że istnieje nieodwiedzona krawędź z v do w
        for w in graph_dict[v]:
            edge = (v, w) if (v, w) in unvisited_edges else (w, v)
            if edge in unvisited_edges:
                # odwiedź krawędź {v, w}
                unvisited_edges.remove(edge)
                # Euler(w);
                Euler(w)
        # C.Add(v);
        C.append(v)

    Euler(1)
    return C


# ==============================================================================
# IMPLEMENTACJA (HAMILTON - PIERWSZY CYKL) - ZGODNA Z PSEUDOKODEM (START OD 1)
# ==============================================================================
def find_first_hamilton_cycle_main(adj):
    n = len(adj)
    V = []  # stwórz listę V;
    V_set = set()
    source = 1
    found_cycle = [None]

    def Hamilton(v):
        V.append(v)
        V_set.add(v)

        # dla każdego nieodwiedzonego sąsiada w wierzchołka v
        for w in adj[v]:
            if w not in V_set:
                Hamilton(w)
                if found_cycle[0] is not None:
                    return

        # if V zawiera wszystkie wierzchołki grafu i istnieje krawędź z v do źródła
        if len(V) == n and source in adj[v]:
            found_cycle[0] = list(V) + [source]
            return
        else:
            V_set.remove(v)
            V.pop()

    Hamilton(source)
    return found_cycle[0]


# ==============================================================================
# --- URUCHOMIENIE EKSPERYMENTU DLA 15 PUNKTÓW POMIAROWYCH ---
# ==============================================================================
NUM_TESTS = 10
n_values = list(range(10, 25))  # 15 punktów pomiarowych (od 10 do 24 wierzchołków)

times_A_30, times_B_30 = [], []
times_A_70, times_B_70 = [], []

print("Rozpoczynam pomiary czasowe (10 testów na każdy punkt pomiarowy)...")

for n in n_values:
    t_A_30_sum, t_B_30_sum = 0, 0
    t_A_70_sum, t_B_70_sum = 0, 0

    for _ in range(NUM_TESTS):
        # --- POMIAR DLA NASYCENIA 30% ---
        g30 = generate_euler_hamilton_graph(n, 0.30)

        t0 = time.perf_counter()
        find_euler_cycle_main(g30)
        t_A_30_sum += (time.perf_counter() - t0)

        t0 = time.perf_counter()
        find_first_hamilton_cycle_main(g30)
        t_B_30_sum += (time.perf_counter() - t0)

        # --- POMIAR DLA NASYCENIA 70% ---
        g70 = generate_euler_hamilton_graph(n, 0.70)

        t0 = time.perf_counter()
        find_euler_cycle_main(g70)
        t_A_70_sum += (time.perf_counter() - t0)

        t0 = time.perf_counter()
        find_first_hamilton_cycle_main(g70)
        t_B_70_sum += (time.perf_counter() - t0)

    # Obliczamy średnie i zamieniamy na milisekundach [ms] dla lepszej skali
    times_A_30.append((t_A_30_sum / NUM_TESTS) * 1000)
    times_B_30.append((t_B_30_sum / NUM_TESTS) * 1000)
    times_A_70.append((t_A_70_sum / NUM_TESTS) * 1000)
    times_B_70.append((t_B_70_sum / NUM_TESTS) * 1000)
    print(f"Zakończono pomiary dla n = {n}")

# ==============================================================================
# --- GENEROWANIE I AUTOMATYCZNY ZAPIS WYKRESÓW ---
# ==============================================================================

# Wykres 1 - Nasycenie 30% (Grafy rzadkie)
plt.figure(figsize=(10, 6))
plt.plot(n_values, times_A_30, label='Algorytm A (Euler) - 30%', marker='o', color='blue', linewidth=2)
plt.plot(n_values, times_B_30, label='Algorytm B (Hamilton) - 30%', marker='s', color='orange', linewidth=2)
plt.title('Wykres 1: Czas działania algorytmów dla nasycenia krawędziami 30%')
plt.xlabel('Liczba wierzchołków (n)')
plt.ylabel('Średni czas t [ms]')
plt.yscale('log')  # Skala logarytmiczna z uwagi na drastyczne różnice złożoności
plt.grid(True, which="both", ls="--")
plt.legend()
plt.tight_layout()
plt.savefig('wykres_zad_I_30.png', dpi=300)
plt.close()

# Wykres 2 - Nasycenie 70% (Grafy gęste)
plt.figure(figsize=(10, 6))
plt.plot(n_values, times_A_70, label='Algorytm A (Euler) - 70%', marker='o', color='green', linewidth=2)
plt.plot(n_values, times_B_70, label='Algorytm B (Hamilton) - 70%', marker='s', color='red', linewidth=2)
plt.title('Wykres 2: Czas działania algorytmów dla nasycenia krawędziami 70%')
plt.xlabel('Liczba wierzchołków (n)')
plt.ylabel('Średni czas t [ms]')
plt.yscale('log')
plt.grid(True, which="both", ls="--")
plt.legend()
plt.tight_layout()
plt.savefig('wykres_zad_I_70.png', dpi=300)
plt.close()

print("\n[SUKCES] Wykresy zostały automatycznie zapisane w folderze jako:")
print("1. 'wykres_zad_I_30.png'")
print("2. 'wykres_zad_I_70.png'")