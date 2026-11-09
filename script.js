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
