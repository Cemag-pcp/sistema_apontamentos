document.addEventListener("DOMContentLoaded", function () {
    const formReteste = document.querySelector("#modalReteste form");
    const qntReinspecaoInput = document.getElementById("qnt_reinspecao");
    const verificar_reteste = document.getElementById("verificar_reteste");
    const spinner_reteste_estanqueidade = document.getElementById("spinner-reteste-estanqueidade");
    const status_button_reteste_estanqueidade = document.getElementById("status-button-reteste-estanqueidade");

    // Função para validar a soma das quantidades
    function validarSomaQuantidades() {
        const statusEstanqueidade = document.getElementById("reteste_status_estanqueidade").value;
        const qntReinspecao = parseInt(qntReinspecaoInput.value) || 0;
        let somaQuantidades = 0;

        // Soma todas as quantidades das causas
        document.querySelectorAll(".quantidade_tubo_estanqueidade").forEach(input => {
            somaQuantidades += parseInt(input.value) || 0;
        });

        if (somaQuantidades > qntReinspecao && statusEstanqueidade === "Não Conforme") {
            Swal.fire({
                icon: "error",
                title: `A soma das quantidades (${somaQuantidades}) não pode ser maior que Quant. Reinspeção (${qntReinspecao}).`,
              });
            return false;
        }
        return true;
    }

    // Função para coletar dados do formulário
    function coletarDadosFormulario() {
        const id_inspecao_estanqueidade = document.getElementById("id_reteste").value;
        const status_estanqueidade = document.getElementById("reteste_status_estanqueidade").value;
        const quantidade_inspecionada = document.getElementById("qnt_reinspecao").value;
        const motivo = document.getElementById("motivo_reteste_estanqueidade").value;
        const ficha = document.getElementById("ficha_reteste_estanqueidade").value;
        const observacao = document.getElementById("observacao_reteste_estanqueidade").value;
        const tipo_inspecao_estanqueidade = document.getElementById("tipo_inspecao_estanqueidade").value;
        const inspetor = document.getElementById("inspetores_reteste_tubo") 
        ? document.getElementById("inspetores_reteste_tubo").value 
        : document.getElementById("inspetores_reteste_cilindro").value;

        let nao_conforme_retrabalho = document.getElementById("qtd_retrabalho_tubo_estanqueidade") 
        ? parseInt(document.getElementById("qtd_retrabalho_tubo_estanqueidade").value) 
        : 0;

        const nao_conforme_refugo = document.getElementById("qtd_refugo_tubo_estanqueidade") 
        ? parseInt(document.getElementById("qtd_refugo_tubo_estanqueidade").value) 
        : 0;

        // Coletando causas
        const causas = [];
        let totalQuantidade = 0
        document.querySelectorAll("#causasContainerEstanqueidade .causasBlock").forEach((block) => {
            const causa = block.querySelector(".causasTuboEstanqueidade").value;
            const quantidade = parseInt(block.querySelector(".quantidade_tubo_estanqueidade").value) || 0;
            const arquivo_input = block.querySelector(".inputGroupFile_tubo");
            const arquivos = arquivo_input.files;

            if (tipo_inspecao_estanqueidade !== 'Tubos' && status_estanqueidade === 'Não Conforme') {
                nao_conforme_retrabalho += parseInt(quantidade);
            }

            totalQuantidade+=parseInt(quantidade);
            
            const causaData = {
                causa,
                quantidade,
                arquivos: Array.from(arquivos).map(file => file.name)
            };
            causas.push(causaData);
        });

        
        if (tipo_inspecao_estanqueidade ==='Tubos' && totalQuantidade !== nao_conforme_retrabalho + nao_conforme_refugo) {
            Swal.fire({
                icon: "error",
                title: `A soma das quantidades tem que ser igual ao valor de Não conforme retrabalho e Não conforme refugo.`,
              });
            return false;
        }

        return {
            id_inspecao_estanqueidade,
            status_estanqueidade,
            quantidade_inspecionada,
            nao_conforme_retrabalho,
            nao_conforme_refugo,
            observacao,
            inspetor,
            motivo,
            ficha,
            causas,
        };
    }

    // Evento de submissão do formulário
    formReteste.addEventListener("submit", function (event) {
        event.preventDefault(); // Previne a submissão padrão

        // Validação da soma das quantidades
        if (!validarSomaQuantidades()) {
            return; // Interrompe o envio se a validação falhar
        }

        // Coleta os dados do formulário
        const dadosFormulario = coletarDadosFormulario();

        if(!dadosFormulario){
            return;
        }

        verificar_reteste.disabled = true;
        spinner_reteste_estanqueidade.classList.remove('d-none');
        status_button_reteste_estanqueidade.textContent = "Carregando ...";

        // Exemplo de envio via Fetch API
        fetch("/reteste-estanqueidade-tubos-cilindros", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(dadosFormulario),
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error("Erro ao enviar os dados");
            }
        })
        .then(data => {
            const Toast = Swal.mixin({
                toast: true,
                position: "bottom-end",
                showConfirmButton: false,
                timer: 2000,
                timerProgressBar: true,
                didOpen: (toast) => {
                  toast.onmouseenter = Swal.stopTimer;
                  toast.onmouseleave = Swal.resumeTimer;
                }
              });
              Toast.fire({
                icon: "success",
                title: "Reteste registrado com sucesso!"
            });
            setTimeout(() => {
                location.reload();
            }, 2000);
        })
        .catch(error => {
            const Toast = Swal.mixin({
                toast: true,
                position: "bottom-end",
                showConfirmButton: false,
                timer: 2000,
                timerProgressBar: true,
                didOpen: (toast) => {
                  toast.onmouseenter = Swal.stopTimer;
                  toast.onmouseleave = Swal.resumeTimer;
                }
              });
              Toast.fire({
                icon: "error",
                title: "Erro ao enviar os dados para o servidor!"
            });
            setTimeout(() => {
                location.reload();
            }, 2000);
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('#cilindrosModal form');
    const causasContainer = document.getElementById("causasContainerEstanqueidadeCilindro");
    const verificar_cilindro = document.getElementById("verificar_cilindro");
    const spinner_cilindro_estanqueidade = document.getElementById("spinner-cilindro-estanqueidade");
    const status_button_cilindro_estanqueidade = document.getElementById("status-button-cilindro-estanqueidade");
    
    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevenir o envio padrão do formulário

        // Capturar dados do formulário
        const naoConformidade = parseInt(document.getElementById("nao_conformidade_cilindro").value) || 0;
        const data = {
            id_inspecao: document.getElementById("id_cilindro").value,
            data_inspecao: document.getElementById("data_cilindro").value,
            tipo_inspecao: "Cilindros",
            inspetor: document.getElementById("inspetores_cilindro").value,
            codigo: document.getElementById("produtoEstanqueidade_cilindro").value,
            quantidade_inspecionada: parseInt(document.getElementById("qtd_inspecionada_cilindro").value) || 0,
            nao_conformidade: naoConformidade,
            motivo: document.getElementById("motivo_cilindro").value,
            observacao: document.getElementById("observacao_cilindro").value,
            ficha: document.getElementById("ficha_cilindro").value,
            causas: [],
        };

        // Capturar as causas dinâmicas
        const causasBlocks = causasContainer.querySelectorAll(".causasBlock");
        let totalQuantidade = 0;

        causasBlocks.forEach((block) => {
            const causa = block.querySelector("select").value;
            const quantidade = parseInt(block.querySelector(".quantidadeBlock input").value) || 0;
            const arquivos = block.querySelector(".custom-file-input").files;
            const arquivosArray = Array.from(arquivos).map(file => file.name); // Captura nomes dos arquivos

            totalQuantidade += quantidade;

            data.causas.push({
                causa,
                quantidade,
                arquivos: arquivosArray,
            });
        });

        if (totalQuantidade !== naoConformidade) {
            Swal.fire({
                icon: "error",
                title: "A soma das quantidades tem que ser igual ao valor de Não Conformidade...",
              });
            return;
        }

        verificar_cilindro.disabled = true;
        spinner_cilindro_estanqueidade.classList.remove('d-none');
        status_button_cilindro_estanqueidade.textContent = "Carregando ...";

        // Enviar os dados via AJAX
        fetch("/envio-estanqueidade-tubos-cilindros", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Erro ao enviar os dados!");
            }
            return response.json();
        })
        .then((result) => {
            const Toast = Swal.mixin({
                toast: true,
                position: "bottom-end",
                showConfirmButton: false,
                timer: 2000,
                timerProgressBar: true,
                didOpen: (toast) => {
                  toast.onmouseenter = Swal.stopTimer;
                  toast.onmouseleave = Swal.resumeTimer;
                }
              });
              Toast.fire({
                icon: "success",
                title: "Inspeção de cilindro registrada com sucesso!"
            });
            setTimeout(() => {
                location.reload();
            }, 2000);
        })
        .catch((error) => {
            console.error(error);
            const Toast = Swal.mixin({
                toast: true,
                position: "bottom-end",
                showConfirmButton: false,
                timer: 2000,
                timerProgressBar: true,
                didOpen: (toast) => {
                  toast.onmouseenter = Swal.stopTimer;
                  toast.onmouseleave = Swal.resumeTimer;
                }
              });
              Toast.fire({
                icon: "error",
                title: "Erro ao enviar os dados para o servidor!"
            });
            setTimeout(() => {
                location.reload();
            }, 2000);
        });
    });
});

