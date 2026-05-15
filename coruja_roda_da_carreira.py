import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Configuração da página web
st.set_page_config(
    page_title="Coruja - Roda da Carreira",
    page_icon="🦉",
    layout="wide"
)

# Injeção de CSS para forçar o visual em tons de azul escuro
st.markdown("""
    <style>
    .stApp {
        background-color: #1a2a3a;
        color: #ffffff;
    }
    h1, h2, h3, label, .stMarkdown {
        color: #ffffff !important;
    }
    .stSlider > label {
        font-weight: bold;
        color: #00ecff !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Título do Aplicativo
st.title("🦉 Coruja - Roda da Carreira")
st.subheader("Avalie cada pilar de 0 a 10 para analisar sua jornada:")
st.markdown("---")

# 3. Definição dos Pilares baseados na dinâmica
pilares = [
    "Satisfação", "Remuneração", "Propósito", "Perspectiva",
    "Equilíbrio", "Relações Interpessoais", "Reconhecimento", "Desenvolvimento"
]

# 4. Divisão da Tela em Duas Colunas (Controles vs Gráfico)
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("### 📋 Suas Notas")
    valores = {}
    
    # Sliders para o usuário definir as notas
    for pilar in pilares:
        valores[pilar] = st.slider(pilar, min_value=0, max_value=10, value=5, step=1)
    
    st.markdown("### 🎨 Personalização")
    # Paleta de cores para pintar as áreas da roda
    cor_selecionada = st.color_picker("Escolha a cor para pintar a sua Roda", "#3498db")

# 5. Construção do Gráfico Radar (Matplotlib)
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
fig.patch.set_facecolor('#1a2a3a') # Fundo de fora do gráfico
ax.set_facecolor('#243746')       # Fundo de dentro da roda

num_vars = len(pilares)
angulos = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angulos += angulos[:1] # Fecha o círculo

valores_lista = [valores[pilar] for pilar in pilares]
valores_lista += valores_lista[:1] # Fecha o polígono

# Pinta a área interna com a cor escolhida pelo usuário
ax.fill(angulos, valores_lista, color=cor_selecionada, alpha=0.6, label="Nível Atual")
ax.plot(angulos, valores_lista, color=cor_selecionada, linewidth=2)

# Ajustes de ângulos para ficar idêntico ao modelo da imagem
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

# Rótulos das Categorias
ax.set_xticks(angulos[:-1])
ax.set_xticklabels(pilares, color='white', fontsize=10, fontweight='bold')

# Configuração da escala (0 a 10)
ax.set_ylim(0, 10)
ax.set_yticks([2, 4, 6, 8, 10])
ax.set_yticklabels(["2", "4", "6", "8", "10"], color='#bdc3c7', fontsize=8)
ax.grid(True, color='#4a5a6a', linestyle='--', linewidth=0.7)

# 6. Renderização do Gráfico na coluna direita
with col2:
    st.markdown("### 📊 Visualização da Roda")
    st.pyplot(fig)

# 7. Função estruturada para gerar o PDF em memória
def gerar_pdf(valores_map, img_buffer):
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    
    style_title = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=24,
        textColor=colors.HexColor('#1a2a3a'), alignment=1, spaceAfter=20
    )
    style_heading = ParagraphStyle(
        'HeadingStyle', parent=styles['Heading2'], fontSize=14,
        textColor=colors.HexColor('#2980b9'), spaceBefore=12, spaceAfter=6
    )
    style_body = ParagraphStyle(
        'BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#333333')
    )
    
    # Montando as páginas do PDF
    story.append(Paragraph("🦉 Relatório: Coruja - Roda da Carreira", style_title))
    story.append(Paragraph("Este relatório apresenta o diagnóstico automatizado da sua jornada e satisfação profissional atual, mapeando as forças e os pontos que demandam atenção.", style_body))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>1. Sua Roda da Carreira Pintada</b>", style_heading))
    story.append(Image(img_buffer, width=380, height=380))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>2. Análise de Prioridades e Melhorias</b>", style_heading))
    
    # Lógica que detecta automaticamente o que precisa melhorar
    criticas = [p for p, v in valores_map.items() if v <= 4]
    atencao = [p for p, v in valores_map.items() if 5 <= v <= 7]
    fortes = [p for p, v in valores_map.items() if v >= 8]
    
    if criticas:
        texto_criticas = f"⚠️ <b>ÁREAS CRÍTICAS (Melhoria Urgente - Nota até 4):</b> {', '.join(criticas)}.<br/>" \
                         f"<i>Recomendação:</i> Sua roda está desequilibrada nestes pontos. Crie planos de ação focados imediatamente nessas vertentes para fazer a roda voltar a girar."
        story.append(Paragraph(texto_criticas, style_body))
        story.append(Spacer(1, 8))
        
    if atencao:
        texto_atencao = f"🔄 <b>ÁREAS DE ATENÇÃO (Desenvolvimento Médio - Nota 5 a 7):</b> {', '.join(atencao)}.<br/>" \
                        f"<i>Recomendação:</i> Apresentam estabilidade parcial, mas possuem pontos cegos e potencial claro de melhoria."
        story.append(Paragraph(texto_atencao, style_body))
        story.append(Spacer(1, 8))
        
    if fortes:
        texto_fortes = f"✅ <b>PONTOS FORTES (Sustentação - Nota 8 a 10):</b> {', '.join(fortes)}.<br/>" \
                       f"<i>Recomendação:</i> São seus pilares de maior fluidez. Utilize essa energia e segurança para impulsionar os setores mais fragilizados."
        story.append(Paragraph(texto_fortes, style_body))
        
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer

# 8. Botão de Download do PDF
with col1:
    st.markdown("---")
    st.markdown("### 📥 Exportar Resultados")
    
    # Converte o gráfico do matplotlib para imagem em formato bytes
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, facecolor='#1a2a3a', bbox_inches='tight', dpi=150)
    img_buffer.seek(0)
    
    # Prepara o arquivo para o usuário baixar
    pdf_data = gerar_pdf(valores, img_buffer)
    
    st.download_button(
        label="💾 Baixar Relatório em PDF",
        data=pdf_data,
        file_name="Roda_da_Carreira_Coruja.pdf",
        mime="application/pdf"
    )