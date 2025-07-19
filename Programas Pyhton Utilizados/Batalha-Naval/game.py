# game.py (MODIFICADO)

import pygame
import sys
import random

# Importa as novas cores
from constantes import (LINHAS_TABULEIRO, COLUNAS_TABULEIRO, LARGURA_TELA_PX, ALTURA_TELA_PX, MARGEM_ESQ_PX,
                        MARGEM_TOP_PX, LARGURA_TABULEIRO_PX, ALTURA_TABULEIRO_PX,
                        ESPACO_ENTRE_TABULEIROS, ALTURA_INTERFACE_JOGO,
                        PRETO, CINZACLARO, VERDEVENCEDOR, VERMELHO, TAMANHO_CELULA, BRANCO,
                        MODERN_BLUE_RGB, MODERN_BLUE_HOVER_RGB, DANGER_COLOR_RGB, DANGER_HOVER_RGB, TEXTO_BOTAO_FIM_JOGO)


from tabuleiro import Tabuleiro
from tipos_de_navio import INFO_NAVIOS, MAX_NAVIOS_JOGADOR, BaseNavio

# --- CONSTANTES DOS BOTÕES ATUALIZADAS ---
BOTÃO_LARGURA = 180
BOTÃO_ALTURA = 50
# As cores agora vêm do arquivo de constantes


