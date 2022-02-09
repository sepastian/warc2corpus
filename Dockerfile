# Base Alpine Linux based image with OpenJDK and Maven
FROM aut

# Metadata
LABEL maintainer="Sebastian Gassner <sebastian.gassner@gmail.com>"
LABEL description="Docker image for warc2corpus, based on the Archives Unleashed Toolkit."
LABEL website="https://github.com/sepastian/warc2corpus/"

WORKDIR /w2c

# Copy pyspark starup script to /usr/local/bin/pyspark
ADD files /

# Install pip3 and requirements.txt
RUN apt-get update && apt-get install -y \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /build/requirements.txt
RUN pip3 install -r /build/requirements.txt \
  && rm -rf /build

# Add /w2c/lib to the Python search path
ADD sample /w2c/sample
ADD lib /w2c/lib
ENV PYTHONPATH=/w2c/lib

ENTRYPOINT ["/usr/local/bin/aut-spark-shell"]
