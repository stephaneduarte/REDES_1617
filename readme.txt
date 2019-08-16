______________________________________________________________________________
|                             PROJETO DE REDES                               |
|                                 GRUPO 33                                   |
|                         81186 - Stephane Duarte                            |
|                       81728 - Madalena Assembleia                          |
|                          81858 - Joao Oliveira                             |
|____________________________________________________________________________|

Este projeto encontra-se dividido em 3 componentes: TCS, TRS e user.

Como correr o projeto:
[Pressupoe-se que a consola ja se encontra na diretoria do projeto.]

1. Correr o TCS:

python TCS.py [-p TCSport]

-p: porta onde pretende que corra o TCS. Default: 58033.


2. Correr um ou mais TRS:

Neste projeto estao disponiveis as seguintes liguagens: ENGLISH e FRENCH.
Adiante designaremos o nome de uma linguagem generica por NL.

cd TRS/NL/
python TRS.py NL [-p TRSport] [-n TCSname] [-e TCSport]

-p: porta onde pretende que corra o TRS. Default: 59000
-n: nome da maquina onde corre o TCS. Default: maquina local.
-e: porta onde corre o TCS. Default: 58033

Traducoes disponiveis:
ENGLISH:
 - Palavras: yellow blue white gray orange magenta brown gold silver black pink purple green red burgundy violet light dark rainbow phone
 - Ficheiros: flower.jpg microwaves.jpg pen.jpg seal.jpg sharks.jpg

FRENCH:
 - Palavras: beige blanc bleu clair fonce gris jaune marron noir orange rose rouge vert violet rougeatre jaunet vert football tennis beau
 - Ficheiros: fleur.jpg microondes.jpg requins.jpg joint.jpg stylo.jpg

3. Correr um ou mais usuarios:

cd user/
python user.py [-n TCSname] [-p TCSport]

-n: nome da maquina onde corre o TCS. Default: maquina local.
-p: porta onde corre o TCS. Default: 58033