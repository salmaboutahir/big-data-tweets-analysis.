import json
import os
import time
import math
import csv

from pyspark.sql import SparkSession


COMMAND_FILE = "/opt/jobs/rebalance_command.json"
RESULTS_FILE = "/opt/jobs/results.csv"


spark = SparkSession.builder \
    .appName("SMA_Spark_Experiment") \
    .getOrCreate()

sc = spark.sparkContext

print("======================================")
print("       SMA SPARK EXPERIMENT")
print("======================================")

data = sc.parallelize(range(3000000), 3)

initial_partitions = data.getNumPartitions()

print("Partitions initiales :", initial_partitions)


def calcul(x):
    result = 0.0

    for i in range(100):
        result += math.sqrt(x + i + 1)

    return result


# ======================================
# 1. EXECUTION INITIALE
# ======================================

print()
print("🔵 EXÉCUTION INITIALE")

start_time = time.perf_counter()

result1 = data.map(calcul).sum()

end_time = time.perf_counter()

initial_time = end_time - start_time

print("Résultat initial :", result1)
print("Partitions :", initial_partitions)
print("Temps initial :", round(initial_time, 3), "secondes")


# ======================================
# 2. LECTURE DE LA COMMANDE SMA
# ======================================

print()
print("🟡 VÉRIFICATION DE LA COMMANDE SMA")


if os.path.exists(COMMAND_FILE):

    with open(COMMAND_FILE, "r") as f:
        command = json.load(f)

    print("Commande reçue :", command)

    if command.get("action") == "REPARTITION":

        target_partitions = command.get(
            "target_partitions",
            12
        )

        print()
        print("🔄 REBALANCEMENT DEMANDÉ")
        print("Partitions cibles :", target_partitions)


        # ======================================
        # 3. REPARTITIONNEMENT
        # ======================================

        data = data.repartition(target_partitions)

        print(
            "Partitions après repartition :",
            data.getNumPartitions()
        )


        # ======================================
        # 4. EXECUTION APRÈS REBALANCEMENT
        # ======================================

        print()
        print("🔵 EXÉCUTION APRÈS REBALANCEMENT")

        start_time = time.perf_counter()

        result2 = data.map(calcul).sum()

        end_time = time.perf_counter()

        rebalanced_time = end_time - start_time

        final_partitions = data.getNumPartitions()

        print(
            "Résultat après rebalancement :",
            result2
        )

        print(
            "Partitions finales :",
            final_partitions
        )

        print(
            "Temps après rebalancement :",
            round(rebalanced_time, 3),
            "secondes"
        )


        # ======================================
        # 5. CALCUL DES PERFORMANCES
        # ======================================

        difference = initial_time - rebalanced_time

        if initial_time > 0:
            improvement = (
                difference / initial_time
            ) * 100
        else:
            improvement = 0


        print()
        print("======================================")
        print("          COMPARAISON")
        print("======================================")

        print(
            "Temps initial        :",
            round(initial_time, 3),
            "s"
        )

        print(
            "Temps après SMA      :",
            round(rebalanced_time, 3),
            "s"
        )

        print(
            "Différence           :",
            round(difference, 3),
            "s"
        )

        print(
            "Variation             :",
            round(improvement, 2),
            "%"
        )

        print(
            "Partitions :",
            initial_partitions,
            "→",
            final_partitions
        )


        # ======================================
        # 6. SAUVEGARDE AUTOMATIQUE
        # ======================================

        with open(
            RESULTS_FILE,
            "w",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "temps_avant",
                "temps_apres",
                "difference",
                "amelioration",
                "partitions_avant",
                "partitions_apres"
            ])

            writer.writerow([
                round(initial_time, 3),
                round(rebalanced_time, 3),
                round(difference, 3),
                round(improvement, 2),
                initial_partitions,
                final_partitions
            ])


        print()
        print("📊 Résultats sauvegardés automatiquement.")
        print("Fichier :", RESULTS_FILE)

        print()
        print("======================================")
        print("      EXPÉRIENCE TERMINÉE ✅")
        print("======================================")


    else:

        print("Aucune action de rebalancement.")


else:

    print("Aucune commande SMA trouvée.")


spark.stop()