[![Master deploy](https://github.com/flaboss/projeto_ROE/actions/workflows/deploy.yaml/badge.svg?branch=main)](https://github.com/flaboss/projeto_ROE/actions/workflows/deploy.yaml)

# projeto_ROE
Este projeto conecta vários serviços *freemium* para montar um sistema de recomendação de operações estruturadas utilizando dados de ações e opções de ações da bolsa brasileira BMF BOVESPA.

O sistema utiliza *github actions* como esteira de deploy, onde cada pull request ou merge na branch master passa por testes automatizados. Se bem sucedido, uma imagem Docker é carregada no docker hub para ser utilizada na execução. A imagem já tem todas as bibliotecas necessárias pré instaladas, o que faz com que a execução seja mais rápida, pulando a etapa de instalação. O projeto é executado diariamente e envia notificações via push e via telegram - os meios que me convém para estar atento a boas operações que possa aparecer.

### Serviços Utilizados:
![services](https://user-images.githubusercontent.com/8702703/168903597-d864a65e-f9b9-46c5-b5f9-72b27a14c734.png)

### Estrutura do Projeto:
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
