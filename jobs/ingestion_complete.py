from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType

OUT = "hdfs://namenode:9000/tweets/full_1600000"

spark = SparkSession.builder.appName("IngestionComplete1600000").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Securite : ne jamais ecraser
path = spark._jvm.org.apache.hadoop.fs.Path(OUT)
fs = path.getFileSystem(spark._jsc.hadoopConfiguration())
if fs.exists(path):
    raise SystemExit("ARRET: " + OUT + " existe deja, rien n'est ecrit")

schema = StructType([StructField(n, StringType()) for n in
    ["sentiment", "tweet_id", "date", "query", "user", "text"]])

raw = spark.read.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "tweets_big") \
    .option("startingOffsets", "earliest") \
    .option("endingOffsets", "latest") \
    .option("minPartitions", 6) \
    .load()

df = raw.selectExpr("CAST(value AS STRING) AS json") \
    .select(from_json(col("json"), schema).alias("t")).select("t.*")

df.write.mode("errorifexists").parquet(OUT)

check = spark.read.parquet(OUT)
print("=== LIGNES ECRITES ===", check.count())
print("=== TWEET_ID DISTINCTS ===", check.select("tweet_id").distinct().count())
check.groupBy("sentiment").count().orderBy("sentiment").show()

spark.stop()
