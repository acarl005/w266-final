# W266 Final Project

### Andrew Carlson and Rich Ung

## References

* [W266 Final Project Report](https://www.overleaf.com/project/5bf8ec87ebc2c334ffdbf87f)
* [W266 Final Project Presentation](https://docs.google.com/presentation/d/1k_VisPTbH82Cg1oOhMV2iTRiZp1jhE2EQnKUO-RkGnI/edit?usp=sharing)
* [W266 Final Project Proposal](https://docs.google.com/document/d/1EsAdXfGgOFcpPfBqLHE-jGutprT5hjUsrJbt2mruAfI/edit?usp=sharing)
* [W266 Google Drive Folder](https://drive.google.com/drive/folders/1ECIYj3QUj5_WV2gX0-OId0HDrKJ9LAyw?usp=sharing)

## Loading Environment

Run the following command within the base directory of this repository to **build** the notebook Docker environment for this project:
```
docker build -t w266/final:1.0 .
```

Run the following command within the base directory of this repository to **run** the notebook Docker environment for this project:
```
docker run --rm -p 8888:8888 -p 6006:6006 -e JUPYTER_ENABLE_LAB=yes -v "$PWD":/home/jovyan/work w266/final:1.0
```
