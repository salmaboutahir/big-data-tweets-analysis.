import json
import os
import time
import math

from pyspark.sql import SparkSession


COMMAND_FILE = "/opt/jobs/rebalance_command.json"


spark = SparkSession.builder \
    .appName("SMA_Controlled_Spark") \
    .getOrCreate()

sc = spark.sparkContext

print("======================================")
print("     SMA CONTROLLED SPARK JOB")
print("======================================")

data = sc.parallelize(range(3000000), 3)

print("Partitions initiales :", data.getNumPartitions())


def calcul(x):
    result = 0.0

    for i in range(100):
        result += math.sqrt(x + i + 1)

    return result


# Première exécution
print()
print("🔵 Exécution initiale...")

result1 = data.map(calcul).sum()

print("Résultat initial :", result1)
print("Partitions :", data.getNumPartitions())


# Vérification de la commande du SMA
print()
print("🟡 Vérification de la commande SMA...")


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
        print(
            "Nouvelles partitions :",
            target_partitions
        )

        data = data.repartition(target_partitions)

        print(
            "Partitions après repartition :",
            data.getNumPartitions()
        )

        print()
        print("🔵 Nouvelle exécution après rebalancement...")

        result2 = data.map(calcul).sum()

        print(
            "Résultat après rebalancement :",
            result2
        )

        print(
            "Partitions finales :",
            data.getNumPartitions()
        )

        print()
        print("======================================")
        print("     REBALANCEMENT TERMINÉ ✅")
        print("======================================")


else:

    print("Aucune commande de rebalancement.")


spark.stop()