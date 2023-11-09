// Inicializando tooltips bootstrap.
setInterval(() => {
    for (element of Array.from($('[data-bs-toggle="tooltip"]:not([tooltiped])'))){
        element.setAttribute('tooltiped', true);
        new bootstrap.Tooltip(element, {
            trigger: 'hover',
            delay: {show: 300}
        });
    }
}, 500)


const API = {
    endpoint: '/rest/plate',
    mimetype: 'application/json',

    get(query){
        query = new URLSearchParams(query);
        return $.get(`${this.endpoint}?${query}`);
    },
    add(data){
        return $.ajax(this.endpoint, {
            method: 'POST',
            contentType: this.mimetype,
            data: JSON.stringify(data)
        });
    },
    replace(data){
        return $.ajax(this.endpoint, {
            method: 'PUT',
            contentType: this.mimetype,
            data: JSON.stringify(data)
        });
    },
    edit(data){
        return $.ajax(this.endpoint, {
            method: 'PATCH',
            contentType: this.mimetype,
            data: JSON.stringify(data)
        });
    },
    delete(plate_id){
        return $.ajax(this.endpoint, {
            method: 'DELETE',
            contentType: this.mimetype,
            data: JSON.stringify({plate_id: plate_id})
        });
    }
}


async function fetch_template(name){
    return await (await fetch(`${UI_TEMPLATE_FOLDER}/${name}.html.j2`)).text();
}


const templates = {
    plate_card: fetch_template('plate_card')
}

function locale_date(date){
    if(!date) return;
    return new Date(date + ' 00:00:00').toLocaleDateString()
}

function locale_datetime(datetime){
    if(!datetime) return;
    return new Date(Date.parse(datetime + ' UTC')).toLocaleString()
}


