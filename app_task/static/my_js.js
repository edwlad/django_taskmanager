async function find_sprints(el, el_parent, proj_id = 0) {
    // console.log("Поиск спринтов в проекте", el.innerHTML, proj_id);
    if (el == null | el_parent == null) { return; }

    let out = document.createElement("div");
    out.innerHTML = "<option value='' selected>-----</option>";
    el.innerHTML = out.innerHTML;
    el_parent.innerHTML = out.innerHTML;

    let resp = await fetch("/api/sprints/?format=json&date_end=none&proj_id=" + proj_id);
    while (resp.ok) {
        let data = await resp.json();
        // console.log(data);
        data.results.forEach((el) => {
            out.innerHTML += `<option value="${el.id}">(${el.id}) ${el.name}</option>`;
        })
        if (data.next) {
            resp = await fetch(data.next);
        } else {
            break;
        }
    }

    // console.log("Завершено", out);
    el.innerHTML = out.innerHTML;

}

async function find_tasks(el, task_id = 0, sprint_id = 0) {
    // console.log("Поиск задач в спринте", el.innerHTML, sprint_id);
    if (el == null) { return; }
    if (sprint_id == "") { sprint_id = 0; }

    let out = document.createElement("div");
    out.innerHTML = "<option value='' selected>-----</option>";
    el.innerHTML = out.innerHTML;

    let url = "/api/tasks/?format=json&parent=none&sprint_id=" + sprint_id
    let resp = await fetch(url);
    while (resp.ok) {
        let data = await resp.json();
        // console.log(data);
        data.results.forEach((el) => {
            if (el.id != task_id) {
                out.innerHTML += `<option value="${el.id}">(${el.id}) ${el.name}</option>`;
            }
        })
        if (data.next) {
            resp = await fetch(data.next);
        } else {
            break;
        }
    }

    // console.log("Завершено", out);
    el.innerHTML = out.innerHTML;

}