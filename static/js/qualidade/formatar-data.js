function formatarDatasDaTabela(tabela_inspecoes) {
    var linhas = document.querySelectorAll('#' + tabela_inspecoes + ' .data-inspecao');
    linhas.forEach(function(celula) {
        var dataOriginal = celula.textContent.trim();
        console.log(dataOriginal)
        if (dataOriginal) {
            var dataFormatada = formatarDataBrComHora(dataOriginal,0);
            celula.textContent = dataFormatada;
            console.log(dataFormatada)
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    formatarDatasDaTabela('dataTableAinspecionarEstamparia')
    formatarDatasDaTabela('dataTableinspecionadosEstamparia')
    formatarDatasDaTabela('dataTableReinspecaoEstamparia')
    formatarDatasDaTabela('tabela-inspecoes')
    formatarDatasDaTabela('tabela-reteste')
});