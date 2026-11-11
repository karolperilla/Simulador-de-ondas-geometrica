"""CSS y bloques HTML del diseño (tema oscuro azul luminoso)."""

CSS = """
<style>
.stApp, .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp li, .stApp button,
.stApp input, .stApp [data-baseweb="select"] { font-family: "Segoe UI", "Helvetica Neue", Arial, system-ui, sans-serif; }
/* Los iconos Material NUNCA deben heredar la fuente de texto (evita "arrow_right" encimado) */
span[data-testid="stIconMaterial"], .material-icons, .material-symbols-rounded, [class*="material-symbols"] {
  font-family: "Material Symbols Rounded", "Material Icons" !important; font-weight: 400 !important;
  line-height: 1 !important; letter-spacing: normal !important; text-transform: none !important;
  white-space: nowrap !important; font-feature-settings: "liga" !important; -webkit-font-feature-settings: "liga" !important;
  overflow: hidden; }
.stApp { background: radial-gradient(1300px 760px at 50% -8%, #0e2f66 0%, #071633 48%, #040b1d 100%); color: #e6f1ff; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1rem; max-width: 1650px; }
[data-testid="stHorizontalBlock"] { align-items: flex-start; gap: 1rem; }
[data-testid="stVerticalBlockBorderWrapper"] {
  background: linear-gradient(160deg, rgba(14,40,88,.88), rgba(6,18,44,.92));
  border: 1px solid rgba(70,130,230,.38) !important; border-radius: 16px;
  box-shadow: 0 0 26px rgba(20,90,220,.16); }
/* texto limpio */
[data-testid="stWidgetLabel"] p, label p { line-height: 1.4 !important; margin: 0 0 .25rem 0 !important; overflow-wrap: anywhere; }
[data-testid="stMarkdownContainer"] p { line-height: 1.55; }
[data-testid="stSlider"] { padding-bottom: .55rem; }
[data-testid="stSliderThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] { line-height: 1.2 !important; }
.stButton > button { line-height: 1.25 !important; padding: .5rem .9rem; min-height: 2.6rem; white-space: nowrap; }
.stButton > button p { margin: 0 !important; line-height: 1.25 !important; }
[data-testid="stMetric"] { background: rgba(10,40,90,.55); border: 1px solid rgba(70,130,230,.38);
  border-radius: 12px; padding: 8px 12px; margin-bottom: .5rem; }
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p { color: #7fd1ff; line-height: 1.25 !important;
  white-space: normal !important; overflow: visible !important; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] div { color: #19e6c1; font-weight: 600; line-height: 1.3 !important; }
[data-baseweb="select"] > div { background: rgba(8,28,66,.85); border-color: rgba(70,130,230,.5); min-height: 2.6rem; }
[data-baseweb="select"] div[value], [data-baseweb="select"] span { line-height: 1.4; }
[data-testid="stExpander"] summary { line-height: 1.5; padding: .5rem .75rem; gap: .6rem; }
[data-testid="stExpander"] summary p { margin: 0 !important; }
/* imagen principal: siempre completa y centrada, sin deformarse */
[data-testid="stImage"] { display: flex; justify-content: center; align-items: center; width: 100%; }
[data-testid="stImage"] img { max-width: 100% !important; height: auto !important; object-fit: contain; border-radius: 12px; }
/* navegación tipo pestañas (radio) */
.st-key-nav div[role="radiogroup"], .st-key-nav2 div[role="radiogroup"] { justify-content: center; gap: 6px; width: fit-content;
  margin: 0 auto 14px auto; background: rgba(10,30,70,.75); border: 1px solid rgba(70,130,230,.45); border-radius: 14px; padding: 6px; }
.st-key-nav label, .st-key-nav2 label { border-radius: 10px; padding: 7px 24px; margin: 0 !important; cursor: pointer; }
.st-key-nav label > div:first-child, .st-key-nav2 label > div:first-child { display: none; }
.st-key-nav label p, .st-key-nav2 label p { color: #cfe3ff; line-height: 1.3 !important; margin: 0 !important; }
.st-key-nav label:has(input:checked), .st-key-nav2 label:has(input:checked) { background: linear-gradient(180deg, #1a86ff, #0a4fd0);
  box-shadow: 0 0 16px rgba(30,130,255,.55); }
.st-key-nav label:has(input:checked) p, .st-key-nav2 label:has(input:checked) p { color: #fff; font-weight: 600; }
.stButton > button[kind="primary"] { background: linear-gradient(90deg, #10d9a0, #1aa0e8); border: 0; color: #fff;
  font-weight: 600; height: 3rem; border-radius: 12px; box-shadow: 0 0 20px rgba(20,220,180,.4); }
.stButton > button[kind="secondary"] { background: rgba(20,60,130,.6); border: 1px solid rgba(90,150,255,.5);
  color: #e6f1ff; border-radius: 10px; }
.titulo-panel { font-weight: 600; font-size: 1.02rem; color: #e6f1ff; margin: 0 0 .6rem 0; line-height: 1.4; }
.titulo-panel span { color: #3fb6ff; margin-right: .5rem; }
.cab { display: flex; align-items: center; gap: 22px; padding: 4px 6px 10px 6px; flex-wrap: wrap; }
.cab h1 { margin: 0; padding: 0; font-size: 2.5rem; font-weight: 700; line-height: 1.1; color: #fff; }
.cab h1 b { color: #35e08a; }
.cab .sub { font-size: 1.3rem; color: #dbe8ff; line-height: 1.3; }
.cab .lema { font-family: "Segoe Script", "Brush Script MT", cursive; font-size: 1.35rem; color: #cfe3ff;
  border-left: 1px solid rgba(120,170,255,.4); padding-left: 22px; line-height: 1.35; }
.cab .lema i { display: block; height: 3px; width: 85%; margin-top: 6px; border-radius: 3px;
  background: linear-gradient(90deg, #35e08a, transparent); }
.optica-card ul { list-style: none; padding: 0; margin: .4rem 0 .8rem 0; }
.optica-card li { padding: 6px 0 6px 22px; position: relative; color: #dbe8ff; font-size: .92rem; line-height: 1.4; }
.optica-card li:before { content: ''; position: absolute; left: 4px; top: 14px; width: 6px; height: 6px;
  border-radius: 50%; background: #3fb6ff; box-shadow: 0 0 8px #3fb6ff; }
.consejo { background: linear-gradient(135deg, #2a1f78, #3a2a9a); border: 1px solid rgba(140,120,255,.6);
  border-radius: 12px; padding: 12px 14px; font-size: .86rem; line-height: 1.5; color: #f0eaff; }
.frase { min-height: 380px; border-radius: 16px; padding: 28px 18px; text-align: center; color: #eaf3ff;
  font-size: 1.2rem; line-height: 1.7; border: 1px solid rgba(70,130,230,.38);
  background: radial-gradient(circle at 50% 108%, #1b8cff 0%, #0b3a8a 28%, #061a46 62%, #050f2a 100%); }
.lk { background: rgba(8,28,66,.7); border: 1px solid rgba(70,130,230,.38); border-radius: 12px;
  padding: 10px 14px; font-size: .95rem; line-height: 1.9; margin-top: .5rem; }
.lk b { color: #7fd1ff; }
.teo { height: 100%; }
.teo h4 { margin: 0 0 .5rem 0; color: #7fd1ff; font-size: 1.05rem; line-height: 1.35; }
.teo p, .teo li { color: #dbe8ff; font-size: .93rem; line-height: 1.6; }
.teo ul { padding-left: 1.1rem; margin: .3rem 0; }
.teo .clave { background: rgba(26,134,255,.14); border-left: 3px solid #3fb6ff; border-radius: 8px;
  padding: 8px 12px; margin: .5rem 0; font-size: .9rem; line-height: 1.55; }
.espectro { height: 14px; border-radius: 7px; margin: .5rem 0 .2rem 0;
  background: linear-gradient(90deg, #7a4dff, #2f6bff, #2fe0ff, #3ddc5a, #ffe83a, #ff9a1f, #ff3b3b); }
.espectro-et { display: flex; justify-content: space-between; font-size: .78rem; color: #9fb4d6; }
</style>
"""

