FROM jupyter/tensorflow-notebook:e8613d84128b

RUN pip install gensim \
                nltk

# Execute the following commands within the base directory of the repository to build and run the environment
# docker build -t w266/final:1.0 .
# docker run --rm -p 8888:8888 -e JUPYTER_ENABLE_LAB=yes -v "$PWD":/home/jovyan/work w266/final:1.0

# Interested in cleaning up your docker environment within your laptop? Check out these commands
# docker image ls
# docker image rm _____ <- insert IMAGE IDs that you want to remove
# docker ps -a
# docker rm _____ <- insert CONTAINER IDs that you want to remove