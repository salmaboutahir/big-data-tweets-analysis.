from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType

spark = SparkSession.builder.appName("KafkaToHDFSTest").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("sentiment", StringType()),
    StructField("tweet_id", StringType()),
    StructField("date", StringType()),
    StructField("query", StringType()),
    StructField("user", StringType()),
    StructField("text", StringType()),
])

raw = spark.read.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "tweets_full") \
    .option("startingOffsets", "earliest") \
    .option("endingOffsets", "latest") \
    .load()

tweets = raw.selectExpr("CAST(value AS STRING) AS json") \
    .select(from_json(col("json"), schema).alias("t")) \
    .select("t.*") \
    .limit(1000)

print("Nombre de tweets du test:", tweets.count())

output = "hdfs://namenode:9000/tweets/test_kafka_parquet"
tweets.write.mode("errorifexists").parquet(output)

check = spark.read.parquet(output)
print("Nombre de tweets dans HDFS:", check.count())
check.show(5, truncate=60)

spark.stop()
