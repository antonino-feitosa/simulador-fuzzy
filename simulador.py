

import math
import pygame
import random
from controlador import *

#CONTROLADOR = Controlador()
CONTROLADOR = ControladorCaminhao()
#CONTROLADOR.fuzzy.exibir()

INCERTEZA = True

TORADIAS = math.pi/180.0
TODEGRESS = 180.0/math.pi
INCREMENTO = 1

POSICAO_INICIAL = (375, 150)

random.seed(0)
pygame.init()

class Posicao:
    def __init__(self, x:float = 0, y:float = 0):
        self.x:float = x
        self.y:float = y
    
    def difference(self, pos:'Posicao') -> 'Posicao':
        return Posicao(self.x - pos.x, self.y - pos.y)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def toUnit(self) -> None:
        magnitude = self.magnitude()
        self.x /= magnitude
        self.y /= magnitude
    
    def scale(self, s: float) -> None:
        self.x *= s
        self.y *= s
    
    def __str__(self) -> str:
        return f"({int(self.x)},{int(self.y)})"


class Caminhao:
    def __init__(self):
        self.angulo:float = 0
        self.motor = Posicao()
        self.traseira = Posicao()
        self.imagem = pygame.image.load("caminhao.png")
        self.reiniciar()
    
    def atualizar(self) -> None:
        if self.motor.x <= 150 + 15 or self.motor.x > 450 or self.motor.y <= 50 + 15 or self.motor.y > 475:
            return

        diferenca = self.traseira.difference(self.motor)
        angulo_atual = math.atan2(diferenca.y, diferenca.x) * TODEGRESS
        angulo_atual += self.angulo

        if INCERTEZA:
            angulo_atual += random.random()

        self.motor.x += INCREMENTO * math.cos(angulo_atual*TORADIAS)
        self.motor.y += INCREMENTO * math.sin(angulo_atual*TORADIAS)

        diferenca = self.traseira.difference(self.motor)
        diferenca.toUnit()
        diferenca.scale(70)
        
        self.traseira.x = diferenca.x + self.motor.x
        self.traseira.y = diferenca.y + self.motor.y
        
    def reiniciar(self):
        self.motor:Posicao = Posicao(POSICAO_INICIAL[0]+13, POSICAO_INICIAL[1] + 13)
        self.traseira:Posicao = Posicao(POSICAO_INICIAL[0]+13, POSICAO_INICIAL[1] + 100 - 13)
    
    def anguloEixoX(self) -> float:
        diferenca = self.traseira.difference(self.motor)
        inclinacao = math.atan2(-diferenca.y, diferenca.x) * TODEGRESS

        inclinacao += 180
        return inclinacao
    
    def estaNoAnguloCerto(self) -> bool:
        inclinacao = self.anguloEixoX()
        return inclinacao < 1 or (inclinacao > 359)
    
    def desenhar(self, tela:pygame.surface) -> None:
        diferenca = self.traseira.difference(self.motor)
        inclinacao = math.atan2(diferenca.y, diferenca.x) * TODEGRESS

        rotacionado = pygame.transform.rotate(self.imagem, -(inclinacao - 90))
        x = self.motor.x - rotacionado.get_rect().centerx
        y = self.motor.y - rotacionado.get_rect().centery
        tela.blit(rotacionado, (x, y))

        pygame.draw.circle(tela, (0,0,200), (self.motor.x, self.motor.y), 5)
        pygame.draw.circle(tela, (0,0,100), (self.traseira.x, self.traseira.y), 10)

        self.desenhar_eixos(tela)

    
    def desenhar_eixos(self, tela:pygame.surface) -> None:
        diferenca = self.motor.difference(self.traseira)
        inclinacao = math.atan2(diferenca.y, diferenca.x) + self.angulo *TORADIAS
        x = 50 * math.cos(inclinacao) + self.motor.x
        y = 50 * math.sin(inclinacao) + self.motor.y
        pygame.draw.line(tela, (0,0, 200), (self.motor.x, self.motor.y), (x, y))

        posicao = self.traseira
        cor = (0, 200, 0) if self.estaNoAnguloCerto() else (200, 0, 0)
        pygame.draw.line(tela, cor, (posicao.x - 50, posicao.y), (posicao.x + 50, posicao.y))
    


class Sistema:
    def __init__(self, caminhao = Caminhao(), controlador = CONTROLADOR):
        self.tela = pygame.display.set_mode((600,600))
        self.clock = pygame.time.Clock()
        self.fonte = pygame.font.SysFont(None, 24)
        self.executando = False
        self.caminhao = caminhao
        self.controlador = controlador
        self.aplicar_ajuste()
        pygame.display.set_caption('Simulador: Caminhão')
        self.reiniciar()
    
    def reiniciar(self):
        self.caminhao.reiniciar()
        
    def atualizar(self) -> None:
        self.aplicar_ajuste()
        self.caminhao.atualizar()
    
    def aplicar_ajuste(self) -> None:
        distancia_para_eixo_y = self.caminhao.motor.x - (150 + 15)
        angulo_com_eixo_x = self.caminhao.anguloEixoX()

        ajuste = self.controlador.ajustar(distancia_para_eixo_y, angulo_com_eixo_x)

        ajuste = min(45, ajuste)
        ajuste = max(-45, ajuste)

        self.caminhao.angulo = ajuste

    def desenhar(self) -> None:
        self.tela.fill((25, 0, 0))
        self.desenharAmbiente()
        self.caminhao.desenhar(self.tela)
        self.desenharLimites()

    def desenharAmbiente(self) -> None:
        pygame.draw.rect(self.tela, (0, 50, 0), pygame.Rect(100, 100, 400, 400))
        texto = self.fonte.render('(100,100)', True, (0, 0, 200))
        self.tela.blit(texto, (60, 70))

        texto = self.fonte.render('(500,500)', True, (0, 0, 200))
        self.tela.blit(texto, (480, 520))

        texto_eixo = self.fonte.render(f'Ângulo com o eixo X: {round(self.caminhao.anguloEixoX(), 1)}', True, (0, 0, 200))
        self.tela.blit(texto_eixo, (20, 520))

        texto_caminhao = self.fonte.render(f'Ângulo das rodas com o caminhão: {round(self.caminhao.angulo, 1)}', True, (0, 0, 200))
        self.tela.blit(texto_caminhao, (20, 560))

        texto_posicao = self.fonte.render(f'Posição do motor do caminhão: {self.caminhao.motor}', True, (0, 0, 200))
        self.tela.blit(texto_posicao, (20, 20))
    
    def desenharLimites(self) -> None:
        cor = (20, 200, 0)
        pygame.draw.line(self.tela, cor, (100, 100), (100, 500))
        pygame.draw.line(self.tela, cor, (100, 100), (500, 100))
        pygame.draw.line(self.tela, cor, (500, 500), (100, 500))
        pygame.draw.line(self.tela, cor, (500, 500), (500, 100))
    
    



    
sistema = Sistema()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                sistema.executando = not sistema.executando
            
            if event.key == pygame.K_ESCAPE:
                sistema.reiniciar()
                sistema.executando = False
        
    if sistema.executando:
        sistema.atualizar()
    sistema.desenhar()

    pygame.display.flip()
    sistema.clock.tick(60)        # 60 fps
