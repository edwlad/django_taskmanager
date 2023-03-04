async function find_sprints(el, proj_id=0){
    // console.log("Поиск спринтов", el.innerHTML, proj_id);
    if (el = null){return;}

    let out = document.createElement("div");
    out.innerHTML = "<option value='' selected>-----</option>";

    let resp = await fetch("/api/sprints/?format=json&date_end=none&proj_id=" + proj_id);
    while (resp.ok) {
        let data = await resp.json();
        // console.log(data);
        data.results.forEach((el) => {
            out.innerHTML += `<option value="${el.id}">${el.id}: ${el.name}</option>`;
        })
        if (data.next){
            resp = await fetch(data.next);
        } else {
            break;
        }
    }

    // console.log("Завершено");
    el.innerHTML = out.innerHTML;

}