class MultiSelect {
    _counter = 0;

    constructor(multiselect){
        // Criando o elemento pai que junta campo de busca com opções.
        let master_container = document.createElement('div')
        master_container.className = 'position-relative ' + multiselect.className

        // Criação do elemento do campo de busca.
        this.input_search = document.createElement('input');
        this.input_search.type = 'text'
        this.input_search.placeholder = multiselect.getAttribute('data-placeholder') || '';
        this.input_search.className = 'multiselect-search form-select form-select-sm bg-dark-4 border-dark'

        // Criação do container de opções.
        this.options_container = document.createElement('div');
        this.options_container.style.zIndex = 1000;
        this.options_container.className = 'multiselect rounded mt-2 position-absolute w-100 bg-dark-3 rounded p-2 gap-1 d-flex flex-column d-none'

        this.input_search.addEventListener('focus', () => {
            this.options_container.classList.toggle('d-none', false)
        })
        this.input_search.addEventListener('input', () => {
            for (let option of this.options_container.children){
                if(!this.input_search.value){
                    option.classList.toggle('d-none', false)
                    continue
                }

                if(option.innerText.toLocaleLowerCase().includes(this.input_search.value.toLocaleLowerCase())){
                    option.classList.toggle('d-none', false)
                }
                else {
                    option.classList.toggle('d-none', true)
                }

                if (this.options_container.querySelectorAll('label.d-none').length == this.options_container.children.length){
                    this.options_container.classList.toggle('d-none', true);
                }
                else {
                    this.options_container.classList.toggle('d-none', false);
                }
            }
        })
        document.body.addEventListener('click', () => {
            if (document.querySelector('.multiselect:hover, .multiselect-search:hover')){
                return;
            }

            this.options_container.classList.toggle('d-none', true)
        })

        for (var option of multiselect.children){
            this.add_option(option.innerText);
        }

        master_container.appendChild(this.input_search)
        master_container.appendChild(this.options_container);
        
        multiselect.after(master_container);
        multiselect.remove();
    }

    add_option(option_text){
        this._counter++;

        let option_id = `option-${this._counter}`;

        let new_option = document.createElement('div');
        new_option.className = 'p-2 multiselect-option d-flex gap-2 rounded'

        let checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = option_id;
        new_option.appendChild(checkbox);

        let text = document.createElement('span');
        text.innerText = option_text;
        new_option.appendChild(text);
        
        let label = document.createElement('label');
        label.style.display = 'block';
        label.setAttribute('for', option_id);
        label.appendChild(new_option);

        this.options_container.appendChild(label);
    }

    get_checked_options(){
        return Array.from(
            this.options_container.querySelectorAll('label:has(input:checked) > div > span')
        ).map(item => item.innerText)
    }

    clear_options(){
        for(let option of Array.from(this.options_container.children)){
            option.remove();
        }
    }
}