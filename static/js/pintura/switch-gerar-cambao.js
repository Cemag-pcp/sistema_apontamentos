const switch1 = document.getElementById('customSwitch1');
const switch2 = document.getElementById('customSwitch2');
const tableBody = document.getElementById('tableBody');

// Atualiza a visibilidade das linhas da tabela com base no estado dos switches
function filterTable() {
    const typeToShow = switch1.checked ? 'PÓ' : (switch2.checked ? 'PU' : null);

    Array.from(tableBody.querySelectorAll('tr')).forEach(row => {
        const type = row.getAttribute('data-type');
        if (typeToShow === null || type === typeToShow) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Define a lógica dos switches
switch1.addEventListener('change', function () {
    if (switch1.checked) {
        switch2.checked = false;
    } else {
        switch2.checked = true;
    }
    filterTable(); // Atualiza a tabela após a mudança do switch1
});

switch2.addEventListener('change', function () {
    if (switch2.checked) {
        switch1.checked = false;
    } else {
        switch1.checked = true;
    }
    filterTable(); // Atualiza a tabela após a mudança do switch2
});

// Percorre cada linha do tbody
for (const row of tableBody.getElementsByTagName('tr')) {
    // Seleciona a célula da coluna de cor (6ª coluna, índice 5)
    const corCell = row.cells[5];
    
    if (corCell) {
        let cor = corCell.textContent.trim();
        
        // Substitui o valor de cor pelo valor correspondente
        if (cor === 'AN') {
            corCell.textContent = 'Azul'; 
            // corCell.style.backgroundColor = 'lightblue';
        } else if (cor === 'CO') { 
            corCell.textContent = 'Cinza';
            // corCell.style.backgroundColor = '#e1e1e1';
        } else if (cor === 'LC') { 
            corCell.textContent = 'Laranja';
            // corCell.style.backgroundColor = '#ffcc6e';
        } else if (cor === 'VJ') {
            corCell.textContent = 'Verde'; 
            // corCell.style.backgroundColor = '#bbffbb';
        } else if (cor === 'VM') {
            corCell.textContent = 'Vermelho'; 
            // corCell.style.backgroundColor = '#ff00006e';
        } else if (cor === 'AV') { 
            corCell.textContent = 'Amarelo';
            // corCell.style.backgroundColor = '#ffff94';
        }
    }
}

