############################### INSTRUÇÕES DE INSTALAÇÃO ###############################
Aqui estarão as instruções recomendadas para rodar o programa de otimização. Pode ser um pouco complicado e diferente para cada máquina baseado no que já havia instalado na máquina anteriormente. Talvez falte algo aqui que requeira um pouco de investigação, se descobrir coloque aqui.

1. Instalar o Anaconda, para gerenciar o ambiente virtual e instalar os pacotes
2. Dentro do Anaconda, instalar o VSCode, para editar e rodar os códigos (abrir sempre pelo anaconda)
3. Para configurara o ambiente para rodar o MDO, digite o seguinte comando no terminal do anaconda:

    > pip install openmdao;pip install pyDOE2;pip install mpi4py; pip install ipympl

    Agora que já estão instalados os pacotes necessários para o OpenMDAO, é preciso instalar e configurar o avlwrapper.

    faça o download do zip do avlwrapper em https://github.com/jbussemaker/AVLWrapper.git, coloque a pasta avlwrapper em C:/Users/"Seu_usuario"/anaconda3/Lib/site-packages/ e. Em seguida copie o arquivo avl.exe para dentro da pasta avlwrapper, abra o arquivo config e especifice Executable como avl.exe.

    3.1. Para configurar no ubuntu, primeiro instalar o anaconda e fazer o mesmo + > conda install petsc4py

4. Baixar o executável do avl na versão 3.36 e copiar para dentro dessa pasta do avlwrapper (se não achar o executável tente especificar mais o caminho do diretório no arquivo config)

############################### DESCRIÇÃO ###############################
Este repositório contém o projeto de um programa de Otimização Multidisciplinar desenvolvido para a equipe Minerva Aerodesign da UFRJ para o projeto de aeronaves destinadas à competição SAE Aerodesign.

O início do desenvolvimento se deu na fase inicial da competição de 2023, porém com o intuito de servir ao futuro da equipe.

A função do programa é otimizar a geometria de uma aeronave de modo a obter uma maior pontuação e satisfazendo as restrições necessárias.

O programa tem base em 2 pacotes:

Avlwrapper: Traz uma interface em python para o uso do Avl, um software de análise de aerodinâmica e estabilidade que utiliza o método de malha de painéis (VLM).
OpemMDAO: Um framework que possibilita a realização simples e rápida de otimizações customizadas.

A geometria é definida no código "prototype.py", que recebe os parâmetros desejados e constrói um modelo de geometria do AVL.

No arquivo "simulator.py", se inserem todos os métodos para rodar, a partir de um indivíduo prototype(), todas as simulações necessárias e calcular todos os coeficientes de aerodinâmica, estabilidade e desempenho, incluindo a pontuação pela qual se deseja avaliar cada indivíduo.

Os arquivos "individual.py" e "optimizer.py" adaptam toda a construção e simulação para a otimização

"performance.py" e "stability.py" são bibliotecas que contém todas as funções, cálculos e verificações das suas respectivas áreas.

Diferentes conceitos de aeronaves precisarão de alterações nos inputs dos arquivos de protótipo, indivíduo e otimizador. O melhor é criar diretórios diferentes para diferentes configurações. Da mesma forma, adaptar o código de um ano para o outro também deve requerer alterações nesses mesmos arquivos, na parte de cálculos de propriedades e restrições além de outras melhorias.

O fluxograma junto do repositório mostra a estrutura básica do funcionamento.

O notebook "viewer.ipynb" possibilita a visualização gráfica da evolução dos indivíduos em termos de objetivos e restrições. Você deve inserir, lá, o nome do arquivo '.db' definido no 'optimizer.py'

O script "post_processing" foi criado para incluir todas as funções de pós processamento além da simples visualização do arquivo "viewer.ipynb". Uma das funções por exemplo é filtrar as melhores aeronaves que se adequem totalmente a todas as restrições fornecendo as variáveis de design adotadas e organizar em um log.

Para poder acompanhar os indivíduos do programa durante a rodagem do mesmo, execute o otimizador através do comando:

> python optimizer.py > log_optimizer.txt

Dessa forma todo o registro da evolução será salvo num arquivo chamado log_optimizer.txt. Você pode nomear o arquivo da forma que desejar, e deixar vários logs!

############################### MSG ###############################
Olá! Tentei documentar o suficiente para que com alguma pesquisa qualquer um com entendimento em python e aerodesign pudesse conseguir entender os códigos, mas não sou nenhum programador e esse programa foi um pouco fruto de um experimento, em colaboração claro com alguns membros de aerodinâmica, desempenho e controle e estabilidade. A equipe já teve um MDO antes cujo domínio sobre se perdeu ao longo dos anos (depois de um tempo ninguém entendia mais como funcionava), então essa foi uma preocupação. Qualquer coisa só me contatar, devem haver as infos no GitHub, mas:

Autor: Lucas Alves da Rosa (lucas.rosa@poli.ufrj.br)

Sinta-se livre para mexer nesses códigos e incluir seu nome aqui ou copiar o que quiser para desenvolver um programa novo!