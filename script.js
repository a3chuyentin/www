const pages = document.querySelectorAll('#fullpage > section, #fullpage > footer');

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
