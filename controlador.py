

import pygame


class Controlador:

    # distancia para parede no eixo y de 0 até 400
    # ângulo do caminhão com o eixo X
    # saída: ângulo das rodas: valor entre -30 e 30 graus
    def ajustar(self, distancia_para_parede: float, angulo_com_eixo_x: float) -> float:
        if angulo_com_eixo_x < 2 and angulo_com_eixo_x > -2:
            return 0
        return -45



class ConjuntoFuzzy(Controlador):
    def __init__(self, nome: str):  # 0 a 100
        self.base_inicio = 0
        self.base_final = 0
        self.topo_inicio = 0
        self.topo_final = 0
        self.nome = nome
        self.escala = 1
        self.corte = 1
        self.cor = (200, 200, 200)

    def pertinencia(self, x: float) -> float:
        resultado = 0
        if x < self.base_inicio:
            resultado = 0
        if x >= self.base_inicio and x < self.topo_inicio:
            diff = self.topo_inicio - self.base_inicio
            resultado = (x - self.base_inicio) / diff if diff > 0 else 0
        if x >= self.topo_inicio and x <= self.topo_final:
            resultado = 1
        if x >= self.topo_final and x < self.base_final:
            diff = self.base_final - self.topo_final
            resultado = (self.base_final - x) / diff if diff > 0 else 1
        if x > self.base_final:
            resultado = 0
        return min(self.corte, resultado * self.escala)

    def __repr__(self) -> str:
        return f"f_{self.nome}(x, {self.base_inicio}, {self.topo_inicio}, {self.topo_final}, {self.base_final})"


