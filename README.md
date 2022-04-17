# Classificando sentenças criminais

Repositório para o Trabalho de Conclusão de Curso da Pós-Graduação de Ciência de Dados e Big Data da PUC/MG.

---

## Python

Todos os programas e scripts foram escritos com Python 3.8. Isso pode ser relevante especialmente para as definições de tipos nas declarações de funções.

## Quickstart

```
mkdir sentencas && cd sentencas
python3 -m venv ./env
source ./env/bin/activate (ou equivalente no windows/mac)
pip install -r requirements.txt
python main.py
```

E seguir as instruções de execução do programa.

---

## Main

Sempre executar o arquivo `main.py`. Não executar os outros módulos diretamente, esses somente devem ser invocados pelo main.

---

## Módulos

* scrap: módulo para coleta de dados.
* classify: módulo para classificação dos dados.
* analyze: módulo para análise dos dados.

---

## Data

### Training

* data/train/full.csv: arquivo com todas as classificações humanas, onde são adicionados as classificações verificadas após cada classificação. Arquivo default de treino dos classificadores.

* data/train/human.csv: arquivo de treinamento simplificado com poucas sentenças apenas classificadas humanamente (sem passagem pelos modelos de IA).

* data/train/train.csv: arquivo de treinamento com mais dados, com dados originalmente treinados pela IA e conferidos por um humano, mas que não é retroalimentado.


### data.csv

Arquivo contendo informações sobre todas as sentenças coletadas, inclusive url para download do texto integral.

### output.csv

Exemplo de output dos modelos de classificação.


---

## Constantes

As constantes de configuração do programa estão no arquivo constants.py. Não há configuração do ambiente. Qualquer alteração nas constantes deve ser feita diretamente no arquivo constants.py