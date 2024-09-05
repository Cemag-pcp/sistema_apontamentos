function showLoading() {
    $('#loading').show();
}

function hideLoading() {
    $('#loading').hide();
}

// Função para formatar a data
function formatDate(dateString) {
    const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', options);
}

// Função para lidar com a lógica do botão "Consumir"
function handleConsumir(item) {
    const confirmed = confirm(`Você deseja consumir o item com número de série: ${item[3]}?`);
    if (confirmed) {
        fetch('/consumir-item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ numero_serie: item[3] })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Resposta do servidor:', data.message);
        })
        .catch(error => {
            console.error('Erro:', error);
        });
    } else {
        // Lógica para quando o usuário cancelar
        console.log('Consumir cancelado para:', item[3]);
    }
}

function updateTable() {
    const tbody = document.querySelector('#dataTableConsulta tbody');
    tbody.innerHTML = '';

    // Obtenha o filtro atual
    const recursoFiltro = document.getElementById('recursoFiltro').value.toLowerCase();

    // Filtra e ordena os dados
    const filteredData = window.receivedData.filter(item => 
        item[1].toLowerCase().includes(recursoFiltro)
    );

    // Ordena por data (assumindo que a data está na primeira posição do item)
    filteredData.sort((a, b) => new Date(a[0]) - new Date(b[0]));

    // Itera sobre os dados recebidos e adiciona linhas à tabela
    filteredData.forEach((item) => {
        const tr = document.createElement('tr');

        item.forEach((cell, index) => {
            const td = document.createElement('td');
            
            // Formata a data se for a primeira coluna (index 0)
            if (index === 0) {
                td.textContent = formatDate(cell);
            } else {
                td.textContent = cell;
            }

            switch (index) {
                case 0:
                    td.setAttribute('data-title', 'Data');
                    break;
                case 1:
                    td.setAttribute('data-title', 'Recurso');
                    break;
                case 2:
                    td.setAttribute('data-title', 'Qtde. Ped');
                    break;
                case 3:
                    td.setAttribute('data-title', 'Nr. Série');
                    break;
                case 4:
                    td.setAttribute('data-title', 'Consumir');
                    break;
            }

            tr.appendChild(td);
        });

        // Adiciona a coluna com o botão "Consumir" se a quarta coluna não estiver vazia
        const tdButton = document.createElement('td');
        if (item[3] !== '' && item[3] !== null) { // Verifica se a quarta coluna não está vazia
            const button = document.createElement('button');
            button.textContent = 'Consumir';
            button.className = 'btn btn-primary';
            button.onclick = function() {
                handleConsumir(item);
            };
            tdButton.appendChild(button);
        }
        tr.appendChild(tdButton);

        tbody.appendChild(tr);
    });
}
