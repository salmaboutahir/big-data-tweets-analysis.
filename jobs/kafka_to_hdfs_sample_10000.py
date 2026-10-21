from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType

spark = (
    SparkSession.builder
    .appName("KafkaToHDFSSample10000")
    .getOrCreate()
)
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
    .option("kafka.bootstrap.servers", "kafka:29092")
    .option("subscribe", "tweets_full")
    .option("startingOffsets", '{"tweets_full":{"0":0}}')
    .option("endingOffsets", '{"tweets_full":{"0":10000}}')
    .load()
)

tweets = (
    raw.selectExpr("CAST(value AS STRING) AS json")
    .select(from_json(col("json"), schema).alias("t"))
    .select("t.*")
)

message_count = raw.count()
print(f"Nombre de messages Kafka lus : {message_count}")

if message_count != 10000:
    raise RuntimeError(
        f"Attendu 10000 messages, reçu {message_count}. "
        "Arrêt avant écriture dans HDFS."
    )

output = "hdfs://namenode:9000/tweets/sample_10000"

tweets.write.mode("errorifexists").parquet(output)

check = spark.read.parquet(output)
saved_count = check.count()
print(f"Nombre de tweets vérifiés dans HDFS : {saved_count}")

if saved_count != 10000:
    raise RuntimeError(
        f"Vérification HDFS échouée : {saved_count} lignes."
    )

check.show(5, truncate=60)
spark.stop()
