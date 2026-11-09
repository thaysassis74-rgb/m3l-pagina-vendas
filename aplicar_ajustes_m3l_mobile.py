#!/usr/bin/env python3
"""Aplica apenas mudanças mobile à hero e aos depoimentos do M3L.

Uso: python3 aplicar_ajustes_m3l_mobile.py /var/www/m3l-vendas /var/www/m3l/public/vendas
Mantém backup dos 3 arquivos públicos e dos 3 arquivos do checkout Git.
Compatível com M3L antes/depois da otimização anterior.
"""
from pathlib import Path
from datetime import datetime
import re
import sys
import shutil

if len(sys.argv) != 3:
    raise SystemExit('Uso: python3 aplicar_ajustes_m3l_mobile.py /var/www/m3l-vendas /var/www/m3l/public/vendas')
source, target = map(lambda p: Path(p).resolve(), sys.argv[1:])
names = ('index.html', 'style.css', 'script.js')
for root in (source, target):
    for name in names:
        if not (root / name).is_file():
            raise SystemExit(f'ERRO: arquivo não encontrado: {root / name}. Nenhum arquivo modificado.')
html, css, js = ((source / name).read_text(encoding='utf-8') for name in names)
original = (html, css, js)

# Consolida a otimização anterior, mesmo que ela ainda não tenha sido executada.
# Remove Meta Pixel: ficará sob gestão exclusiva da Cloudflare.
html = re.sub(r'\s*<!-- Meta Pixel Code -->[\s\S]*?<!-- End Meta Pixel Code -->', '', html)
html = re.sub(r'\s*<noscript>\s*<img\b[^>]*facebook\.com/tr[^>]*?/?>\s*</noscript>', '', html, flags=re.I)
if re.search(r'fbq\s*\(|fbevents\.js|facebook\.com/tr|3570010619958270', html, re.I):
    raise SystemExit('ERRO: Meta Pixel extra encontrado; nenhum arquivo alterado.')
# Preload responsivo, garantindo prioridade da arte correta sem alterar seu visual.
if 'M3L PERFORMANCE HERO PRELOAD' not in html and not ('fetchpriority="high" media="(min-width: 761px)"' in html):
    html = re.sub(r'\s*<link\s+rel="preload"\s+as="image"\s+href="assets/HERO_V3_MOBILE\.webp"[^>]*>', '', html)
    preload = ("\n<!-- M3L PERFORMANCE HERO PRELOAD -->\n"
               "<link rel=\"preload\" as=\"image\" type=\"image/webp\" href=\"assets/HERO_V3_MOBILE.webp\" fetchpriority=\"high\" media=\"(max-width: 760px)\">\n"
               "<link rel=\"preload\" as=\"image\" type=\"image/webp\" href=\"assets/hero-completa-desktop.webp\" fetchpriority=\"high\" media=\"(min-width: 761px)\">")
    html = html.replace('</head>', preload+'\n</head>', 1)
html = html.replace('loading="eager" decoding="async"', 'loading="lazy" decoding="async"')
html = html.replace('src="assets/thays-retrato-quem-sou.webp"', 'src="assets/thays-retrato-quem-sou.webp?v=20261109-2"')

# Desktop mantém seu H1 e parágrafo existentes. Mobile mostra H1 e texto próprios.
if 'class="hero-mobile-title"' not in html:
    marker = re.search(r'<h1>\s*<span class="hero-headline-line">\s*<strong>3 Liberdades:</strong>[\s\S]*?</h1>', html)
    lead = re.search(r'<p class="hero-lead">([\s\S]*?)</p>', html)
    if not marker or not lead:
        raise SystemExit('ERRO: markup da hero não encontrado. Nenhum arquivo modificado.')
    html = (html[:marker.end()] + '\n<h1 class="hero-mobile-title">Aprenda as 7 fontes de renda que me apresentaram aos 26 anos</h1>' + html[marker.end():])
    # Encontra novamente após a inserção do H1.
    lead = re.search(r'<p class="hero-lead">([\s\S]*?)</p>', html)
    new_paragraph = (
        'Começando com apenas 100 reais, vou te revelar o passo a passo '
        'para você alcançar as 3 liberdades: tempo, geográfica e financeira.'
    )
    replacement = ('<p class="hero-lead hero-lead--desktop">' + lead.group(1) + '</p>\n'
                   '<p class="hero-lead hero-lead--mobile">' + new_paragraph + '</p>')
    html = html[:lead.start()] + replacement + html[lead.end():]

