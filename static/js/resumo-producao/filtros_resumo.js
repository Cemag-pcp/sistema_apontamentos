// document.addEventListener('DOMContentLoaded', function() {
//     const checkbox = document.getElementById('filtro_faltando_pecas');
//     const input = document.getElementById('filtrar_carreta');

//     checkbox.addEventListener('change', filter);
//     input.addEventListener('keyup', filter);
// });


// function filter() {
//     const filtroFaltandoPecas = document.getElementById('filtro_faltando_pecas').checked;
//     const filtroCarretaValue = document.getElementById('filtrar_carreta').value.toLowerCase();

//     const rows = document.querySelectorAll('#dataTableReuniao tbody tr');
//     rows.forEach(row => {
//         const hasFP = Array.from(row.cells).some(cell => cell.textContent.includes('FP -'));
//         const cellText = row.cells[0].textContent.toLowerCase();

//         let showRow = true;
//         if (filtroFaltandoPecas && !hasFP) {
//             showRow = false;
//         }
//         if (!cellText.includes(filtroCarretaValue)) {
//             showRow = false;
//         }
        
//         row.style.display = showRow ? '' : 'none';
//     });
// }

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
   
    // Adicionar a classe "active" à aba clicada
    var clickedTab = document.querySelector('[onclick="changeTab(\'' + tabName + '\')"]');
    clickedTab.classList.add('active');
}