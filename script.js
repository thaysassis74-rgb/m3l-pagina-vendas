/* M3L v7 — autoplay contínuo sem controles, sem scrollbars */
const CHECKOUT_URL = 'https://pay.hub.la/krI3dagqJnY8AE2Vgq6P';
(function () {
  const year = document.getElementById('copyright-year');
  if (year) year.textContent = String(new Date().getFullYear());
  const scroller = document.getElementById('module-scroller');
  const track = scroller && scroller.querySelector('.module-track');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (track && !reduced) {
    const originalCards = Array.from(track.children);
    originalCards.forEach(card => {
      const clone = card.cloneNode(true);
      clone.setAttribute('aria-hidden', 'true');
      track.append(clone);
    });
    const measure = () => {
      const first = originalCards[0];
      const clone = track.children[originalCards.length];
      if (!first || !clone) return;
      const distance = clone.offsetLeft - first.offsetLeft;
      if (distance > 0) {
        track.style.setProperty('--module-distance', `${distance}px`);
        track.style.setProperty('--module-duration', `${Math.round(distance / 27)}s`);
      }
    };
    measure();
    window.addEventListener('resize', measure, {passive:true});
  }
  
const sticky = document.querySelector('.mobile-cta');
const hero = document.querySelector('.hero');
const checkout = document.querySelector('#oferta');

if (sticky && hero && checkout) {
  const update = () => {
    const heroRect = hero.getBoundingClientRect();
    const checkoutRect = checkout.getBoundingClientRect();

    // Verifica se a pessoa já passou da hero
    const passouHero = heroRect.bottom < 90;

    // Verifica se o checkout está visível
    const checkoutVisivel =
      checkoutRect.top < window.innerHeight &&
      checkoutRect.bottom > 0;

    // Mostra somente fora da hero e do checkout
    sticky.classList.toggle(
      'is-active',
      passouHero && !checkoutVisivel
    );
  };

  window.addEventListener('scroll', update, {
    passive: true
  });

  window.addEventListener('resize', update);

  update();
}

  const button = document.querySelector('[data-checkout="true"]');
  if (button) button.addEventListener('click', e => {
    e.preventDefault();
    if (/^https:\/\//i.test(CHECKOUT_URL)) location.assign(CHECKOUT_URL);
    else {
      const message = document.getElementById('checkout-message');
      if (message) { message.hidden = false; message.scrollIntoView({behavior:'smooth', block:'nearest'}); }
    }
  });
})();


/* M3L · Seletor de placas de reconhecimento */
(function () {
  const section = document.getElementById('premiacoes');
  if (!section) return;
  const featured = section.querySelector('#award-featured-image');
  const showcase = section.querySelector('.awards-showcase');
  const selectedValue = section.querySelector('#award-selected-value');
  const selectedLabel = section.querySelector('#award-selected-label');
  const options = section.querySelectorAll('.award-option');
  if (!featured || !showcase || !selectedValue || !selectedLabel) return;

  options.forEach(option => {
    option.addEventListener('click', function () {
      if (this.getAttribute('aria-pressed') === 'true') return;
      options.forEach(item => {
        item.classList.remove('is-active');
        item.setAttribute('aria-pressed', 'false');
      });
      this.classList.add('is-active');
      this.setAttribute('aria-pressed', 'true');
      featured.src = this.dataset.awardSrc;
      featured.alt = 'Placa M3L de ' + this.dataset.awardLabel;
      selectedValue.textContent = this.dataset.awardValue;
      selectedLabel.textContent = this.dataset.awardLabel;
      showcase.dataset.awardTheme = this.dataset.awardTheme;
    });
  });
})();


document.addEventListener("DOMContentLoaded", () => {

  const swingCard = document.querySelector(
    ".bonus-card--swing"
  );

  if (!swingCard) return;

  const observer = new IntersectionObserver(
    (entries) => {

      entries.forEach((entry) => {

        if (entry.isIntersecting) {

          // Ativa o reflexo dourado
          entry.target.classList.add("brilho-ativo");

        } else {

          // Permite repetir ao voltar à seção
          entry.target.classList.remove("brilho-ativo");

        }

      });

    },
    {
      threshold: 0.4
    }
  );

  observer.observe(swingCard);

});


/* M3L · Scroll reveal progressivo, sem dependências externas.
   Os elementos continuam visíveis caso JS/IntersectionObserver falhe. */
(function () {
  function initScrollEffects() {
    const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (motionPreference.matches || !('IntersectionObserver' in window)) return;

    // Elementos já sinalizados no HTML + pontos de entrada das demais seções.
    const effects = [
      ['#premiacoes .awards-intro', 'up'],
      ['#premiacoes .awards-showcase', 'left'],
      ['#premiacoes .awards-explainer', 'right'],
      ['#depoimentos .testimonial-video-card', 'up'],
      ['#sobre .about-photo-wrap', 'left'],
      ['#sobre .about-content', 'right'],
      ['#conteudo-m3l .module-feature-copy', 'left'],
      ['#conteudo-m3l .module-feature-art', 'right'],
      ['#conteudo-m3l .module-subheading', 'up'],
      ['#conteudo-m3l .module-scroller', 'up'],
      ['#imprensa .press-phone-figure', 'right'],
      ['#bonus .bonus-card', 'up'],
      ['#oferta .guarantee-card', 'up'],
      ['#faq .faq-item', 'up'],
      ['.section-cta', 'up']
    ];

    effects.forEach(([selector, direction]) => {
      document.querySelectorAll(selector).forEach(element => {
        element.classList.add('reveal');
        element.dataset.reveal = direction;
      });
    });

    // Retardo discreto entre cards da mesma fileira, sem prender a rolagem.
    [
      ['#depoimentos .testimonial-video-card', 4, 85],
      ['#para-quem .benefit-card', 2, 110],
      ['#bonus .bonus-card', 3, 90],
      ['#faq .faq-item', 5, 65]
    ].forEach(([selector, columns, interval]) => {
      document.querySelectorAll(selector).forEach((element, index) => {
        element.style.setProperty('--reveal-delay', `${(index % columns) * interval}ms`);
      });
    });

    const elements = Array.from(document.querySelectorAll('.reveal'));
    if (!elements.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target); // Aparece uma vez; não pisca ao voltar.
      });
    }, {
      threshold: 0.06,
      rootMargin: '0px 0px -7% 0px'
    });

    // É ativado somente quando o observador já foi criado.
    document.documentElement.classList.add('scroll-effects-ready');
    elements.forEach(element => observer.observe(element));

    // Caso a preferência seja alterada com o site aberto, revela tudo.
    const revealWithoutMotion = () => {
      if (!motionPreference.matches) return;
      elements.forEach(element => {
        element.classList.add('is-visible');
        observer.unobserve(element);
      });
      document.documentElement.classList.remove('scroll-effects-ready');
    };
    if (motionPreference.addEventListener) {
      motionPreference.addEventListener('change', revealWithoutMotion);
    } else if (motionPreference.addListener) {
      motionPreference.addListener(revealWithoutMotion);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initScrollEffects, { once: true });
  } else {
    initScrollEffects();
  }
})();
