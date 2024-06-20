function modalReteste(id,codigo_descricao,causa) {

    $('#causaReteste1').val(codigo_descricao);

    $("#id_reteste").val(id)

    $("#p_confirmar_reteste_tubo_cilindro").text("Campo para realizar o reteste referente ao " + codigo_descricao + ", o motivo da(s) não conformidade(s) foi (" + causa + ")")

    // Exibir o modal
    $('#modalReteste').modal('show');

    $("#reteste_status1").val('')
    $("#linha_reteste2").css("display","none")
    $("#reteste_status2").val('')
    $("#linha_reteste3").css("display","none")
    $("#reteste_status3").val('')
}

$("#reteste_status1").on('change',function () {

    if($("#reteste_status1").val() === "Não Conforme"){
        $("#linha_reteste2").css("display","block")
    } else {
        $("#linha_reteste2").css("display","none")
        $("#reteste_status2").val('')
        $("#linha_reteste3").css("display","none")
        $("#reteste_status3").val('')
    }

})

$("#reteste_status2").on('change',function () {

    if($("#reteste_status2").val() === "Não Conforme"){
        $("#linha_reteste3").css("display","block")
    } else {
        $("#linha_reteste3").css("display","none")
        $("#reteste_status3").val('')
    }

})

$("#btnEnviarReteste").on('click',function() {

    $("#loading").show();

    $('#btnEnviarReteste').prop('disabled',true);

    var formData = new FormData();

    let id = $("#id_reteste").val()
    let reteste_status1 = $("#reteste_status1").val()
    let reteste_status2 = $("#reteste_status2").val()
    let reteste_status3 = $("#reteste_status3").val()

    if (reteste_status1 === ''){
        alert('Preencha o reteste')
        return
    }

    function verificarStatus(status) {
        if (status === "Conforme") {
            return true;
        } else if(status === "Não Conforme") {
            return false;
        } else {
            return null;
        }
    }

    reteste_status1 = verificarStatus(reteste_status1);
    reteste_status2 = verificarStatus(reteste_status2);
    reteste_status3 = verificarStatus(reteste_status3);

    formData.append('id',id)
    formData.append('reteste_status1',reteste_status1)
    formData.append('reteste_status2',reteste_status2)
    formData.append('reteste_status3',reteste_status3)

    $.ajax({
        url: '/reteste-tubos-cilindros',
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
            $('#btnEnviarReteste').prop('disabled',false);
        }
    });

})