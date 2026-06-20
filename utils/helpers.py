"""
utils/helpers.py
Funções utilitárias puras (sem estado, sem Streamlit).
"""


def svg_gauge(valor: int, label: str, descricao: str) -> str:
    """Gera HTML/SVG de um gauge circular para exibir no Streamlit."""
    circ       = 2 * 3.14159 * 54
    preenchido = (max(0, min(100, valor)) / 100) * circ
    vazio      = circ - preenchido
    cor        = "#0060ab" if label != "Confiança" else "#b81120"
    return f"""
    <div style="text-align:center; display:flex; flex-direction:column; align-items:center; padding:10px 20px;">
      <svg width="130" height="130" viewBox="0 0 130 130">
        <circle cx="65" cy="65" r="54" fill="none" stroke="#eceef2" stroke-width="10"/>
        <circle cx="65" cy="65" r="54" fill="none" stroke="{cor}" stroke-width="10"
          stroke-dasharray="{preenchido:.1f} {vazio:.1f}"
          stroke-linecap="round" transform="rotate(-90 65 65)"/>
        <text x="65" y="62" text-anchor="middle" font-size="28" font-weight="700" fill="#191c1f">{valor}</text>
        <text x="65" y="80" text-anchor="middle" font-size="13" fill="#888">%</text>
      </svg>
      <div style="font-weight:700; font-size:15px; color:#191c1f; margin-top:8px;">{label}</div>
      <div style="font-size:12px; color:#5b403e; margin-top:4px; max-width:170px; line-height:1.4;">{descricao}</div>
    </div>
    """


def estrelas(nota: int) -> str:
    """Converte nota 0-100 em string de estrelas (★☆)."""
    cheia  = round(nota / 20)
    vazia  = 5 - cheia
    return "★" * cheia + "☆" * vazia


def cor_nota(nota: int) -> str:
    """Retorna a cor hex de acordo com a nota."""
    if nota >= 70:
        return "#0060ab"
    return "#b81120"


def media_avaliacao(aval: dict) -> int:
    """Calcula a média das três métricas globais de uma avaliação."""
    c = aval.get("comunicacao", 0)
    t = aval.get("tecnico", 0)
    f = aval.get("confianca", 0)
    return round((c + t + f) / 3)
