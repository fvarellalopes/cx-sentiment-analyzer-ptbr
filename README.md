# CX Ticket Sentiment Analyzer (PT-BR)

Projeto de análise de sentimento supervisionada aplicado a **tickets de atendimento ao cliente em português**, com foco em apoiar times de Customer Experience (CX) a priorizar atendimentos e entender o risco de churn a partir de texto livre.

---

## Visão geral

Este repositório contém:

- Um **notebook** de modelagem (`cx_ticket_sentiment_modeling.ipynb`) que prepara os dados, treina e avalia um modelo de sentimento para tickets de CX em PT-BR. [file:138]  
- Um **app Streamlit** (`app.py`) que carrega o modelo treinado e fornece uma interface simples para analistas e gestores testarem tickets reais e visualizarem um histórico de análises. [file:96]  

O objetivo não é só classificar como positivo/negativo, mas aproximar a saída do modelo da linguagem de negócio de CX: **risco de churn, nível de satisfação e leitura acionável**.

---

## Problema de negócio

Times de CX recebem diariamente dezenas ou centenas de tickets em texto livre (chat, e-mail, formulários), e nem sempre conseguem:

- Identificar rapidamente quais tickets têm maior **risco de churn**.
- Diferenciar feedbacks claramente positivos de mensagens **neutras ou “mornas”**.
- Ter uma visão consolidada da **“temperatura de satisfação”** em um período.

Este projeto propõe um MVP de produto que:

- Classifica cada ticket como **Bom**, **Ruim** ou **Neutro**.
- Associa uma **confiança** ao rótulo.
- Gera uma **leitura de CX** curta, explicando o resultado em termos de risco e próximos passos.

---

## Abordagem técnica

### Modelagem

No notebook de modelagem é treinado um pipeline de NLP em Python usando scikit-learn: [file:138]

- **Vetorização de texto** com `TfidfVectorizer`, em português, usando:
  - n-gramas de 1 a 2 palavras (`ngram_range=(1, 2)`).
  - `min_df=2` para ignorar termos extremamente raros.
- **Classificação** com `LogisticRegression`:
  - `class_weight='balanced'` para lidar melhor com desequilíbrios entre classes.
  - `max_iter=1000` para garantir convergência do otimizador.

O modelo é treinado para distinguir entre tickets **positivos (1)** e **negativos (0)** a partir de frases rotuladas manualmente. [file:138]

Após o treino, o pipeline é serializado em disco (ex.: `tfidf_logreg_model.pkl`) usando `joblib` para ser consumido pelo app Streamlit.

### Métricas

O modelo é avaliado com métricas padrão de classificação (accuracy, precision, recall, f1) em um conjunto de validação separado. [file:138]

Em vez de otimizar apenas um número, a análise do desempenho considera:

- Exemplos onde o modelo erra (ex.: frases negativas classificadas como positivas).
- O impacto desses erros na operação de CX.
- A necessidade de uma **classe Neutro** baseada em limiar de confiança para reduzir falsos positivos/negativos na ponta.

---

## App Streamlit

O arquivo `app.py` implementa uma interface simples em Streamlit para testar o modelo com tickets reais. [file:96]

### Funcionalidades atuais

- **Entrada de ticket**  
  Caixa de texto onde o usuário digita a frase do cliente (ex.: “Atendente demorou para responder no chat”).

- **Predição de sentimento**  
  Ao clicar em **“Analisar sentimento”**, o app:
  - Gera as probabilidades de cada classe com `predict_proba`.
  - Seleciona o rótulo previsto (`Bom` para positivo, `Ruim` para negativo). [file:96]  
  - Calcula a confiança máxima (`max_prob`).

- **Classe Neutro baseada em confiança**  
  Foi adotada uma regra de negócio para tratar incerteza: [file:96]  
  - Se `max_prob` for menor que um limiar (atualmente `0.6`), o ticket é classificado como **Neutro**.  
  - Isso representa frases mais **informativas/mornas**, sem sinal forte de satisfação ou frustração, reduzindo a chance de interpretações erradas pelo time de CX.

- **Leitura de CX em linguagem de negócio**  
  Para cada ticket, o app gera uma leitura curta, por exemplo: [file:96]  
  - **Bom**: “Cliente provavelmente satisfeito, baixo risco de churn.”  
  - **Ruim**: “Cliente possivelmente frustrado, maior risco de churn; priorizar follow-up.”  
  - **Neutro**: “Baixo sinal de emoção; frase informativa, sem indício forte de satisfação ou frustração.”

- **Histórico de tickets analisados**  
  O app mantém, em `st.session_state`, um **DataFrame** com as colunas: [file:96]  
  - `Texto do cliente`  
  - `Sentimento identificado` (rótulo + confiança)  
  - `Leitura de CX`  