const ui = {
    on_request_error(reason){
        console.log(reason);
        if(!reason){
            message = 'Houve um problema de conexão com sua internet.';
        }
        else {
            message = reason.responseJSON?.message;

            if (!reason.responseJSON){
                message = `${reason.status}: ${reason.statusText}`
            }
            else if (!message){
                error = reason.responseJSON.validation_error.body_params[0];
                message = `${error.loc[0]}: ${error.msg}`;
            }
        }

        ui.toasts.show(
            message,
            false
        )
    },

    plate_cards: {
        container: $('.plate-cards-results'),
        action_data: {},
        plates: {},

        async render_group(rows) {
            return nunjucks.renderString(await templates.plate_card, {
                is_admin: IS_ADMIN,
                rows: rows,
                date: locale_date,
                datetime: locale_datetime
            });
        },

        render_row(row){
            return nunjucks.renderString(
                `{% import '${UI_TEMPLATE_FOLDER}/plate_card.html.j2' as plate_card %}`
                + `{{ plate_card.render_plate_row(row, date, datetime, is_admin) }}`,
                {
                    is_admin: IS_ADMIN,
                    row: row,
                    date: locale_date,
                    datetime: locale_datetime
            }
            )
        },

        async add_group(rows){
            for(row of rows){
                this.plates[row.id] = row;
            }
            this.container.append(await this.render_group(rows));
        },

        async set_groups(groups){
            this.clear();

            for(rows of groups){
                await this.add_group(rows);
            }
        },

        clear(){
            this.container.html('');
            this.plates = {};
        },

        prepare_to_remove(button_element){
            row = button_element.parentElement.parentElement.parentElement;

            this.action_data = {
                plate_id: row.querySelector('td').innerText,
                row: row
            }
        },

        prepare_to_add(){
            $('#modal-add-new-or-edit-plate').attr('data-mode', 'add');
        },

        prepare_to_edit(button_element){
            const modal_element = $('#modal-add-new-or-edit-plate')
            const row = button_element.parentElement.parentElement.parentElement;
            const plate_id = parseInt(row.querySelector('td').innerText)

            modal_element.attr('data-mode', 'edit');

            this.action_data = {
                plate_id: plate_id,
                row: row
            }

            const plate = ui.plate_cards.plates[plate_id];

            const fieldnames = [
                'serial_number',
                'certificate_number',
                'certificate_url',
                'calibration_date',
                'first_installation_date',
                'due_date',
                'external_diameter',
                'internal_diameter_reference',
                'local',
                'point',
                'status_date',
                'status_local',
                'type',
                'status_text'
            ];

            for(let fieldname of fieldnames){
                let element = modal_element.find(`input[name=${fieldname}]`);
                let value = plate[fieldname || ''];
                
                if(element.attr('type') == 'radio'){
                    for(let radio of element){
                        if(radio.value == value){
                            radio.checked = true;
                        }
                    }
                }
                else {
                    element.val(value);
                }
            }
        },

        prepare_to_replace(button_element){
            const plate_card_header = button_element.parentElement;

            this.action_data = {
                serial_number: plate_card_header.querySelector('#serial_number').innerText,
                table: plate_card_header.parentElement.querySelector('table tbody')
            }
        }
    },

    loading: new bootstrap.Modal($('#modal-loading')),

    multiselect: {
        obj: new MultiSelect(document.querySelector('select[multiple]')),
        async reload_options(){
            this.obj.clear_options();

            API.get({onlylocations: true}).then(response => {
                for(let location of response){
                    this.obj.add_option(location);
                }
            }).catch(ui.on_request_error);
        }
    },

    toasts: {
        show(text, success){
            const toast_element = $('.toast');
            const toast_body_element = toast_element.find('.toast-body');
            const toast_icon_element = toast_body_element.find('i');

            if(success || success === null || success === undefined){
                toast_body_element.toggleClass('bg-success', true);
                toast_body_element.toggleClass('bg-danger', false);
                toast_icon_element.toggleClass('fa-check', true)
                toast_icon_element.toggleClass('fa-xmark', false)
            }
            else {
                toast_body_element.toggleClass('bg-danger', true);
                toast_body_element.toggleClass('bg-success', false);
                toast_icon_element.toggleClass('fa-check', false)
                toast_icon_element.toggleClass('fa-xmark', true)
            }

            toast_body_element.find('span').text(text);
            new bootstrap.Toast(toast_element).show();
        }
    }
};


// Evento acionado ao pesquisar por placas.
$('.plate-filter').on('submit', async event => {
    event.preventDefault();

    // Obtendo elemento de formulário.
    const parent = $(event.target);

    // Obtendo todos os campos encessários do formulário.
    const serial_number = parent.find('input[name="serial_number"]').val();
    const certificate_number = parent.find('input[name="certificate_number"]').val();
    const statuses = Array.from(parent.find('input[name="status"]:checked')).map(item => ['status', item.value]);
    const types = Array.from(parent.find('input[name="type"]:checked')).map(item => ['type', item.value]);
    const locations = ui.multiselect.obj.get_checked_options().map(item => ['location', item]);

    // Construindo a query de busca.
    query = [
        ['serial_number', serial_number],
        ['certificate_number', certificate_number],
        ...statuses,
        ...types,
        ...locations
    ]

    // Exibindo modal de carregamento.
    ui.loading.show();
    
    await API.get(query).then(
        response => ui.plate_cards.set_groups(response)
    ).catch(ui.on_request_error)

    // Recarregando as opções do multiselect.
    await ui.multiselect.reload_options();

    ui.loading.hide();
})


// Evento acionado ao confirmar a remoção de um registro de placa.
$('button#confirm-delete-plate-row').on('click', () => {
    ui.loading.show();
    let action_data = ui.plate_cards.action_data;

    API.delete(action_data.plate_id)
    .then(response => {
        const group = row.parentElement.parentElement.parentElement.parentElement;

        if(group.querySelectorAll('tr:has(td)').length == 1){
            group.remove();
        }
        else {
            action_data.row.remove();
        }

        ui.toasts.show(response.message);
    })
    .catch(ui.on_request_error)
    .always(() => ui.loading.hide())
})

