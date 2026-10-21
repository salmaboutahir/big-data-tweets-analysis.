from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("TestCluster").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

df = spark.read.parquet("hdfs://namenode:9000/tweets/sample_random_10000")
print("=== LIGNES ===", df.count())
df.groupBy("sentiment").count().orderBy("sentiment").show()
print("=== EXECUTEURS ===", spark.sparkContext.master)

spark.stop()
