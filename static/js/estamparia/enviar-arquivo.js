document.getElementById('btnSalvarArquivos').addEventListener('click', function() {
    showLoading();
    const fileInput = document.querySelector('input[type="file"]');
    const file = fileInput.files[0]; // Obtém o primeiro arquivo selecionado
    const dataInput = document.getElementById('inputData_').value; // Obtém o valor da data

    if (file && dataInput) {
        // Cria um objeto FormData para enviar o arquivo e a data
        const formData = new FormData();
        formData.append('arquivo', file); // 'arquivo' é o nome do campo no backend
        formData.append('data', dataInput); // 'data' é o nome do campo no backend

        // Envia o arquivo e a data usando fetch
        fetch('/api/enviar-arquivos/estamparia', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                return response.json(); // Se o backend retornar JSON
            } else {
                throw new Error(response.json());
            }
        })
        .then(data => {
            // Sucesso, faça algo com a resposta (data)
            if (data.error) {
                // Exibe a mensagem de erro
                alert(`Erro: ${data.error}`);
            } else {
                // Exibe a mensagem de sucesso
                alert(`Sucesso: ${data.message}`);
            }
            location.reload()
        })
        .catch(error => {
            // Tratamento de erro
            hideLoading();
            alert(`${error}`);
            console.error('Erro:', error);
        });
    } else {
        hideLoading();
        alert('Por favor, selecione um arquivo e insira uma data antes de enviar.');
    }
});