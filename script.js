const fullpage = document.getElementById('fullpage');
const pages = document.querySelectorAll('#fullpage > section, #fullpage > footer');
const overlay = document.getElementById('gradient-overlay');

const pageGradients = [
  { top: '#ffffff', bottom: '#f0fdfa' },
  { top: '#eff6ff', bottom: '#ffffff' },
  { top: '#f1f5f9', bottom: '#ffffff' },
  { top: '#f0fdfa', bottom: '#ffffff' },
  { top: '#fefce8', bottom: '#ffffff' },
  { top: '#faf5ff', bottom: '#ffffff' },
  { top: '#fdf2f8', bottom: '#ffffff' },
  { top: '#ecfdf5', bottom: '#ffffff' },
  { top: '#0f172a', bottom: '#020617' },
];

function lerpColor(hex1, hex2, t) {
  const r1 = parseInt(hex1.slice(1, 3), 16);
  const g1 = parseInt(hex1.slice(3, 5), 16);
  const b1 = parseInt(hex1.slice(5, 7), 16);
  const r2 = parseInt(hex2.slice(1, 3), 16);
  const g2 = parseInt(hex2.slice(3, 5), 16);
  const b2 = parseInt(hex2.slice(5, 7), 16);
  const r = Math.round(r1 + (r2 - r1) * t);
  const g = Math.round(g1 + (g2 - g1) * t);
  const b = Math.round(b1 + (b2 - b1) * t);
  return `rgb(${r},${g},${b})`;
}

function getScrollTop() {
  if (window.innerWidth < 640) {
    return window.scrollY || window.pageYOffset;
  }
  return fullpage.scrollTop;
}

function getPageAt(scrollY) {
  for (let i = 0; i < pages.length; i++) {
    if (scrollY < pages[i].offsetTop + pages[i].offsetHeight) {
      return i;
    }
  }
  return pages.length - 1;
}

let ticking = false;

function updateGradient() {
  const scrollTop = getScrollTop();
  const idx = getPageAt(scrollTop);
  const lastIdx = pages.length - 1;

  const section = pages[idx];
  const progress = Math.max(0, Math.min(1, (scrollTop - section.offsetTop) / section.offsetHeight));
  const nextIdx = Math.min(idx + 1, lastIdx);

  const topColor = lerpColor(pageGradients[idx].top, pageGradients[nextIdx].top, progress);
  const bottomColor = lerpColor(pageGradients[idx].bottom, pageGradients[nextIdx].bottom, progress);

  overlay.style.background = `linear-gradient(180deg, ${topColor}, ${bottomColor})`;
  ticking = false;
}

function onScroll() {
  if (!ticking) {
    requestAnimationFrame(updateGradient);
    ticking = true;
  }
}

fullpage.addEventListener('scroll', onScroll);
window.addEventListener('scroll', onScroll);
window.addEventListener('resize', () => {
  if (!ticking) {
    requestAnimationFrame(updateGradient);
    ticking = true;
  }
});

// Entrance animation observer
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('active');
    } else {
      entry.target.classList.remove('active');
    }
  });
}, { threshold: 0.25 });

pages.forEach((page) => observer.observe(page));

updateGradient();
