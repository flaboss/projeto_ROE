[![Master deploy](https://github.com/flaboss/projeto_ROE/actions/workflows/deploy.yaml/badge.svg?branch=main)](https://github.com/flaboss/projeto_ROE/actions/workflows/deploy.yaml)

[![Maintainability](https://api.codeclimate.com/v1/badges/e9a713886b45ed45962d/maintainability)](https://codeclimate.com/github/flaboss/projeto_ROE/maintainability)

# Projeto ROE (Radar de Operações Estruturadas)
Este projeto conecta vários serviços *freemium* para montar um sistema de recomendação de operações estruturadas utilizando dados de ações e opções de ações da bolsa brasileira B3.

O sistema utiliza *github actions* como esteira de deploy, onde cada pull request ou merge na branch master passa por testes automatizados. Se bem sucedido, uma imagem Docker é carregada no docker hub para ser utilizada na execução. A imagem já tem todas as bibliotecas necessárias pré instaladas, o que faz com que a execução seja mais rápida, pulando a etapa de instalação. O projeto é executado diariamente e envia notificações via push e via telegram - os meios que me convém para estar atento a boas operações que possam aparecer.

### Serviços Utilizados:
![services](https://user-images.githubusercontent.com/8702703/168903597-d864a65e-f9b9-46c5-b5f9-72b27a14c734.png)

* [Github Actions](https://github.com/features/actions): usado como esteira de deploy (CICD).
* [Docker HUB](https://hub.docker.com/): armazena a imagem utilizada no processamento.
* [Deepnote](https://deepnote.com): plataforma que executa o código. Aqui o código é agendado para ser executado diariamente.
* [Yahoo Finance](https://finance.yahoo.com/): contém os dados de ações da B3.
* [Datapane](https://datapane.com/getting-started/#): serviço usado como relatório contendo as operações sugeridas.
* [Airtable](https://airtable.com/): serviço que funciona como **lista gerenciável**. Tabelas contém configurações de execução, preço médio de ações em custódia, e outras opções de configuração. Dessa maneira não é necessário fazer alterações no código para alterações menores, mas significativas, como por exemplo: "não quero executar a estratégia de trava de alta com put nos próximos dias" ou "não quero receber recomendações de operações envolvendo PETR4" ou até mesmo "quero receber operações com mais de 2% de lucro". Tudo isso pode ser feito pelo app no celular.
* [Bit.io](https://docs.bit.io/v1.0/docs): serve como uma base de dados para armazenar o histórico de operações. É possível visualizar as tabelas, plotar gráficos e fazer queries usando SQL.
* [Push Bullet](https://www.pushbullet.com/): serviço usado para receber notificações pelo celular (falhas de deploy ou operações interessantes). É possível desabilitar as notificações com um clique em uma variável no airtable.
* [Telegram](https://telegram.org/): serviço usado para receber notificação de execuções.  Também é possível desabilitar as notificações com um clique em uma variável no airtable.

### Estrutura do Projeto:
![structure](https://user-images.githubusercontent.com/8702703/168903745-f0f289dc-c39a-448c-ad53-2d1da65c2102.png)

A estrutura acima mostra como os serviços se relacionam. Todos os serviços se conectam por apis salvas em um arquivo `.env` que o código lê e que por motivos de segurança não está nesse repositório. Esse arquivo deve ser configurado apenas uma vez no ambiente de execução (nesse caso o Deepnote).

Qualquer alteração no código é submetida a testes automaticamente. Um merge na branch master sobe a nova imagem para o Docker hub.
O scheduler do Deepnote executa diariamente o código que faz pull request do código, da imagem Docker, dos dados de ações e opções e das configurações nas tabelas do airtable.
Uma vez que as recomendações de estratégias são geradas, são inseridas em uma tabela histórica (bit.io) e atualizam um relatório (datapane).
Notificações são enviadas via pushbullet (celular) e via telegram.

É importante mencionar que esse serviço não é um serviço online, pois utiliza dados com defasagem de 1 dia. Já encontrei operações interessantes por meio dessas recomendações. A análise desses relatórios me ajuda a ficar de olho para movimentos que ocorrem no mercado onde algumas estratégias com boa rentabilidade podem ser aplicadas.
