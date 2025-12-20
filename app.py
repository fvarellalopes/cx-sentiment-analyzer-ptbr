import streamlit as st
import pandas as pd
import os
from typing import Tuple, Dict

# ----- Configuração da página -----
st.set_page_config(
    page_title="CX Sentiment Analyzer PT-BR",
    page_icon="📊",
    layout="wide"
)

# ----- Léxico PT-BR expandido -----
ptbr_positive = [
    "ótimo", "excelente", "perfeita", "perfeito", "rápido", "eficiente",
    "obrigado", "obrigada", "educado", "educada", "atencioso", "atenciosa",
    "resolvido", "resolvida", "funciona", "recomendo", "nota 10", "maravilhoso",
    "satisfeito", "satisfeita", "bom", "boa", "adorei", "amei", "legal",
    "prático", "fácil", "simples", "claro", "clara", "completo", "completa"
]

ptbr_negative = [
    "grosseiro", "grosseira", "demora", "demorado", "demorada", "travando",
    "erro", "ruim", "inaceitável", "urgente", "sem resposta", "reembolso",
    "atraso", "atrasada", "atrasado", "demorou", "espera", "aguardando",
    "não funciona", "péssimo", "péssima", "horrível", "frustrado", "frustrada",
    "decepcionado", "decepcionada", "problema", "falha", "defeito", "cancelar",
    "insatisfeito", "insatisfeita", "chateado", "chateada", "irritado", "irritada"
]

def sentiment_ptbr(text: str) -> Tuple[float, float]:
    """
    Calcula o sentimento do texto usando léxico PT-BR.
    
    Args:
        text: Texto do ticket
        
    Returns:
        Tuple com (probabilidade_positiva, score_normalizado)
    """
    if not text or not text.strip():
        return 0.5, 0.0
    
    text_lower = text.lower()
    # Remove punctuation and split into words
    import re
    words = re.findall(r'\b\w+\b', text_lower)
    
    # Conta palavras positivas e negativas (whole word matching)
    # Check if the keyword appears as a complete word in the text
    pos_count = sum(1 for keyword in ptbr_positive if keyword in words)
    neg_count = sum(1 for keyword in ptbr_negative if keyword in words)
    
    # Score normalizado
    total_count = pos_count + neg_count
    if total_count == 0:
        # Sem palavras de sentimento detectadas
        return 0.5, 0.0
    
    # Probabilidade positiva (0 a 1)
    pos_prob = pos_count / total_count
    
    # Score normalizado (-1 a 1)
    score_norm = (pos_count - neg_count) / max(1, len(words))
    
    return pos_prob, score_norm

def classify_sentiment(pos_prob: float, confidence_threshold: float = 0.6) -> Tuple[str, float]:
    """
    Classifica o sentimento com base na probabilidade e limiar de confiança.
    
    Args:
        pos_prob: Probabilidade positiva (0 a 1)
        confidence_threshold: Limiar de confiança para classificação como Neutro
        
    Returns:
        Tuple com (label, confidence)
    """
    if pos_prob > 0.5:
        # Positivo
        confidence = pos_prob
        if confidence >= confidence_threshold:
            return "Bom", confidence
        else:
            return "Neutro", confidence
    elif pos_prob < 0.5:
        # Negativo
        confidence = 1 - pos_prob
        if confidence >= confidence_threshold:
            return "Ruim", confidence
        else:
            return "Neutro", confidence
    else:
        # Exatamente 0.5 ou sem sinal
        return "Neutro", 0.5

def get_cx_reading(label: str, confidence: float) -> str:
    """
    Gera leitura de CX em linguagem de negócio.
    
    Args:
        label: Sentimento identificado (Bom, Ruim, Neutro)
        confidence: Confiança da predição
        
    Returns:
        Texto de leitura de CX
    """
    readings = {
        "Bom": "Cliente provavelmente satisfeito, baixo risco de churn. Considere solicitar feedback público ou case de sucesso.",
        "Ruim": "Cliente possivelmente frustrado, maior risco de churn; priorizar follow-up. Ação recomendada: contato proativo em até 24h.",
        "Neutro": "Baixo sinal de emoção; frase informativa, sem indício forte de satisfação ou frustração. Monitorar evolução."
    }
    return readings.get(label, "Leitura não disponível.")

# ----- Inicializar estado da sessão -----
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=[
        "Texto do cliente",
        "Sentimento identificado",
        "Leitura de CX"
    ])

if "confidence_threshold" not in st.session_state:
    st.session_state.confidence_threshold = 0.6

# ----- Interface principal -----
st.title("📊 CX Sentiment Analyzer PT-BR")
st.markdown("**Análise de sentimento para tickets de atendimento em português**")
st.markdown("---")

