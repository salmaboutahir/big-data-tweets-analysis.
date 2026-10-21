import csv
import matplotlib.pyplot as plt


CSV_FILE = "jobs/cpu_results.csv"


# Lire toutes les données
rows = []

with open(CSV_FILE, "r", encoding="utf-8") as f:

    reader = csv.reader(f)

    for row in reader:

        if len(row) >= 6:

            rows.append(row)


# Chercher automatiquement :
# 1. une situation de déséquilibre
# 2. une situation d'équilibre après celle-ci

before = None
after = None

for i, row in enumerate(rows):

    status = row[5]

    # Le premier déséquilibre trouvé
    if status == "DESÉQUILIBRE" and before is None:

        before = row

        # Chercher le premier équilibre après
        for next_row in rows[i + 1:]:

            if next_row[5] == "ÉQUILIBRE":

                after = next_row
                break

        if after is not None:
            break


# Vérification
if before is None or after is None:

    print("Impossible de trouver une situation")
    print("DESÉQUILIBRE suivie d'une situation ÉQUILIBRE.")

    exit()


# Récupérer automatiquement les CPU
workers = [
    "Worker 1",
    "Worker 2",
    "Worker 3"
]

cpu_before = [
    float(before[1]),
    float(before[2]),
    float(before[3])
]

cpu_after = [
    float(after[1]),
    float(after[2]),
    float(after[3])
]


difference_before = float(before[4])
difference_after = float(after[4])


print("======================================")
print("      DONNÉES DU GRAPHIQUE")
print("======================================")

print("Avant SMA :")
print("Worker 1 :", cpu_before[0], "%")
print("Worker 2 :", cpu_before[1], "%")
print("Worker 3 :", cpu_before[2], "%")
print("Différence :", difference_before, "%")

print()

print("Après SMA :")
print("Worker 1 :", cpu_after[0], "%")
print("Worker 2 :", cpu_after[1], "%")
print("Worker 3 :", cpu_after[2], "%")
print("Différence :", difference_after, "%")


# -------------------------------
# Création du graphique
# -------------------------------

x = range(len(workers))
width = 0.35

plt.figure(figsize=(10, 6))

bars_before = plt.bar(
    [i - width / 2 for i in x],
    cpu_before,
    width,
    label="Avant SMA"
)

bars_after = plt.bar(
    [i + width / 2 for i in x],
    cpu_after,
    width,
    label="Après SMA"
)


# Valeurs au-dessus des barres
for bar, value in zip(bars_before, cpu_before):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 2,
        f"{value:.2f}%",
        ha="center"
    )


for bar, value in zip(bars_after, cpu_after):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 2,
        f"{value:.2f}%",
        ha="center"
    )


plt.title(
    "Charge CPU des Workers avant et après le rebalancement"
)

plt.xlabel("Workers")

plt.ylabel("Charge CPU (%)")

plt.xticks(
    list(x),
    workers
)

plt.legend()

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()


# Sauvegarder automatiquement
plt.savefig(
    "graph_charge_cpu.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


print()
print("======================================")
print("Graphique créé avec succès !")
print("Fichier : graph_charge_cpu.png")
print("======================================")