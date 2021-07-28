FROM ubuntu

WORKDIR /home

RUN apt-get update

# pasang sertifikat bps agar bisa internetan
# kalau copy satu file pakai COPY, kalau folder dan isinya pakai ADD
ADD cert /usr/local/share/ca-certificates/cert
RUN apt-get install -y ca-certificates
RUN update-ca-certificates

# install python 3 dan pip ny
RUN apt-get -y install python && apt-get -y install python3-pip

# buat folder untuk persiapan
RUN mkdir airflow
RUN mkdir airflow/dags
RUN mkdir airflow/logs
RUN mkdir airflow/plugins

RUN mkdir scraper
RUN mkdir web
RUN mkdir databases

# Install Airflow
# RUN export AIRFLOW_HOME=/home/airflow
# JANGAN PAKAI RUN EXPORT karena hanya di eksekusi saat proses tapi nggak disimpan di images, pakai ENV
ENV AIRFLOW_HOME /home/airflow

# ENV AIRFLOW_VERSION=2.1.0
# RUN pip3 --trusted-host pypi.python.org install "apache-airflow==${AIRFLOW_VERSION}"
RUN pip3 --trusted-host pypi.org --trusted-host files.pythonhosted.org install "apache-airflow"

# Kita ubah dulu WORKDIR ny karena kalau pakai cd cuma untuk sekali run, nanti diubah lagi WORKDIR ny
WORKDIR /home/airflow

# Inisialisasi database
RUN airflow db init

# username dan password -> aiflow / airflow
RUN airflow users create \
    --username airflow \
    --firstname Airflow \
    --lastname Airflow \
    --role Admin \
    --email pms@bps.go.id \
    -p airflow

# Workdir diubah ke semula
WORKDIR /home

# Copy library tambahan dan install semua yang ada di list
COPY library_tambahan.txt /home/library_tambahan.txt

COPY library_tambahan.txt /home/library_tambahan.txt

RUN pip3 --trusted-host pypi.org --trusted-host files.pythonhosted.org install -r library_tambahan.txt



# install browser chrome, dibawah ini scriptny:
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee -a /etc/apt/sources.list
RUN apt-get install -y wget
RUN wget https://dl.google.com/linux/linux_signing_key.pub
RUN apt-get install -y gnupg
RUN apt-key add linux_signing_key.pub
RUN apt update

# debian frontend dimatikan biar nggak ada interaksi dengan user apalagi pas diminta pilih regional
ENV DEBIAN_FRONTEND=noninteractive

RUN apt install -y google-chrome-stable

RUN apt-get install -yqq unzip curl
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/



# install php tapi tanpa mysql, karena database akan diinstall dengan container yang lain, kl yg ini khusus run aplikasi
RUN apt install -y apache2
RUN apt install -y php


CMD ["bash"]