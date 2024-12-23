$("#reteste_status_estanqueidade").on('change', function() {
    
    if ($(this).val() == "Não Conforme") {
        $("#causasContainerEstanqueidade").css("display", "flex");
        $("#motivo_ficha_retrabalho_estanqueidade").css("display", "flex");
        $("#add_remove_cause").css("display", "flex");

        // Adicionando "required" aos elementos relevantes
        $("#causas_estanqueidade select, .quantidade_tubo_estanqueidade, #motivo_reteste_estanqueidade").attr("required", true);

        if ($("#tipo_inspecao_estanqueidade").val() === 'Tubos') {
            $("#nao_conformidade_tubos").html(`
                <div class="col-sm-6 mb-4">
                    <label>Não conforme retrabalho</label>
                    <input type="number" class="form-control qtd_retrabalho_tubo_estanqueidade" id="qtd_retrabalho_tubo_estanqueidade" min=0 required> 
                </div>
                <div class="col-sm-6 mb-4">
                    <label>Não conforme refugo</label>
                    <input type="number" class="form-control qtd_refugo_tubo_estanqueidade" id="qtd_refugo_tubo_estanqueidade" min=0 required> 
                </div>
            `);
            $("#inspetor_reteste_estanqueidade").html(`
                <label>Inspetor</label>
                <select class="form-control" name="inspetores_reteste_tubo" id="inspetores_reteste_tubo" required>
                    <option value="" hidden selected disabled></option>
                    <option value="Carlos Henrique">Carlos Henrique</option>
                    <option value="Gabriel Florêncio">Gabriel Florêncio</option>
                    <option value="Bruno Sousa">Bruno Sousa</option>
                    <option value="Gabriel G.">Gabriel G.</option>
                    <option value="Francisco Paulo">Francisco Paulo</option>
                </select>
            `);
        } else {
            $("#inspetor_reteste_estanqueidade").html(`
                <label>Inspetor</label>
                <select class="form-control" name="inspetores_reteste_cilindro" id="inspetores_reteste_cilindro" required>
                    <option value="" hidden selected disabled></option>
                    <option value="Matheus">Matheus</option>
                    <option value="Cauã">Cauã</option>
                    <option value="Paulo">Paulo</option>
                    <option value="Gabriel">Gabriel</option>
                    <option value="Leonidas">Leonidas</option>
                    <option value="Marcelo">Marcelo</option>
                    <option value="Severiano">Severiano</option>
                    <option value="Carlos Henrique">Carlos Henrique</option>
                    <option value="Bruno">Bruno</option>
                    <option value="Gabriel G.">Gabriel G.</option>
                </select>
            `);
        }
    } else {
        $("#nao_conformidade_tubos").empty();
        $("#causasContainerEstanqueidade").css("display", "none");
        $("#motivo_ficha_retrabalho_estanqueidade").css("display", "none");
        $("#add_remove_cause").css("display", "none");

        if ($("#tipo_inspecao_estanqueidade").val() === 'Tubos') {
            $("#inspetor_reteste_estanqueidade").html(`
                <label>Inspetor</label>
                <select class="form-control" name="inspetores_reteste_tubo" id="inspetores_reteste_tubo" required>
                    <option value="" hidden selected disabled></option>
                    <option value="Carlos Henrique">Carlos Henrique</option>
                    <option value="Gabriel Florêncio">Gabriel Florêncio</option>
                    <option value="Bruno Sousa">Bruno Sousa</option>
                    <option value="Gabriel G.">Gabriel G.</option>
                    <option value="Francisco Paulo">Francisco Paulo</option>
                </select>
            `);
        } else {
            $("#inspetor_reteste_estanqueidade").html(`
                <label>Inspetor</label>
                <select class="form-control" name="inspetores_reteste_cilindro" id="inspetores_reteste_cilindro" required>
                    <option value="" hidden selected disabled></option>
                    <option value="Matheus">Matheus</option>
                    <option value="Cauã">Cauã</option>
                    <option value="Paulo">Paulo</option>
                    <option value="Gabriel">Gabriel</option>
                    <option value="Leonidas">Leonidas</option>
                    <option value="Marcelo">Marcelo</option>
                    <option value="Severiano">Severiano</option>
                    <option value="Carlos Henrique">Carlos Henrique</option>
                    <option value="Bruno">Bruno</option>
                    <option value="Gabriel G.">Gabriel G.</option>
                </select>
            `);
        }

        // Removendo "required" dos elementos relevantes
        $("#causas_estanqueidade select, .quantidade_tubo_estanqueidade, #motivo_reteste_estanqueidade").removeAttr("required");
    }
});

$("#nao_conformidade_cilindro").on("input", function() {
    if (parseInt($(this).val()) === 0) {
        $("#campo_causas_cilindro_estanqueidade").css("display","none");
        $("#div_motivo_cilindro").css("display","none");
        $(".causas_cilindro, .quantidade_causas_cilindro, #motivo_cilindro").removeAttr("required");
    } else {
        $("#campo_causas_cilindro_estanqueidade").css("display","block");
        $("#div_motivo_cilindro").css("display","block");
        $(".causas_cilindro, .quantidade_causas_cilindro, #motivo_cilindro").attr("required", true);
    }
})

$(".nao_conformidade_retrabalho_tubo_estanqueidade").on("input",function() {
    if(parseInt($(this).val()) + parseInt($(".nao_conformidade_refugo_tubo_estanqueidade").val()) === 0) {
        $("#causasContainerEstanqueidadeTubo").css("display","none");
        $("#div_motivo_tubos").css("display","none");
        $(".causas_tubos, .quantidade_causas_tubos, #motivo_tubo_estanqueidade").removeAttr("required");
        $("#add_causa_tubo_estanqueidade").css("display", "none");
    } else {
        $("#causasContainerEstanqueidadeTubo").css("display","block");
        $("#div_motivo_tubos").css("display","block");
        $(".causas_tubos, .quantidade_causas_tubos, #motivo_tubo_estanqueidade").attr("required", true);
        $("#add_causa_tubo_estanqueidade").css("display", "flex");
    }
})

$(".nao_conformidade_refugo_tubo_estanqueidade").on("input",function() {
    if(parseInt($(this).val()) + parseInt($(".nao_conformidade_retrabalho_tubo_estanqueidade").val()) === 0) {
        $("#causasContainerEstanqueidadeTubo").css("display","none");
        $("#div_motivo_tubos").css("display","none");
        $(".causas_tubos, .quantidade_causas_tubos, #motivo_tubo_estanqueidade").removeAttr("required");
        $("#add_causa_tubo_estanqueidade").css("display", "none");
    } else {
        $("#causasContainerEstanqueidadeTubo").css("display","block");
        $("#div_motivo_tubos").css("display","block");
        $(".causas_tubos, .quantidade_causas_tubos, #motivo_tubo_estanqueidade").attr("required", true);
        $("#add_causa_tubo_estanqueidade").css("display", "flex");
    }
})