import csv
import matplotlib.pyplot as plt


# Fichier contenant les résultats de Spark
RESULTS_FILE = r"jobs/results.csv"


# Lire automatiquement les résultats
with open(RESULTS_FILE, "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    row = next(reader)


# Récupérer les valeurs automatiquement
temps_avant = float(row["temps_avant"])
temps_apres = float(row["temps_apres"])


# Données du graphique
labels = ["Avant SMA", "Après SMA"]
values = [temps_avant, temps_apres]


# Créer le graphique
plt.figure(figsize=(8, 5))

bars = plt.bar(labels, values)


# Afficher les valeurs au-dessus des barres
for bar, value in zip(bars, values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 0.5,
        f"{value:.3f} s",
        ha="center"
    )


plt.title(
    "Comparaison du temps d'exécution avant et après le rebalancement"
)

plt.ylabel("Temps d'exécution (secondes)")

plt.grid(axis="y", alpha=0.3)

plt.tight_layout()


# Sauvegarder automatiquement le graphique
plt.savefig(
    "resultat_temps_execution.png",
    dpi=300,
    bbox_inches="tight"
)


# Afficher le graphique
plt.show()