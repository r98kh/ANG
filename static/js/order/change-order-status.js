changeStatusBtn = document.querySelector('#changeStatusBtn')
if (changeStatusBtn) {
    changeStatusBtn.addEventListener('click', function () {
        orderId = this.dataset.id
        track = document.querySelector('#statusSelect')
        trackValue = track.value
        trackName = track.options[track.selectedIndex].text

        Swal.fire({
            title: 'تغییر وضعیت سفارش',
            text: `سفارش به وضعیت ${trackName} تغییر کند؟`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: 'بله تغییر بده',
            cancelButtonText: 'انصراف',
            customClass: {
                confirmButton: 'btn btn-primary me-3',
                cancelButton: 'btn btn-label-secondary'
            },
            buttonsStyling: false,
        }).then(async function (result) {
            if (result.value) {
                url = '/fetch/order-change-status/'
                response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    },
                    body: JSON.stringify({ 'orderId': orderId, 'trackValue': trackValue, 'trackName': trackName })
                })
                data = await response.json()

                Swal.fire({
                    icon: "success",
                    title: 'وضعیت سفارش تغییر کرد',
                    text: 'وضعیت سفارش به ' + trackName + ' تغییر یافت',
                    customClass: {
                        confirmButton: 'btn btn-success'
                    },
                    confirmButtonText: 'باشه'
                })

            }
        });

    })
}
