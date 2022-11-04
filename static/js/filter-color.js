filterColorRadio = document.querySelectorAll('.filterColor')

filterColorRadio.forEach(element => {
    element.addEventListener('change', async function () {
        productId = this.value

        response = await fetch(`/fetch/filter-color/?productId=${productId}`)
        data = await response.json()

        $('#colorDiv').html(data['data'])
    })
});