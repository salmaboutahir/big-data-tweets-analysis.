import random
import csv

# 70% des lignes auront la clé "hot_key" -> skew volontaire
rows = []
for i in range(500000):
    if random.random() < 0.7:
        key = "hot_key"
    else:
        key = f"key_{random.randint(1, 50)}"
    rows.append((key, random.randint(1, 1000)))

with open("/opt/jobs/data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["key", "value"])
    writer.writerows(rows)

print("Dataset généré :", len(rows), "lignes")
