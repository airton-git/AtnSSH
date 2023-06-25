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
        self.senha = ""
        self.lines = []
        self.error_maps = []

    def test_ip(self):
        while True:
            self.ip = input("\nDigite o endereço IP: ")

            print("\nTestando conectividade ICMP...\n")

            # Executar o comando ping
            ping_process = subprocess.run(
                ['ping', '-n', '4', self.ip], capture_output=True)

            # Verificar o código de retorno do processo
            if ping_process.returncode == 0:
                print("Conectividade ICMP bem-sucedida!\n")
                self.username = input("Digite o nome de usuário: ")
                self.senha = getpass.getpass("Digite a senha: ")
                print('\nTentando conexão SSH com o equipamento remoto...\n')
                break  # Sair do loop se a conectividade ICMP for bem-sucedida
            else:
                print("Falha na conectividade ICMP. Digite o endereço IP novamente.\n")

    def connect(self):

        while True:
            try:
                # Criar uma instância do cliente SSH
                ssh = paramiko.SSHClient()

                # Adicionar a chave do host automaticamente (só é necessário se o host não estiver na lista conhecida)
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                # Conectar ao equipamento remoto
                ssh.connect(self.ip, username=self.username,
                            password=self.senha)

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
        self.lines = output.split("\n")

        # Fechar a conexão SSH
        ssh.close()

        return self.lines

    def arquivo_csv(self):
        # Obter o caminho absoluto do diretório atual
        diretorio_atual = os.getcwd()

        # Concatenar o caminho do diretório com o nome do arquivo
        caminho_arquivo = os.path.join(diretorio_atual, 'error_maps.csv')

        # Abrir o arquivo utilizando o caminho absoluto
        with open(caminho_arquivo, 'r') as file:
            # Criar um leitor CSV
            reader = csv.DictReader(file, delimiter=';')

            # Ler todas as linhas do arquivo e armazená-las em uma lista
            self.error_maps = list(reader)

    def check_errors_int(self):

        print('Verificando erros de interfaces...\n')
        # Variáveis para armazenar as configurações das interfaces

        current_interface = None
        interface_configs = {}

        # Iterar sobre as linhas do output
        for line in self.lines:
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

        # Variável para controlar se algum erro conhecido foi encontrado
        error_found = False

        # Imprimir as configurações das interfaces
        for interface, configs in interface_configs.items():
            print("-" * 40 + '\n')
            print(f"Interface: {interface}\n")
            print("Configurações:\n")

            for config in configs:
                print(config)
            print()

            # Verificar se algum erro conhecido está presente

            for row in self.error_maps:
                error_code = row['Erro']
                interface_column = row['Interface']

                # Verifica se a coluna Interface é igual a 1 para corrigir somente interfaces.
                if interface_column == '1':
                    if error_code in " ".join(configs):
                        print(f"Erro encontrado: {error_code}")
                        print(f"Causa: {row['Cause']}")
                        print(f"Solução: {row['Solution']}")
                        print(
                            f"Comando de solução: {row['Command Solution']}\n")

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
                                    self.ip, username=self.username, password=self.senha)

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
                            self.username = input(
                                "Digite o nome de usuário: ")
                            self.senha = getpass.getpass("Digite a senha: ")

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
            print(
                "\nNão foi encontrado erros nas interfaces.")

    def check_errors(self):
        print("-" * 40)
        print('\nVerificando outros erros...')

        # Verificar se algum erro conhecido está presente
        error_found = False
        for row in self.error_maps:
            error_code = row['Erro']
            interface_column = row['Interface']

            # Verifica se a coluna Interface é igual a 0 para diferenciar da correção das interfaces.
            if interface_column == '0':

                if any(row['Erro'] == line.strip() for line in self.lines):
                    print(f"Erro encontrado: {error_code}")
                    print(f"Causa: {row['Cause']}")
                    print(f"Solução: {row['Solution']}")
                    print(
                        f"Comando de solução: {row['Command Solution']}\n")

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
                            ssh.connect(self.ip, username=self.username,
                                        password=self.senha)

                            break  # Sair do loop se a conexão SSH for estabelecida com sucesso
                        except paramiko.AuthenticationException:
                            print(
                                "Erro de autenticação. Verifique o nome de usuário e senha.")
                        except paramiko.SSHException as e:
                            print(f"Erro na conexão SSH: {str(e)}")
                        except paramiko.socket.error as e:
                            print(f"Erro de socket: {str(e)}")

                        self.test_ip()

                    # Executar os comandos em uma sessão interativa
                    channel = ssh.invoke_shell()

                    # Enviar os comandos um a um
                    channel.send("configure terminal\n")
                    channel.send(f"{command_solution}\n")
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

        # Verificar se nenhum erro conhecido foi encontrado
        if not error_found:
            print("Nenhum outro erro conhecido encontrado.\n")

        print("-" * 40)


def main():
    ssh_client = AtnSSH()
    ssh_client.test_ip()
    ssh_client.connect()
    ssh_client.arquivo_csv()
    ssh_client.check_errors_int()
    ssh_client.check_errors()


# Verificar erros no código
if __name__ == "__main__":
    main()
