function filtrarTabela(filtroId, tabelaId, somaId) {
    var select = document.getElementById(filtroId);
    var selectedValues = Array.from(select.selectedOptions).map(option => option.value.toLowerCase());
    var table = document.getElementById(tabelaId);
    var totalElement = document.getElementById(somaId);
    var rows = table.getElementsByTagName('tr');
    var totalSum = 0;

    // Se nenhum valor estiver selecionado, exibir todas as linhas
    var mostrarTodas = selectedValues.length === 0;

    for (var i = 1; i < rows.length; i++) { // start at 1 to skip the header row
        var cells = rows[i].getElementsByTagName('td');
        var causa = cells[1].textContent || cells[1].innerText;
        var quantidade = parseInt(cells[2].textContent || cells[2].innerText, 10);
        if (mostrarTodas || selectedValues.includes(causa.toLowerCase())) {
            rows[i].style.display = '';
            totalSum += quantidade;
        } else {
            rows[i].style.display = 'none';
        }
    }

    totalElement.textContent = totalSum;
}

$('#filtro_total_causas').on('change', function() {
    filtrarTabela('filtro_total_causas', 'dataTableCausas', 'total_causas');
});

$('#filtro_liquida').on('change', function() {
    filtrarTabela('filtro_liquida', 'dataTableCausasLiquida', 'soma_total_liquida');
});

$('#filtro_po').on('change', function() {
    filtrarTabela('filtro_po', 'dataTableCausasPo', 'soma_total_po');
});

$('#filtro_total_causas').select2({
    placeholder: "Selecione as causas",
    allowClear: true,
    width: 'resolve'
});

$('#filtro_liquida').select2({
    placeholder: "Selecione as causas dos tubos",
    allowClear: true,
    width: 'resolve'
});

$('#filtro_po').select2({
    placeholder: "Selecione as causas dos cilindros",
    allowClear: true,
    width: 'resolve'
});

