/* =========================================================
   LASER SPOT — скрипты
   Номер WhatsApp меняется здесь (только цифры, с кодом страны):
   ========================================================= */
const WHATSAPP_NUMBER = '77025829889';

document.documentElement.classList.add('js');

// Ссылки WhatsApp: у любого элемента с data-wa="текст" формируется ссылка с готовым сообщением
document.querySelectorAll('[data-wa]').forEach((el) => {
  const text = el.getAttribute('data-wa');
  el.href = `https://wa.me/${WHATSAPP_NUMBER}${text ? `?text=${encodeURIComponent(text)}` : ''}`;
});

// Год в подвале
const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

// Шапка: тень при прокрутке + плавающая кнопка
const header = document.getElementById('header');
const waFloat = document.querySelector('.wa-float');
const hero = document.querySelector('.hero');
const onScroll = () => {
  const y = window.scrollY;
  header.classList.toggle('is-scrolled', y > 10);
  const heroBottom = hero ? hero.offsetTop + hero.offsetHeight * 0.6 : 400;
  waFloat.classList.toggle('is-visible', y > heroBottom);
};
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

// Мобильное меню
const burger = document.getElementById('burger');
const nav = document.getElementById('nav');
const setMenu = (open) => {
  burger.setAttribute('aria-expanded', String(open));
  burger.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
  nav.classList.toggle('is-open', open);
  document.body.classList.toggle('menu-open', open);
};
burger.addEventListener('click', () => setMenu(burger.getAttribute('aria-expanded') !== 'true'));
nav.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => setMenu(false)));
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setMenu(false); });
window.addEventListener('resize', () => { if (window.innerWidth > 960) setMenu(false); });

// Подсветка активного пункта меню
const links = [...document.querySelectorAll('.nav__list a')];
const sections = links.map((a) => document.querySelector(a.getAttribute('href'))).filter(Boolean);
const spy = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      links.forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === `#${entry.target.id}`));
    }
  });
}, { rootMargin: '-45% 0px -50% 0px' });
sections.forEach((s) => spy.observe(s));

// Появление элементов при прокрутке
const reveals = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  // небольшая задержка для соседних элементов
  reveals.forEach((el) => {
    const siblings = [...el.parentElement.children].filter((c) => c.classList.contains('reveal'));
    el.style.setProperty('--d', `${Math.min(siblings.indexOf(el), 6) * 0.08}s`);
    io.observe(el);
  });
} else {
  reveals.forEach((el) => el.classList.add('is-in'));
}

// Эффект «волны» при нажатии на кнопку
document.querySelectorAll('.btn').forEach((btn) => {
  btn.addEventListener('pointerdown', (e) => {
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const ripple = document.createElement('span');
    ripple.className = 'ripple';
    ripple.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX - rect.left - size / 2}px;top:${e.clientY - rect.top - size / 2}px`;
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 700);
  });
});

// Аккордеон: плавное раскрытие
document.querySelectorAll('.acc').forEach((d) => {
  const summary = d.querySelector('summary');
  const body = d.querySelector('.acc__body');
  summary.addEventListener('click', (e) => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    e.preventDefault();
    if (d.open) {
      body.animate([{ height: `${body.scrollHeight}px`, opacity: 1 }, { height: '0px', opacity: 0 }], { duration: 320, easing: 'ease' })
        .onfinish = () => { d.open = false; };
    } else {
      d.open = true;
      body.animate([{ height: '0px', opacity: 0 }, { height: `${body.scrollHeight}px`, opacity: 1 }], { duration: 380, easing: 'ease' });
    }
  });
});
