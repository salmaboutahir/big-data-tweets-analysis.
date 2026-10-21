from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType

spark = SparkSession.builder.appName("KafkaToHDFSFull").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("sentiment", StringType(), True),
    StructField("tweet_id", StringType(), True),
    StructField("date", StringType(), True),
    StructField("query", StringType(), True),
    StructField("user", StringType(), True),
    StructField("text", StringType(), True),
])

raw = (
    spark.read.format("kafka")
    .option("kafka.bootstrap.servers", "172.19.0.7:29092")
    .option("subscribe", "tweets_full")
    .option("startingOffsets", "earliest")
    .option("endingOffsets", "latest")
    .load()
)

tweets = (
    raw.selectExpr("CAST(value AS STRING) AS json")
    .select(from_json(col("json"), schema).alias("t"))
    .select("t.*")
)

print("Nombre de messages lus par Spark:", raw.count())
print("Nombre de tweets après parsing:", tweets.count())

output = "hdfs://172.20.0.2:9000/tweets/full_parquet"

tweets.write.mode("errorifexists").parquet(output)

check = spark.read.parquet(output)
print("Nombre de tweets vérifiés dans HDFS:", check.count())
check.show(5, truncate=60)

spark.stop()

