# AtnSSH

### Procura erros conhecidos e aplica as correções automaticamente.
O AtnSSH é um script em Python que permite conectar-se a um dispositivo de rede remoto via SSH e analisar sua configuração em busca de erros. Ele auxilia administradores e engenheiros de redes a identificar e resolver rapidamente problemas comuns de configuração, garantindo um desempenho e estabilidade da rede.

### Recursos
Teste de conectividade ICMP: O script realiza um teste de ping ICMP para verificar a conectividade com o dispositivo de destino antes de estabelecer a conexão SSH.

Conexão SSH: Ele estabelece uma conexão SSH com o dispositivo remoto usando o endereço IP, nome de usuário e senha fornecidos.

Análise de configuração: O script recupera a configuração em execução do dispositivo e a analisa em busca de erros ou problemas conhecidos.

Detecção de erros: O script compara a configuração do dispositivo com uma lista pré-definida de padrões de erros conhecidos e destaca qualquer correspondência encontrada.

Resolução de erros: Se um erro for detectado, o script fornece informações detalhadas sobre o erro, incluindo sua causa, solução e os comandos necessários para corrigi-lo. Ele também permite executar os comandos de solução no dispositivo remoto.

Personalização do mapa de erros: É possível personalizar a lista de erros conhecidos e suas soluções correspondentes atualizando o arquivo **error_maps.csv**.

### Começando
Clone o repositório: git clone https://github.com/airton-git/AtnSSH/

Instale as dependências necessárias: pip install paramiko

Execute o script: python AtnSSH.py

Siga as instruções na tela para inserir o endereço IP, nome de usuário e senha do dispositivo de destino.

O script irá analisar a configuração das interfaces exibir os erros encontrador que estão na coluna "**Erro**" do arquivo **error_maps.csv**, ira aplicar o comando que estiver na coluna "**Command Solution**".

![image](https://github.com/airton-git/AtnSSH/assets/82294435/928955d9-8096-4f6a-ac04-5c126e7953b7)



Contribuição
Contribuições são bem-vindas! Se você encontrar um bug ou tiver sugestões de melhorias, abra um problema ou envie uma solicitação de pull.

### Licença
Este projeto está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para obter mais detalhes.
