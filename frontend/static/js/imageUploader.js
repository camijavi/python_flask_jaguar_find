const input = document.getElementById('fileUpload');
const preview = document.getElementById('preview');
const placeholder = document.getElementById('placeholder');

input.addEventListener('change', () => {
    const file = input.files[0];
    if (!file) return;

    if (preview.src.startsWith('blob:')) URL.revokeObjectURL(preview.src);

    preview.src = URL.createObjectURL(file);
    preview.style.display = 'block';
    placeholder.style.display = 'none';
});
