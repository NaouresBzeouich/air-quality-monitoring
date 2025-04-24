# air-quality-monitoring
An open-source distributed real-time air quality monitoring system using Kafka, Spark, and Hadoop — built to collect, process, and analyze environmental data with efficient data distribution, storage, and analytics.

---

## 📌 Architecture Overview

- **OpenAQ API**: Source of real-time air quality data (PM2.5, CO₂, NO₂, etc.).
- **Kafka**: Message broker to collect and distribute data in real-time.
- **Spark**: Real-time processing of data from Kafka to detect trends and pollution hotspots.
- **HDFS (Hadoop)**: Stores raw data; daily MapReduce jobs compute daily stats.
- **HBase**: Stores processed data for fast access.
- **Django REST API**: Serves processed and historical data to the frontend.
- **Angular Dashboard**: Displays air quality data in a modern, interactive UI.

---

## ⚙️ Technologies Used

| Layer         | Technology                      |
|--------------|----------------------------------|
| Data Source   | OpenAQ API                      |
| Messaging     | Apache Kafka                    |
| Processing    | Apache Spark                    |
| Storage       | HDFS, HBase                     |
| Backend       | Python, Django REST Framework   |
| Frontend      | Angular                         |

---

## 🎯 Features

- Real-time air quality tracking.
- Detection of the most polluted locations by gas type.
- Analysis of pollution trends (increase/decrease).
- Daily aggregated reports using MapReduce.
- Historical gas data for each location (retrieved from HDFS).
- Prediction of gas levels for the next day by location.
- Interactive dashboard with charts, maps, and filters.

---

## 🏁 Getting Started


## 🗂 Project Structure

air-quality-distributed-system/
├── backend/              # Django REST API
├── frontend/             # Angular Dashboard
├── kafka_producer/       # Python script to send data from OpenAQ
├── spark_streaming/      # Spark job to process streaming data
├── hadoop_mapreduce/     # MapReduce job for daily aggregation
├── hbase_integration/    # Data writing/reading from HBase
├── README.md
├── docker-compose.yml   
└── requirements.txt
