from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("KafkaTest") \
    .getOrCreate()

df = spark.read \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "172.19.0.7:29092") \
    .option("subscribe", "tweets") \
    .option("startingOffsets", "earliest") \
    .option("endingOffsets", "latest") \
    .load()

print("Nombre de messages:", df.count())

df.selectExpr("CAST(value AS STRING) AS message").show(5, truncate=False)

spark.stop()
