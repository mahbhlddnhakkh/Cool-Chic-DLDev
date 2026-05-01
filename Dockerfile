#FROM python:3.10-slim as BUILDER
FROM nvidia/cuda:11.7.1-cudnn8-devel-ubuntu22.04 as BUILDER

WORKDIR /code

RUN apt update && apt install -y build-essential g++ curl unzip python3 python3-dev python3-pip

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

COPY --parents coolchic/* cfg/* toolbox/* setup.py pyproject.toml docker-scripts/preload-models.py ./

RUN pip install --user -e .

RUN python3 docker-scripts/preload-models.py

# Store dataset

RUN mkdir -p dataset-test/

COPY docker-scripts/download-kodak.sh docker-scripts/download-kodak.sh
RUN bash docker-scripts/download-kodak.sh "dataset-test/"

#RUN curl https://data.vision.ee.ethz.ch/cvl/clic/professional_valid_2020.zip -o dataset-test/clic20-pro.zip
#RUN unzip -j dataset-test/clic20-pro.zip "valid/*" -d "dataset-test/"
#RUN rm -f dataset-test/clic20-pro.zip

COPY . .

#CMD ["bash"]

#CMD ["python", "-m", "test.sanity_check"]
CMD ["sh", "docker-scripts/run-test.sh"]
