function filtrarDatasPorCarretas() {
    showLoading();
    const dataInicial = document.getElementById('dataReuniaoInicial').value;
    const dataFinal = document.getElementById('dataReuniaoFinal').value;

    // Crie o objeto com os dados a serem enviados
    const data = {
        data_inicial: dataInicial,
        data_final: dataFinal
    };

    // Envie os dados para o servidor usando fetch
    fetch('/consultar-carreta-reuniao', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        console.log('Sucesso:', result);

        window.receivedData = result.ImportarDados;

        // Atualize a tabela com os dados recebidos e o filtro atual
        updateSearch(dataInicial,dataFinal);
        
        hideLoading();
        document.getElementById('campoTableConsulta').style.display = 'block';
        document.getElementById('consumir_tudo').style.display = 'block';
    })
    .catch(error => {
        console.error('Erro:', error);
        hideLoading();
    });
}

document.getElementById('filtrar_datas_por_carretas').addEventListener('click', filtrarDatasPorCarretas);

document.getElementById('recursoFiltro').addEventListener('input', function() {
    if (window.receivedData) {
        updateSearch();
    }
});