# Docker Setup Guide

Este guia mostra **como instalar e testar o Docker** em um ambiente Windows.
Ele foi escrito para **quem nunca utilizou Docker antes**.

Ao final deste guia você será capaz de:

* instalar o Docker Desktop
* ativar o WSL (Windows Subsystem for Linux)
* verificar se o Docker está funcionando corretamente

---

# 1. Pré-requisitos

Antes de instalar o Docker, verifique:

* Windows 10 ou Windows 11
* Virtualização habilitada na BIOS
* Permissão de administrador no computador
* Conexão com a internet

---

# 2. Instalar o WSL (Windows Subsystem for Linux)

O Docker utiliza um ambiente Linux interno para rodar containers.
Por isso precisamos instalar o **WSL**.

## Passo 1 — Abrir o PowerShell como administrador

1. Clique no **Menu Iniciar**
2. Digite:

```
powershell
```

3. Clique com o botão direito em **Windows PowerShell**
4. Selecione **Executar como administrador**

---

## Passo 2 — Instalar o WSL

Execute o comando abaixo:

```
wsl --install
```

O Windows iniciará a instalação automática.

Esse processo irá:

* instalar o WSL
* instalar um kernel Linux
* configurar a distribuição padrão

---

## Passo 3 — Reiniciar o computador

Após a instalação, **reinicie o computador**.

Isso é necessário para concluir a configuração.

---

# 3. Instalar o Docker Desktop

## Passo 1 — Baixar o instalador

Acesse o site oficial:

```
https://www.docker.com/products/docker-desktop/
```

Baixe **Docker Desktop for Windows**.

---

## Passo 2 — Executar o instalador

Abra o arquivo baixado e siga o assistente de instalação.

Durante a instalação, mantenha marcada a opção:

```
Use WSL 2 instead of Hyper-V (recommended)
```

Essa configuração permite que o Docker utilize o ambiente Linux criado pelo WSL.

---

## Passo 3 — Reiniciar o computador

Após a instalação, reinicie novamente o computador.

---

# 4. Iniciar o Docker

Após reiniciar:

1. Abra o **Docker Desktop**
2. Aguarde o programa iniciar

Quando estiver funcionando corretamente, você verá uma mensagem semelhante a:

```
Docker Engine running
```

---

# 5. Testar se o Docker está funcionando

Agora vamos executar um container de teste.

## Passo 1 — Abrir o terminal

Abra novamente o **PowerShell**.

---

## Passo 2 — Verificar versão do Docker

Digite:

```
docker --version
```

Se o Docker estiver instalado corretamente, aparecerá algo parecido com:

```
Docker version XX.X.X
```

---

## Passo 3 — Executar container de teste

Agora execute:

```
docker run hello-world
```

O Docker irá:

1. baixar uma imagem de teste
2. criar um container
3. executá-lo

Se tudo estiver funcionando corretamente, aparecerá uma mensagem como:

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

---

# 6. Verificar containers em execução

Para listar containers:

```
docker ps
```

Para listar todos (inclusive os finalizados):

```
docker ps -a
```

---

# 7. Problemas comuns

### Docker não inicia

Verifique se o **WSL está ativo**:

```
wsl -l -v
```

A versão deve ser **2**.

---

### Virtualização desativada

Se aparecer erro de virtualização:

1. reinicie o computador
2. entre na **BIOS**
3. habilite:

```
Virtualization Technology
```

---

# 8. Próximo passo

Agora que o Docker está funcionando, você poderá:

* criar containers
* executar bancos de dados
* rodar aplicações isoladas

No projeto deste repositório, o Docker será utilizado para iniciar um container com **PostgreSQL**, garantindo que o ambiente do banco seja **reproduzível em qualquer máquina**.


'''
docker compose down -v
docker compose up -d
docker ps
Get-Content ../database/schema.sql | docker exec -i catalogo_postgres psql -U admin -d catalogo
docker exec -it catalogo_postgres psql -U admin -d catalogo
'''