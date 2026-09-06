# ============================================================
# BEN AURA — Constantes globales
# ============================================================

# --- Paleta Minimalista Moderno / Clean SaaS ---
FONDO_APP   = "#F8FAFC"  # Slate 50
TEXTO_DARK  = "#0F172A"  # Slate 900
TEXTO_MUTED = "#64748B"  # Slate 500
BORDE_LIGHT = "#E2E8F0"  # Slate 200
CARD_BG     = "#FFFFFF"  # White
PRIMARY     = "#1E293B"  # Slate 800 (Dark elegant modern)
ACCENT      = "#3B82F6"  # Blue 500
OK          = "#10B981"  # Emerald
ALERTA      = "#F59E0B"  # Amber
PELIGRO     = "#EF4444"  # Red

# Compatibilidad con imports existentes
MARRON      = "#1E293B"
TAUPE       = "#475569"
ARENA       = "#E2E8F0"
MARFIL      = "#F8FAFC"
CREMA       = "#FFFFFF"

# --- Meses en español ---
MESES_ES = {
    1: "Enero",    2: "Febrero",   3: "Marzo",     4: "Abril",
    5: "Mayo",     6: "Junio",     7: "Julio",      8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

# --- Insumos y sus unidades de medida ---
UNIDAD_INSUMO = {
    "Cera":        "gramos",
    "Esencia":     "gramos",
    "Colorante":   "gramos",
    "Pabilo":      "cm",
    "Bolsa":       "unidades",
    "Brochet":     "unidades",
    "Sticker":     "unidades",
    "Papel Madera": "unidades",
    "Cinta Bebé":  "unidades",
}
INSUMOS_MATERIALES = ["Cera", "Esencia", "Colorante", "Pabilo"]
INSUMOS_PACKAGING  = ["Bolsa", "Brochet", "Sticker", "Papel Madera", "Cinta Bebé"]

# --- Estados unificados del pedido ---
# Antes había dos campos separados (estado + entrega). Ahora uno solo.
ESTADOS_PEDIDO = [
    "⏳ Pendiente",
    "💰 Pago recibido",
    "🚚 Enviado",
    "✅ Entregado",
    "❌ Cancelado",
]

MEDIOS_PAGO = ["Transferencia", "Efectivo"]


def normalizar_estado(estado: str, entrega: str | None = None) -> str:
    """Convierte registros viejos (estado + entrega separados) al nuevo
    estado unificado. Los registros nuevos ya vienen con el valor correcto."""
    # Si el estado ya tiene el formato nuevo, lo devuelve tal cual
    for e in ESTADOS_PEDIDO:
        if estado == e:
            return estado

    # Migración de valores legacy
    if estado == "Cancelado":
        return "❌ Cancelado"
    if entrega == "Entregado":
        return "✅ Entregado"
    if entrega == "Envío":
        return "🚚 Enviado"
    if estado == "Pagado":
        return "💰 Pago recibido"
    return "⏳ Pendiente"


def format_currency(valor: float) -> str:
    """Formatea moneda argentina sin decimales si es entero redondo ($1.234) o con decimales si los tiene."""
    val = float(valor)
    if val.is_integer():
        return f"${int(val):,}".replace(",", ".")
    return f"${val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
