from pyspark.sql import SparkSession
from pyspark.sql.functions import (col, length, trim, count, when, avg,
    to_timestamp, regexp_replace)

BASE = "hdfs://namenode:9000/tweets/results/dashboard_kpis_v1"
spark = SparkSession.builder.appName("KpisDashboard").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

path = spark._jvm.org.apache.hadoop.fs.Path(BASE)
fs = path.getFileSystem(spark._jsc.hadoopConfiguration())
if fs.exists(path):
    raise SystemExit("ARRET: " + BASE + " existe deja, rien n'est ecrit")

df = spark.read.parquet("hdfs://namenode:9000/tweets/sample_random_10000").cache()
total = df.count()
nulls = df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns]).first()
vides = df.select([count(when(trim(col(c)) == "", c)).alias(c) for c in df.columns]).first()
ts = to_timestamp(regexp_replace(col("date"), " P[SD]T ", " "), "EEE MMM dd HH:mm:ss yyyy")

kpis = [
 ("lignes", total),
 ("utilisateurs_distincts", df.select("user").distinct().count()),
 ("tweet_id_distincts", df.select("tweet_id").distinct().count()),
 ("doublons_complets", total - df.dropDuplicates().count()),
 ("doublons_tweet_id", total - df.dropDuplicates(["tweet_id"]).count()),
 ("longueur_moyenne", round(df.select(avg(length("text"))).first()[0], 2)),
 ("dates_non_converties", df.filter(ts.isNull()).count()),
]
cols = [(c, nulls[c], vides[c]) for c in df.columns]

def save(rows, schema, name):
    spark.createDataFrame(rows, schema).coalesce(1).write.mode("errorifexists") \
        .option("header", True).csv(BASE + "/" + name)
    print("=== ECRIT ===", name)

save([(k, str(v)) for k, v in kpis], ["metrique", "valeur"], "kpis")
save(cols, ["colonne", "nulls", "vides"], "qualite_colonnes")
spark.stop()
