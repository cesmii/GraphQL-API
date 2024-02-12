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
        var partStatus = getRandomPartStatus();

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
            widgetStatus.classList.add("fault-unknown");
            newWidget.appendChild(widgetStatus);
        

        var widgetPartStatusContainer = document.createElement("div");
            widgetPartStatusContainer.classList.add("widgetPartStatusContainer");

        var widgetPartStatusParts = document.createElement("div");
            widgetPartStatusParts.classList.add("widget-status", "widgetPartStatusParts");
            widgetPartStatusParts.appendChild(spanWithText("Parts")).classList.add("widget-title");
            widgetPartStatusParts.appendChild(spanWithText(partStatus.parts));

        var widgetPartStatusScrap = document.createElement("div");
            widgetPartStatusScrap.classList.add("widget-status", "widgetPartStatusScrap");
            widgetPartStatusScrap.appendChild(spanWithText("Scrap")).classList.add("widget-title");
            widgetPartStatusScrap.appendChild(spanWithText(partStatus.scrap));

        var widgetPartStatusPercentComplete = document.createElement("div");
            widgetPartStatusPercentComplete.classList.add("widget-status", "widgetPartStatusPercentComplete");
            widgetPartStatusPercentComplete.appendChild(spanWithText("% Complete")).classList.add("widget-title");
            widgetPartStatusPercentComplete.appendChild(spanWithText(partStatus.percentComplete));

        var widgetPartStatusHoursRemaining = document.createElement("div");
            widgetPartStatusHoursRemaining.classList.add("widget-status", "widgetPartStatusHoursRemaining");
            widgetPartStatusHoursRemaining.appendChild(spanWithText("Hrs Remaining")).classList.add("widget-title");
            widgetPartStatusHoursRemaining.appendChild(spanWithText(partStatus.hoursRemaining));

        widgetPartStatusContainer.appendChild(widgetPartStatusParts);
        widgetPartStatusContainer.appendChild(widgetPartStatusScrap);
        widgetPartStatusContainer.appendChild(widgetPartStatusPercentComplete);
        widgetPartStatusContainer.appendChild(widgetPartStatusHoursRemaining);

        newWidget.appendChild(widgetPartStatusContainer);
}
        function getRandomPartStatus() {
            var partStatus = {};
            partStatus.parts = Math.floor(1000 + Math.random() * 9000);
            partStatus.scrap = Math.round(partStatus.parts * .03);
            partStatus.totalParts = Math.round((partStatus.parts + 500)/1000)*1000;
            partStatus.percentComplete = `${Math.round((partStatus.parts / partStatus.totalParts) * 100)}%`;
            partStatus.hours = Math.floor(100 + Math.random() * 900);
            partStatus.totalHours = Math.round((partStatus.hours + 50)/100)*100;
            partStatus.hoursRemaining = `${partStatus.totalHours - partStatus.hours}`;

            return partStatus;
        }

        function spanWithText(elementText) {
            // Create a new span element
            const spanElement = document.createElement('span');

            // Set the text content of the span element
            spanElement.textContent = elementText;

            return spanElement;
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