function filtrarTabela(filtroId, tabelaId, somaId) {
    var input = document.getElementById(filtroId).value.toLowerCase();
    var table = document.getElementById(tabelaId);
    var totalElement = document.getElementById(somaId);
    var rows = table.getElementsByTagName('tr');
    var totalSum = 0;

    for (var i = 1; i < rows.length; i++) { // start at 1 to skip the header row
        var cells = rows[i].getElementsByTagName('td');
        var causa = cells[1].textContent || cells[1].innerText;
        var quantidade = parseInt(cells[2].textContent || cells[2].innerText, 10);
        if (causa.toLowerCase().startsWith(input)) {
            rows[i].style.display = '';
            totalSum += quantidade;
        } else {
            rows[i].style.display = 'none';
        }
    }

    totalElement.textContent = totalSum;
}

document.getElementById('filtro_total_causas').addEventListener('input', function() {
    filtrarTabela('filtro_total_causas', 'dataTableCausas', 'total_causas');
});

document.getElementById('filtro_liquida').addEventListener('input', function() {
    filtrarTabela('filtro_liquida', 'dataTableCausasLiquida', 'soma_total_liquida');
});

document.getElementById('filtro_po').addEventListener('input', function() {
    filtrarTabela('filtro_po', 'dataTableCausasPo', 'soma_total_po');
});