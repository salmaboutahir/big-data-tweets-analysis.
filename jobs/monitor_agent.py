import docker
import json
import time
import csv
import os
from datetime import datetime


WORKERS = [
    "spark-worker-1",
    "spark-worker-2",
    "spark-worker-3"
]

client = docker.from_env()

CSV_FILE = "jobs/cpu_results.csv"
THRESHOLD = 5.0


print("======================================")
print("     Spark Monitor Agent")
print("======================================")
print("Monitoring des workers...")
print("Appuyez sur Ctrl+C pour arrêter.\n")


# Créer le fichier CSV s'il n'existe pas
if not os.path.exists(CSV_FILE):

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([
            "timestamp",
            "worker1_cpu",
            "worker2_cpu",
            "worker3_cpu",
            "difference",
            "status"
        ])


while True:

    state = {
        "timestamp": datetime.now().isoformat(),
        "workers": {}
    }

    cpu_values = []

    for worker_name in WORKERS:

        try:

            container = client.containers.get(worker_name)

            stats = container.stats(stream=False)

            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )

            system_delta = (
                stats["cpu_stats"]["system_cpu_usage"]
                - stats["precpu_stats"]["system_cpu_usage"]
            )

            cpu_count = stats["cpu_stats"].get(
                "online_cpus",
                len(
                    stats["cpu_stats"]["cpu_usage"].get(
                        "percpu_usage",
                        []
                    )
                )
            )

            if system_delta > 0 and cpu_delta > 0:

                cpu_percent = (
                    cpu_delta / system_delta
                ) * cpu_count * 100

            else:

                cpu_percent = 0.0


            memory_usage = stats["memory_stats"].get(
                "usage",
                0
            )

            memory_limit = stats["memory_stats"].get(
                "limit",
                0
            )

            memory_percent = (
                memory_usage / memory_limit * 100
                if memory_limit > 0
                else 0
            )


            cpu_percent = round(cpu_percent, 2)

            cpu_values.append(cpu_percent)


            state["workers"][worker_name] = {

                "status": container.status,

                "cpu_percent": cpu_percent,

                "memory_percent": round(
                    memory_percent,
                    2
                )
            }


            print(
                f"{worker_name} | "
                f"CPU: {cpu_percent:.2f}% | "
                f"RAM: {memory_percent:.2f}%"
            )


        except Exception as e:

            print(
                f"{worker_name} | ERROR: {e}"
            )


    # Vérifier que les 3 workers ont été mesurés
    if len(cpu_values) == 3:

        maximum = max(cpu_values)

        minimum = min(cpu_values)

        difference = round(
            maximum - minimum,
            2
        )


        if difference > THRESHOLD:

            status = "DESÉQUILIBRE"

        else:

            status = "ÉQUILIBRE"


        # Enregistrer automatiquement dans CSV
        with open(
            CSV_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                state["timestamp"],
                cpu_values[0],
                cpu_values[1],
                cpu_values[2],
                difference,
                status
            ])


        print(
            f"Différence max-min : "
            f"{difference:.2f}%"
        )

        print(
            f"État du cluster : {status}"
        )


    # Sauvegarder state.json
    with open(
        "jobs/state.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            state,
            f,
            indent=4
        )


    print("--------------------------------------")

    time.sleep(3)