document.querySelector('input[type="file"]').addEventListener('change',function () {
    const fileInput = this;
    const btnSalvarPlanejamento = document.getElementById('btnSalvarPlanejamento')
    const btnSalvarArquivos = document.getElementById('btnSalvarArquivos')

    if(fileInput.files.length > 0){
        btnSalvarArquivos.classList.remove('d-none')
        btnSalvarPlanejamento.classList.add('d-none')
    } else {
        btnSalvarPlanejamento.classList.remove('d-none')
        btnSalvarArquivos.classList.add('d-none')
    }

})

document.getElementById('inserir-arquivos').addEventListener('change', function(event) {
    const input = event.target;
    const label = input.nextElementSibling;
    const fileName = input.files.length > 0 ? input.files[0].name : 'Inserir arquivo';
    label.textContent = fileName;
});