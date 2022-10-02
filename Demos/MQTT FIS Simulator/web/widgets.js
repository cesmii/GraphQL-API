class widgetFactory {
    constructor(id, item, childType) {
        this.id = id;
        this.displayName = item.displayName;
        this.typeName = item.typeName;
        this.childType = childType;
        this.statusId = null;
    }

    build(self) {
        var newWidget = document.createElement("div");
        newWidget.id = this.id;
        newWidget.className = "widget " + this.typeName;
        newWidget.widget = self;
        var widgetTitle = document.createTextNode(this.displayName);
        newWidget.appendChild(widgetTitle);
        if (this.typeName == this.childType) {
            var widgetStatus = document.createElement("div");
            widgetStatus.id = this.id.replace("station", "status");
            widgetStatus.className = "fis_status";
            widgetStatus.innerText = "<No Status>";
            newWidget.appendChild(widgetStatus);
        }
        return newWidget;
    }

    update(item) {
        document.getElementById(machineId).classList.remove("updating");
        var refresh = Math.floor(Math.random()*(4-1+1)+1);
        refresh = 1000 + (refresh * 100);
        setTimeout(() => {
            document.getElementById(this.id).classList.add("updating");
        }, refresh);
    }
}