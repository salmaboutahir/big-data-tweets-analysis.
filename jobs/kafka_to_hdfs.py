
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType

spark = SparkSession.builder.appName("KafkaToHDFS").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("sentiment", StringType()),
    StructField("tweet_id", StringType()),
    StructField("date", StringType()),
    StructField("query", StringType()),
    StructField("user", StringType()),
    StructField("text", StringType()),
])

raw = spark.read \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "tweets_full") \
    .option("startingOffsets", "earliest") \
    .option("endingOffsets", "latest") \
    .load()

tweets = raw.selectExpr("CAST(value AS STRING) AS json") \
    .select(from_json(col("json"), schema).alias("t")) \
    .select("t.*")

print("Nombre de tweets lus:", tweets.count())

tweets.write.mode("overwrite").parquet("hdfs://namenode:9000/tweets/raw")

check = spark.read.parquet("hdfs://namenode:9000/tweets/raw")
print("Nombre de tweets dans HDFS:", check.count())
check.show(5, truncate=60)

spark.stop()
