// Iniciar produção 

document.getElementById('btnSalvar').addEventListener('click', function () {

    showLoading();

    var peca = document.getElementById('userInput').value;
    var dt_planejada = document.getElementById('inputData').value;
    var qt_planejada = document.getElementById('inputQuantidade').value;

    let _data = {
        peca: peca,
        dt_planejada: dt_planejada,
        qt_planejada: qt_planejada,

    };

    if (!inputData || !dt_planejada || !qt_planejada) {
        alert('Preencha todos os campos.');
        hideLoading();
        return;
    };


    fetch('/iniciar-producao-serralheria', {
        method: "POST",
        body: JSON.stringify(_data),
        headers: { "Content-type": "application/json; charset=UTF-8" }
    })
        .then(response => {
            // Retorna a promessa JSON

            return response.json();
        })
        .then(json => {
            console.log(json);
            $('#modalPecaFora').modal('hide');
            hideLoading();
            chamarAPI();
            chamarAPIInterrompidas();
        })
        .catch(err => {
            console.log(err);
            hideLoading();
        });

    document.getElementById('userInput').value = '';
    document.getElementById('inputData').value = '';
    document.getElementById('inputQuantidade').value = '';


});

document.addEventListener('DOMContentLoaded', () => {
    chamarAPI();
    chamarAPIInterrompidas();
});

document.getElementById('enviarMotivo').addEventListener('click', function () {
    
    idPecaInterromper = $('#idPecaInterromper').val();
    motivoInterrompido = $('#idMotivosParada option:selected').text();

    showLoading();

    fetch('/api/pecas-interrompida/serralheria', {
        method: "POST",
        body: JSON.stringify({ id: idPecaInterromper, motivo: motivoInterrompido }),
        headers: { "Content-type": "application/json; charset=UTF-8" }
    })
        .then(response => {
            // Retorna a promessa JSON

            return response.json();
        })
        .then(json => {
            console.log(json);
            $('#modalMotivoInterrompido').modal('hide');
            hideLoading();
            chamarAPI();
            chamarAPIInterrompidas();
        })
        .catch(err => {
            console.log(err);
            hideLoading();
        });

});

document.getElementById('confimarRetornoProducao').addEventListener('click', function () {
    
    idPecaRetornar = $('#retornarPecaProducao').val();

    showLoading();

    fetch('/api/pecas-retornou/serralheria', {
        method: "POST",
        body: JSON.stringify({ id: idPecaRetornar }),
        headers: { "Content-type": "application/json; charset=UTF-8" }
    })
        .then(response => {
            // Retorna a promessa JSON

            return response.json();
        })
        .then(json => {

            $('#modalConfirmarInicioProducao').modal('hide');
            hideLoading();
            chamarAPI();
            chamarAPIInterrompidas();
        })
        .catch(err => {
            console.log(err);
            hideLoading();
        });

});

$('#desistirMotivo').on('click', function () {
    $('#modalMotivoInterrompido').modal('hide');
})

$('#desistirInicioProducao').on('click', function () {
    $('#modalConfirmarInicioProducao').modal('hide');
})


function chamarAPI() {
    fetch("/api/consulta-pecas-em-processo/serralheria")
        .then(response => response.json())
        .then(data => {
            // Limpa o conteúdo atual dos cards
            document.getElementById('cardsContainer').innerHTML = "";
            processarDados(data);
        })
        .catch(error => console.error('Erro ao chamar a API:', error));
}

function processarDados(data) {

    data.forEach(peca => {
        // Aqui você pode continuar com o processamento dos dados e a criação dos cards
        var cardHtml = `
    <div class="col-sm-6 mb-2">
        <div class="card shadow mb-4">
            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-secondary"><small>${peca[2]}</small></h6>
                <span id="contador-${peca[0]}" class="badge badge-primary badge-pill"></span>   
                <input style="display:none;" id="dataInicial-${peca[0]}" type="datetime" value="${peca[3]}">
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-sm-6">
                        <h6 class="m-0 font-weight-bold text-primary"><small><strong>Qt. Planejada:</strong> ${peca[7]}</small></h6>
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <button type="button" class="btn btn-info btn-finalizar-producao"
                    onclick="finalizarPeca(${peca[0]})">Finalizar
                </button>
                <button type="button" class="btn btn-warning btn-interromper-producao"
                    onclick="interromperProcesso(${peca[0]})">Interromper
                </button>
            </div>
        </div>
    </div>`;
        document.getElementById('cardsContainer').innerHTML += cardHtml;
    });

    atualizarContador(data);

    setInterval(() => atualizarContador(data), 1000);
}

