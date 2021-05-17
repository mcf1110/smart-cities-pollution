# Smart Cities

## Predicting Pollution from Waze Data

![São Paulo prediction for Marginal do Tietê](./readme.png)

## Inclusão de novos dados

Para gerar predições para uma nova cidade e/ou mês, os passos a se tomar são os seguintes:

1. **Obter os dados reais de poluição da cidade naquele mês em específico.** 
  Naturalmente, esse passo varia de caso para caso, pois cada cidade costuma ter N estações de monitoramento localizadas em pontos diferentes, e não existe maneira uniforme de obtê-los, pois cada agência governamental pode disponibilizá-los (ou não) da maneira que for conveniente.
2. **Gerar o csv com pelo menos as colunas h3id e NO2 (conforme os modelos no repositório).** 
   Novamente, varia de agência para agência, pois os dados “brutos” podem vir em qualquer formato. O h3id deve, idealmente, ter a resolução 9. Esse csv será usado para ajustar linearmente o modelo ao final do processo. Alguns scripts esperam que o csv esteja no caminho `data/Nome da Cidade/nomedacidade2019.csv`, mas isso pode facilmente ser configurado.
3. **Obter os dados do waze para as estações.**
   Este passo consiste em executar o arquivo `Waze Data/Generate Datasets`. Na segunda célula, é possível configurar quais arquivos csv serão considerados. Na quinta célula do arquivo, é impressa a consulta SQL otimizada para executar no Athena. Após a execução, que costuma levar cerca de 6-7min, basta baixar o csv e substituir o arquivo`X_stations.csv`.
4. **Obter os dados do waze para a vizinhança.**
   No mesmo arquivo, há a seção Neighborhood, em que são geradas as queries para os hexágonos vizinhos de cada estação. A função `makeQuery` é chamada para cada chunk de cada cidade, gerando as consultas SQL. O tamanho do *chunk* que funcionou na prática foi em torno de 100, que é a configuração padrão da função, mas pode ser customizado (por exemplo, São Paulo usa 110 para economizar uma consulta). Os arquivos foram colocados na pasta `neighbors`, com o padrão “nomedacidade_n”, em que n é o número do *chunk*+1. Embora esse padrão seja totalmente opcional, dado que os scripts lêem todos os arquivos nesta pasta, acreditamos que isso auxilia na organização.
5. **Executar a predição.**
   O código completo é executado em `predictions/using_mean_with_neighbor`. As cidades a serem consideradas podem ser configuradas na variável cities.
6. **Gerar os mapas, através do arquivo `gui/Make HTMLs`.**
   Também é possível mudar a variável cities. Aqui, serão gerados novamente todos os arquivos da pasta maps.
7. **Atualizar a interface.** 
   Este passo é manual e consiste em editar os HTMLs existentes na raiz da pasta gui se necessário (no caso de adição de uma nova cidade, por exemplo). Caso isso se torne muito comum, este passo pode ser automatizado com o uso de uma “templating engine”, por exemplo.