
# Simulador Fuzzy

O objetivo do sistema consiste em simular o estacionamento de um caminhão através de um controlador fuzzy.


O caminhão só pode movimentar para trás e pode alterar o ângulo das rodas entre -45º e 45º em relação ao eixo central do caminhão. Além disso, o caminhão é munido de dois sensores, um para medir a distância até a parede e outro para indicar o ângulo entre o eixo central do caminhão e o eixo horizontal do
estacionamento. O sensor de distância fornece valores metros e o sensor do ângulo fornece valores entre 0 e 360º.

#### Execução

python simulador.py


#### Dependência

python3 -m pip install -U pygame --user
