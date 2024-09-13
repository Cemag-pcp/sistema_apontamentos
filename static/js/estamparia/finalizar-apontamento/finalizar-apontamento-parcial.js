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
        inputQuantidadeMorta = $('#inputQuantidadeMorta').val();
        dataCarga = $('#dataCargaFinalizacao').val();
        idPecaEmProcesso = $('#idPecaEmProcesso').val();
        origem = $('#origemPecaEmProcesso').val();

        if (pecaFinalizada.split(' - ')[1]) {
            descricao = pecaFinalizada.split(' - ')[1];
        } else {
            descricao = '';
        }

        if (inputQuantidadeRealizada === '' || inputQuantidadeMorta === '') {
            showAndHideAlert('Por favor informe a quantidade realizada e a quantidade morta', 2000);
            return;
        };


        if (parseInt($('#inputQuantidadeRealizada').val()) < 0) {
            showAndHideAlert('Por favor informe a quantidade correta de peças realizadas.', 2000);
            return;
        };

        if (parseInt($('#inputQuantidadeMorta').val()) < 0) {
            showAndHideAlert('Por favor informe a quantidade correta de peças mortas.', 2000);
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
        
        showLoading();

        var pecaFinalizada = $('#nomePecaApontada').val();

        var quantidadePlanejada = parseInt($('#inputQuantidadePlanejada').val());
        var codificacao = $('#codificacaoOrdem').val();
        var celula = $('#celulaOrdem').val();
        var textAreaObservacao = $('#textAreaObservacao_').val();
        var dataHoraInicio = $('#dataHoraInicio').val();
        var operadorInputModal_1 = $('#operadorInputModal_1').val();
        var inputQuantidadeRealizada = parseInt($('#inputQuantidadeRealizada').val());
        var inputQuantidadeMorta = parseInt($('#inputQuantidadeMorta').val());
        var dataCarga = $('#dataCargaFinalizacao').val();
        var idPecaEmProcesso = $('#idPecaEmProcesso').val();
        var origem = $('#origemPecaEmProcesso').val();

        quantidadePlanejada = quantidadePlanejada - inputQuantidadeRealizada;
    
        var partes = pecaFinalizada.split(' - ');
        var codigo = partes[0];
        var descricao = partes.slice(1).join(' - ');

        dados = {
            codigo: codigo,
            descricao: descricao,
            qtdePlanejada: quantidadePlanejada,
            codificacao: codificacao,
            celula: celula,
            textAreaObservacao: textAreaObservacao,
            dataHoraInicio: dataHoraInicio,
            operadorInputModal_1: operadorInputModal_1,
            inputQuantidadeRealizada: inputQuantidadeRealizada,
            inputQuantidadeMorta:inputQuantidadeMorta,
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
                updateTable();
                $('#modalConfirmarApontamentoFinalizado').modal('hide');
                location.reload();
            },
            error: function (error) {
                console.error('Erro na solicitação POST:', error);
                hideLoading();
                $('#modalConfirmarApontamentoFinalizado').modal('hide');
                location.reload();
            }
        });
    });

    $("#desistirFimApontamento").on('click',function () {
        console.log('Printou')
        $('#modalConfirmarApontamentoFinalizado').modal('hide');
        $('#modalExecucaoApontamento').modal('show');
    })
});