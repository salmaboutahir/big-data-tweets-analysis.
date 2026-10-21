# Big Data Tweets Analysis

## Project Overview

This academic project implements a Big Data pipeline for collecting, processing, analyzing, and storing tweet data using distributed technologies.

## Architecture

Dataset → Apache Kafka → Apache Spark → Hadoop HDFS → Dashboard

## Technologies Used

- **Python** — Data processing and analysis
- **Apache Kafka** — Data ingestion and streaming
- **Apache Spark 3.5.1** — Distributed processing
- **Hadoop HDFS** — Distributed storage
- **Docker** — Containerized environment
- **Streamlit and Plotly** — Interactive data visualization

## Main Components

- jobs/ — Data processing and Spark jobs
- dashboard/ — Interactive dashboard and visualizations
- conf/ — Spark configuration
- hadoop-conf/ — Hadoop configuration
- jars/ — Kafka connector dependencies
- docker-compose.yml — Spark cluster configuration
- graphiques/ and graphiques_v2/ — Generated visualizations
- esultats/ and esultats_v2/ — Analysis results

## Spark Cluster

The Docker Compose configuration defines:

- One Spark Master
- Three Spark Workers
- One Spark Client

The project connects to an external Docker network used by the HDFS environment.

## Prerequisites

- Docker Desktop
- Git
- A compatible Hadoop HDFS environment
- The required Kafka service and topic

## Setup

1. Clone this repository.
2. Start and verify the required HDFS environment and Docker network.
3. Review the Docker Compose configuration.
4. Start the Spark services.
5. Execute the appropriate processing jobs.
6. Launch the dashboard using its documented configuration.

## Notes

The original dataset is not included in this repository. Configure the required input data and external services before running the pipeline.

## Academic Project

Big Data and Artificial Intelligence