// Evento acionado ao clicar no botão de adicionar nova placa.
$('button#add-new-plate').on('click', ui.plate_cards.prepare_to_add)

// Acionado sempre que um click no modal for feito, garante que os elementos
// ocultos estejam sem o atributo `required` e com campos limpos.
$('#modal-add-new-or-edit-plate').on('click', () => {
    $('input[name=status_date], input[name=status_local]').each((_, element) => {
        element = $(element);

        if(element.is(':visible')){
            element.attr('required', true);
        }
        else {
            element.removeAttr('required');
            element.val('');
        }
    })
});

// Evento acionado ao enviar formulário no modal de adicionar ou editar placa.
const modal_add_new_or_edit_plate = new bootstrap.Modal($('#modal-add-new-or-edit-plate'));
$('#modal-add-new-or-edit-plate form').on('submit', async event => {
    event.preventDefault();
    const fields = Object.fromEntries($(event.target).serializeArray().map(item => [item.name, item.value || null]));
    const mode = event.target.parentElement.parentElement.getAttribute('data-mode');

    modal_add_new_or_edit_plate.hide();
    ui.loading.show()

    if(mode != 'edit'){
        await API.add(fields)
        .then(response => {
            ui.plate_cards.add_group([response.plate]);
            ui.toasts.show(response.message);
            event.target.reset();
            ui.multiselect.reload_options();
        })
        .catch(ui.on_request_error)
        .always(() => ui.loading.hide());
        return;
    }

    let full_plate = ui.plate_cards.plates[ui.plate_cards.action_data.plate_id]
    fields.id = full_plate.id;

    await API.edit(fields)
    .then(response => {
        fields.created_at = full_plate.created_at;
        fields.created_by_operator = full_plate.created_by_operator;

        ui.plate_cards.plates[fields.id] = fields;
        ui.plate_cards.action_data.row.outerHTML = ui.plate_cards.render_row(fields);
        ui.toasts.show(response.message);
        event.target.reset();
        ui.multiselect.reload_options();
    })
    .catch(ui.on_request_error)
    .always(() => ui.loading.hide());
})


// Evento acionado ao enviar formulário no modal de substituir placa.
const modal_replace_plate = new bootstrap.Modal($('#modal-replace-plate'));
$('#modal-replace-plate form').on('submit', async event => {
    event.preventDefault();
    const fields = Object.fromEntries($(event.target).serializeArray().map(item => [item.name, item.value || null]))

    modal_replace_plate.hide();
    ui.loading.show()
    fields.serial_number = ui.plate_cards.action_data.serial_number;

    await API.replace(fields)
    .then(response => {
        event.target.reset();
        for(const row_element of ui.plate_cards.action_data.table.querySelectorAll('tr:has(td)')){
            const row_id = parseInt(row_element.querySelector('td').innerText);
            const plate_row = ui.plate_cards.plates[row_id];
            const now = new Date();

            if(plate_row.status_text != 'REMOVIDA'){
                plate_row.status_text = 'REMOVIDA';
                plate_row.status_date = [now.getFullYear(), now.getMonth(), now.getDate()].join('-');
                plate_row.status_local = null;
                row_element.outerHTML = ui.plate_cards.render_row(plate_row);
            }
        }
        ui.plate_cards.plates[response.plate.id] = response.plate;
        ui.plate_cards.action_data.table.innerHTML += ui.plate_cards.render_row(response.plate);
        ui.toasts.show(response.message);
        ui.multiselect.reload_options();
    })
    .catch(ui.on_request_error)
    .always(() => ui.loading.hide());
});


async function main(){
    ui.loading.show();

    // Obtendo os locais de placas.
    ui.multiselect.reload_options();

    // Obtendo todas as placas e exibindo na interface.
    await API.get().then(
        response => ui.plate_cards.set_groups(response)
    ).catch(ui.on_request_error)

    // Ocultando o modal de carregamento.
    ui.loading.hide();
}

main();