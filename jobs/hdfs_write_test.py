from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("HDFSWritingTest").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

df = spark.createDataFrame(
    [("test1", "bonjour"), ("test2", "hdfs fonctionne")],
    ["id", "message"]
)

df.write.mode("overwrite").parquet("hdfs://namenode:9000/tweets/connectivity_test")

result = spark.read.parquet("hdfs://namenode:9000/tweets/connectivity_test")
print("TEST HDFS - nombre de lignes :", result.count())
result.show(truncate=False)

spark.stop()
