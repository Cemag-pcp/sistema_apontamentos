$(document).ready(function () {
    $('#btnFinalizarOrdemParcial').on('click', function () {
        pecaFinalizada = $('#nomePecaApontada').val();
        quantidadePlanejada = parseInt($('#inputQuantidadePlanejada').val());
        codificacao = $('#codificacaoOrdem').val();
        celula = $('#celulaOrdem').val();
        textAreaObservacao = $('#textAreaObservacao_').val();
        dataHoraInicio = $('#dataHoraInicio').val();
        operadorInputModal_1 = $('#operadorInputModal_1').val();
        inputQuantidadeRealizada = $('#inputQuantidadeRealizada').val();
        dataCarga = $('#dataCargaFinalizacao').val();
        idPecaEmProcesso = $('#idPecaEmProcesso').val();
        origem = $('#origemPecaEmProcesso').val();

        if (pecaFinalizada.split(' - ')[1]) {
            descricao = pecaFinalizada.split(' - ')[1];
        } else {
            descricao = '';
        }

        dados = {
            codigo: pecaFinalizada.split(' - ')[0],
            descricao: descricao,
            qtdePlanejada: quantidadePlanejada,
            codificacao: codificacao,
            celula: celula,
            textAreaObservacao: textAreaObservacao,
            dataHoraInicio: dataHoraInicio,
            operadorInputModal_1: operadorInputModal_1,
            inputQuantidadeRealizada: inputQuantidadeRealizada,
            dataCarga: formatarData(dataCarga),
            idPecaEmProcesso: idPecaEmProcesso,
            origem: origem
        }

        if (inputQuantidadeRealizada === '') {
            showAndHideAlert('Por favor informe a quantidade.', 2000);
            return;
        };


        if (parseInt($('#inputQuantidadeRealizada').val()) < 0 || parseInt($('#inputQuantidadeRealizada').val()) >= quantidadePlanejada ) {
            showAndHideAlert('Por favor informe a quantidade correta.', 2000);
            return;
        };

        if (operadorInputModal_1 === '') {
            showAndHideAlert('Por favor informar o operador.', 2000);
            return;
        }

        $('#confimarFimApontamentoParcial').css('display','block');
        $('#confimarFimApontamento').css('display','none');
        $('#modalExecucaoApontamento').modal('hide');
        $('#modalConfirmarApontamentoFinalizado').modal('show');

        $("#pecaTextoFinalizar").text('Deseja finalizar parcialmente a peça '+pecaFinalizada);
        $("#confirmarApontamento").text('Confirmar Apontamento Parcial');
    });

    $('#confimarFimApontamentoParcial').on('click', function () {

        pecaFinalizada = $('#nomePecaApontada').val();

        quantidadePlanejada = parseInt($('#inputQuantidadePlanejada').val());
        codificacao = $('#codificacaoOrdem').val();
        celula = $('#celulaOrdem').val();
        textAreaObservacao = $('#textAreaObservacao_').val();
        dataHoraInicio = $('#dataHoraInicio').val();
        operadorInputModal_1 = $('#operadorInputModal_1').val();
        inputQuantidadeRealizada = parseInt($('#inputQuantidadeRealizada').val());
        dataCarga = $('#dataCargaFinalizacao').val();
        idPecaEmProcesso = $('#idPecaEmProcesso').val();
        origem = $('#origemPecaEmProcesso').val();

        quantidadePlanejada = quantidadePlanejada - inputQuantidadeRealizada;
    
        dados = {
            codigo: pecaFinalizada.split(' - ')[0],
            descricao: descricao,
            qtdePlanejada: quantidadePlanejada,
            codificacao: codificacao,
            celula: celula,
            textAreaObservacao: textAreaObservacao,
            dataHoraInicio: dataHoraInicio,
            operadorInputModal_1: operadorInputModal_1,
            inputQuantidadeRealizada: inputQuantidadeRealizada,
            dataCarga: formatarData(dataCarga),
            idPecaEmProcesso: idPecaEmProcesso,
            origem: origem,
            parcial:"Parcial"
        }
    
        $.ajax({
            type: 'POST',
            url: '/finalizar-peca-em-processo/estamparia',
            contentType: 'application/json',  // Define o tipo de conteúdo como JSON
            data: JSON.stringify(dados),
            success: function (data) {
                hideLoading();
                showAndHideSuccessAlert('Salvo.', 2000);
                chamarAPI();
                chamarAPIInterrompidas();
                $('#modalConfirmarApontamentoFinalizado').modal('hide');
            },
            error: function (error) {
                console.error('Erro na solicitação POST:', error);
                hideLoading();
                $('#modalConfirmarApontamentoFinalizado').modal('hide');
            }
        });
    });

    $("#desistirFimApontamento").on('click',function () {
        console.log('Printou')
        $('#modalConfirmarApontamentoFinalizado').modal('hide');
        $('#modalExecucaoApontamento').modal('show');
    })
});