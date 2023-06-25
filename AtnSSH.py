import subprocess
import paramiko
import getpass
import csv
import os
import time


class AtnSSH:
    def __init__(self):
        self.ip = ""
        self.username = ""

    def test_ip(self):
        while True:
            self.ip = input("Digite o endereço IP: ")

            print("\nTestando conectividade ICMP...\n")

            # Executar o comando ping
            ping_process = subprocess.run(
                ['ping', '-n', '4', self.ip], capture_output=True)

            # Verificar o código de retorno do processo
            if ping_process.returncode == 0:
                print("Conectividade ICMP bem-sucedida!\n")
                break  # Sair do loop se a conectividade ICMP for bem-sucedida
            else:
                print("Falha na conectividade ICMP. Digite o endereço IP novamente.\n")

    def connect(self):
        self.username = input("Digite o nome de usuário: ")
        senha = getpass.getpass("Digite a senha: ")

        while True:
            try:
                # Criar uma instância do cliente SSH
                ssh = paramiko.SSHClient()

                # Adicionar a chave do host automaticamente (só é necessário se o host não estiver na lista conhecida)
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                # Conectar ao equipamento remoto
                ssh.connect(self.ip, username=self.username, password=senha)
                break  # Sair do loop se a conexão SSH for estabelecida com sucesso
            except paramiko.AuthenticationException:
                print("Erro de autenticação. Digite os dados novamente!")
                AtnSSH.test_ip(self)
            except paramiko.SSHException as e:
                print(f"Erro na conexão SSH: {str(e)}")
                AtnSSH.test_ip(self)
            except paramiko.socket.error as e:
                print(f"Erro de socket: {str(e)}")
                AtnSSH.test_ip(self)

        # Executar um comando no equipamento remoto
        stdin, stdout, stderr = ssh.exec_command('show running-config')

        # Ler a saída do comando
        output = stdout.read().decode('utf-8')

        # Separar as linhas do output
        lines = output.split("\n")

        # Fechar a conexão SSH
        ssh.close()

        return lines

    def check_errors(self, lines):
        # Variáveis para armazenar as configurações das interfaces
        current_interface = None
        interface_configs = {}

        # Iterar sobre as linhas do output
        for line in lines:
            if line.startswith("interface "):
                # Nova interface encontrada
                current_interface = line.split("interface ")[1]
                interface_configs[current_interface] = []
            elif line.startswith("!"):
                # Fim das configurações da interface atual
                current_interface = None
            elif current_interface is not None:
                # Adicionar a linha à configuração da interface atual
                interface_configs[current_interface].append(line.strip())

        # Obter o caminho absoluto do diretório atual
        diretorio_atual = os.getcwd()

        # Concatenar o caminho do diretório com o nome do arquivo
        caminho_arquivo = os.path.join(diretorio_atual, 'error_maps.csv')

        # Abrir o arquivo utilizando o caminho absoluto
        with open(caminho_arquivo, 'r') as file:
            # Criar um leitor CSV
            reader = csv.DictReader(file, delimiter=';')

            # Ler todas as linhas do arquivo e armazená-las em uma lista
            error_maps = list(reader)

        # Variável para controlar se algum erro conhecido foi encontrado
        error_found = False

        # Imprimir as configurações das interfaces
        for interface, configs in interface_configs.items():
            print("-" * 40+'\n')
            print(f"Interface: {interface}\n")
            print("Configurações:\n")

            for config in configs:
                print(config)
            print()

            # Verificar se algum erro conhecido está presente
            for row in error_maps:
                error_code = row['Erro']
                error_description = row['Cause']
                if error_code in " ".join(configs):
                    print(f"Erro encontrado: {error_code}")
                    print(f"Causa: {row['Cause']}")
                    print(f"Solução: {row['Solution']}")
                    print(f"Comando de solução: {row['Command Solution']}\n")

                    # Executar o comando de correção
                    command_solution = row['Command Solution']

                    while True:
                        try:
                            # Criar uma instância do cliente SSH
                            ssh = paramiko.SSHClient()

                            # Adicionar a chave do host automaticamente (só é necessário se o host não estiver na lista conhecida)
                            ssh.set_missing_host_key_policy(
                                paramiko.AutoAddPolicy())

                            # Conectar ao equipamento remoto
                            ssh.connect(
                                self.ip, username=self.username, password=senha)
                            break  # Sair do loop se a conexão SSH for estabelecida com sucesso
                        except paramiko.AuthenticationException:
                            print(
                                "Erro de autenticação. Verifique o nome de usuário e senha.")
                        except paramiko.SSHException as e:
                            print(f"Erro na conexão SSH: {str(e)}")
                        except paramiko.socket.error as e:
                            print(f"Erro de socket: {str(e)}")

                        print(
                            "Erro ao conectar ao equipamento. Digite as informações novamente.\n")
                        self.username = input("Digite o nome de usuário: ")
                        senha = getpass.getpass("Digite a senha: ")

                    # Executar os comandos em uma sessão interativa
                    channel = ssh.invoke_shell()

                    # Enviar os comandos um a um
                    channel.send("configure terminal\n")
                    channel.send(f"interface {interface}\n")
                    channel.send(f"{command_solution}\n")
                    channel.send("exit\n")
                    channel.send("exit\n")
                    channel.send("write\n")

                    # Aguardar alguns segundos para garantir que a configuração seja salva
                    time.sleep(5)

                    # Ler a saída do canal para verificar se houve algum erro
                    output = channel.recv(4096).decode('utf-8')

                    # Verificar se houve algum erro na saída
                    if "Error" in output or "Invalid" in output:
                        print(
                            "Erro ao executar os comandos. Verifique a saída para mais informações.")
                        print("Saída:")
                        print(output)
                    else:
                        print("Comandos executados com sucesso.")

                    ssh.close()

                    # Definir a flag de erro encontrado como True
                    error_found = True

        print("-" * 40)

        # Verificar se nenhum erro conhecido foi encontrado
        if not error_found:
            print("\nNenhum erro conhecido encontrado nas configurações.\n")


# Instanciar a classe AtnSSH
atn_ssh = AtnSSH()

# Testar a conectividade ICMP
atn_ssh.test_ip()

# Conectar ao equipamento remoto
lines = atn_ssh.connect()

# Verificar erros nas configurações
atn_ssh.check_errors(lines)