function chamarAPIInterrompidas() {
    fetch("/api/consulta-pecas-interrompidas/serralheria")
        .then(response => response.json())
        .then(data => {
            // Limpa o conteúdo atual dos cards
            document.getElementById('cardsContainerInterrompida').innerHTML = "";

            processarDadosInterrompida(data);

        })
        .catch(error => console.error('Erro ao chamar a API:', error));
}

function processarDadosInterrompida(data) {
    data.forEach(peca => {
        var cardHtml = `
        <div class="col-sm-6 mb-2">
            <div class="card shadow mb-4">
                <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                    <h6 class="m-0 font-weight-bold text-secondary"><small>${peca[2]}</small></h6>
                    <span id="contador-${peca[0]}" class="badge badge-primary badge-pill"></span>  
                    <input style="display:none;" id="dataInicial-${peca[0]}" type="datetime" value="${peca[3]}">
                </div>
                <div class="card-body">
                    <h6 class="m-0 font-weight-bold text-primary"><small><strong>Qt. Planejada:</strong> ${peca[7]}</small></h6>
                    <h6 class="m-0 font-weight-bold text-primary"><small><strong>Motivo:</strong> ${peca[6]}</small></h6>
                </div>
                <div class="card-footer">
                    <button type="button" class="btn btn-info btn-retornar-producao"
                        onclick="retornarPeca(${peca[0]})">Retornar
                    </button>
                </div>
            </div>
        </div>`;

        document.getElementById('cardsContainerInterrompida').innerHTML += cardHtml;

    });

    atualizarContador(data);

    setInterval(() => atualizarContador(data), 1000);
}

function formatarData(dataString) {
    var data = new Date(dataString);
    return data.toISOString().slice(0, 19);
}

// Função para finalizar a peça e mostrar informações
function finalizarPeca(id) {
    // Exemplo: Mostrar informações em um alerta

    showLoading();

    var dados = {
        id_peca: id  // Substitua pelos dados reais que você deseja enviar
    };

    $.ajax({
        url: '/consulta-id-em-processo/serralheria',
        method: 'GET',
        contentType: 'application/json',
        data: $.param(dados),
        success: function (data) {
            $('#nomePecaApontada').val(data[0][2]);
            $('#inputQuantidadePlanejada').val(data[0][7]);
            $('#dataHoraInicio').val(formatarData(data[0][3]));
            $('#codificacaoOrdem').val(data[0][4]);
            $('#chavePecaProcesso').val(data[0][1]);
            $('#idPecaEmProcesso').val(data[0][0]);

            $('#inputQuantidadeRealizada').val();
            $('#textAreaObservacao_').val();
            $('#operadorInputModal_1').val();

            hideLoading();
            $('#modalExecucaoApontamento').modal('show');

        },
        error: function (err) {
            console.error('Erro:', err);
            hideLoading();
        }
    });

    // Aqui você pode adicionar lógica adicional conforme necessário
}

function atualizarContador(data) {

    data.forEach(peca => {

        const agora = new Date();
        const dataInicial = new Date(formatarData(peca[3]));
        const diferenca = agora.getTime() - dataInicial.getTime();

        const segundos = Math.floor(diferenca / 1000);
        const minutos = Math.floor(segundos / 60);
        const horas = Math.floor(minutos / 60);
        const dias = Math.floor(horas / 24); // Calcula o número de dias

        const segundosRestantes = segundos % 60;
        const minutosRestantes = minutos % 60;
        const horasRestantes = horas % 24;

        const formatoTempo = `${dias.toString().padStart(2, '0')} : ${horasRestantes.toString().padStart(2, '0')} : ${minutosRestantes.toString().padStart(2, '0')} : ${segundosRestantes.toString().padStart(2, '0')}`;

        document.getElementById(`contador-${peca[0]}`).textContent = formatoTempo;

    })
}

function interromperProcesso(id) {

    $('#modalMotivoInterrompido').modal('show');

    $('#idPecaInterromper').val(id);

}

function retornarPeca(id) {

    $('#modalConfirmarInicioProducao').modal('show');
    document.getElementById('modalConfirmarInicioProducaoLabel').textContent = 'Retorno'
    document.getElementById('pecaTextoModalIniciar').textContent = ''
    document.getElementById('labelConfirmar').textContent = 'Confirmar retorno para produção?'

    $('#retornarPecaProducao').val(id);

    var botaoRetornar = document.getElementById('confimarRetornoProducao');
    botaoRetornar.style.display = 'block';

    var botaoIniciar = document.getElementById('confimarInicioProducao');
    botaoIniciar.style.display = 'none';

}