class UniversoDiscurso:
    def __init__(self, nome: str):
        self.conjuntos: list[ConjuntoFuzzy] = []
        self.nome = nome

    def obter(self, nome: str) -> ConjuntoFuzzy:
        for conjunto in self.conjuntos:
            if conjunto.nome == nome:
                return conjunto

    def adicionarConjunto(self, nome: str, a: float, b: float, c: float, d: float, cor: tuple[int, int, int] = (255, 255, 255)) -> None:
        conjunto = ConjuntoFuzzy(nome)
        conjunto.cor = cor
        conjunto.base_inicio = a
        conjunto.topo_inicio = b
        conjunto.topo_final = c
        conjunto.base_final = d
        self.conjuntos.append(conjunto)

    def avaliar(self, x: float) -> list[tuple[float, ConjuntoFuzzy]]:
        valores: list[tuple[float, ConjuntoFuzzy]] = []
        for conjunto in self.conjuntos:
            valores.append((conjunto.pertinencia(x), conjunto))

    def exibir(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode([600, 300])
        fonte = pygame.font.SysFont(None, 24)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((0, 0, 0))

            pygame.draw.line(screen, (0, 0, 200), (100, 90), (100, 210))
            pygame.draw.line(screen, (0, 0, 200), (90, 200), (510, 200))

            for i in range(0, 11):
                x = i * 40 + 100
                pygame.draw.line(screen, (0, 0, 200), (x, 190), (x, 210))
                texto_eixo = fonte.render(f'{i*10}', True, (0, 0, 200))
                screen.blit(texto_eixo, (x - 7, 220))

            for i in range(0, 6):
                y = 200 - i * 20
                texto_eixo = fonte.render(
                    f'{round(i*0.20, 2)}', True, (0, 0, 200))
                screen.blit(texto_eixo, (60, y - 7))
                pygame.draw.line(screen, (0, 0, 200), (95, y), (105, y))

            def deslocar(x):
                return x * 4 + 100

            texto = fonte.render(self.nome, True, (255, 255, 255))
            screen.blit(texto, (20, 20))

            x = 20
            for conjunto in self.conjuntos:
                pygame.draw.line(screen, conjunto.cor, (deslocar(
                    conjunto.base_inicio), 200), (deslocar(conjunto.topo_inicio), 100))
                pygame.draw.line(screen, conjunto.cor, (deslocar(
                    conjunto.topo_inicio), 100), (deslocar(conjunto.topo_final), 100))
                pygame.draw.line(screen, conjunto.cor, (deslocar(
                    conjunto.topo_final), 100), (deslocar(conjunto.base_final), 200))
                texto_eixo = fonte.render(conjunto.nome, True, conjunto.cor)
                screen.blit(texto_eixo, (x, 60))
                x += 100

            pygame.display.flip()
        pygame.quit()
    
    def exibirAtivacao(self, x:float) -> None:
        nomes = [f"{conjunto.nome}: {conjunto.pertinencia(x)}" for conjunto in self.conjuntos]
        print("{" + ", ".join(nomes) + "}")

    def __repr__(self) -> str:
        nomes = [conjunto.nome for conjunto in self.conjuntos]
        return f"{self.nome}: {", ".join(nomes)}"


class ControladorFuzzy:
    def __init__(self, x_universo: UniversoDiscurso, y_universo: UniversoDiscurso, saida: UniversoDiscurso):
        self.x_universo: UniversoDiscurso = x_universo
        self.y_universo: UniversoDiscurso = y_universo
        self.saida: UniversoDiscurso = saida
        self.regras: dict[tuple[ConjuntoFuzzy,
                                ConjuntoFuzzy], ConjuntoFuzzy] = dict()

    def alterarRegra(self, A: ConjuntoFuzzy, B: ConjuntoFuzzy, C: ConjuntoFuzzy):
        # TODO assert
        self.regras[(A, B)] = C

    def avalie(self, x: float, y: float) -> float:
        for C in self.saida.conjuntos:
            C.corte = 0.0
        for A in self.x_universo.conjuntos:
            for B in self.y_universo.conjuntos:
                C = self.regras[(A, B)]
                ativacao = min(A.pertinencia(x), B.pertinencia(y))
                C.corte = max(ativacao, C.corte)

        num = 0
        den = 0
        for x in range(0, 100, 10):
            maximo = 0
            for C in self.saida.conjuntos:
                ativacao = C.pertinencia(x)
                maximo = max(ativacao, maximo)
            num += maximo * x
            den += maximo
        # print("Numerador ", num, " den ", den)

        return num/den if den > 0 else 0

    def exibir(self):
        self.x_universo.exibir()
        self.y_universo.exibir()
        self.saida.exibir()

    def exibirRegras(self) -> None:
        print(' '.ljust(20), end="| ")
        for A in self.x_universo.conjuntos:
            print(A.nome.ljust(20), end="| ")
        print()

        for B in self.y_universo.conjuntos:
            print(B.nome.ljust(20), end="| ")
            for A in self.x_universo.conjuntos:
                C = self.regras[(A, B)]
                print(A.nome, B.nome, C.nome.rjust(20), end="| ")
            print()

    def exibirAtivacao(self) -> None:
        print(' '.ljust(20), end="| ")
        for A in self.x_universo.conjuntos:
            print(A.nome.ljust(20), end="| ")
        print()

        for B in self.y_universo.conjuntos:
            print(B.nome.ljust(20), end="| ")
            for A in self.x_universo.conjuntos:
                C = self.regras[(A, B)]
                print(f"{C.nome}: {round(C.corte, 2)}".rjust(20), end="| ")
            print()


class ControladorCaminhao(ControladorFuzzy):
    def __init__(self) -> None:
        distancia = UniversoDiscurso("Distancia")
        distancia.adicionarConjunto("Perto", 0, 0, 0, 10)
        distancia.adicionarConjunto("Adequado", 5, 15, 15, 25)
        distancia.adicionarConjunto("Longe", 20, 35, 100, 100)

        angulo = UniversoDiscurso("Eixo X")
        angulo.adicionarConjunto("Esquerdo", 0, 0, 40, 50)
        angulo.adicionarConjunto("Adequado", 40, 50, 50, 60)
        angulo.adicionarConjunto("Direito", 50, 60, 100, 100)

        rodas = UniversoDiscurso("Rodas")
        rodas.adicionarConjunto("Muito Esquerdo", 0, 0, 10, 30)
        rodas.adicionarConjunto("Esquerdo", 20, 35, 35, 50)
        rodas.adicionarConjunto("Adequado", 40, 50, 50, 60)
        rodas.adicionarConjunto("Direito", 50, 65, 65, 80)
        rodas.adicionarConjunto("Muito Direito", 70, 90, 100, 100)

        self.fuzzy = ControladorFuzzy(distancia, angulo, rodas)

        self.fuzzy.alterarRegra(distancia.obter("Perto"), angulo.obter("Esquerdo"), rodas.obter("Esquerdo"))
        self.fuzzy.alterarRegra(distancia.obter("Perto"), angulo.obter("Adequado"), rodas.obter("Adequado"))
        self.fuzzy.alterarRegra(distancia.obter("Perto"), angulo.obter("Direito"), rodas.obter("Direito"))

        self.fuzzy.alterarRegra(distancia.obter("Adequado"), angulo.obter("Esquerdo"), rodas.obter("Esquerdo"))
        self.fuzzy.alterarRegra(distancia.obter("Adequado"), angulo.obter("Adequado"), rodas.obter("Adequado"))
        self.fuzzy.alterarRegra(distancia.obter("Adequado"), angulo.obter("Direito"), rodas.obter("Direito"))

        self.fuzzy.alterarRegra(distancia.obter("Longe"), angulo.obter("Esquerdo"), rodas.obter("Muito Esquerdo"))
        self.fuzzy.alterarRegra(distancia.obter("Longe"), angulo.obter("Adequado"), rodas.obter("Adequado"))
        self.fuzzy.alterarRegra(distancia.obter("Longe"), angulo.obter("Direito"), rodas.obter("Muito Direito"))


    # distancia para parede no eixo y de 0 até 400
    # ângulo do caminhão com o eixo X
    # saída: ângulo das rodas: valor entre -45 e 45 graus
    def ajustar(self, distancia_para_parede: float, angulo_com_eixo_x: float) -> float:
        
        x = self.escalar(distancia_para_parede, 0, 400)

        angulo = angulo_com_eixo_x
        if angulo > 180:
            angulo = angulo - 360
        angulo = -angulo
        y = self.escalar(angulo, -180, 180)

        z_out = self.fuzzy.avalie(x, y)
        z_out /= 100

        z = z_out * (90) - 45

        return z

    def escalar(self, x, minimo: float, maximo: float) -> None:
        return 100*(x-minimo)/(maximo-minimo)


