// Confirmación para eliminación
document.addEventListener('DOMContentLoaded', function() {
    // Confirmación para enlaces de eliminación
    const deleteLinks = document.querySelectorAll('a[href*="eliminar"]');
    
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que deseas eliminar este libro?')) {
                e.preventDefault();
            }
        });
    });
    
    // Validación de formularios
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Por favor complete todos los campos obligatorios.');
            }
        });
    });
});