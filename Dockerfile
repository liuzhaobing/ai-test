FROM docker.io/library/ubuntu:22.04
WORKDIR /code
ADD requirements.txt requirements.txt
RUN apt-get update && apt-get install -y python3-pip
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
ENTRYPOINT ["sleep", "infinity"]
