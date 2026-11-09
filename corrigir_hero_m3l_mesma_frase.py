#!/usr/bin/env python3
"""M3L — mesma chamada completa em mobile e desktop, só trecho dourado.

Uso no Droplet:
  python3 corrigir_hero_m3l_mesma_frase.py /var/www/m3l-vendas /var/www/m3l/public/vendas

Altera somente index.html e style.css; preserva JS, depoimentos e o restante da página.
Faz backups antes de gravar, valida a mudança antes de tocar nos arquivos,
e pode ser executado novamente sem duplicar código.
"""
from datetime import datetime
from pathlib import Path
import re
import shutil
import sys

if len(sys.argv) != 3:
    raise SystemExit('Uso: python3 corrigir_hero_m3l_mesma_frase.py PASTA_GITHUB PASTA_PUBLICADA')

roots = list(dict.fromkeys(Path(p).resolve() for p in sys.argv[1:]))
for root in roots:
    for name in ('index.html', 'style.css'):
        if not (root / name).is_file():
            raise SystemExit(f'Arquivo ausente: {root / name}. Nenhum arquivo foi alterado.')

HEADLINE = ('<h1 class="hero-main-title">Aprenda as '
            '<span class="hero-gold-gradient">7 fontes de renda</span> '
            'que me apresentaram aos 26 anos</h1>')
LEAD = ('<p class="hero-lead">Começando com apenas 100 reais. '
        'Vou te revelar o passo a passo para você alcançar as 3 liberdades: '
        'tempo, geográfica e financeira.</p>')
MARKER = 'M3L HERO UNIFICADA — DESKTOP E MOBILE'
CSS = r'''/* M3L HERO UNIFICADA — DESKTOP E MOBILE */
/* Mesma frase nos dois layouts, destacando APENAS as 7 fontes de renda. */
#inicio.hero--ready .hero-content > h1.hero-main-title {
  display: block !important;
  color: #f7f5f0;
  font-weight: 800;
  max-width: 100%;
}
#inicio.hero--ready .hero-content > h1.hero-main-title .hero-gold-gradient {
  color: #e8bb5e;
  background: linear-gradient(105deg, #fff0b6 0%, #e7b751 28%, #b87d21 52%, #ffe7a0 76%, #d39b35 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  box-decoration-break: clone;
  -webkit-box-decoration-break: clone;
}
@media (max-width: 760px) {
  #inicio.hero--ready .hero-content > h1.hero-main-title {
    display: block !important;
    width: 100%;
    max-width: 430px;
    margin: 0 auto 18px;
    font-size: clamp(31px, 8.6vw, 40px);
    line-height: 1.16;
    letter-spacing: -.04em;
    text-align: center;
  }
  #inicio.hero--ready .hero-content > p.hero-lead {
    display: block !important;
  }
}
'''

def patch_html(html):
    # Trabalha apenas dentro da seção hero; não altera headings e parágrafos de outras seções.
    start = html.find('<section class="hero')
    stop = html.find('<!-- DOBRA 2:', start)
    if start < 0 or stop < 0:
        raise ValueError('Não consegui delimitar a seção hero. Nada alterado.')
    hero = html[start:stop]
    headings = list(re.finditer(r'<h1\b[^>]*>[\s\S]*?</h1>', hero, re.I))
    if not 1 <= len(headings) <= 2:
        raise ValueError(f'Eram esperados 1 ou 2 títulos na hero, encontrados: {len(headings)}')
    for m in reversed(headings):
        hero = hero[:m.start()] + (HEADLINE if m is headings[0] else '') + hero[m.end():]
    leads = list(re.finditer(r'<p\b[^>]*\bclass="[^"]*\bhero-lead[^\"]*"[^>]*>[\s\S]*?</p>', hero, re.I))
    if not 1 <= len(leads) <= 2:
        raise ValueError(f'Eram esperados 1 ou 2 parágrafos de apresentação, encontrados: {len(leads)}')
    for m in reversed(leads):
        hero = hero[:m.start()] + (LEAD if m is leads[0] else '') + hero[m.end():]
    html = html[:start] + hero + html[stop:]
    # Renovação isolada do CSS para contornar caches do navegador/Cloudflare.
    link_pattern = r'(<link\b[^>]*\bhref=")style\.css(?:\?[^\"]*)?("[^>]*>)'
    html, count = re.subn(link_pattern, lambda m: m.group(1) + 'style.css?v=hero-unificada-20261109' + m.group(2), html, count=1)
    if count != 1:
        raise ValueError('Link da folha de estilos não encontrado. Nada alterado.')
    if html.count('class="hero-main-title"') != 1 or html.count('class="hero-gold-gradient"') != 1:
        raise ValueError('Headline duplicada ou ausente. Nada alterado.')
    return html

def patch_css(css):
    # Se repetir, preserva o patch existente sem duplicar regras.
    if MARKER in css:
        return css
    return css.rstrip() + '\n\n' + CSS + '\n'

changes = []
for root in roots:
    hp, cp = root / 'index.html', root / 'style.css'
    oldh, oldc = hp.read_text(encoding='utf-8'), cp.read_text(encoding='utf-8')
    newh, newc = patch_html(oldh), patch_css(oldc)
    if newh.count('class="hero-main-title"') != 1 or newh.count('class="hero-lead"') < 1:
        raise SystemExit('Validação do texto falhou. Nada alterado.')
    if hp.read_text(encoding='utf-8') != newh:
        changes.append((hp, newh))
    if cp.read_text(encoding='utf-8') != newc:
        changes.append((cp, newc))

if not changes:
    print('OK: frase unificada já aplicada em mobile e desktop; nenhuma mudança necessária.')
    sys.exit(0)

stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
backup_base = Path('/root') if Path('/root').is_dir() and str(roots[-1]).startswith('/var/www') else roots[0].parent
backup = backup_base / ('backup-m3l-hero-unificada-' + stamp)
backup.mkdir(parents=True, exist_ok=False)
for path, newcontent in changes:
    prefix = 'git-' if path.parent == roots[0] else 'public-'
    shutil.copy2(path, backup / (prefix + path.name))
for path, newcontent in changes:
    path.write_text(newcontent, encoding='utf-8')
print('OK: mesma frase no desktop e no mobile.')
print('H1: Aprenda as 7 fontes de renda que me apresentaram aos 26 anos')
print('Destaque dourado: somente “7 fontes de renda”.')
print('Texto complementar preservado; carrossel e demais seções sem alterações.')
print('Backup:', backup)
print('Aviso: mudanças no checkout Git ainda precisam de git add, commit e push.')
