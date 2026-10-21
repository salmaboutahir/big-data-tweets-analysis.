from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, isnan, length, trim, countDistinct

spark = SparkSession.builder.appName("QualiteSampleRandom").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

df = spark.read.parquet("hdfs://namenode:9000/tweets/sample_random_10000")

print("=== SCHEMA ===")
df.printSchema()

total = df.count()
print("=== TOTAL LIGNES ===", total)

print("=== NULLS PAR COLONNE ===")
df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns]).show(truncate=False)

print("=== CHAINES VIDES PAR COLONNE ===")
df.select([count(when(trim(col(c)) == "", c)).alias(c) for c in df.columns]).show(truncate=False)

print("=== DOUBLONS ===")
print("Lignes completement dupliquees:", total - df.dropDuplicates().count())
print("tweet_id distincts:", df.select(countDistinct("tweet_id")).first()[0])
print("Doublons sur tweet_id:", total - df.dropDuplicates(["tweet_id"]).count())

print("=== VALEURS DE SENTIMENT ===")
df.groupBy("sentiment").count().orderBy("sentiment").show()

print("=== VALEURS DE QUERY ===")
df.groupBy("query").count().orderBy(col("count").desc()).show(5, truncate=False)

print("=== LONGUEUR DU TEXTE ===")
df.select(length("text").alias("len")).describe().show()

spark.stop()
