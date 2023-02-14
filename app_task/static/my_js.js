function (proj_id){
    let b = null;
    let a = document.getElementsByTagName("a");
    let out = [];
    for (let index = 0; index < a.length; index++) {
        const element = a[index];
        if (element.dataset.id != undefined) {
            out.push(element.dataset)
        }
    }
    console.log(out);
}