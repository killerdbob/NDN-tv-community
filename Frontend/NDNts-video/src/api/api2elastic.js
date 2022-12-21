let elastic_url = ""


function sendInterest(router, resolution, bandwidth, frames, latency, rtt, cubic) {
    let = $.post(elastic_url, {
        "router": router,
        "resolution": resolution,
        "bandwidth": bandwidth,
        "frames": frames,
        "latency": latency,
        "rtt": rtt,
        "cubic": cubic
    })
        .success(function () { alert("second success"); })
        .error(function () { alert("error"); })
        .complete(function () { alert("complete"); });
}
