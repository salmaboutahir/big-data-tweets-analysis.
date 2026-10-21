from pyspark.sql import SparkSession

print("======================================")
print("      SPARK REBALANCING ACTION")
print("======================================")

spark = SparkSession.builder \
    .appName("SMA_Rebalancing_Action") \
    .getOrCreate()

sc = spark.sparkContext

print("Spark connecté au cluster.")

initial_partitions = 3
target_partitions = 12

print("--------------------------------------")
print("Partitions initiales :", initial_partitions)
print("Partitions cibles    :", target_partitions)
print("--------------------------------------")

data = sc.parallelize(range(3000000), initial_partitions)

print("Nombre initial de partitions :",
      data.getNumPartitions())

print()
print("🔄 Repartitionnement en cours...")

rebalanced_data = data.repartition(target_partitions)

print(
    "Nouveau nombre de partitions :",
    rebalanced_data.getNumPartitions()
)

result = rebalanced_data.map(
    lambda x: x * 2
).sum()

print()
print("======================================")
print("REBALANCING TERMINÉ")
print("======================================")
print("Résultat :", result)
print(
    "Partitions finales :",
    rebalanced_data.getNumPartitions()
)
print("======================================")

spark.stop()