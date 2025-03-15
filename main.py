import pygame
import random
import sqlite3
import datetime

# Inicializa o Pygame
pygame.init()

# Constantes
LARGURA, ALTURA = 800, 600
FPS = 60

# Cores
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)
PRETO = (0, 0, 0)

# Configuração do banco de dados
conn = sqlite3.connect("pontuacoes.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS pontuacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        pontuacao INTEGER NOT NULL,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

# Criar a tela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo 2D - Desafio!")

# Fonte
fonte = pygame.font.Font(None, 36)


def salvar_pontuacao(nome_jogador, pontuacao_final):
    # Ajuste para o fuso horário (exemplo para UTC-3)
    hora_local = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
    # Converter o objeto datetime para string para evitar o DeprecationWarning
    hora_local_str = hora_local.strftime('%Y-%m-%d %H:%M:%S.%f%z')
    cursor.execute("INSERT INTO pontuacoes (nome, pontuacao, data) VALUES (?, ?, ?)",
                   (nome_jogador, pontuacao_final, hora_local_str))
    conn.commit()


def obter_melhores_pontuacoes():
    cursor.execute("SELECT nome, pontuacao, data FROM pontuacoes ORDER BY pontuacao DESC LIMIT 10")
    return cursor.fetchall()


def centralizar_texto(texto, fonte, tela):
    # Calcula a posição para centralizar o texto na tela
    largura_texto = texto.get_width()
    altura_texto = texto.get_height()
    x = (LARGURA - largura_texto) // 2
    y = (ALTURA - altura_texto) // 2
    return x, y


def mostrar_game_over(pontuacao_final):
    nome_jogador = ""
    game_over_ativo = True
    while game_over_ativo:
        tela.fill(BRANCO)

        # Texto de game over
        texto_game_over = fonte.render(f"Fim de jogo! Pontuação: {pontuacao_final}", True, VERMELHO)
        x, y = centralizar_texto(texto_game_over, fonte, tela)
        tela.blit(texto_game_over, (x, y - 50))  # Um pouco acima do centro

        # Texto de digitar nome
        texto_nome = fonte.render(f"Digite seu nome: {nome_jogador}", True, PRETO)
        x, y = centralizar_texto(texto_nome, fonte, tela)
        tela.blit(texto_nome, (x, y))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN and nome_jogador:
                    salvar_pontuacao(nome_jogador, pontuacao_final)
                    game_over_ativo = False
                elif evento.key == pygame.K_BACKSPACE:
                    nome_jogador = nome_jogador[:-1]
                elif len(nome_jogador) < 10:
                    nome_jogador += evento.unicode

    # Retorna ao menu inicial
    mostrar_menu()


def mostrar_menu():
    menu_ativo = True
    while menu_ativo:
        tela.fill(BRANCO)

        # Texto do menu
        texto_titulo = fonte.render("Pressione ESPAÇO para Jogar ou S para Ver Pontuações", True, PRETO)
        x, y = centralizar_texto(texto_titulo, fonte, tela)
        tela.blit(texto_titulo, (x, y))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    menu_ativo = False
                    iniciar_jogo()
                if evento.key == pygame.K_s:
                    mostrar_pontuacoes()


def mostrar_pontuacoes():
    pontuacoes = obter_melhores_pontuacoes()
    pontuacoes_ativas = True
    while pontuacoes_ativas:
        tela.fill(BRANCO)

        # Texto do título
        texto_titulo = fonte.render("Top 10 Pontuações", True, PRETO)
        x, y = centralizar_texto(texto_titulo, fonte, tela)
        tela.blit(texto_titulo, (x, 50))  # Título no topo

        # Exibe as pontuações abaixo do título
        y_offset = 100
        for nome, pontuacao, data in pontuacoes:
            # Parse da data utilizando o formato que contempla frações e fuso horário
            data_formatada = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S.%f%z')
            texto_pontuacao = fonte.render(
                f"{data_formatada.strftime('%d/%m/%Y %H:%M')} - {nome}: {pontuacao}", True, PRETO)
            tela.blit(texto_pontuacao, (LARGURA // 2 - 175, y_offset))
            y_offset += 30

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return


def iniciar_jogo():
    # Configuração do jogador
    largura_jogador = 50
    altura_jogador = 50
    x_jogador = (LARGURA - largura_jogador) // 2
    y_jogador = ALTURA - altura_jogador - 10
    velocidade_jogador = 5

    # Configuração dos inimigos
    largura_inimigo = 50
    altura_inimigo = 50
    inimigos = []
    velocidade_inimigo = 3
    pontuacao = 0

    relogio = pygame.time.Clock()
    jogo_ativo = True

    def criar_inimigo():
        x = random.randint(0, LARGURA - largura_inimigo)
        y = random.randint(-100, -50)
        inimigos.append([x, y])

    while jogo_ativo:
        tela.fill(BRANCO)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Movimento do jogador
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] and x_jogador > 0:
            x_jogador -= velocidade_jogador
        if teclas[pygame.K_RIGHT] and x_jogador < LARGURA - largura_jogador:
            x_jogador += velocidade_jogador

        # Criar inimigos ao longo do tempo
        if random.randint(1, 30) == 1:
            criar_inimigo()

        # Movimento dos inimigos
        for inimigo in inimigos:
            inimigo[1] += velocidade_inimigo
            if inimigo[1] > ALTURA:
                inimigos.remove(inimigo)
                pontuacao += 1  # Incrementa pontuação

        # Detecção de colisão
        for inimigo in inimigos:
            if (x_jogador < inimigo[0] + largura_inimigo and
                x_jogador + largura_jogador > inimigo[0] and
                y_jogador < inimigo[1] + altura_inimigo and
                y_jogador + altura_jogador > inimigo[1]):
                jogo_ativo = False

        # Aumenta gradativamente a dificuldade
        velocidade_inimigo += 0.001

        # Desenhar jogador
        pygame.draw.rect(tela, AZUL, (x_jogador, y_jogador, largura_jogador, altura_jogador))

        # Desenhar inimigos
        for inimigo in inimigos:
            pygame.draw.rect(tela, VERMELHO, (inimigo[0], inimigo[1], largura_inimigo, altura_inimigo))

        # Exibir pontuação atual
        texto_pontuacao = fonte.render(f"Pontuação: {pontuacao}", True, PRETO)
        tela.blit(texto_pontuacao, (10, 10))

        pygame.display.update()
        relogio.tick(FPS)

    # Exibe tela de game over
    mostrar_game_over(pontuacao)


# Inicia o menu principal
mostrar_menu()

# Fecha a conexão com o banco de dados ao sair
conn.close()
pygame.quit()
