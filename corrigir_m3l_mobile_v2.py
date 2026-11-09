#!/usr/bin/env python3
"""M3L: depoimentos grandes em carrossel e título mobile em degradê dourado.

Uso no Droplet:
    python3 corrigir_m3l_mobile_v2.py /var/www/m3l-vendas /var/www/m3l/public/vendas

Altera SOMENTE index.html e style.css, preserva JS e versão desktop.
Executa backup de cada arquivo antes de gravar, e pode ser repetido.
"""
from datetime import datetime
from pathlib import Path
import re
import shutil
import sys

if len(sys.argv) != 3:
    raise SystemExit('Uso: python3 corrigir_m3l_mobile_v2.py PASTA_GITHUB PASTA_PUBLICADA')

source, target = (Path(p).resolve() for p in sys.argv[1:])
roots = list(dict.fromkeys((source, target)))
for folder in roots:
    for name in ('index.html', 'style.css'):
        if not (folder / name).is_file():
            raise SystemExit(f'Arquivo ausente: {folder / name}. Nada alterado.')

# Patch CSS no fim do arquivo para vencer estilos antigos dos breakpoints 480/760px.
CSS_MARKER = 'M3L MOBILE V2 — depoimentos em tela cheia + hero dourada'
CSS_PATCH = r'''
/* M3L MOBILE V2 — depoimentos em tela cheia + hero dourada */
/* Desktop (a partir de 992px) permanece como estava. */
@media (max-width: 991px) {
  #depoimentos.section-testimonials .testimonial-grid {
    display: flex !important;
    grid-template-columns: none !important;
    grid-auto-columns: auto !important;
    grid-auto-flow: initial !important;
    width: min(100%, 480px) !important;
    max-width: 480px !important;
    margin-inline: auto !important;
    gap: 16px !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    scroll-snap-type: x mandatory;
    scroll-padding-inline: 0;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    overscroll-behavior-x: contain;
    justify-content: flex-start !important;
    align-items: stretch;
  }
  #depoimentos.section-testimonials .testimonial-grid::-webkit-scrollbar { display: none; }
  #depoimentos.section-testimonials .testimonial-video-card {
    flex: 0 0 100% !important;
    min-width: 100% !important;
    max-width: 100% !important;
    width: 100% !important;
    scroll-snap-align: start;
    scroll-snap-stop: always;
  }
  #depoimentos.section-testimonials .testimonial-pagination {
    display: flex !important;
    justify-content: center;
    align-items: center;
    gap: 9px;
    margin-top: 16px;
  }
  #depoimentos.section-testimonials .testimonial-pagination button {
    display: block;
    width: 8px;
    height: 8px;
    padding: 0;
    border: 0;
    border-radius: 50%;
    background: rgba(220,191,125,.4);
    cursor: pointer;
  }
  #depoimentos.section-testimonials .testimonial-pagination button.is-active {
    background: #e6c170;
    transform: scale(1.35);
  }
}
@media (max-width: 760px) {
  #inicio.hero--ready .hero-content > h1:not(.hero-mobile-title) { display: none !important; }
  #inicio.hero--ready .hero-content > h1.hero-mobile-title {
    display: block !important;
    width: 100%;
    max-width: 430px;
    margin: 0 auto 18px;
    font-size: clamp(36px, 9vw, 46px);
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -.045em;
    text-align: center;
    color: #f5d486;
    background-image: linear-gradient(105deg, #fff0b6 0%, #e7b751 28%, #b87d21 52%, #ffe7a0 76%, #d39b35 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  #inicio.hero--ready .hero-lead--desktop { display: none !important; }
  #inicio.hero--ready .hero-lead--mobile { display: block !important; }
}
'''

# A headline antiga permanece no HTML para desktop. Apenas uma versão mobile é exibida.
LEAD_MOBILE = ('Aprenda as 7 fontes que me apresentaram aos 26 anos, começando com apenas 100 reais. '
               'Vou te revelar o passo a passo para você alcançar as 3 liberdades: tempo, geográfica e financeira.')


