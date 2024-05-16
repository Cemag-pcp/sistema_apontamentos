function baixar_resumo(dataLevantamentoInicialStr,dataLevantamentoFinalStr){
    
    $.ajax({
        url: '/baixar-resumo/levantamento',
        type: 'GET',
        data: { dataInicio: dataLevantamentoInicialStr, dataFinal: dataLevantamentoFinalStr },
        xhrFields: {
            responseType: 'blob' // Define o tipo de resposta para 'blob' (binário)
        },
        success: function (response) {
            $('#loading').hide();
            var blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }); // Cria um Blob a partir da resposta
            var link = document.createElement('a'); // Cria um elemento <a> para o download
            link.href = window.URL.createObjectURL(blob); // Define o URL do link como o URL do Blob
            link.download = 'resumos.xlsx'; // Define o nome do arquivo a ser baixado
            document.body.appendChild(link); // Adiciona o link ao corpo do documento
            link.click(); // Simula um clique no link para iniciar o download
            document.body.removeChild(link); // Remove o link do corpo do documento após o download
        },
        error: function (xhr, status, error) {
            $('#loading').hide();
            console.error('Erro ao baixar o arquivo:', error);
        }
    });
    
}

function getStatusIcon(icon) {

    if (icon === 'checked') {
        return '<i style="color:red;" class="fas fa-times"></i>'; // Exemplo de ícone de x (você pode substituir pelo ícone desejado)
    } else {
        return '<i style="color:green;" class="fas fa-check"></i>'; // Exemplo de ícone de check (você pode substituir pelo ícone desejado)
    }
    
}

function carretCadastradas(bodyCarretasCadastradas,carretasCadastradas) {

    carretasCadastradas.forEach(function (item) {
        var statusIcon = (item[1] === '') ? 'checked' : 'x';
        var rowBodyCarretasCadastradas = '<tr>' +
            '<td>' + item[0] + '</td>' + // carreta
            '<td>' + getStatusIcon(statusIcon) + '</td>' + // status
            '</tr>';
        $(rowBodyCarretasCadastradas).appendTo(bodyCarretasCadastradas);
    });

}