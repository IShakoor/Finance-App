// Select key parts of html
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.signup-container form');
    const inputs = form.querySelectorAll('input');

    // Add effects to input boxes
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.style.boxShadow = '0 0 10px rgba(87, 196, 229, 0.8)';
        });

        input.addEventListener('blur', () => {
            input.style.boxShadow = 'none';
        });
    });
});