# Os depoimentos ficam leves e arrastáveis antes do clique. Se já passaram
# pela otimização anterior, mantém os poster buttons existentes.
video_ids = ('CNTwI8tZIVU', 'yraXGJ8sSZY', 'vQBOZJVpxfU', 'Pw0fmUdePlk')
if 'class="testimonial-play"' not in html:
    found = []
    def swap_iframe(match):
        video_id = match.group(1)
        if video_id not in video_ids:
            return match.group(0)
        found.append(video_id)
        i = video_ids.index(video_id) + 1
        return (f'<button type="button" class="testimonial-play" data-video-id="{video_id}" '
                f'aria-label="Reproduzir depoimento {i:02d} nesta página">'
                f'<img src="https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" '
                f'alt="" width="480" height="360" loading="lazy" decoding="async">'
                '<span class="testimonial-play-icon" aria-hidden="true"></span></button>')
    html = re.sub(
        r'<iframe\b[^>]*src="https://www\.youtube\.com/embed/([A-Za-z0-9_-]{11})[^\"]*"[^>]*>\s*</iframe>',
        swap_iframe, html, flags=re.I
    )
    if sorted(found) != sorted(video_ids):
        raise SystemExit('ERRO: não foram encontrados os quatro depoimentos esperados. Nenhum arquivo modificado.')

# Atualiza versões de CSS/JS no HTML para contornar cache do navegador e CDN.
version = 'm3l-mobile-carousel-20261109'
html = re.sub(r'(<link\b[^>]*?href=")style\.css(?:\?[^\"]*)?("[^>]*>)',
              lambda m: m.group(1) + 'style.css?v=' + version + m.group(2), html)
html = re.sub(r'(<script\b[^>]*?src=")script\.js(?:\?[^\"]*)?("[^>]*>)',
              lambda m: m.group(1) + 'script.js?v=' + version + m.group(2), html)

poster_css = '''
/* M3L: capas leves dos depoimentos — sem carregar YouTube antes do clique. */
#depoimentos .testimonial-play {
  position:absolute;inset:0;display:block;width:100%;height:100%;padding:0;
  border:0;overflow:hidden;cursor:pointer;
  background:linear-gradient(155deg,#251d10,#090909 55%);
}
#depoimentos .testimonial-play img {display:block;width:100%;height:100%;object-fit:cover;opacity:.82}
#depoimentos .testimonial-play::after {content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,transparent 35%,rgba(0,0,0,.35) 100%)}
#depoimentos .testimonial-play-icon {
  position:absolute;top:50%;left:50%;z-index:1;display:grid;place-items:center;
  width:62px;height:62px;border-radius:50%;background:rgba(10,10,10,.83);
  border:1px solid rgba(247,213,125,.85);box-shadow:0 8px 28px rgba(0,0,0,.55);
  transform:translate(-50%,-50%);
}
#depoimentos .testimonial-play-icon::before {content:"";display:block;margin-left:4px;border-top:10px solid transparent;border-bottom:10px solid transparent;border-left:16px solid #f7d57d}
#depoimentos .testimonial-play:focus-visible {outline:3px solid #f7d57d;outline-offset:-3px}
'''
if not ('M3L PERF: players somente após clique' in css
        or 'M3L performance — players leves' in css
        or 'M3L: capas leves dos depoimentos' in css):
    css += '\n' + poster_css

