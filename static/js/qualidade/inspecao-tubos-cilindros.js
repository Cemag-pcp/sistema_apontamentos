function modalTubos() {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);


    $('#data_tubo').val(today.toLocaleDateString());
   
    // Exibir o modal
    $('#tubosModal').modal('show');
}

function modalCilindros() {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $('#data_cilindro').val(today.toLocaleDateString());

    // Exibir o modal
    $('#cilindrosModal').modal('show');
}

// ################ INÍCIO CILINDROS ################

$("#codigo_cilindro").on('blur',function () {
    
    let lista_descricoes = ['CILINDRO HIDRÁULICO [CBH5/CBHM5000]','CILINDRO HIDRÁULICO [CBHM6000 CAFEEIRA]','CILINDRO HIDRÁULICO [CBH7/CBHM6000]']
    let codigo = $("#codigo_cilindro").val()

    if(codigo == '034550'){
        $('#descricao_cilindro').val(lista_descricoes[0]);
        $('#descricao_cilindro').prop('disabled',true);
    } else if(codigo == '034630'){
        $('#descricao_cilindro').val(lista_descricoes[1]);
        $('#descricao_cilindro').prop('disabled',true);
    } else if(codigo == '034830'){
        $('#descricao_cilindro').val(lista_descricoes[2]);
        $('#descricao_cilindro').prop('disabled',true);
    } else {
        $('#descricao_cilindro').val('');
        $('#descricao_cilindro').prop('disabled',false);
    }

})

$("#nao_conformidade_cilindro").on('input',function() {
    let nao_conformidade_cilindro =  parseInt($("#nao_conformidade_cilindro").val())
    let causasCilindroC = $("#causasCilindroT-0")
    let quantidade_causas_cilindroC = $("#quantidade_causas_cilindroT-0")
    let div_motivo_cilindro = $("#div_motivo_cilindro")
    let motivo_cilindro = $("#motivo_cilindro")

    if(nao_conformidade_cilindro <= 0){
        $("#selectContainer").css('display','none')
        causasCilindroC.val('')
        quantidade_causas_cilindroC.val('')
        div_motivo_cilindro.css('display','none')
        motivo_cilindro.val('')
    } else {
        $("#selectContainer").css('display','flex')
        div_motivo_cilindro.css('display','block')
    }
})

