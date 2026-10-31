import os                          # acessa variáveis de ambiente (onde a chave vai parar)
import sys                         # usado pra encerrar o programa com mensagem de erro
import time                        # usado pra medir quanto tempo cada IA leva

import httpx                       # faz as requisições HTTP
from dotenv import load_dotenv     # traz só a função que lê o .env