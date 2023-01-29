// Thêm hàng vào giỏ
function addToCart(id, name, price) {
    event.preventDefault()

    //gửi request lên server bằng javascript, /api/add-cart : trong index.py
    fetch('/api/add-cart', {
        method: 'post',
        body: JSON.stringify({ //stringify : ép đối tượng thành chuỗi
            'id': id,
            'name': name,
            'price': price
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {
        console.info(data)

        let counter = document.getElementsByClassName('cart-counter')
        for (let i = 0; i < counter.length; i++)
            counter[i].innerText = data.total_quantity
    }).catch(function(err) {
        console.error(err)
    })
}

// Trả tiền
function pay() {
    if (confirm("Êtes-vous sûr de vouloir payer ?") == true) {
        fetch("/api/pay", {
            method: 'post'
        }).then(res => res.json()).then(data => {
        if (data.code == 200)
            location.reload()
        }).catch(err => console.error(err))
    }
}

// Cập nhật số lượng sau khi dùng tăng số lượng trong giỏ - onblur
function updateCart(id, obj) {
    fetch('/api/update-cart', {
        method: "put",
        body: JSON.stringify({
            "id": id,
            "quantity": parseInt(obj.value) //pareseInt để chắc đó là số không phải là chuỗi
        }),
        headers: {
            'Content-Type': 'application/json' //loại dữ liệu của mình trong activity
        }
    }).then(res => res.json()).then(data => { //trả về hàm, data là kết quả trả ra từ res.json()
        let counter = document.getElementsByClassName('cart-counter')
        for (let i = 0; i < counter.length; i++)
            counter[i].innerText = data.total_quantity

        let amount = document.getElementById('total-amount')
        amount.innerText = new Intl.NumberFormat().format(data.total_amount)
    }).catch(err => console.error(err))
}

//Xóa sản phẩm trong giỏ - onclick
function deleteCart(id) {
    if (confirm("Etes-vous sûr de vouloir supprimer ?") == true) {
         fetch('/api/delete-cart/' + id, {
            method: "delete",
            headers: {
            'Content-Type': 'application/json' //loại dữ liệu của mình trong activity
            }
        }).then(res => res.json()).then(data => {
            let counter = document.getElementsByClassName('cart-counter')
            for (let i = 0; i < counter.length; i++)
                counter[i].innerText = data.total_quantity

            let amount = document.getElementById('total-amount')
            amount.innerText = new Intl.NumberFormat().format(data.total_amount)

            let e = document.getElementById("product" + id)
            e.style.display = "none"
        }).catch(err => console.error(err))
    }
}

function addComment(productId) {
    let content = document.getElementById('commentId')
    if (content !== null) {
        fetch('/api/comments', {
            method: "post",
            body: JSON.stringify({
                "product_id": productId,
                "content": content.value
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            if (data.status == 201) {
                let c = data.comment //comment từ index.py

                let area = document.getElementById('commentArea')

                area.innerHTML = `
                <div class="row">
                    <div class="col-md-1 col-xs-4">
                        <img src="${c.user.avatar}" class="img-fluid rounded-circle" alt="demo"/>
                    </div>
                    <div class="col-md-11 col-xs-8">
                        <p>${c.content}</p>
                        <p><em>${c.created_date}</em></p>
                    </div>
                </div>
                ` + area.innerHTML //cái này bao gồm đoạn ở trong commentArea ở file html, `` cho phép cộng chuỗi, xuống dòng
            }
            else if (data.status == 404)
                alert(data.err_msg)
        })
    }
}