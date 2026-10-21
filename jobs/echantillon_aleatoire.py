from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, rand
from pyspark.sql.types import StructType, StructField, StringType

OUT = "hdfs://namenode:9000/tweets/sample_random_10000"

spark = SparkSession.builder.appName("EchantillonAleatoire").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Securite : ne jamais ecraser un dossier existant
jvm = spark._jvm
conf = spark._jsc.hadoopConfiguration()
path = jvm.org.apache.hadoop.fs.Path(OUT)
fs = path.getFileSystem(conf)
if fs.exists(path):
    raise SystemExit("ARRET: " + OUT + " existe deja, rien n'est ecrit")

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

sample = df.orderBy(rand(42)).limit(10000)
sample.write.mode("errorifexists").parquet(OUT)

check = spark.read.parquet(OUT)
print("=== LIGNES ECRITES ===", check.count())
check.groupBy("sentiment").count().orderBy("sentiment").show()

spark.stop()
