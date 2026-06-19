// Images Management JavaScript

document.addEventListener('DOMContentLoaded', function() {
  const fileRadio = document.getElementById('source-file');
  const urlRadio = document.getElementById('source-url');
  const fileGroup = document.getElementById('file-input-group');
  const urlGroup = document.getElementById('url-input-group');
  
  function toggleSource() {
    if (fileRadio.checked) {
      fileGroup.classList.remove('hidden');
      urlGroup.classList.add('hidden');
    } else {
      fileGroup.classList.add('hidden');
      urlGroup.classList.remove('hidden');
    }
  }
  
  fileRadio.addEventListener('change', toggleSource);
  urlRadio.addEventListener('change', toggleSource);
  toggleSource();

  // Edit modal source toggle elements
  const editFileRadio = document.getElementById('edit-source-file');
  const editUrlRadio = document.getElementById('edit-source-url');
  const editFileGroup = document.getElementById('edit-file-input-group');
  const editUrlGroup = document.getElementById('edit-url-input-group');
  
  function toggleEditSource() {
    if (editFileRadio.checked) {
      editFileGroup.classList.remove('hidden');
      editUrlGroup.classList.add('hidden');
    } else {
      editFileGroup.classList.add('hidden');
      editUrlGroup.classList.remove('hidden');
    }
  }
  
  editFileRadio.addEventListener('change', toggleEditSource);
  editUrlRadio.addEventListener('change', toggleEditSource);
  toggleEditSource();
});