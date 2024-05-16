document.addEventListener('DOMContentLoaded', function() {
    const input_filtrar_processo = document.getElementById('filtrar_processo');
    const input_filtrar_conjunto = document.getElementById('filtrar_conjunto');

    input_filtrar_processo.addEventListener('keyup', function(){
        filter('filtrar_processo',1)
    });
    input_filtrar_conjunto.addEventListener('keyup', function(){
        filter('filtrar_conjunto',2)
    });
});


function filter(filterId,indexCollumn) {
    const filtroProcessoValue = document.getElementById(filterId).value.toLowerCase();

    const rows = document.querySelectorAll('#dataTableBaseFinal tbody tr');
    rows.forEach(row => {
        const cellText = row.cells[indexCollumn].textContent.toLowerCase();

        let showRow = true;

        if (!cellText.startsWith(filtroProcessoValue)) {
            showRow = false;
        }
        
        row.style.display = showRow ? '' : 'none';
    });
}

function changeTab(tabName) {
    // Ocultar todas as tabelas
    var tables = document.querySelectorAll('.table-body');
    tables.forEach(function(table) {
        table.style.display = 'none';
    });
   
    // Mostrar a tabela correspondente à aba clicada
    document.getElementById(tabName + 'Table').style.display = 'block';
   
    // Remover a classe "active" de todas as abas
    var tabs = document.querySelectorAll('.nav-link');
    tabs.forEach(function(tab) {
        tab.classList.remove('active');
    });

    tabName === 'reuniao' ? document.getElementById('filtros_resumo_reuniao').style.display = 'none' : document.getElementById('filtros_resumo_reuniao').style.display = 'flex'

    console.log(tabName === 'reuniao')
   
    // Adicionar a classe "active" à aba clicada
    var clickedTab = document.querySelector('[onclick="changeTab(\'' + tabName + '\')"]');
    clickedTab.classList.add('active');
}