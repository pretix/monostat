var DateTime = luxon.DateTime;
document.addEventListener("DOMContentLoaded", function (event) {
    document.querySelectorAll("time[datetime]").forEach((el) => {
        const datetime = el.attributes["datetime"].value;
        const dt = DateTime.fromISO(datetime).setLocale("en");
        const date = dt.toLocaleString(DateTime.DATE_MED);
        const time = dt.toLocaleString(DateTime.TIME_24_WITH_SHORT_OFFSET);
        el.innerHTML = date + " " + time + " (" + dt.toRelative() + ")";
    })
});