import os
import sys
from fuse import FUSE, Operations

class MemoriaFS(Operations):
    def __init__(self):
        self.arquivos = {}
        self.dados = {}

    def getattr(self, caminho):
        """Obtém os atributos do arquivo ou diretório"""
        if caminho == '/':
            return {
                'st_mode': 0o755 | 0o040000,  # diretório
                'st_nlink': 2,
            }
        elif caminho in self.arquivos:
            return {
                'st_mode': 0o666 | 0o100000,  # arquivo regular com permissão de escrita
                'st_nlink': 1,
                'st_size': len(self.dados[caminho]),
            }
        else:
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    def readdir(self, caminho, offset):
        """Lista os arquivos de um diretório"""
        if caminho != '/':
            raise FileNotFoundError("Diretório não encontrado")
        return ['.', '..'] + list(self.arquivos.keys())

    def create(self, caminho, modo, fi=None):
        """Cria um novo arquivo"""
        print(f"📝 Criando arquivo: {caminho}")  # Log para depuração
        self.arquivos[caminho] = {
            'st_mode': modo | 0o100000,  # Garantir que seja um arquivo
            'st_nlink': 1,
        }
        self.dados[caminho] = b''  # Dados do arquivo inicializados como vazio
        return 0

    def open(self, caminho, fi):
        """Abre um arquivo"""
        if caminho not in self.arquivos:
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
        return 0

    def read(self, caminho, tamanho, offset, fi):
        """Lê o conteúdo de um arquivo"""
        if caminho not in self.arquivos:
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
        dados = self.dados[caminho]
        return dados[offset:offset + tamanho]

    def write(self, caminho, dados, offset, fi):
        """Escreve dados em um arquivo"""
        if caminho not in self.arquivos:
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

        conteudo_atual = self.dados.get(caminho, b'')
        novo_conteudo = conteudo_atual[:offset] + dados + conteudo_atual[offset + len(dados):]
        self.dados[caminho] = novo_conteudo

        print(f"✍️ Escrevendo {len(dados)} bytes em {caminho}")  # Log para depuração
        return len(dados)

    def unlink(self, caminho):
        """Deleta um arquivo"""
        if caminho in self.arquivos:
            del self.arquivos[caminho]
            del self.dados[caminho]
            print(f"🗑️ Arquivo deletado: {caminho}")  # Log para depuração
            return 0
        else:
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

def main(caminho_montagem):
    if not os.path.exists(caminho_montagem):
        os.makedirs(caminho_montagem)
    
    print(f"📂 Montando sistema de arquivos em {caminho_montagem}")
    fuse = FUSE(MemoriaFS(), caminho_montagem, foreground=True, nothreads=True, ro=False)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Erro: Você deve fornecer um diretório de montagem!")
        print("Uso: python meu_fs.py C:\\meu_fs")
        sys.exit(1)

    caminho_montagem = sys.argv[1]
    print(f"📂 Diretório de montagem recebido: {caminho_montagem}")

    try:
        main(caminho_montagem)
    except Exception as e:
        print(f"Erro ao montar o sistema de arquivos: {e}")
        sys.exit(1)

