========================= DESCRIÇÃO =========================

Este repositório contém o projeto do programa de Otimização Multidisciplinar desenvolvido para a equipe Minerva Aerodesign da UFRJ para o projeto de aeronaves destinadas à competição SAE Aerodesign.

O início do desenvolvimento se deu na fase inicial da competição de 2023, porém com o intuito de servir ao futuro da equipe.

A função do programa é otimizar a geometria de uma aeronave de modo a obter uma maior pontuação e satisfazendo as restrições necessárias. O programa atual está configurado baseado no regulamento de 2026.

O programa tem base em 2 pacotes:

Avlwrapper: Traz uma interface em python para o uso do Avl, um software de análise de aerodinâmica e estabilidade que utiliza o método de malha de painéis (VLM).
OpemMDAO: Um framework que possibilita a realização simples e rápida de otimizações customizadas.

A geometria é definida no código "prototype.py", que recebe os parâmetros desejados e constrói um modelo de geometria do AVL.

No arquivo "simulator.py", se inserem todos os métodos para rodar, a partir de um indivíduo prototype(), todas as simulações necessárias e calcular todos os coeficientes de aerodinâmica, estabilidade e desempenho, incluindo a pontuação pela qual se deseja avaliar cada indivíduo.

Os arquivos "individual.py" e "optimizer.py" adaptam toda a construção e simulação para a otimização

"performance.py" e "stability.py" são bibliotecas que contém todas as funções, cálculos e verificações das suas respectivas áreas.

O fluxograma junto do repositório mostra a estrutura básica do funcionamento.

O notebook "viewer.ipynb" possibilita a visualização gráfica da evolução dos indivíduos em termos de objetivos e restrições.

O script "post_processing" foi criado para incluir todas as funções de pós processamento além da simples visualização do arquivo "viewer.ipynb". Uma das funções por exemplo é filtrar as melhores aeronaves que se adequem totalmente a todas as restrições fornecendo as variáveis de design adotadas e organizar em um log.

Autores: 

Lucas Alves da Rosa (lucas.rosa@poli.ufrj.br)
Ana Luiza Silva Duarte (als.duarte.20232@poli.ufrj.br)

========================= INSTRUÇÕES DE INSTALAÇÃO =========================

Neste arquivo se encontram as instruções recomendadas para rodar o programa de otimização. A experiência do usuário pode ser diferente dependendo no que já havia instalado na máquina anteriormente, dependendo do caso, será necessária uma maior investigação.

Primeiros passos:

1. Instalar o Anaconda, para gerenciar o ambiente virtual e instalar os pacotes;
2. Dentro do Anaconda, instalar o VSCode, para editar e rodar os códigos (abrir sempre pelo anaconda);
3. Para configurar o ambiente para rodar o MDO, digite o seguinte comando no terminal do Anaconda:

    > pip install openmdao;pip install pyDOE2;pip install mpi4py; pip install ipympl

Agora que já estão instalados os pacotes necessários para o OpenMDAO, é preciso instalar e configurar o avlwrapper:

1. Faça o download do zip do avlwrapper em https://github.com/jbussemaker/AVLWrapper.git
2. Coloque a pasta avlwrapper em C:/Users/"Seu_usuario"/anaconda3/Lib/site-packages/
3. Copie o arquivo avl352.exe contido na pasta do Virtus 2 para dentro da pasta avlwrapper, abra o arquivo config e especifice Executable como avl352.exe.

P.S.: Para configurar no Ubuntu, Primeiro instalar o anaconda e fazer o mesmo + > conda install petsc4py

========================= INSTRUÇÕES DE USO =========================

Caso seja sua primeira vez rodando o Virtus, é necessário retirar os arquivos de aerofólios (.dat) da pasta ./dats e colocá-los no diretório raiz do programa (./). Caso contrário, o programa não funcionará.

Todas as restrições da sua aeronave devem ser alteradas no arquivo variables.py. Nesse arquivo, é possível alterar informações como:
- Configuração da aeronave;
- Fatores de pontuação;
- Perfis dos componentes da aeronave;
- Restrições geométricas;
- Restrições de estabilidade;
- Configurações de otimização,
- Etc.

As variáveis estão comentadas para fácil entendimento, você também poderá definir o nome do projeto para melhor identificação na análise dos logs.

Para prosseguir para a execução do programa, dê run no arquivo optimizer.py. No seu terminal, aparecerão informações de carregamentos dos aerofólios e, logo em seguida, a otimização deverá começar a rodar.

Na pasta ./log/evolutions você poderá acessar um arquivo .txt referente à otimização. No nome do arquivo está o nome do projeto configurado no variables.py, o tipo de configuração da aeronave e o horário de início de execução para fácil catalogação.

Há também, na mesma pasta, um arquivo de mesmo nome com final .db. Este arquivo não pode ser lido, porém você pode utilizá-lo no viewer.py para acompanhar a evolução dos indivíduos por meio de gráficos. Para isso:
1. Rode a primeira parte do código;
2. Na segunda parte, altere o nome do arquivo para aquele que você gostaria de visualizar;
3. Em "cases", pressione "Select all",
4. Selecionar no X-axis e Y-axis a informação que você gostaria de visualizar.

O viewer.py não atualiza em tempo real. Por isso, toda vez que você quiser atualizar será necessário rodar novamente a segunda parte do código.

Caso você queira adicionar novos aerofólios ao banco de dados para utilizá-los:
Na pasta ./airfoils, selecione a pasta aonde o perfil que você gostaria de adicionar se enquadra (simétrico, assimétrico ou invertido) e crie uma nova pasta referente ao seu aerofólio. Dentro dessa pasta é necessário que tenham esses itens: o arquivo geometry.dat contendo a geometria e o arquivo info.yaml, sendo esse muito importante que siga o formato esspecífico que os outros já possuem. É fortemente recomendado que você crie uma cópia de algum info.yaml já existente e apenas altere as informações.

No diretório raiz (./), adicione novamente o arquivo .dat do aerofólio, porém, dessa vez, com o nome "af_(nomedoperfil).dat, caso contrário o código não lerá o arquivo.

É EXTREMAMENTE NECESSÁRIO QUE O NOME DO PERFIL NO ARQUIVO .DAT E O NOME DA PASTA NO ./AIRFOILS SEJÁ O MESMO.

PS.: No momento, a configuração de Asa Voadora não está funcionando.

