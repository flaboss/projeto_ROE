[![Master deploy](https://github.com/flaboss/projeto_ROE/actions/workflows/deploy.yaml/badge.svg?branch=main)](https://github.com/flaboss/projeto_ROE/actions/workflows/deploy.yaml)

# projeto_ROE
Este projeto executa recomendação de operações estruturadas com ações e opções da BMF BOVESPA.
Serviços utilizados:
![services](https://user-images.githubusercontent.com/8702703/168903597-d864a65e-f9b9-46c5-b5f9-72b27a14c734.png)

![structure](https://user-images.githubusercontent.com/8702703/168903745-f0f289dc-c39a-448c-ad53-2d1da65c2102.png)

├── Dockerfile <br>
├── Makefile <br>
├── README.md <br>
├── __init__.py <br>
├── modules <br>
│   ├── __init__.py <br>
│   ├── capital_garantido.py <br>
│   ├── lancamento_coberto.py <br>
│   ├── main.py <br>
│   ├── test <br>
│   │   ├── __init__.py <br>
│   │   └── test_functions.py <br>
│   ├── trava_alta_put.py <br>
│   ├── utils.py <br>
│   └── venda_put_seco.py <br>
├── requirements.txt <br>
├── setup.py <br>
└── tree.txt <br>
