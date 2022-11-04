state_select = document.querySelectorAll('.state_select')
for (i = 0; i < state_select.length; i++) {
    state_select[i].addEventListener('change', function () {
        state_id = this.value
        city_id = this.dataset.id

        city_select = document.getElementById('id_city_' + city_id)

        fetch(`/fetch/get-city/?state=${state_id}`)
            .then(response => response.json())
            .then(data => {
                length = city_select.options.length;
                for (i = length - 1; i >= 0; i--) {
                    city_select.options[i] = null;
                }

                for (i = 0; i < data.length; i++) {
                    option = document.createElement('option')
                    option.text = data[i]['fields']['name']
                    option.value = data[i]['pk']
                    city_select.append(option)
                }
            })
    })
}