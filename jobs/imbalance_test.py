import math
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("SMA_Imbalance_Test") \
    .getOrCreate()

sc = spark.sparkContext


def imbalanced_computation(x):
    result = 0.0

    if x < 1000000:
        iterations = 200
    else:
        iterations = 3000

    for i in range(iterations):
        result += math.sqrt(x + i + 1) * math.sin(x + i + 1)

    return result


data = sc.parallelize(range(3000000), 30)

result = data.map(imbalanced_computation).sum()

print("===================================")
print("RESULT =", result)
print("PARTITIONS =", data.getNumPartitions())
print("===================================")