mobile_css = '''
/* M3L MOBILE CAROUSEL — sem alterações no desktop. */
#inicio.hero--ready .hero-mobile-title,
#inicio.hero--ready .hero-lead--mobile {display:none}
#depoimentos .testimonial-pagination {display:none}
@media (max-width:760px) {
  #inicio.hero--ready .hero-content > h1:not(.hero-mobile-title) {display:none!important}
  #inicio.hero--ready .hero-content > .hero-mobile-title {
    display:block!important;font-size:clamp(29px,7.8vw,38px);
    line-height:1.16;letter-spacing:-.04em;max-width:420px;
    margin:0 auto 18px;
  }
  #inicio.hero--ready .hero-content > .hero-lead--desktop {display:none!important}
  #inicio.hero--ready .hero-content > .hero-lead--mobile {display:block!important}
  #depoimentos .testimonial-grid {
    display:grid!important;grid-template-columns:none!important;
    grid-auto-flow:column;grid-auto-columns:minmax(0,100%);
    width:100%;max-width:100%;overflow-x:auto;overflow-y:hidden;
    gap:16px;justify-content:initial;align-items:stretch;
    scroll-snap-type:x mandatory;scroll-padding-inline:0;
    overscroll-behavior-x:contain;touch-action:auto;
    -webkit-overflow-scrolling:touch;scrollbar-width:none;
  }
  #depoimentos .testimonial-grid::-webkit-scrollbar {display:none}
  #depoimentos .testimonial-video-card {
    min-width:0;max-width:none;width:100%;scroll-snap-align:start;
    scroll-snap-stop:always;
  }
  #depoimentos .testimonial-pagination {
    display:flex;justify-content:center;align-items:center;
    gap:9px;margin-top:16px;
  }
  #depoimentos .testimonial-pagination button {
    display:block;width:8px;height:8px;border:0;border-radius:50%;padding:0;
    cursor:pointer;background:rgba(220,191,125,.4);transition:background .2s,transform .2s;
  }
  #depoimentos .testimonial-pagination button.is-active {
    background:#e6c170;transform:scale(1.35);
  }
  #depoimentos .testimonial-pagination button:focus-visible {
    outline:2px solid #ffe3a4;outline-offset:5px;
  }
}
'''
if 'M3L MOBILE CAROUSEL — sem alterações no desktop' not in css:
    css += '\n' + mobile_css

poster_js = '''
/* M3L: inicia o YouTube no mesmo card somente após o clique. */
(() => {
  document.querySelectorAll('.testimonial-play').forEach(button => {
    button.addEventListener('click', () => {
      const id = button.dataset.videoId || '';
      if (!/^[a-zA-Z0-9_-]{11}$/.test(id)) return;
      const frame = document.createElement('iframe');
      frame.width = '560';frame.height = '315';
      frame.title = button.getAttribute('aria-label') || 'Depoimento M3L';
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      frame.allowFullscreen = true;
      frame.src = `https://www.youtube.com/embed/${id}?autoplay=1&playsinline=1&rel=0`;
      button.replaceWith(frame);
    }, {once:true});
  });
})();
'''
if not ('M3L PERF: YouTube e seus scripts' in js
        or 'M3L performance: poster primeiro' in js
        or 'M3L: inicia o YouTube no mesmo card' in js):
    js += '\n' + poster_js

pager_js = '''
/* M3L MOBILE CAROUSEL — arraste para navegar; indicadores acessíveis. */
(() => {
  const grid = document.querySelector('#depoimentos .testimonial-grid');
  if (!grid) return;
  const cards = [...grid.querySelectorAll('.testimonial-video-card')];
  if (cards.length < 2) return;
  const pagination = document.createElement('div');
  pagination.className = 'testimonial-pagination';
  pagination.setAttribute('role', 'group');
  pagination.setAttribute('aria-label', 'Navegação dos depoimentos');
  const buttons = cards.map((card, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.setAttribute('aria-label', `Ir ao depoimento ${index+1} de ${cards.length}`);
    button.classList.toggle('is-active', index===0);
    button.setAttribute('aria-current', index===0 ? 'true':'false');
    button.addEventListener('click', () => {
      const left = card.getBoundingClientRect().left - grid.getBoundingClientRect().left + grid.scrollLeft;
      grid.scrollTo({left,behavior:'smooth'});
    });
    pagination.appendChild(button);
    return button;
  });
  grid.insertAdjacentElement('afterend', pagination);
  let ticking = false;
  grid.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      ticking = false;
      const left = grid.getBoundingClientRect().left;
      let current = 0, min = Infinity;
      cards.forEach((card,i) => {
        const distance = Math.abs(card.getBoundingClientRect().left - left);
        if (distance < min) {min = distance;current = i;}
      });
      buttons.forEach((button,i) => {
        button.classList.toggle('is-active',i===current);
        button.setAttribute('aria-current',i===current ? 'true' : 'false');
      });
    });
  }, {passive:true});
})();
'''
if 'M3L MOBILE CAROUSEL — arraste para navegar' not in js:
    js += '\n' + pager_js

