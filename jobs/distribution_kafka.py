from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType

spark = SparkSession.builder.appName("DistributionKafka").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

schema = StructType([StructField(n, StringType()) for n in
    ["sentiment", "tweet_id", "date", "query", "user", "text"]])

raw = spark.read.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "tweets_big") \
    .option("startingOffsets", "earliest") \
    .option("endingOffsets", "latest") \
    .load()

df = raw.selectExpr("CAST(value AS STRING) AS json") \
    .select(from_json(col("json"), schema).alias("t")).select("t.*")

print("=== TOTAL KAFKA ===", df.count())
print("=== SENTIMENTS DANS KAFKA ===")
df.groupBy("sentiment").count().orderBy("sentiment").show()

spark.stop()