def patch_html(html: str):
    original = html
    mobile_heading = re.compile(r'(<h1\b[^>]*\bclass=["\'][^"\']*hero-mobile-title[^"\']*["\'][^>]*>)[\s\S]*?(</h1>)', re.I)
    if mobile_heading.search(html):
        html = mobile_heading.sub(lambda m: m.group(1) + '7 fontes de renda' + m.group(2), html, count=1)
    else:
        h1 = re.search(r'<h1>\s*<span class="hero-headline-line">[\s\S]*?</h1>', html)
        if not h1:
            raise ValueError('Não encontrei o H1 da hero para inserir título mobile')
        html = html[:h1.end()] + '\n<h1 class="hero-mobile-title">7 fontes de renda</h1>' + html[h1.end():]

    mobile_lead = re.compile(r'(<p\b[^>]*\bclass=["\'][^"\']*hero-lead--mobile[^"\']*["\'][^>]*>)[\s\S]*?(</p>)', re.I)
    if mobile_lead.search(html):
        html = mobile_lead.sub(lambda m: m.group(1) + LEAD_MOBILE + m.group(2), html, count=1)
    else:
        lead = re.search(r'<p class="hero-lead">([\s\S]*?)</p>', html)
        if not lead:
            raise ValueError('Não encontrei o parágrafo da hero para inserir versão mobile')
        block = ('<p class="hero-lead hero-lead--desktop">' + lead.group(1) + '</p>\n'
                 '<p class="hero-lead hero-lead--mobile">' + LEAD_MOBILE + '</p>')
        html = html[:lead.start()] + block + html[lead.end():]

    # Versão no CSS para evitar stylesheet antigo mantido pelo Cloudflare.
    pattern = r'(<link\b[^>]*?href=["\'])style\.css(?:\?[^"\']*)?(["\'][^>]*>)'
    html, n = re.subn(pattern, lambda m: m.group(1) + 'style.css?v=m3l-mobile-v2-20261109' + m.group(2), html, count=1)
    if n != 1:
        raise ValueError('Não encontrei a referência a style.css')
    if html.count('class="hero-mobile-title"') != 1:
        raise ValueError('Encontrei mais de um título mobile ou título mobile ausente')
    return html, html != original


def patch_css(css: str):
    if CSS_MARKER in css:
        return css, False
    return css.rstrip() + '\n\n' + CSS_PATCH.strip() + '\n', True

# Prepara tudo na memória e faz checagens ANTES de tocar em qualquer arquivo.
changes = []
for folder in roots:
    html_path, css_path = folder / 'index.html', folder / 'style.css'
    h, c = html_path.read_text(encoding='utf-8'), css_path.read_text(encoding='utf-8')
    nh, hchanged = patch_html(h)
    nc, cchanged = patch_css(c)
    if '7 fontes de renda</h1>' not in nh:
        raise SystemExit('Título mobile incorreto, nada alterado')
    if 'testimonial-grid' not in nc or 'scroll-snap-type: x mandatory' not in nc:
        raise SystemExit('CSS do carrossel ausente, nada alterado')
    if hchanged:
        changes.append((html_path, nh))
    if cchanged:
        changes.append((css_path, nc))

if not changes:
    print('OK: versão mobile v2 já aplicada. Nenhuma alteração necessária.')
    sys.exit(0)

stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
backup_base = Path('/root') if target.is_relative_to('/var/www') and Path('/root').is_dir() else source.parent
backup = backup_base / ('backup-m3l-mobile-v2-' + stamp)
backup.mkdir(parents=True, exist_ok=False)
for path, content in changes:
    destination = backup / (('git-' if path.parent == source else 'public-') + path.name)
    shutil.copy2(path, destination)
for path, content in changes:
    path.write_text(content, encoding='utf-8')
print('OK: carrossel com 1 depoimento grande por vez até 991px e hero mobile em degradê dourado.')
print('Título mobile: 7 fontes de renda. Desktop preservado.')
print('Backup:', backup)
print('Atenção: alterações locais ainda não estão sincronizadas com o GitHub remoto.')
