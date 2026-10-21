import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = "resultats"
OUT = "graphiques"
os.makedirs(OUT, exist_ok=True)

def lire(nom):
    return pd.read_csv(os.path.join(SRC, nom + ".csv"), encoding="utf-8-sig")

# 1. Sentiments
s = lire("sentiments")
plt.figure(figsize=(5, 5))
plt.pie(s["count"], labels=s["label"], autopct="%1.1f%%", startangle=90,
        colors=["#d9534f", "#5cb85c"])
plt.title("Repartition des sentiments (10 000 tweets)")
plt.savefig(os.path.join(OUT, "1_sentiments.png"), dpi=150, bbox_inches="tight")
plt.close()

# 2. Top hashtags
h = lire("top_hashtags").sort_values("count")
plt.figure(figsize=(7, 5))
plt.barh(h["hashtag"], h["count"], color="#337ab7")
plt.xlabel("Nombre d'occurrences")
plt.title("Top 10 des hashtags")
plt.savefig(os.path.join(OUT, "2_top_hashtags.png"), dpi=150, bbox_inches="tight")
plt.close()

# 3. Top mentions
m = lire("top_mentions").sort_values("count")
plt.figure(figsize=(7, 5))
plt.barh(m["mention"], m["count"], color="#f0ad4e")
plt.xlabel("Nombre d'occurrences")
plt.title("Top 10 des mentions")
plt.savefig(os.path.join(OUT, "3_top_mentions.png"), dpi=150, bbox_inches="tight")
plt.close()

# 4. Repartition par heure
r = lire("repartition_heure")
plt.figure(figsize=(8, 4))
plt.plot(r["heure"], r["count"], marker="o", color="#5bc0de")
plt.xticks(range(0, 24))
plt.xlabel("Heure (heure de la colonne date, fuseau PDT)")
plt.ylabel("Nombre de tweets")
plt.title("Repartition des tweets par heure")
plt.grid(alpha=0.3)
plt.savefig(os.path.join(OUT, "4_repartition_heure.png"), dpi=150, bbox_inches="tight")
plt.close()

# 5. Comparaison negatif / positif
t = lire("stats_par_sentiment").set_index("label")
fig, axes = plt.subplots(1, 2, figsize=(9, 4))
t["mentions_moy"].plot.bar(ax=axes[0], color=["#d9534f", "#5cb85c"], rot=0)
axes[0].set_title("Mentions par tweet")
axes[0].set_xlabel("")
t["part_avec_lien"].plot.bar(ax=axes[1], color=["#d9534f", "#5cb85c"], rot=0)
axes[1].set_title("Part de tweets avec lien")
axes[1].set_xlabel("")
plt.savefig(os.path.join(OUT, "5_comparaison_sentiments.png"), dpi=150, bbox_inches="tight")
plt.close()

print("GRAPHIQUES CREES:", sorted(os.listdir(OUT)))
