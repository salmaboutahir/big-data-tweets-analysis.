from pyspark.sql import SparkSession
from pyspark.sql.functions import (col, length, lower, explode, split, regexp_extract_all,
    lit, avg, count, round as rnd, expr, hour, to_timestamp, regexp_replace, size)

spark = SparkSession.builder.appName("AnalyseDescriptive").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

df = spark.read.parquet("hdfs://namenode:9000/tweets/sample_random_10000") \
    .withColumn("label", expr("CASE WHEN sentiment = '0' THEN 'negatif' WHEN sentiment = '4' THEN 'positif' ELSE 'autre' END")) \
    .withColumn("len", length("text")) \
    .withColumn("hashtags", expr("regexp_extract_all(lower(text), '(#\\\\w+)', 1)")) \
    .withColumn("mentions", expr("regexp_extract_all(lower(text), '(@\\\\w+)', 1)")) \
    .withColumn("has_url", col("text").rlike("http[s]?://|www\\.")) \
    .withColumn("ts", to_timestamp(regexp_replace(col("date"), " P[SD]T ", " "), "EEE MMM dd HH:mm:ss yyyy")) \
    .cache()

print("=== 1. SENTIMENTS ===")
df.groupBy("label").count().show()

print("=== 2. LONGUEUR PAR SENTIMENT ===")
df.groupBy("label").agg(rnd(avg("len"), 1).alias("longueur_moy"),
    rnd(avg(size("hashtags")), 3).alias("hashtags_moy"),
    rnd(avg(size("mentions")), 3).alias("mentions_moy"),
    rnd(avg(col("has_url").cast("int")), 3).alias("part_avec_lien")).show()

print("=== 3. TOP 10 UTILISATEURS ===")
df.groupBy("user").count().orderBy(col("count").desc()).show(10, truncate=False)

print("=== 4. TOP 10 HASHTAGS ===")
df.select(explode("hashtags").alias("hashtag")).groupBy("hashtag").count() \
    .orderBy(col("count").desc()).show(10, truncate=False)

print("=== 5. TOP 10 MENTIONS ===")
df.select(explode("mentions").alias("mention")).groupBy("mention").count() \
    .orderBy(col("count").desc()).show(10, truncate=False)

print("=== 6. REPARTITION PAR HEURE ===")
print("Dates non converties:", df.filter(col("ts").isNull()).count())
df.filter(col("ts").isNotNull()).groupBy(hour("ts").alias("heure")).count().orderBy("heure").show(24)

spark.stop()