ENCABEZADO = """
<div class="cab">
  <svg width="104" height="74" viewBox="0 0 104 74" fill="none">
    <defs><linearGradient id="lg" x1="0" x2="1"><stop offset="0" stop-color="#1b8cff"/><stop offset="1" stop-color="#35e0ff"/></linearGradient></defs>
    <path d="M4 62 C16 8, 30 8, 40 40 S58 66, 68 24 S88 6, 100 56" stroke="url(#lg)" stroke-width="8" stroke-linecap="round"/>
    <path d="M14 66 C26 22, 38 22, 48 48 S66 66, 76 34" stroke="#7fe9ff" stroke-width="3" stroke-linecap="round" opacity=".7"/>
  </svg>
  <div><h1>Simulador <b>Físico</b></h1><div class="sub">Ondas y Óptica Geométrica</div></div>
  <div class="lema">Explora, experimenta,<br>descubre la física<i></i></div>
</div>
"""

PANEL_OPTICA = """
<div class="optica-card">
  <div class="titulo-panel"><span>△</span>Óptica Geométrica</div>
  <svg viewBox="0 0 270 175" width="100%">
    <defs><linearGradient id="pr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity=".55"/>
    <stop offset="1" stop-color="#7fb8ff" stop-opacity=".25"/></linearGradient></defs>
    <line x1="0" y1="82" x2="108" y2="92" stroke="#fff" stroke-width="3"/>
    <polygon points="110,18 58,150 168,150" fill="url(#pr)" stroke="#dbe9ff" stroke-width="1.5"/>
    <g stroke-width="3" stroke-linecap="round">
      <line x1="128" y1="96" x2="270" y2="50" stroke="#ff3b3b"/><line x1="128" y1="97" x2="270" y2="64" stroke="#ff9a1f"/>
      <line x1="128" y1="98" x2="270" y2="78" stroke="#ffe83a"/><line x1="128" y1="99" x2="270" y2="92" stroke="#3ddc5a"/>
      <line x1="128" y1="100" x2="270" y2="106" stroke="#2fb6ff"/><line x1="128" y1="101" x2="270" y2="120" stroke="#7a4dff"/>
    </g>
  </svg>
  <ul><li>Reflexión</li><li>Refracción</li><li>Leyes de Snell</li><li>Índice de refracción</li></ul>
  <div class="consejo">💡 ¡Descubre cómo la luz se comporta en diferentes medios!</div>
</div>
"""

