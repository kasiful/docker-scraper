#!/bin/bash
cd $AIRFLOW_HOME
rm airflow-webserver*.pid
airflow webserver --port 8080 -D
airflow scheduler -D
