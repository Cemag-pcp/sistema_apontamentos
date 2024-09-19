function modalInspecaoEstamparia(id_inspecao,maquina,conjunto,quantidade,codigo) {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $('#inspecionarEstampariaLabel').text(id_inspecao)

    $("#inputMaquina_estamparia").val(maquina);
    $("#inputConjunto_estamparia").val(conjunto);
    $('#inputPecasProduzidas_estamparia').val(quantidade);
    $('#codigo_estamparia').val(codigo);

    $("#causa_estamparia").prop('disabled',false);
    $("#outraCausa_estamparia").val('');
    $("#outraCausa_estamparia").prop('disabled',true);
    $("#causasEstamparia-0").val('')
    $("#inspecao_total").val('')
    $("#quantidade_causas_estamparia-0").val('')
    $("#inputConformidades_estamparia").val(0)
    $("#inputNaoConformidades_estamparia").val(0)

    $('#data_inspecao_estamparia').val(today.toLocaleDateString());

    const tbody = $(".tabela_editavel");
    tbody.empty();

    if(parseInt(quantidade) < 3) {
        for (let i = 0; i < quantidade; i++) {
            tbody.append(`<tr>
                    <td contenteditable="true" class="editable"></td>
                    <td contenteditable="true" class="editable"></td>
                    <td contenteditable="true" class="editable"></td>
                    <td contenteditable="true" class="editable"></td>
                    <td class="checkbox-container"><input type="checkbox" class="checkbox"></td>
                    <td class="checkbox-container"><input type="checkbox" class="checkbox"></td>
                </tr>
            `);
        }
    } else {
        for (let i = 0; i < 3; i++) {
            tbody.append(`<tr>
                    <td contenteditable="true" class="editable"></td>
                    <td contenteditable="true" class="editable"></td>
                    <td contenteditable="true" class="editable"></td>
                    <td contenteditable="true" class="editable"></td>
                    <td class="checkbox-container"><input type="checkbox" class="checkbox"></td>
                    <td class="checkbox-container"><input type="checkbox" class="checkbox"></td>
                </tr>
            `);
        }
    }

    initializeCheckboxLogic('.tabela_editavel', 'selectContainer', 'inputConformidades_estamparia', 'inputNaoConformidades_estamparia', 'outraCausa_estamparia');

    $('#inspecionarEstamparia').modal('show');

}

$('#inputConformidades_estamparia').on('blur', function() {
    let pecasInspecionadasSolda = parseInt($('#inputPecasInspecionadas_estamparia').val());
    let numConformidadesSolda = parseInt($('#inputConformidades_estamparia').val());
    let numNaoConformidadesSolda = $('#inputNaoConformidades_estamparia');

    if(numConformidadesSolda > pecasInspecionadasSolda || numNaoConformidadesSolda.val() > pecasInspecionadasSolda || numConformidadesSolda < 0){
        alert("Preencha o número de peças inspecionadas")
        $('#inputConformidades_estamparia').val('')
        numNaoConformidadesSolda.val('')
        return
    } 
})

$('#inputConformidades_estamparia').on('input', function() {
    
    let pecasInspecionadasSolda = $('#inputPecasInspecionadas_estamparia').val();
    let numConformidadesSolda = parseInt($('#inputConformidades_estamparia').val());
    let numNaoConformidadesSolda = $('#inputNaoConformidades_estamparia');
    let outroCausaSolda = $("#outraCausa_estamparia");
    let containerCausas = $("#selectContainer");
    
    let origemInspecaoSoldaReinspecionadas = $('#origemInspecaoCol_estamparia');

    numNaoConformidadesSolda.val(pecasInspecionadasSolda - numConformidadesSolda);

    if(pecasInspecionadasSolda === ''){
        alert("Preencha o número de peças inspecionadas")
        $('#inputConformidades_estamparia').val('')
        numNaoConformidadesSolda.val('')
        return
    } 

    if(numConformidadesSolda === ''){
        numNaoConformidadesSolda.val('')
    } 

    if(numNaoConformidadesSolda.val() === '' || numNaoConformidadesSolda.val() <= 0 || numConformidadesSolda < 0){
        outroCausaSolda.prop('disabled',true);
        containerCausas.css('display','none')
        $("#causasEstamparia-0").val('')
        $("#quantidade_causas_estamparia-0").val('')
        outroCausaSolda.val('')
        origemInspecaoSoldaReinspecionadas.css('display','none')
        origemInspecaoSoldaReinspecionadas.val(null)
    } else {
        outroCausaSolda.prop('disabled',false);
        containerCausas.css('display','flex')
        origemInspecaoSoldaReinspecionadas.css('display','block')
    }
    

})

