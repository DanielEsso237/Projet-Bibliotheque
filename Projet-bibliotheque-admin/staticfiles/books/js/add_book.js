document.addEventListener('DOMContentLoaded', function () {
    console.log('JavaScript chargé depuis add_book.js !');

    const isPhysicalCheckbox = document.getElementById('id_is_physical');
    const ebookFileField = document.getElementById('ebook-file-field');
    const quantityField = document.getElementById('quantity-field');
    const ebookFileInput = document.getElementById('id_ebook_file');
    const quantityInput = document.getElementById('id_quantity');
    const form = document.querySelector('form');

    if (!isPhysicalCheckbox || !ebookFileField || !quantityField || !ebookFileInput || !quantityInput || !form) {
        console.log('Erreur : un élément n\'a pas été trouvé', {
            isPhysicalCheckbox: isPhysicalCheckbox,
            ebookFileField: ebookFileField,
            quantityField: quantityField,
            ebookFileInput: ebookFileInput,
            quantityInput: quantityInput,
            form: form
        });
        return;
    }

    

    function toggleFields() {
        const isPhysical = isPhysicalCheckbox.checked;
        console.log('État de la case "Livre physique ?":', isPhysical);

        ebookFileField.style.display = isPhysical ? 'none' : 'block';
        quantityField.style.display = isPhysical ? 'block' : 'none';

        if (isPhysical) {
            ebookFileInput.value = '';
            console.log('Champ ebook_file masqué, valeur réinitialisée');
        } else {
            quantityInput.value = '0';
            console.log('Champ quantity masqué, valeur réinitialisée à 0');
        }
    }

    isPhysicalCheckbox.addEventListener('change', toggleFields);
    toggleFields();

    // Afficher la modale de succès si elle existe
    const successModal = document.getElementById('successModal');
    if (successModal) {
        // Initialiser et ouvrir la modale Bootstrap
        const modal = new bootstrap.Modal(successModal, {
            backdrop: 'static', // Empêche la fermeture en cliquant à l'extérieur
            keyboard: false // Empêche la fermeture avec la touche Échap
        });
        modal.show();
        
    } else {
        console.log('Aucune modale de succès trouvée dans le DOM');
    }
});