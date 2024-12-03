async function set_wwan() {
    //get what the next state of wwan should be
    let set_state = {};
    const cb = document.getElementById("wwan");
    //current state of checked is after it was clicked, so the state it needs to become
    set_state.new_state = cb.checked;
    //try to make it a reality
    try {
        const resp = await post_json("/api/set_wwan", set_state);
    } catch (err) {
        console.log("Could not toggle wwan:\n" + err);
        cb.checked = !cb.checked;
    }
}

document.addEventListener('DOMContentLoaded', async function () {
    try {
        const wwan_request = await (await fetch('/api/get_wwan')).json();
        document.getElementById("wwan").checked = wwan_request.state;
        if (wwan_request.state) {
            try {
                const wwan_stats_request = await (await fetch('/api/get_wwan_stats')).json();
                document.getElementById("imei").innerText = wwan_stats_request.imei;
                document.getElementById("operator").innerText = wwan_stats_request.operator;
                document.getElementById("model").innerText = wwan_stats_request.model;
                document.getElementById("signal").innerText = wwan_stats_request.signal;
                document.getElementById("wwan_info").style.display = "block";
            } catch (err) {
                console.log(err);
                document.getElementsByClassName("body")[0].append("Could not get WWAN info, if it was just switch on this can take some time to be available");
                return;
            }
        }
    } catch (err) {
        console.log(err);
        return;
    }
}, false);
