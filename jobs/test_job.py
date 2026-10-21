from pyspark.sql import SparkSession
import time

spark = SparkSession.builder \
    .appName("TestClusterSkew") \
    .master("spark://spark-master-spark:7077") \
    .config("spark.executor.memory", "512m") \
    .config("spark.executor.memoryOverhead", "384m") \
    .config("spark.sql.shuffle.partitions", "12") \
    .getOrCreate()

df = spark.read.csv(
    "/opt/jobs/data.csv",
    header=True,
    inferSchema=True
)

start = time.time()

result = df.groupBy("key").sum("value")

result.collect()

end = time.time()

print(f"Temps d'exécution : {end - start:.2f} secondes")
print("Nombre de partitions shuffle :", result.rdd.getNumPartitions())

time.sleep(120)

spark.stop()