$('#inputPecasInspecionadas_estamparia').on('blur', function() {

    let inspecionados = $('#inputPecasInspecionadas_estamparia');
    let produzidas = parseInt($('#inputPecasProduzidas_estamparia').val());

    if((inspecionados.val() > produzidas || inspecionados.val() <= 0) && inspecionados.val() != ''){
        alert("Preencha a quantidade correta para o número de peças produzidas")
        inspecionados.val('')
    }
})

$('#envio_inspecao_estamparia').on('click',function() {

    let inputConformidadesSolda = parseInt($('#inputConformidades_estamparia').val());
    let inputNaoConformidadesSolda = parseInt($('#inputNaoConformidades_estamparia').val());
    let qtd_pecas_mortas = parseInt($('#qtd_pecas_mortas').val());
    let inputConjunto = $('#inputConjunto_estamparia').val();
    let inputPecasInspecionadasSolda = parseInt($('#inputPecasProduzidas_estamparia').val());
    let inspetoresSolda = $('#inspetor_estamparia').val();
    let operadoresSolda = $('#operador_estamparia').val();
    let tipos_causas_estamparia = $("#tipos_causas_estamparia").val();
    let inspecao_total = $("#inspecao_total").val();
    let qtd_causas = 0;
    let verificacao_quantidade_produzida = inputPecasInspecionadasSolda >= 3 ? 3 : inputPecasInspecionadasSolda;

    for (let i = 0; i < tipos_causas_estamparia; i++) {
        qtd_causas += parseInt($("#quantidade_causas_estamparia-" + i).val())
    }

    if((qtd_causas != inputNaoConformidadesSolda) && inputNaoConformidadesSolda != 0){
        alert('Um ou mais checkboxes ficaram desmarcados ou a quantidade de não conformidades está diferente da quantidade de causas');
        return; // Interrompe a execução
    }

    if((inputConformidadesSolda + inputNaoConformidadesSolda) !== verificacao_quantidade_produzida){
        alert('Verifique se o campo de conformidades está com valor correto, ou se o campo de inspetor foi preenchido');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    if (inputConformidadesSolda === "" || inspetoresSolda === null || operadoresSolda === null || inputConformidadesSolda > inputPecasInspecionadasSolda || inputConformidadesSolda < 0) {
        alert('Verifique se o campo de conformidades está com valor correto, ou se o campo de inspetor foi preenchido');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    console.log(typeof qtd_pecas_mortas)
    console.log(qtd_pecas_mortas)
    if(qtd_pecas_mortas < 0 || isNaN(qtd_pecas_mortas)) {
        alert('Preencha a quantidade de peças mortas corretamente, se não tiver nenhuma coloque 0. Campo de motivo das peças mortas não é obrigatório.');
        $("#loading").hide();
        return; 
    }

    $("#confirmarConformidades_estamparia").val(inputConformidadesSolda);
    $("#confirmarNaoConformidades_estamparia").val(inputNaoConformidadesSolda);
    $("#confirmarInspecao_100").val(inspecao_total);
    
    $('#modalConfirmacaoEstamparia #p_confirmar_inspecao_estamparia').text("Deseja confirmar as informações preenchidas referente a inspeção do conjunto " + inputConjunto);

    $("#btnEnviarEstampariaReinspecao").css("display","none")
    $("#btnEnviarEstamparia").css("display","block")
    $("#campo_confirmarInspecao_100").css("display","block")

    $('#inspecionarEstamparia').modal('hide');

    $('#modalConfirmacaoEstamparia').modal('show');
})

$('#btnEnviarEstamparia').on('click',function() {

    $("#loading").show();

    var formData = new FormData();

    $('#btnEnviarEstamparia').prop('disabled',true);

    let id_inspecao = $('#inspecionarEstampariaLabel').text();
    let data_inspecao = $('#data_inspecao_estamparia').val();
    let inputCategoria = $('#inputMaquina_estamparia').val();
    let inputConjunto = $('#inputConjunto_estamparia').val();
    let inputPecasInspecionadasSolda = parseInt($('#inputPecasInspecionadas_estamparia').val());
    let inputConformidadesSolda = parseInt($('#inputConformidades_estamparia').val());

    let qtd_pecas_mortas = parseInt($('#qtd_pecas_mortas').val());
    let motivo_pecas_mortas = $('#motivo_pecas_mortas').val();

    let inputNaoConformidadesSolda = $('#inputNaoConformidades_estamparia').val();
    let inspetorSolda = $('#inspetor_estamparia').val();
    let operador_estamparia = $('#operador_estamparia').val();
    let list_causas = [];
    let list_quantidade = [];
    let outraCausaSolda = $('#outraCausa_estamparia').val();
    let observacaoSolda = $('#observacao_estamparia').val();
    let origemInspecaoSolda = $('#origemInspecao_estamparia').val();
    let inspecao_total = $('#inspecao_total').val();
    let tipos_causas_estamparia = $("#tipos_causas_estamparia").val();

    let reinspecao = 'False';

    if (inputConformidadesSolda === "" || inputConformidadesSolda > inputPecasInspecionadasSolda || inputConformidadesSolda < 0) {
        alert('Verifique se o campo de conformidades está com valor correto');
        $('#btnEnviarEstamparia').prop('disabled',false);
        $("#loading").hide();
        return; // Interrompe a execução
    }

    $('tbody.tabela_editavel tr').each(function() {
        let cells = $(this).find('td');
        let cellData = [];
        cells.each(function(index) {
            if ($(this).hasClass('editable')) {
                cellData.push($(this).text());
            } else if ($(this).hasClass('checkbox-container')) {
                cellData.push($(this).find('input.checkbox').is(':checked'));
            }
        });
        formData.append('tabela_dados', JSON.stringify(cellData));
    });

    for (let i = 0; i < tipos_causas_estamparia; i++) {
        let causas = $("#causasEstamparia-" + i).val();
        let quantidade = $("#quantidade_causas_estamparia-" + i).val();
        let inputId = '#inputGroupFile_estamparia-' + i;
        let files = $(inputId)[0].files;
        for (let file of files) {
            formData.append('foto_inspecao_' + i + '[]', file);
        }
        list_causas.push(causas)
        list_quantidade.push(quantidade)
    }

    formData.append('id_inspecao', id_inspecao);
    formData.append('data_inspecao', data_inspecao);
    formData.append('inputCategoria', inputCategoria);
    formData.append('inputConjunto', inputConjunto);
    formData.append('inspetorEstamparia', inspetorSolda);
    formData.append('num_pecas', 3);
    formData.append('inputConformidadesEstamparia', inputConformidadesSolda);
    formData.append('inputNaoConformidadesEstamparia', inputNaoConformidadesSolda);
    formData.append('qtd_pecas_mortas', qtd_pecas_mortas);
    formData.append('motivo_pecas_mortas', motivo_pecas_mortas);
    formData.append('list_causas', JSON.stringify(list_causas));
    formData.append('list_quantidade', JSON.stringify(list_quantidade));
    formData.append('inspecao_total', inspecao_total);
    formData.append('outraCausaEstamparia', outraCausaSolda);
    formData.append('tipos_causas_estamparia',tipos_causas_estamparia);
    formData.append('operador_estamparia',operador_estamparia);
    formData.append('reinspecao', reinspecao);

    $.ajax({
        url: '/inspecao-estamparia',
        type: 'POST',
        data: formData,
        processData: false, // Não processe os dados
        contentType: false, // Não defina o tipo de conteúdo
        success: function (response) {
            location.reload();
            console.log(response);
        },
        error: function (error) {
            $("#loading").hide();
            console.log(error);
            $('#btnEnviarEstamparia').prop('disabled',false);
        }
    });

})