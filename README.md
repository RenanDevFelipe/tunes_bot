# tunes_bot
Tunes Bot é um bot para Discord que toca músicas do YouTube diretamente em canais de voz.

## Funcionalidades

- Conectar a um canal de voz
- Tocar músicas do YouTube
- Pausar e retomar músicas
- Desconectar do canal de voz

## Pré-requisitos

- Python 3.8 ou superior
- pip

## Instalação

1. Clone este repositório:

```bash
git clone https://github.com/seu-usuario/tunes_bot.git
cd tunes_bot
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Adicione seu token de bot no arquivo `tunes_bot.py` substituindo `'seu_token_aqui'`:

```python
DISCORD_TOKEN = 'seu_token_aqui'
```

4. Execute o bot:

```bash
python tunes_bot.py
```



#Comandos


- `!join`: Conecta o bot ao canal de voz do usuário.
- `!leave`: Desconecta o bot do canal de voz.
- `!play <url ou termo de busca>`: Toca uma música do YouTube.
- `!pause`: Pausa a música atual.
- `!resume`: Retoma a música pausada.
- `!stop`: Para a música e desconecta o bot do canal de voz.