FRASE = """
<div class="frase">
  <svg width="46" height="46" viewBox="0 0 46 46" fill="none" stroke="#7fd1ff" stroke-width="2.4">
    <path d="M23 4 L40 40 H6 Z"/><path d="M2 28 L16 24"/><path d="M30 28 L44 20"/></svg><br>
  Las ondas<br>nos conectan<br>con la naturaleza<br>y la luz nos revela<br>el mundo.
</div>
"""


TEORIA_DISPERSION = """
<div class="teo"><h4>〰 Dispersión de ondas</h4>
<p>Un medio es <b>dispersivo</b> cuando la frecuencia no es proporcional al número de onda: <b>ω = ω(k)</b>.
Cada longitud de onda viaja con su propia velocidad, así que un pulso se <b>ensancha</b> y sus componentes se
separan.</p>
<ul><li><b>Velocidad de fase</b> v<sub>f</sub> = ω/k: lo que avanza una cresta.</li>
<li><b>Velocidad de grupo</b> v<sub>g</sub> = dω/dk: lo que avanza el paquete (la energía).</li></ul>
<div class="clave">Agua profunda: ω = √(g·k) → v<sub>g</sub> = v<sub>f</sub>/2. Las ondas largas van más rápido,
por eso una gota se deshace en un tren de anillos ordenados por tamaño.</div>
<p>Si la profundidad h es comparable a λ, ω² = g·k·tanh(k·h): al reducir h las ondas se vuelven no dispersivas
(v = √(g·h)).</p></div>
"""

TEORIA_OPTICA = """
<div class="teo"><h4>△ Óptica geométrica</h4>
<p>Cuando la longitud de onda es mucho menor que los objetos (λ ≪ tamaño), la luz se describe con <b>rayos</b>:
líneas perpendiculares a los <b>frentes de onda</b> que indican la dirección de propagación.</p>
<svg viewBox="0 0 240 90" width="100%" style="margin:.2rem 0">
 <g fill="none" stroke="#3fb6ff" stroke-width="1.6"><path d="M60 8 Q70 45 60 82"/><path d="M95 8 Q105 45 95 82"/><path d="M130 8 Q140 45 130 82"/></g>
 <g stroke="#ffd54a" stroke-width="2"><line x1="10" y1="25" x2="225" y2="25"/><line x1="10" y1="45" x2="225" y2="45"/><line x1="10" y1="65" x2="225" y2="65"/></g>
 <text x="150" y="86" fill="#9fb4d6" font-size="9">frentes de onda ⟂ rayos</text></svg>
<ul><li><b>Reflexión:</b> θ<sub>i</sub> = θ<sub>r</sub>.</li>
<li><b>Refracción (Snell):</b> n₁·sen θ₁ = n₂·sen θ₂, con n = c/v.</li>
<li><b>Reflexión interna total</b> si n₁ &gt; n₂ y θ₁ &gt; θ<sub>c</sub> = arcsen(n₂/n₁).</li>
<li><b>Lentes y espejos:</b> 1/f = 1/d<sub>o</sub> + 1/d<sub>i</sub>.</li></ul>
<div class="clave">Principio de Fermat: la luz recorre el camino de tiempo mínimo (o estacionario).</div></div>
"""

TEORIA_ESPECTRO = """
<div class="teo"><h4>🌈 Comportamiento del espectro</h4>
<p>La luz blanca es la suma de todas las longitudes de onda visibles (≈ 380–750 nm). En el vidrio, n depende de λ
(modelo de Cauchy: <b>n = A + B/λ²</b>), así que cada color se refracta con un ángulo distinto.</p>
<div class="espectro"></div><div class="espectro-et"><span>400 nm violeta</span><span>550 nm</span><span>700 nm rojo</span></div>
<ul><li>El <b>violeta</b> tiene mayor n → se desvía <b>más</b>.</li>
<li>El <b>rojo</b> tiene menor n → se desvía <b>menos</b>.</li>
<li>El espectro es <b>continuo</b>: no hay bandas, solo un cambio gradual de color.</li>
<li>El violeta es el primero en sufrir reflexión interna total (su ángulo crítico es menor).</li></ul>
<div class="clave">Desviación mínima: δ<sub>min</sub> = 2·arcsen(n·sen(α/2)) − α. El arcoíris es este mismo
efecto en gotas de agua.</div></div>
"""
