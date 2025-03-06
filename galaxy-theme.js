// Create star background
function createStarBackground() {
    const starBackground = document.createElement('div');
    starBackground.className = 'star-background';
    
    // Create 100 stars
    for (let i = 0; i < 100; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        
        // Random position
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        
        // Random size between 1px and 3px
        const size = Math.random() * 2 + 1;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        
        // Random animation delay
        star.style.animationDelay = `${Math.random() * 4}s`;
        
        starBackground.appendChild(star);
    }
    
    document.body.appendChild(starBackground);
}

// Add subtle parallax effect to cards
function addParallaxEffect() {
    const cards = document.querySelectorAll('.card');
    
    window.addEventListener('mousemove', (e) => {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const cardX = rect.left + rect.width / 2;
            const cardY = rect.top + rect.height / 2;
            
            const angleX = (mouseY - cardY / window.innerHeight) * 10;
            const angleY = (mouseX - cardX / window.innerWidth) * 10;
            
            card.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) translateY(-5px)`;
        });
    });
}

// Initialize theme
document.addEventListener('DOMContentLoaded', () => {
    createStarBackground();
    addParallaxEffect();
}); 