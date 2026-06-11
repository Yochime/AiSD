import time
import random
import matplotlib.pyplot as plt

# ==============================================================================
# 1. IMPLEMENTACJA ALGORYTMÓW
# ==============================================================================

def knapsack_dynamic(weights, values, capacity):
    """Rozwiązanie dokładne za pomocą programowania dynamicznego (DP)."""
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w = weights[i - 1]
        v = values[i - 1]
        for c in range(capacity + 1):
            if w <= c:
                dp[i][c] = max(dp[i - 1][c], dp[i - 1][c - w] + v)
            else:
                dp[i][c] = dp[i - 1][c]

    return dp[n][capacity]


def knapsack_greedy(weights, values, capacity):
    """
    Rozwiązanie przybliżone za pomocą algorytmu zachłannego.
    POPRAWKA: Algorytm nie przerywa pracy po napotkaniu za ciężkiego kontenera,
    lecz próbuje dopakować kolejne, mniejsze przedmioty.
    """
    n = len(weights)
    items = []
    for i in range(n):
        ratio = values[i] / weights[i]
        items.append((ratio, weights[i], values[i]))

    # Sortowanie malejąco po opłacalności (wartość/waga)
    items.sort(key=lambda x: x[0], reverse=True)

    total_value = 0
    current_weight = 0

    for ratio, w, v in items:
        if current_weight + w <= capacity:
            current_weight += w
            total_value += v
        # Jeśli się nie mieści, pomijamy go i sprawdzamy następne (uzupełnianie luku)

    return total_value


# ==============================================================================
# 2. GENERATOR INSTANCJI TESTOWYCH
# ==============================================================================

def generate_instance(n):
    """Generuje losowe wagi i wartości dla n kontenerów."""
    weights = [random.randint(5, 50) for _ in range(n)]
    values = [random.randint(10, 100) for _ in range(n)]
    return weights, values


# ==============================================================================
# 3. ZWIĘKSZONA PROCEDURA BADAWCZA (Miarodajne zakresy)
# ==============================================================================

NUM_TESTS = 15  # Zwiększona liczba prób dla lepszego uśrednienia

# --- EKSPERYMENT A: Stała ładowność, duża, zmienna liczba kontenerów ---
FIXED_CAPACITY = 2000  # Zwiększono z 500
n_values = [50, 150, 250, 350, 450, 550, 660, 750, 850, 950, 1050, 1150, 1250, 1350, 1500]

times_dyn_A, times_gre_A, errors_A = [], [], []

print("Uruchamianie Eksperymentu A (Stała ładowność B=2000, rosnące N)...")
for n in n_values:
    t_dyn_sum, t_gre_sum, err_sum = 0, 0, 0

    for _ in range(NUM_TESTS):
        w, v = generate_instance(n)

        t0 = time.perf_counter()
        val_dyn = knapsack_dynamic(w, v, FIXED_CAPACITY)
        t_dyn_sum += (time.perf_counter() - t0)

        t0 = time.perf_counter()
        val_gre = knapsack_greedy(w, v, FIXED_CAPACITY)
        t_gre_sum += (time.perf_counter() - t0)

        if val_dyn > 0:
            err_sum += (val_dyn - val_gre) / val_dyn

    times_dyn_A.append((t_dyn_sum / NUM_TESTS) * 1000)  # ms
    times_gre_A.append((t_gre_sum / NUM_TESTS) * 1000)  # ms
    errors_A.append((err_sum / NUM_TESTS) * 100)  # %

# --- EKSPERYMENT B: Duża, zmienna ładowność, stała liczba kontenerów ---
FIXED_N = 300  # Zwiększono z 50
capacity_values = [200, 500, 800, 1100, 1400, 1700, 2000, 2300, 2600, 2900, 3200, 3500, 3800, 4100, 4500]

times_dyn_B, times_gre_B, errors_B = [], [], []

print("Uruchamianie Eksperymentu B (Stała liczba kontenerów N=300, rosnące B)...")
for cap in capacity_values:
    t_dyn_sum, t_gre_sum, err_sum = 0, 0, 0

    for _ in range(NUM_TESTS):
        w, v = generate_instance(FIXED_N)

        t0 = time.perf_counter()
        val_dyn = knapsack_dynamic(w, v, cap)
        t_dyn_sum += (time.perf_counter() - t0)

        t0 = time.perf_counter()
        val_gre = knapsack_greedy(w, v, cap)
        t_gre_sum += (time.perf_counter() - t0)

        if val_dyn > 0:
            err_sum += (val_dyn - val_gre) / val_dyn

    times_dyn_B.append((t_dyn_sum / NUM_TESTS) * 1000)  # ms
    times_gre_B.append((t_gre_sum / NUM_TESTS) * 1000)  # ms
    errors_B.append((err_sum / NUM_TESTS) * 100)  # %


# ==============================================================================
# 4. GENEROWANIE I ZAPIS WYKRESÓW
# ==============================================================================
plt.rcParams.update({'font.size': 10, 'figure.titlesize': 12})

# --- WYKRES 1: EKSPERYMENT A ---
fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(n_values, times_dyn_A, label='Dynamiczny (DP)', marker='o', color='#1f77b4')
ax1.plot(n_values, times_gre_A, label='Zachłanny', marker='s', color='#ff7f0e')
ax1.set_title('Czas działania algorytmów\n(Stała ładowność B = 2000)')
ax1.set_xlabel('Liczba kontenerów (n)')
ax1.set_ylabel('Średni czas t [ms]')
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend()

ax2.plot(n_values, errors_A, marker='^', color='#d62728', linestyle='-.')
ax2.set_title('Średni błąd względny algorytmu zachłannego\n(Stała ładowność B = 2000)')
ax2.set_xlabel('Liczba kontenerów (n)')
ax2.set_ylabel('Błąd względny [%]')
ax2.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('wykres_eksperyment_A.png', dpi=300)
plt.close()

# --- WYKRES 2: EKSPERYMENT B ---
fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(14, 5))

ax3.plot(capacity_values, times_dyn_B, label='Dynamiczny (DP)', marker='o', color='#1f77b4')
ax3.plot(capacity_values, times_gre_B, label='Zachłanny', marker='s', color='#ff7f0e')
ax3.set_title('Czas działania algorytmów\n(Stała liczba kontenerów n = 300)')
ax3.set_xlabel('Ładowność statku (b)')
ax3.set_ylabel('Średni czas t [ms]')
ax3.grid(True, linestyle='--', alpha=0.5)
ax3.legend()

ax4.plot(capacity_values, errors_B, marker='^', color='#d62728', linestyle='-.')
ax4.set_title('Średni błąd względny algorytmu zachłannego\n(Stała liczba kontenerów n = 300)')
ax4.set_xlabel('Ładowność statku (b)')
ax4.set_ylabel('Błąd względny [%]')
ax4.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('wykres_eksperyment_B.png', dpi=300)
plt.close()

print("\n[SUKCES] Wygenerowano miarodajne wykresy.")