- **Relatório consolidado (últimos 20)**  
  Um botão permite visualizar uma tabela com os **últimos 20 tickets analisados**, simulando uma visão rápida para um analista/gestor acompanhar a “temperatura” recente dos atendimentos. [file:96]

---

## Como rodar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/fvarellalopes/cx-sentiment-analyzer-ptbr.git
cd cx-sentiment-analyzer-ptbr
```

### 2. Opção A: Rodar com Docker (recomendado)

#### Pré-requisitos
- Docker instalado ([instruções de instalação](https://docs.docker.com/get-docker/))
- Docker Compose instalado (geralmente incluído com Docker Desktop)

#### Usando Docker Compose (mais fácil)

```bash
docker-compose up
```

Isso irá:
- Construir a imagem Docker automaticamente
- Iniciar o container
- Expor a aplicação na porta 8501

Acesse: `http://localhost:8501`

Para parar o container:
```bash
docker-compose down
```

#### Usando Docker diretamente

```bash
# Construir a imagem
docker build -t cx-sentiment-analyzer-ptbr .

# Executar o container
docker run -p 8501:8501 cx-sentiment-analyzer-ptbr
```

Acesse: `http://localhost:8501`

### 2. Opção B: Rodar localmente com Python

#### 2.1. Criar ambiente e instalar dependências

Recomenda-se usar Python 3.10+.

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2.2. Treinar o modelo (opcional)

Se quiser refazer o treino:

1. Abra o notebook `cx_ticket_sentiment_modeling.ipynb` em Jupyter/VSCode. [file:138]  
2. Execute as células até a etapa de salvamento do modelo (`joblib.dump(...)`).  
3. Confirme que o arquivo `tfidf_logreg_model.pkl` foi gerado na raiz do projeto ou no caminho esperado pelo `app.py`.

#### 2.3. Rodar o app Streamlit

```bash
streamlit run app.py
```

Depois, acesse o link gerado (geralmente `http://localhost:8501`) no navegador.

---

## Deployment em servidor

### Usando Docker em servidor de produção

#### 1. Em um servidor Linux (Ubuntu/Debian)

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clonar o repositório
git clone https://github.com/fvarellalopes/cx-sentiment-analyzer-ptbr.git
cd cx-sentiment-analyzer-ptbr

# Construir e executar
docker-compose up -d
```

O parâmetro `-d` executa o container em segundo plano (detached mode).

#### 2. Verificar logs

```bash
docker-compose logs -f
```

#### 3. Gerenciar o container

```bash
# Parar o container
docker-compose stop

# Reiniciar o container
docker-compose restart

# Remover o container
docker-compose down
```

#### 4. Atualizar a aplicação

```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```

### Configurações de produção

Para executar em produção, considere:

- **Proxy reverso**: Use Nginx ou Caddy na frente da aplicação
- **SSL/HTTPS**: Configure certificados SSL para conexões seguras
- **Firewall**: Abra apenas as portas necessárias (80, 443)
- **Monitoramento**: Configure logs e alertas
- **Backup**: Faça backup regular dos dados e configurações

### Exemplo de configuração Nginx

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Roadmap (próximos passos)

As próximas melhorias planejadas para evoluir este MVP em direção a um produto mais completo para CX são:

- **Configurações de limiar de Neutro**  
  - Adicionar uma aba ou painel de “Configurações” no app para permitir que o usuário ajuste o limiar de confiança (ex.: 0.5–0.9) sem alterar o código.

- **Visão de gestor / resumo de saúde**  
  - Criar um mini resumo com contagem de **Bom / Neutro / Ruim** nos últimos N tickets.  
  - Expor essa visão no topo da tela ou em uma aba específica para facilitar o acompanhamento da “temperatura” de satisfação.

- **Termômetro de satisfação e plano de ação**  
  - Construir um “termômetro” simples (ex.: verde, amarelo, vermelho) com base na distribuição de sentimentos e níveis de confiança.  
  - Associar a cada faixa um **texto de interpretação** e sugestões de ação em CX (ex.: reforçar canais de feedback, priorizar contato com clientes detratores).

Essas evoluções vão aproximar o projeto de um **produto de suporte à decisão para CX**, indo além de um experimento isolado de machine learning.

---

## Inspiração e limitações

- Modelo treinado em um conjunto reduzido de tickets em português, focado em um tipo de atendimento específico, o que limita a generalização para outros contextos. [file:138]  
- Não há tratamento específico para sarcasmo, ironia ou contexto multicanal.  
- O foco deste projeto é didático e de portfólio: demonstrar a capacidade de **definir problema de negócio, treinar um modelo simples e empacotar isso em um app utilizável por times de CX**.

Sinta-se à vontade para abrir issues ou sugestões de melhoria, especialmente em relação à UX do app, novas regras de negócio de CX e ampliação do conjunto de dados.


