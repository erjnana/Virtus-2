========================================================= INSTRUÇÕES DE INSTALAÇÃO =========================================================

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

P.S.: Para configurar no ubuntu, primeiro instalar o anaconda e fazer o mesmo + > conda install petsc4py

========================================================= DESCRIÇÃO =========================================================

Este repositório contém o projeto do programa de Otimização Multidisciplinar desenvolvido para a equipe Minerva Aerodesign da UFRJ para o projeto de aeronaves destinadas à competição SAE Aerodesign.

O início do desenvolvimento se deu na fase inicial da competição de 2023, porém com o intuito de servir ao futuro da equipe.

A função do programa é otimizar a geometria de uma aeronave de modo a obter uma maior pontuação e satisfazendo as restrições necessárias.

O programa tem base em 2 pacotes:

Avlwrapper: Traz uma interface em python para o uso do Avl, um software de análise de aerodinâmica e estabilidade que utiliza o método de malha de painéis (VLM).
OpemMDAO: Um framework que possibilita a realização simples e rápida de otimizações customizadas.

A geometria é definida no código "prototype.py", que recebe os parâmetros desejados e constrói um modelo de geometria do AVL.

No arquivo "simulator.py", se inserem todos os métodos para rodar, a partir de um indivíduo prototype(), todas as simulações necessárias e calcular todos os coeficientes de aerodinâmica, estabilidade e desempenho, incluindo a pontuação pela qual se deseja avaliar cada indivíduo.

Os arquivos "individual.py" e "optimizer.py" adaptam toda a construção e simulação para a otimização

"performance.py" e "stability.py" são bibliotecas que contém todas as funções, cálculos e verificações das suas respectivas áreas.

O fluxograma junto do repositório mostra a estrutura básica do funcionamento.

O notebook "viewer.ipynb" possibilita a visualização gráfica da evolução dos indivíduos em termos de objetivos e restrições. Você deve inserir, lá, o nome do arquivo '.db' definido no 'optimizer.py'

O script "post_processing" foi criado para incluir todas as funções de pós processamento além da simples visualização do arquivo "viewer.ipynb". Uma das funções por exemplo é filtrar as melhores aeronaves que se adequem totalmente a todas as restrições fornecendo as variáveis de design adotadas e organizar em um log.


=========================================================

Autores: 

Lucas Alves da Rosa (lucas.rosa@poli.ufrj.br)
Ana Luiza Silva Duarte (als.duarte.20232@poli.ufrj.br)