class Jogo:
    """Controla o fluxo do jogo Batalha Naval."""

    def __init__(self):
        pygame.display.set_mode((LARGURA_TELA_PX, ALTURA_TELA_PX))
        pygame.display.set_caption("Batalha Naval")
        self._tela = pygame.display.get_surface()

        self._fonte = pygame.font.SysFont(None, 25)
        self._fonte_coords = pygame.font.SysFont(None, 18)
        self._fonte_botao = pygame.font.SysFont("Segoe UI", 22, bold=True) # Fonte mais parecida com a do menu

        self._tabuleiro_jogador = Tabuleiro()
        self._tabuleiro_ia = Tabuleiro()

        self._offset_jogador_x = MARGEM_ESQ_PX
        self._offset_jogador_y = MARGEM_TOP_PX
        self._offset_ia_x = MARGEM_ESQ_PX + LARGURA_TABULEIRO_PX + ESPACO_ENTRE_TABULEIROS
        self._offset_ia_y = MARGEM_TOP_PX

        self._tamanho_navio_atual = min(INFO_NAVIOS.keys()) if INFO_NAVIOS else None

        self._direcao_navio_atual = "horizontal"
        self._tipos_navios_colocados_jogador = set()

        self._jogo_iniciado = False
        self._vencedor = None
        self._turno_jogador = True

        self._mensagem_notf = "Selecione no teclado numérico entre (1-6) para selecionar um navio, Mude a direção (R), Posicione (Clique no seu tabuleiro)."
        self._clock = pygame.time.Clock()

        self._ret_botao_jogar_novamente = None
        self._ret_botao_sair = None
        
        # --- NOVO: Variável para controlar a ação final e o estado do clique ---
        self._acao_final = None
        self._botao_pressionado = None

    def _pegar_celula(self, pos_mouse: tuple[int, int], offset_x: int, offset_y: int) -> tuple[int, int]:
        x_mouse, y_mouse = pos_mouse
        x_relativo = x_mouse - offset_x
        y_relativo = y_mouse - offset_y

        if 0 <= x_relativo < LARGURA_TABULEIRO_PX and 0 <= y_relativo < ALTURA_TABULEIRO_PX:
            coluna = x_relativo // TAMANHO_CELULA
            linha = y_relativo // TAMANHO_CELULA
            return linha, coluna
        return -1, -1

    def _gerar_navios_ia(self):
        tipos_navios_ia = list(INFO_NAVIOS.keys())
        navios_colocados_ia = 0
        for tamanho in tipos_navios_ia:
            ClasseNavio = INFO_NAVIOS[tamanho]["classe"]
            tentativas = 0
            max_tentativas = 150
            while tentativas < max_tentativas:
                direcao = random.choice(["horizontal", "vertical"])
                navio_ia = ClasseNavio(direcao)
                linha = random.randint(0, LINHAS_TABULEIRO - 1)
                coluna = random.randint(0, COLUNAS_TABULEIRO - 1)
                if self._tabuleiro_ia.colocar_navio(linha, coluna, navio_ia):
                    navios_colocados_ia += 1
                    break
                tentativas += 1
            if tentativas == max_tentativas:
                print(f"AVISO: IA não conseguiu posicionar o navio de tamanho {tamanho} após {max_tentativas} tentativas.")
        print(f"IA posicionou {navios_colocados_ia} navios.")

    def _ataque_ia(self):
        self._mensagem_notf = "A IA está pensando onde atacar..."
        self._desenhar_tudo(pygame.mouse.get_pos())
        pygame.display.flip()
        pygame.time.wait(100)

        celulas_disponiveis = [(r, c) for r in range(self._tabuleiro_jogador.linhas)
                               for c in range(self._tabuleiro_jogador.colunas)
                               if self._tabuleiro_jogador.grid[r][c] in [0, 1]]
        if not celulas_disponiveis:
            if self._vencedor is None:
                self._mensagem_notf = "IA sem jogadas disponíveis!"
                self._turno_jogador = True
            return

        linha, coluna = random.choice(celulas_disponiveis)
        resultado = self._tabuleiro_jogador.atacar(linha, coluna)

        if resultado is True:
            self._mensagem_notf = f"IA ACERTOU um navio! ({linha},{coluna})! Sua vez."
            if self._tabuleiro_jogador.todos_navios_afundados():
                self._vencedor = "IA"
                self._mensagem_notf = "Todos os seus navios foram afundados! IA venceu o jogo."
                return
        elif resultado is False:
            self._mensagem_notf = f"IA errou o tiro na água. ({linha},{coluna})! Sua vez."
        elif resultado is None:
            self._mensagem_notf = "IA ja tentou atacar posição já atingida."

        if self._vencedor is None:
            self._turno_jogador = True

    # --- MÉTODO MODIFICADO PARA USAR AS NOVAS CORES E ESTILOS ---
    def _desenhar_botões_fim_jogo(self, pos_mouse):
        y_base = self._offset_jogador_y + ALTURA_TABULEIRO_PX + (ALTURA_INTERFACE_JOGO - BOTÃO_ALTURA) // 2 + 30
        largura_total_botoes = (2 * BOTÃO_LARGURA) + 40
        x_inicial = (LARGURA_TELA_PX - largura_total_botoes) // 2

        # --- Botão Jogar Novamente (Azul) ---
        ret_jogar = pygame.Rect(x_inicial, y_base, BOTÃO_LARGURA, BOTÃO_ALTURA)
        cor_jogar = MODERN_BLUE_HOVER_RGB if ret_jogar.collidepoint(pos_mouse) else MODERN_BLUE_RGB
        pygame.draw.rect(self._tela, cor_jogar, ret_jogar, border_radius=25)
        texto_jogar = self._fonte_botao.render("Jogar Novamente", True, TEXTO_BOTAO_FIM_JOGO)
        texto_rect_jogar = texto_jogar.get_rect(center=ret_jogar.center)
        self._tela.blit(texto_jogar, texto_rect_jogar)

        # --- Botão Sair do Jogo (Vermelho) ---
        x_botao_sair = x_inicial + BOTÃO_LARGURA + 40
        ret_sair = pygame.Rect(x_botao_sair, y_base, BOTÃO_LARGURA, BOTÃO_ALTURA)
        cor_sair = DANGER_HOVER_RGB if ret_sair.collidepoint(pos_mouse) else DANGER_COLOR_RGB
        pygame.draw.rect(self._tela, cor_sair, ret_sair, border_radius=25)
        texto_sair = self._fonte_botao.render("Sair do Jogo", True, TEXTO_BOTAO_FIM_JOGO)
        texto_rect_sair = texto_sair.get_rect(center=ret_sair.center)
        self._tela.blit(texto_sair, texto_rect_sair)

        return ret_jogar, ret_sair

    def _desenhar_tudo(self, pos_mouse):
        self._tela.fill(pygame.Color(CINZACLARO))
        self._tabuleiro_jogador.desenhar(self._tela, self._offset_jogador_x, self._offset_jogador_y, mostrar_navios=True)
        mostrar_navios_ia = True if self._vencedor else False
        self._tabuleiro_ia.desenhar(self._tela, self._offset_ia_x, self._offset_ia_y, mostrar_navios=mostrar_navios_ia)

        y_interface = self._offset_jogador_y + ALTURA_TABULEIRO_PX + 5
        pygame.draw.line(self._tela, BRANCO, (0, self._offset_jogador_y + ALTURA_TABULEIRO_PX), (LARGURA_TELA_PX, self._offset_jogador_y + ALTURA_TABULEIRO_PX), 2)

        if not self._jogo_iniciado:
            nome_navio = INFO_NAVIOS.get(self._tamanho_navio_atual, {"nome": "N/A"})["nome"]
            sel_txt = self._fonte.render(f"Navio Selecionado: {nome_navio}({self._tamanho_navio_atual})", True, BRANCO)
            rot_txt = self._fonte.render(f"Girar direção (R): {self._direcao_navio_atual}", True, BRANCO)
            colocados = sorted(list(self._tipos_navios_colocados_jogador))
            nomes_colocados = [INFO_NAVIOS[t]["nome"] for t in colocados if t in INFO_NAVIOS]
            col_txt = self._fonte.render(f"Navios colocados ({len(colocados)}/{MAX_NAVIOS_JOGADOR}): {', '.join(nomes_colocados)}", True, BRANCO)
            self._tela.blit(sel_txt, (10, y_interface)); y_interface += 20
            self._tela.blit(rot_txt, (10, y_interface)); y_interface += 20
            self._tela.blit(col_txt, (10, y_interface)); y_interface += 20
        elif self._jogo_iniciado and not self._vencedor:
            turno_txt = self._fonte.render(f"Vez de jogar: {'Sua vez' if self._turno_jogador else 'Vez da IA'}", True, BRANCO)
            self._tela.blit(turno_txt, (10, y_interface)); y_interface += 25
            if self._turno_jogador:
                inst_txt = self._fonte.render("Clique no tabuleiro da DIREITA para atacar!", True, BRANCO)
                self._tela.blit(inst_txt, (10, y_interface)); y_interface += 20

        if self._mensagem_notf:
            notf_txt = self._fonte.render(f"Notificação: {self._mensagem_notf}", True, BRANCO)
            self._tela.blit(notf_txt, (10, y_interface)); y_interface += 20

        if self._vencedor:
            cor = VERDEVENCEDOR if self._vencedor == "Jogador" else VERMELHO
            fonte_vitoria = pygame.font.SysFont(None, 36)
            vic_txt = fonte_vitoria.render(f"Fim de jogo! O VENCEDOR foi: {self._vencedor.upper()}", True, cor)
            l_txt, a_txt = vic_txt.get_size()
            px = (LARGURA_TELA_PX - l_txt) // 2
            py = self._offset_jogador_y + ALTURA_TABULEIRO_PX + (ALTURA_INTERFACE_JOGO - a_txt) // 4
            self._tela.blit(vic_txt, (px, py))

            self._ret_botao_jogar_novamente, self._ret_botao_sair = self._desenhar_botões_fim_jogo(pos_mouse)
        else:
            self._ret_botao_jogar_novamente = None
            self._ret_botao_sair = None

    def executar(self):
        rodando = True
        while rodando:
            eventos = pygame.event.get()
            pos_mouse = pygame.mouse.get_pos()

            sobre_botoes = self._vencedor and ((self._ret_botao_jogar_novamente and self._ret_botao_jogar_novamente.collidepoint(pos_mouse)) or (self._ret_botao_sair and self._ret_botao_sair.collidepoint(pos_mouse)))
            sobre_tabuleiro_ia_para_atacar = self._jogo_iniciado and not self._vencedor and self._turno_jogador and self._pegar_celula(pos_mouse, self._offset_ia_x, self._offset_ia_y)[0] != -1
            sobre_tabuleiro_jogador_para_posicionar = not self._jogo_iniciado and self._pegar_celula(pos_mouse, self._offset_jogador_x, self._offset_jogador_y)[0] != -1
            if sobre_botoes or sobre_tabuleiro_ia_para_atacar or sobre_tabuleiro_jogador_para_posicionar:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            for evento in eventos:
                if evento.type == pygame.QUIT:
                    rodando = False

                # --- LÓGICA DE FIM DE JOGO MODIFICADA ---
                if self._vencedor:
                    if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                        if self._ret_botao_jogar_novamente and self._ret_botao_jogar_novamente.collidepoint(pos_mouse):
                            self._acao_final = "reiniciar"
                            rodando = False # Termina o loop para reiniciar
                        elif self._ret_botao_sair and self._ret_botao_sair.collidepoint(pos_mouse):
                            self._acao_final = "sair"
                            rodando = False # Termina o loop para sair

                # A lógica de posicionamento de navios permanece a mesma...
                if not self._jogo_iniciado:
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_r:
                            self._direcao_navio_atual = "vertical" if self._direcao_navio_atual == "horizontal" else "horizontal"
                            self._mensagem_notf = f"Direção: {self._direcao_navio_atual}"
                        elif evento.unicode.isdigit():
                            tamanho_desejado = int(evento.unicode)
                            if tamanho_desejado in INFO_NAVIOS:
                                if tamanho_desejado in self._tipos_navios_colocados_jogador:
                                    self._mensagem_notf = f"{INFO_NAVIOS[tamanho_desejado]['nome']} já posicionado!"
                                else:
                                    self._tamanho_navio_atual = tamanho_desejado
                                    self._mensagem_notf = f"Selecionado: {INFO_NAVIOS[tamanho_desejado]['nome']}. Clique no seu tabuleiro para posicionar."
                            else:
                                self._mensagem_notf = f"Tamanho de navio inválido: {tamanho_desejado}. Use 1-{MAX_NAVIOS_JOGADOR}."
                    elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                        linha, coluna = self._pegar_celula(pos_mouse, self._offset_jogador_x, self._offset_jogador_y)
                        if linha != -1:
                            if self._tamanho_navio_atual is None:
                                self._mensagem_notf = "Selecione um navio primeiro (1-6)."
                            elif self._tamanho_navio_atual in self._tipos_navios_colocados_jogador:
                                self._mensagem_notf = f"{INFO_NAVIOS[self._tamanho_navio_atual]['nome']} já foi posicionado. Escolha outro navio (1-{MAX_NAVIOS_JOGADOR})."
                            else:
                                ClasseNavio = INFO_NAVIOS[self._tamanho_navio_atual]["classe"]
                                navio = ClasseNavio(self._direcao_navio_atual)
                                if self._tabuleiro_jogador.colocar_navio(linha, coluna, navio):
                                    self._tipos_navios_colocados_jogador.add(navio.tamanho)
                                    restantes = MAX_NAVIOS_JOGADOR - len(self._tipos_navios_colocados_jogador)
                                    self._mensagem_notf = f"{navio.nome} posicionado! Restam {restantes} navio(s) para posicionar."
                                    if restantes == 0:
                                        self._gerar_navios_ia()
                                        self._jogo_iniciado = True
                                        self._mensagem_notf = "Todos os navios posicionados! Jogo iniciado. Sua vez."
                                    else:
                                        proximo_tamanho = min([t for t in INFO_NAVIOS.keys() if t not in self._tipos_navios_colocados_jogador], default=None)
                                        self._tamanho_navio_atual = proximo_tamanho
                                        if proximo_tamanho:
                                            self._mensagem_notf += f" Selecione o próximo: {INFO_NAVIOS[proximo_tamanho]['nome']}({proximo_tamanho})."
                                else:
                                    self._mensagem_notf = "Você não consegue colocar o navio selecionado nesta posição."
                        else:
                            self._mensagem_notf = "Clique DENTRO do seu tabuleiro para posicionar navios."

                # Lógica de batalha
                elif self._jogo_iniciado and self._vencedor is None:
                    if self._turno_jogador:
                        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                            linha, coluna = self._pegar_celula(pos_mouse, self._offset_ia_x, self._offset_ia_y)
                            if linha != -1:
                                resultado = self._tabuleiro_ia.atacar(linha, coluna)
                                passar_turno = False
                                if resultado is True:
                                    passar_turno = True
                                    if self._tabuleiro_ia.todos_navios_afundados():
                                        self._vencedor = "Jogador"
                                        self._mensagem_notf = "Todos os navios da IA afundados! Você VENCEU!"
                                    else:
                                        self._mensagem_notf = "Você ACERTOU um navio! Vez da IA."
                                elif resultado is False:
                                    self._mensagem_notf = "Você acertou a água. Vez da IA."
                                    passar_turno = True
                                elif resultado is None:
                                    self._mensagem_notf = "Você já atacou esta posição. Tente outra."

                                if passar_turno and self._vencedor is None:
                                    self._turno_jogador = False
                            else:
                                self._mensagem_notf = "Clique no tabuleiro da DIREITA para atacar."

            if self._jogo_iniciado and not self._turno_jogador and self._vencedor is None:
                self._ataque_ia()

            self._desenhar_tudo(pos_mouse)

            pygame.display.flip()
            self._clock.tick(60)

        # --- NOVO: Retorna a ação decidida pelo jogador ---
        return self._acao_final