const form = document.querySelector('#estanqueidadeTanqueModal form');
const submitButton = document.getElementById('inspecionar-tanque');
const spinnerTanqueEstanqueidade = document.getElementById("spinner-tanque-estanqueidade");
const statusButtonTanqueEstanqueidade = document.getElementById("status-button-tanque-estanqueidade");
const submitButtonReinspecao = document.getElementById('inspecionar-tanque-reinspecao');
const spinnerTanqueEstanqueidadeReinspecao = document.getElementById("spinner-tanque-estanqueidade-reinspecao");
const statusButtonTanqueEstanqueidadeReinspecao = document.getElementById("status-button-tanque-estanqueidade-reinspecao");

// Adicionar evento de envio
form.addEventListener('submit', async (event) => {
    event.preventDefault(); // Previne o comportamento padrão de envio do formulário

    // Exibir o spinner e mudar o texto do botão
    submitButton.disabled = true;
    spinnerTanqueEstanqueidade.classList.remove('d-none');
    statusButtonTanqueEstanqueidade.innerText = 'Enviando...';

    // Capturar os dados do formulário
    const data = {
        tipo_inspecao: "Tanques",
        inspetor: document.getElementById('inspetores_estanqueidade_tanque').value,
        produto: document.getElementById('produto-estanqueidade-tanque').value,
        testes: {
            parte_inferior: {
                pressao_inicial: document.getElementById('pressao-inicial-parte-inferior').value,
                duracao: document.getElementById('duracao-parte-inferior').value,
                pressao_final: document.getElementById('pressao-final-parte-inferior').value,
                vazamento: document.getElementById('vazamento-parte-inferior').value,
            },
            corpo_longarina: {
                pressao_inicial: document.getElementById('pressao-inicial-longarina').value,
                duracao: document.getElementById('duracao-longarina').value,
                pressao_final: document.getElementById('pressao-final-longarina').value,
                vazamento: document.getElementById('vazamento-longarina').value,
            },
            corpo_tanque: {
                pressao_inicial: document.getElementById('pressao-inicial-corpo-tanque').value,
                duracao: document.getElementById('duracao-corpo-tanque').value,
                pressao_final: document.getElementById('pressao-final-corpo-tanque').value,
                vazamento: document.getElementById('vazamento-corpo-tanque').value,
            },
            corpo_chassi: {
                pressao_inicial: document.getElementById('pressao-inicial-corpo-chassi').value,
                duracao: document.getElementById('duracao-corpo-chassi').value,
                pressao_final: document.getElementById('pressao-final-corpo-chassi').value,
                vazamento: document.getElementById('vazamento-corpo-chassi').value,
            }
        }
    };

    // Enviar dados via fetch (ou outra forma, como axios)
    try {
        const response = await fetch('/envio-inspecao-estanqueidade-tanque', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        console.log(result)
        // Processar a resposta aqui
        if (response.ok) {
            // Se a resposta for OK, mostre uma mensagem de sucesso
            const Toast = Swal.mixin({
                toast: true,
                position: "bottom-end",
                showConfirmButton: false,
                timer: 1000,
                timerProgressBar: true,
                didOpen: (toast) => {
                  toast.onmouseenter = Swal.stopTimer;
                  toast.onmouseleave = Swal.resumeTimer;
                }
              });
              Toast.fire({
                icon: "success",
                title: "Inspeção registrada com sucesso!"
              });
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            // Se houver erro, mostre uma mensagem de erro
            const Toast = Swal.mixin({
                toast: true,
                position: "bottom-end",
                showConfirmButton: false,
                timer: 1000,
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
            }, 1000);
        }
    } catch (error) {
        console.error('Erro ao enviar dados:', error);
        const Toast = Swal.mixin({
            toast: true,
            position: "bottom-end",
            showConfirmButton: false,
            timer: 1000,
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
        }, 1000);
    } 
});

document.querySelector('#reinspecaoForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Impede o envio padrão do formulário

    // Exibir o spinner e mudar o texto do botão
    submitButtonReinspecao.disabled = true;
    spinnerTanqueEstanqueidadeReinspecao.classList.remove('d-none');
    statusButtonTanqueEstanqueidadeReinspecao.innerText = 'Enviando...';

    // Itera sobre todos os inputs do formulário
    const data = {
        id: document.getElementById('id_estanqueidade_tanque_reinspecao').value,
        tipo_inspecao: "Tanques",
        inspetor: document.getElementById('inspetores_estanqueidade_tanque_reinspecao').value,
        produto: document.getElementById('produto-estanqueidade-tanque-reinspecao').value,
        testes: {
            parte_inferior: {
                flag:document.getElementById('flag-parte-inferior-tanque-reinspecao').value,
                pressao_inicial: document.getElementById('pressao-inicial-parte-inferior-reinspecao').value,
                duracao: document.getElementById('duracao-parte-inferior-reinspecao').value,
                pressao_final: document.getElementById('pressao-final-parte-inferior-reinspecao').value,
                vazamento: document.getElementById('vazamento-parte-inferior-reinspecao').value,
                tipo_teste: "Corpo do tanque parte inferior"
            },
            corpo_longarina: {
                flag:document.getElementById('flag-longarina-tanque-reinspecao').value,
                pressao_inicial: document.getElementById('pressao-inicial-longarina-reinspecao').value,
                duracao: document.getElementById('duracao-longarina-reinspecao').value,
                pressao_final: document.getElementById('pressao-final-longarina-reinspecao').value,
                vazamento: document.getElementById('vazamento-longarina-reinspecao').value,
                tipo_teste: "Corpo do tanque + longarinas"
            },
            corpo_tanque: {
                flag:document.getElementById('flag-corpo-tanque-reinspecao').value,
                pressao_inicial: document.getElementById('pressao-inicial-corpo-tanque-reinspecao').value,
                duracao: document.getElementById('duracao-corpo-tanque-reinspecao').value,
                pressao_final: document.getElementById('pressao-final-corpo-tanque-reinspecao').value,
                vazamento: document.getElementById('vazamento-corpo-tanque-reinspecao').value,
                tipo_teste: "Corpo do tanque"
            },
            corpo_chassi: {
                flag:document.getElementById('flag-corpo-chassi-reinspecao').value,
                pressao_inicial: document.getElementById('pressao-inicial-corpo-chassi-reinspecao').value,
                duracao: document.getElementById('duracao-corpo-chassi-reinspecao').value,
                pressao_final: document.getElementById('pressao-final-corpo-chassi-reinspecao').value,
                vazamento: document.getElementById('vazamento-corpo-chassi-reinspecao').value,
                tipo_teste: "Corpo do tanque + chassi"
            }
        }
    };

    console.log('Dados coletados:', data); // Mostra os dados no console

    // Aqui você pode enviar os dados para o servidor, por exemplo usando fetch:
    fetch('/reteste-estanqueidade-tanque', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
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
            timer: 1000,
            timerProgressBar: true,
            didOpen: (toast) => {
              toast.onmouseenter = Swal.stopTimer;
              toast.onmouseleave = Swal.resumeTimer;
            }
          });
          Toast.fire({
            icon: "success",
            title: "Reinspeção registrada com sucesso!"
        });
        setTimeout(() => {
            location.reload();
        }, 1000);
    })
    .catch((error) => {
        const Toast = Swal.mixin({
            toast: true,
            position: "bottom-end",
            showConfirmButton: false,
            timer: 1000,
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
        }, 1000);
    });
});

