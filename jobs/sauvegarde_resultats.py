from pyspark.sql import SparkSession
from pyspark.sql.functions import (col, length, explode, avg, round as rnd, expr, hour,
    to_timestamp, regexp_replace, size)

BASE = "hdfs://namenode:9000/tweets/results/analyse_descriptive_v1"

spark = SparkSession.builder.appName("SauvegardeResultats").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Securite : ne jamais ecraser
path = spark._jvm.org.apache.hadoop.fs.Path(BASE)
fs = path.getFileSystem(spark._jsc.hadoopConfiguration())
if fs.exists(path):
    raise SystemExit("ARRET: " + BASE + " existe deja, rien n'est ecrit")

df = spark.read.parquet("hdfs://namenode:9000/tweets/sample_random_10000") \
    .withColumn("label", expr("CASE WHEN sentiment = '0' THEN 'negatif' WHEN sentiment = '4' THEN 'positif' ELSE 'autre' END")) \
    .withColumn("len", length("text")) \
    .withColumn("hashtags", expr("regexp_extract_all(lower(text), '(#\\\\w+)', 1)")) \
    .withColumn("mentions", expr("regexp_extract_all(lower(text), '(@\\\\w+)', 1)")) \
    .withColumn("has_url", col("text").rlike("http[s]?://|www\\.")) \
    .withColumn("ts", to_timestamp(regexp_replace(col("date"), " P[SD]T ", " "), "EEE MMM dd HH:mm:ss yyyy")) \
    .cache()

def save(frame, name):
    frame.coalesce(1).write.mode("errorifexists").option("header", True).csv(BASE + "/" + name)
    print("=== ECRIT ===", name)

save(df.groupBy("label").count(), "sentiments")
save(df.groupBy("label").agg(rnd(avg("len"), 1).alias("longueur_moy"),
    rnd(avg(size("hashtags")), 3).alias("hashtags_moy"),
    rnd(avg(size("mentions")), 3).alias("mentions_moy"),
    rnd(avg(col("has_url").cast("int")), 3).alias("part_avec_lien")), "stats_par_sentiment")
save(df.groupBy("user").count().orderBy(col("count").desc()).limit(10), "top_utilisateurs")
save(df.select(explode("hashtags").alias("hashtag")).groupBy("hashtag").count()
    .orderBy(col("count").desc()).limit(10), "top_hashtags")
save(df.select(explode("mentions").alias("mention")).groupBy("mention").count()
    .orderBy(col("count").desc()).limit(10), "top_mentions")
save(df.filter(col("ts").isNotNull()).groupBy(hour("ts").alias("heure")).count().orderBy("heure"), "repartition_heure")

spark.stop()
