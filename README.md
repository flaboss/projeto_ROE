[![Master deploy](https://github.com/flaboss/projeto_ROE/actions/workflows/deploy.yaml/badge.svg?branch=main)](https://github.com/flaboss/projeto_ROE/actions/workflows/deploy.yaml)

# projeto_ROE
Este projeto executa recomendação de operações estruturadas com ações e opções da BMF BOVESPA.
Serviços utilizados:
![services](https://user-images.githubusercontent.com/8702703/168903597-d864a65e-f9b9-46c5-b5f9-72b27a14c734.png)

![structure](https://user-images.githubusercontent.com/8702703/168903745-f0f289dc-c39a-448c-ad53-2d1da65c2102.png)

├── Dockerfile
├── Makefile
├── README.md
├── __init__.py
├── modules
│   ├── __init__.py
│   ├── capital_garantido.py
│   ├── lancamento_coberto.py
│   ├── main.py
│   ├── test
│   │   ├── __init__.py
│   │   └── test_functions.py
│   ├── trava_alta_put.py
│   ├── utils.py
│   └── venda_put_seco.py
├── requirements.txt
├── setup.py
└── tree.txt