const form = document.querySelector('#estanqueidadeTubosModal form');
const submitButton = document.getElementById('verificar_tubo');
const spinner_tubo_estanqueidade = document.getElementById("spinner-tubo-estanqueidade");
const status_button_tubo_estanqueidade = document.getElementById("status-button-tubo-estanqueidade");

// Adicionar evento de envio
form.addEventListener('submit', async (event) => {
    event.preventDefault(); // Previne o comportamento padrão de envio do formulário

    // Capturar os dados do formulário
    const data = {
        id_inspecao: document.getElementById("id_tubo").value,
        data_inspecao: document.querySelector('#data_tubo').value,
        tipo_inspecao: "Tubos",
        inspetor: form.querySelector('.inspetor_tubo_estanqueidade').value,
        codigo: form.querySelector('.produto_tubo_estanqueidade').value,
        quantidade_inspecionada: parseInt(form.querySelector('.qtd_inspecionada_tubo_estanqueidade').value, 10),
        nao_conforme_retrabalho: parseInt(form.querySelector('.nao_conformidade_retrabalho_tubo_estanqueidade').value, 10),
        nao_conforme_refugo: parseInt(form.querySelector('.nao_conformidade_refugo_tubo_estanqueidade').value, 10),
        causas: [],
        motivo: document.querySelector('#motivo_tubo_estanqueidade').value,
        ficha: document.getElementById('ficha_tubo_estanqueidade').value,
        observacao: document.querySelector('#observacao_tubo_estanqueidade').value,
    };

    // Verificar se a soma de não conformidades excede a quantidade inspecionada
    const somaNaoConformes = data.nao_conforme_retrabalho + data.nao_conforme_refugo;
    if ((somaNaoConformes > data.quantidade_inspecionada)) {
        Swal.fire({
            icon: "error",
            title: "A soma de não conformidades (retrabalho e refugo) não pode ser maior que a quantidade inspecionada...",
        });
        return; // Impede o envio do formulário
    }

    // Capturar as causas dinamicamente
    const causasBlocks = document.querySelectorAll('#causasContainerEstanqueidadeTubo .causasBlock');
    let somaCausas = 0;
    causasBlocks.forEach(block => {
        const causa = block.querySelector('select').value;
        const quantidade = block.querySelector('input[type=number]').value;
        const arquivos = block.querySelector('input[type=file]').files;

        somaCausas += parseInt(quantidade);
        const arquivosArray = Array.from(arquivos).map(file => file.name); // Captura apenas os nomes dos arquivos

        data.causas.push({ causa, quantidade, arquivos: arquivosArray });
    });

    if ((somaNaoConformes !== somaCausas) && (somaNaoConformes !== 0)) {
        Swal.fire({
            icon: "error",
            title: "A soma das quantidades de causas deve ser igual à soma de não conformidades (retrabalho + refugo)...",
          });
        return;
    }

    submitButton.disabled = true;
    spinner_tubo_estanqueidade.classList.remove('d-none');
    status_button_tubo_estanqueidade.textContent = "Carregando ...";

    fetch("/envio-estanqueidade-tubos-cilindros", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error("Erro ao enviar os dados!");
        }
        return response.json();
    })
    .then((result) => {
        const Toast = Swal.mixin({
            toast: true,
            position: "bottom-end",
            showConfirmButton: false,
            timer: 2000,
            timerProgressBar: true,
            didOpen: (toast) => {
              toast.onmouseenter = Swal.stopTimer;
              toast.onmouseleave = Swal.resumeTimer;
            }
          });
          Toast.fire({
            icon: "success",
            title: "Inspeção de tubo registrada com sucesso!"
        });
        setTimeout(() => {
            location.reload();
        }, 2000);
    })
    .catch((error) => {
        console.error(error);
        const Toast = Swal.mixin({
            toast: true,
            position: "bottom-end",
            showConfirmButton: false,
            timer: 2000,
            timerProgressBar: true,
            didOpen: (toast) => {
              toast.onmouseenter = Swal.stopTimer;
              toast.onmouseleave = Swal.resumeTimer;
            }
          });
          Toast.fire({
            icon: "error",
            title: "Erro ao enviar os dados para o servidor!"
        });
        setTimeout(() => {
            location.reload();
        }, 2000);
    });
});