# ----- Sidebar com configurações -----
with st.sidebar:
    st.header("⚙️ Configurações")
    confidence_threshold = st.slider(
        "Limiar de confiança para Neutro",
        min_value=0.5,
        max_value=0.9,
        value=st.session_state.confidence_threshold,
        step=0.05,
        help="Valores abaixo deste limiar serão classificados como Neutro"
    )
    st.session_state.confidence_threshold = confidence_threshold
    
    st.markdown("---")
    st.markdown("### 📈 Estatísticas da Sessão")
    if len(st.session_state.history) > 0:
        total = len(st.session_state.history)
        bom = sum(1 for s in st.session_state.history["Sentimento identificado"] if "Bom" in s)
        ruim = sum(1 for s in st.session_state.history["Sentimento identificado"] if "Ruim" in s)
        neutro = sum(1 for s in st.session_state.history["Sentimento identificado"] if "Neutro" in s)
        
        st.metric("Total analisados", total)
        st.metric("Bom", f"{bom} ({bom/total*100:.0f}%)")
        st.metric("Ruim", f"{ruim} ({ruim/total*100:.0f}%)")
        st.metric("Neutro", f"{neutro} ({neutro/total*100:.0f}%)")
        
        # Termômetro de satisfação
        if ruim / total > 0.4:
            st.error("🌡️ Temperatura: ALTA (Atenção necessária)")
        elif ruim / total > 0.2:
            st.warning("🌡️ Temperatura: MÉDIA (Monitorar)")
        else:
            st.success("🌡️ Temperatura: BOA (Situação estável)")
    else:
        st.info("Nenhum ticket analisado ainda")
    
    if st.button("🗑️ Limpar histórico"):
        st.session_state.history = pd.DataFrame(columns=[
            "Texto do cliente",
            "Sentimento identificado",
            "Leitura de CX"
        ])
        st.rerun()

# ----- Área de análise -----
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Entrada de Ticket")
    ticket = st.text_area(
        "Digite o texto do atendimento:",
        value="Atendente demorou para responder no chat",
        height=150,
        help="Insira o texto do ticket do cliente para análise"
    )
    
    analyze_button = st.button("🔍 Analisar sentimento", type="primary", use_container_width=True)

with col2:
    st.subheader("ℹ️ Sobre o Sistema")
    st.info(
        "Este sistema analisa o sentimento de tickets de CX em português, "
        "classificando-os como **Bom**, **Ruim** ou **Neutro** com base em "
        "um léxico especializado para atendimento ao cliente."
    )

# ----- Processamento da análise -----
if analyze_button:
    if not ticket or not ticket.strip():
        st.error("⚠️ Por favor, insira um texto válido para análise.")
    else:
        with st.spinner("Analisando sentimento..."):
            # Calcula sentimento
            pos_prob, score = sentiment_ptbr(ticket)
            label, confidence = classify_sentiment(pos_prob, confidence_threshold)
            cx_reading = get_cx_reading(label, confidence)
            
            # Exibe resultados
            st.markdown("---")
            st.subheader("📊 Resultado da Análise")
            
            # Métricas principais
            metric_cols = st.columns(3)
            with metric_cols[0]:
                if label == "Bom":
                    st.success(f"### ✅ {label}")
                elif label == "Ruim":
                    st.error(f"### ❌ {label}")
                else:
                    st.warning(f"### ⚠️ {label}")
            
            with metric_cols[1]:
                st.metric("Confiança", f"{confidence:.0%}")
            
            with metric_cols[2]:
                st.metric("Score", f"{score:.3f}")
            
            # Leitura de CX
            st.markdown("### 💼 Leitura de CX")
            if label == "Bom":
                st.success(cx_reading)
            elif label == "Ruim":
                st.error(cx_reading)
            else:
                st.info(cx_reading)
            
            # Adiciona ao histórico
            new_entry = pd.DataFrame({
                "Texto do cliente": [ticket],
                "Sentimento identificado": [f"{label} ({confidence:.0%})"],
                "Leitura de CX": [cx_reading]
            })
            st.session_state.history = pd.concat(
                [new_entry, st.session_state.history],
                ignore_index=True
            )

# ----- Histórico de tickets -----
st.markdown("---")
st.subheader("📋 Histórico de Análises")

if len(st.session_state.history) > 0:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Total de tickets analisados:** {len(st.session_state.history)}")
    with col2:
        show_last_20 = st.checkbox("Mostrar últimos 20", value=True)
    
    # Exibe histórico
    if show_last_20:
        display_df = st.session_state.history.head(20)
        st.markdown("*Exibindo os 20 tickets mais recentes*")
    else:
        display_df = st.session_state.history
        st.markdown("*Exibindo todos os tickets*")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Opção de download (lazy generation)
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')
    
    csv = convert_df_to_csv(st.session_state.history)
    st.download_button(
        label="📥 Baixar histórico completo (CSV)",
        data=csv,
        file_name="historico_analise_sentimento.csv",
        mime="text/csv"
    )
else:
    st.info("💡 Nenhum ticket analisado ainda. Insira um texto acima e clique em 'Analisar sentimento' para começar.")

# ----- Footer -----
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    CX Sentiment Analyzer PT-BR | Desenvolvido para análise de tickets de atendimento ao cliente
    </div>
    """,
    unsafe_allow_html=True
)