$("#verificar_cilindro").on('click',function() {
    let qtd_inspecionada_cilindro = parseInt($('#qtd_inspecionada_cilindro').val());
    let inputNaoConformidadesSolda = parseInt($('#nao_conformidade_cilindro').val());
    let inputCodigo = $('#codigo_cilindro').val();
    let descricao_cilindro = $('#descricao_cilindro').val();
    let inspetoresSolda = $('#inspetores_cilindro').val();
    let tipos_causas_cilindro = $('#tipos_causas_cilindro').val();
    let qtd_causas = 0

    if (inspetoresSolda === null) {
        alert('Verifique se o campo de inspetores está com valor correto');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    for (var i = 0; i < tipos_causas_cilindro; i++) {
        qtd_causas += parseInt($("#quantidade_causas_cilindroC-" + i).val())
    }

    if((qtd_causas != inputNaoConformidadesSolda) && inputNaoConformidadesSolda != 0) {
        alert('Verifique se a soma dos campos de "Quantidade de causas" está igual ao valor de "Não conformidades"');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    $("#confirmarConformidades").val(qtd_inspecionada_cilindro);
    $("#confirmarNaoConformidades").val(inputNaoConformidadesSolda);
    
    $('#modalConfirmacaoSolda #p_confirmar_inspecao_tubo_cilindro').text("Deseja confirmar as informações preenchidas referente a inspeção do " + inputCodigo + " " + descricao_cilindro);

    $("#btnEnviarTubo").css("display","none")
    $("#btnEnviarCilindro").css("display","block")

    $('#cilindrosModal').modal('hide');

    $('#modalConfirmacaoSolda').modal('show');
})

$('#btnEnviarCilindro').on('click',function() {

    $("#loading").show();

    var formData = new FormData();

    $('#btnEnviarCilindro').prop('disabled',true);

    let data_cilindro = $('#data_cilindro').val();
    let codigo_cilindro = $('#codigo_cilindro').val();
    let descricao_cilindro = $('#descricao_cilindro').val();
    let qtd_inspecionada_cilindro = parseInt($('#qtd_inspecionada_cilindro').val());
    let nao_conformidade_cilindro = $('#nao_conformidade_cilindro').val();
    let inputConformidadesSolda = (qtd_inspecionada_cilindro * 6) - nao_conformidade_cilindro
    console.log(inputConformidadesSolda)
    let inspetores_cilindro = $('#inspetores_cilindro').val();
    let list_causas = [];
    let list_quantidade = [];
    let observacao_cilindro = $('#observacao_cilindro').val();
    let tipos_causas_cilindro = $('#tipos_causas_cilindro').val();
    let motivo_cilindro = $("#motivo_cilindro").val();
    let montador_cilindro = $('#montador_cilindro').val();
    let reinspecao = 'False';

    for (var i = 0; i < tipos_causas_cilindro; i++) {
        let causas = $("#causasCilindroC-" + i).val();
        let quantidade = $("#quantidade_causas_cilindroC-" + i).val();
        let inputId = '#inputGroupFile_cilindroC-' + i;
        let files = $(inputId)[0].files;
        for (let file of files) {
            formData.append('foto_inspecao_' + i + '[]', file);
        }
        list_causas.push(causas)
        list_quantidade.push(quantidade)
    }

    formData.append('data_inspecao', data_cilindro);
    formData.append('inputConjunto', codigo_cilindro);
    formData.append('descricao_cilindro', descricao_cilindro);
    formData.append('inspetorSolda', inspetores_cilindro);
    formData.append('num_pecas', qtd_inspecionada_cilindro);
    formData.append('inputConformidadesSolda', inputConformidadesSolda);
    formData.append('inputNaoConformidadesSolda', nao_conformidade_cilindro);
    formData.append('list_causas', JSON.stringify(list_causas));
    formData.append('list_quantidade', JSON.stringify(list_quantidade));
    formData.append('observacao_cilindro', observacao_cilindro);
    formData.append('tipos_causas_solda',tipos_causas_cilindro);
    formData.append('motivo_cilindro',motivo_cilindro)
    formData.append('operador', montador_cilindro);
    formData.append('reinspecao', reinspecao);
    formData.append('setor', 'Cilindro');

    $.ajax({
        url: '/inspecao-tubos-cilindros',
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
            $('#btnEnviarCilindro').prop('disabled',false);
        }
    });

})
// ################ FIM CILINDROS ################

// ################ INÍCIO TUBOS ################

$("#codigo_tubo").on('blur',function () {
    
    let lista_descricoes = ['TUBO HIDRÁULICO [CBHM5000 M17]','TUBO HIDRÁULICO [CBH6/CBHM6000-2E M17]','TUBO HIDRÁULICO [CBH6/CBH7/CBHM6000]']
    let codigo = $("#codigo_tubo").val()

    if(codigo == '030671'){
        $('#descricao_tubo').val(lista_descricoes[0]);
        $('#descricao_tubo').prop('disabled',true);
    } else if(codigo == '031566'){
        $('#descricao_tubo').val(lista_descricoes[1]);
        $('#descricao_tubo').prop('disabled',true);
    } else if(codigo == '030753'){
        $('#descricao_tubo').val(lista_descricoes[2]);
        $('#descricao_tubo').prop('disabled',true);
    } else {
        $('#descricao_tubo').val('');
        $('#descricao_tubo').prop('disabled',false);
    }

})

$("#nao_conformidade_tubo").on('input',function() {
    let nao_conformidade_tubo =  parseInt($("#nao_conformidade_tubo").val())
    let causasCilindroT = $("#causasCilindroT-0")
    let quantidade_causas_cilindroT = $("#quantidade_causas_cilindroT-0")
    let div_motivo_tubo = $("#div_motivo_tubo")
    let motivo_tubo = $("#motivo_tubo")

    if(nao_conformidade_tubo <= 0){
        $("#selectContainerTubos").css('display','none')
        causasCilindroT.val('')
        quantidade_causas_cilindroT.val('')
        div_motivo_tubo.css('display','none')
        motivo_tubo.val('')
    } else {
        $("#selectContainerTubos").css('display','flex')
        div_motivo_tubo.css('display','block')
    }
})

$("#verificar_tubo").on('click',function() {
    let qtd_inspecionada_tubo = parseInt($('#qtd_inspecionada_tubo').val());
    let inputNaoConformidadesSolda = parseInt($('#nao_conformidade_tubo').val());
    let inputCodigo = $('#codigo_tubo').val();
    let descricao_tubo = $('#descricao_tubo').val();
    let inspetoresSolda = $('#inspetores_tubo').val();
    let tipos_causas_tubo = $('#tipos_causas_tubo').val();
    let qtd_causas = 0

    if (inspetoresSolda === null) {
        alert('Verifique se o campo de inspetores está com valor correto');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    for (var i = 0; i < tipos_causas_tubo; i++) {
        qtd_causas += parseInt($("#quantidade_causas_cilindroT-" + i).val())
    }

    if((qtd_causas != inputNaoConformidadesSolda) && inputNaoConformidadesSolda != 0) {
        alert('Verifique se a soma dos campos de "Quantidade de causas" está igual ao valor de "Não conformidades"');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    $("#confirmarConformidades").val(qtd_inspecionada_tubo);
    $("#confirmarNaoConformidades").val(inputNaoConformidadesSolda);
    
    $('#modalConfirmacaoSolda #p_confirmar_inspecao_tubo_cilindro').text("Deseja confirmar as informações preenchidas referente a inspeção do " + inputCodigo + " " + descricao_tubo);

    $("#btnEnviarCilindro").css("display","none")
    $("#btnEnviarTubo").css("display","block")

    $('#tubosModal').modal('hide');

    $('#modalConfirmacaoSolda').modal('show');
})

$('#btnEnviarTubo').on('click',function() {

    $("#loading").show();

    var formData = new FormData();

    $('#btnEnviarTubo').prop('disabled',true);

    let data_cilindro = $('#data_tubo').val();
    let codigo_cilindro = $('#codigo_tubo').val();
    let descricao_cilindro = $('#descricao_tubo').val();
    let qtd_inspecionada_cilindro = parseInt($('#qtd_inspecionada_tubo').val());
    let nao_conformidade_cilindro = $('#nao_conformidade_tubo').val();
    let inputConformidadesSolda = (qtd_inspecionada_cilindro * 1) - nao_conformidade_cilindro
    console.log(inputConformidadesSolda)
    let inspetores_cilindro = $('#inspetores_tubo').val();
    let list_causas = [];
    let list_quantidade = [];
    let observacao_cilindro = $('#observacao_tubo').val();
    let tipos_causas_cilindro = $('#tipos_causas_tubo').val();
    let motivo_cilindro = $("#motivo_tubo").val();
    let soldador_tubo = $('#soldador_tubo').val();
    let reinspecao = 'False';

    for (var i = 0; i < tipos_causas_cilindro; i++) {
        let causas = $("#causasCilindroT-" + i).val();
        let quantidade = $("#quantidade_causas_cilindroT-" + i).val();
        let inputId = '#inputGroupFile_cilindroT-' + i;
        let files = $(inputId)[0].files;
        for (let file of files) {
            formData.append('foto_inspecao_' + i + '[]', file);
        }
        list_causas.push(causas)
        list_quantidade.push(quantidade)
    }

    formData.append('data_inspecao', data_cilindro);
    formData.append('inputConjunto', codigo_cilindro);
    formData.append('descricao_cilindro', descricao_cilindro);
    formData.append('inspetorSolda', inspetores_cilindro);
    formData.append('num_pecas', qtd_inspecionada_cilindro);
    formData.append('inputConformidadesSolda', inputConformidadesSolda);
    formData.append('inputNaoConformidadesSolda', nao_conformidade_cilindro);
    formData.append('list_causas', JSON.stringify(list_causas));
    formData.append('list_quantidade', JSON.stringify(list_quantidade));
    formData.append('observacao_cilindro', observacao_cilindro);
    formData.append('tipos_causas_solda',tipos_causas_cilindro);
    formData.append('motivo_cilindro',motivo_cilindro)
    formData.append('operador', soldador_tubo);
    formData.append('reinspecao', reinspecao);
    formData.append('setor', 'Tubo');

    $.ajax({
        url: '/inspecao-tubos-cilindros',
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
            $('#btnEnviarTubo').prop('disabled',false);
        }
    });

})

// ################ FIM TUBOS ################
