function getResumo() {
    var url = '/resumos-geral?datainicio=2024-04-29&datafim=2024-04-30';

    var xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.onload = function() {
        if (xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            // Manipular os dados recebidos da API aqui
            console.log(data);
        } else {
            console.error('Erro ao chamar a API:', xhr.statusText);
        }
    };
    xhr.onerror = function() {
        console.error('Erro ao chamar a API.');
    };
    xhr.send();
};