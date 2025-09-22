function toggleMenu() {
  const nav = document.getElementById('nav');
  nav.classList.toggle('active');
}

document.addEventListener('DOMContentLoaded', () => {
    const steps = document.querySelectorAll('.timeline-step');

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
        }
      });
    }, { threshold: 0.3 });

    steps.forEach(step => observer.observe(step));
  });