# Adia clones do carrossel de módulos até ele se aproximar da tela.
start=js.find('  if (track && !reduced) {')
end=js.find('\n  \nconst sticky',start)
if start!=-1 and end>start and 'let started = false' not in js[start:end] and 'track.append(clone)' in js[start:end]:
    js=js[:start]+'''  if (track && !reduced) {
    let started = false;
    const startAnimation = () => {
      if (started) return;
      started = true;
      const originalCards = Array.from(track.children);
      originalCards.forEach(card => {
        const clone = card.cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        clone.querySelectorAll('img').forEach(img => {img.loading='lazy';img.setAttribute('fetchpriority','low');});
        track.append(clone);
      });
      const measure = () => {
        const first=originalCards[0], clone=track.children[originalCards.length];
        if (!first || !clone) return;
        const distance=clone.offsetLeft-first.offsetLeft;
        if (distance>0) {
          track.style.setProperty('--module-distance', `${distance}px`);
          track.style.setProperty('--module-duration', `${Math.round(distance / 27)}s`);
        }
      };
      measure();
      window.addEventListener('resize', measure, {passive:true});
    };
    if ('IntersectionObserver' in window) {
      const observer=new IntersectionObserver(entries => {
        if (!entries.some(entry => entry.isIntersecting)) return;
        observer.disconnect();startAnimation();
      }, {rootMargin:'400px 0px'});
      observer.observe(scroller);
    } else {
      window.addEventListener('load', startAnimation, {once:true});
    }
  }'''+js[end:]

# Sanidade e segurança antes de qualquer escrita.
if html.count('class="hero-mobile-title"') != 1:
    raise SystemExit('ERRO: título mobile duplicado ou ausente. Nada modificado.')
if not all(f'data-video-id="{vid}"' in html for vid in video_ids):
    raise SystemExit('ERRO: vídeos ausentes. Nada modificado.')
if 'https://pay.hub.la/krI3dagqJnY8AE2Vgq6P' not in js:
    raise SystemExit('ERRO: link do checkout não localizado. Nada modificado.')
if 'M3L MOBILE CAROUSEL — sem alterações no desktop' not in css:
    raise SystemExit('ERRO: CSS do carrossel ausente. Nada modificado.')
if 'M3L MOBILE CAROUSEL — arraste para navegar' not in js:
    raise SystemExit('ERRO: JS do carrossel ausente. Nada modificado.')
if re.search(r'fbq\s*\(|fbevents\.js|facebook\.com/tr|3570010619958270', html+css+js, re.I):
    raise SystemExit('ERRO: Pixel permaneceu no projeto.')

if (html,css,js)==original:
    print('OK: ajustes já aplicados; nenhuma alteração necessária.')
    sys.exit(0)

stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
backup_dir = Path('/root' if str(target).startswith('/var/www/') and Path('/root').is_dir() else source.parent)
backup = backup_dir / ('backup-m3l-mobile-'+stamp)
backup.mkdir(parents=True, exist_ok=False)
for name in names:
    shutil.copy2(source/name, backup/(name+'.git'))
    shutil.copy2(target/name, backup/(name+'.publicado'))
for name,data in zip(names,(html,css,js)):
    (source/name).write_text(data, encoding='utf-8')
    shutil.copy2(source/name, target/name)
print('OK: hero mobile, carrossel 1 por vez, 4 depoimentos por clique, Pixel removido e performance consolidada.')
print('DESKTOP: mantido. BACKUP:', backup)
print('Os arquivos atualizados estão no checkout local, mas ainda não no GitHub remoto.')
