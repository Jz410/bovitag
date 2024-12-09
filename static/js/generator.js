
document.addEventListener('DOMContentLoaded', function() {
    // Function to list files in a directory
    function listFiles() {
        const folderInput = document.getElementById('input_folder');
        const previewContainer = document.getElementById('preview-container');
        
        // Clear previous previews
        previewContainer.innerHTML = '';
        
        // Send AJAX request to list files
        fetch('/list_files?folder=' + encodeURIComponent(folderInput.value))
            .then(response => response.json())
            .then(files => {
                if (files.length === 0) {
                    previewContainer.innerHTML = '<p>No image files found in the specified folder.</p>';
                    return;
                }
                
                files.slice(0, 10).forEach(file => {
                    const img = document.createElement('img');
                    img.src = '/get_image_preview?folder=' + encodeURIComponent(folderInput.value) + '&filename=' + encodeURIComponent(file);
                    img.classList.add('preview-image');
                    img.alt = file;
                    previewContainer.appendChild(img);
                });
            })
            .catch(error => {
                console.error('Error:', error);
                previewContainer.innerHTML = '<p>Error loading previews. Check the folder path.</p>';
            });
    }

    // Add event listener to trigger file listing
    const folderInput = document.getElementById('input_folder');
    folderInput.addEventListenaer('change', listFiles);
});

document.getElementById('input_folder').addEventListener('change', function(event) {
    const previewContainer = document.getElementById('preview-container');
    previewContainer.innerHTML = ''; // Limpiar contenido anterior

    const file = event.target.files[0]; // Obtener el primer archivo seleccionado

    if (file) {
        const reader = new FileReader();

        // Cuando la imagen esté lista, agregarla al contenedor
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.alt = file.name;
            img.style.maxWidth = '200px'; // Ajustar tamaño de la imagen
            img.style.margin = '10px';
            previewContainer.appendChild(img);
        }

        reader.readAsDataURL(file); // Leer la imagen como URL
    } else {
        previewContainer.innerHTML = '<p>No se seleccionó ninguna imagen.</p>';
    }
});

