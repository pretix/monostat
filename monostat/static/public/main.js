var DateTime = luxon.DateTime;
document.addEventListener("DOMContentLoaded", function (event) {
    document.querySelectorAll("time[datetime]").forEach((el) => {
        const datetime = el.attributes["datetime"].value;
        const dt = DateTime.fromISO(datetime);
        const date = dt.setLocale("en").toLocaleString(DateTime.DATE_MED);
        const time = dt.setLocale("en").toLocaleString(DateTime.TIME_24_WITH_SHORT_OFFSET);
        el.innerHTML = date + " " + time;
    })
});