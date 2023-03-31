var errorHandled = false;
var updateTimer = null;
var currentBearerToken = "";
var debug = true;

async function loadConfig() {
        var form = document.getElementById('configForm').elements;
        form.smipurl.value = config.url;
        form.authenticator.value = config.authenticator;
        form.smipusername.value = config.username;
        form.password.value = config.password;
        form.role.value = config.role; 
        document.getElementById("login").style.display = "block";
        document.getElementById("machines").style.display = "none";
}

function showElement(id, show) {
    document.getElementById(id).style.display = show == true ? "block" : "none" ;
}

function toggle(id) {
    document.getElementById(id).style.display = document.getElementById(id).style.display == "block" ? "none" : "block" ;
}

function submitConfig() {
    var form = document.getElementById('configForm').elements;

    config.url = form.smipurl.value;
    config.authenticator = form.authenticator.value;
    config.username = form.smipusername.value;
    config.password =  form.password.value;
    config.role = form.role.value;
    config.machineType = "fis_machine";
    config.stationType = "fis_station";
    
    alert("Successfully submitted SMIP Config! Click OK to continue...")
    showElement("login", false)
    loadMachines()
    updateLoop()
    showElement("machines", true)
}
function loadMachines() {
    document.getElementById("btnRefresh").innerHTML = "<img src=\"spinner.gif\" height=\"22px\">";
    sendSmipQuery({
        query: `{
            equipments(filter: {typeName: {equalTo: "${config.machineType}"}}) {
                displayName
                typeName
                id
                childEquipment {
                displayName
                typeName
                id
                attributes(filter: {relativeName: {startsWithInsensitive: "evt_desc"}}) {
                        relativeName
                        id
                    }
                }
            }
        }`
    }, populateUI)
}

function updateStation(statusId, stationId) {
    var endDate = new Date();
    var startDate = new Date(endDate);
    var durationInMinutes = 10;
    startDate.setMinutes(endDate.getMinutes() - durationInMinutes);
    sendSmipQuery({
        query: `query HistoryQuery {
            getRawHistoryDataWithSampling(
                ids: ["${statusId}"]
                maxSamples: 1
                startTime: "${startDate.toISOString()}"
                endTime: "${endDate.toISOString()}"
            ) {
                id
                ts
                stringvalue
            }
        }`
    }, updateUI, stationId)
}

async function sendSmipQuery(theQuery, callBack, metaData) {
    if (!currentBearerToken) {
        currentBearerToken = await smip.getBearerToken();
    } 
    try {
        callBack(await smip.performGraphQLRequest(theQuery, config.url, currentBearerToken), metaData);
    }
    catch (ex) {
        if (ex == 400 || ex == 401) {
            console.log("perhaps the bearer token has expired, let's get a new one");
            currentBearerToken = await smip.getBearerToken();
            callBack(await smip.performGraphQLRequest(theQuery, config.url, currentBearerToken));
        } else {
            console.log("caught an error: " + ex);
            if (!errorHandled)
                alert ("An unexpected error occured accessing the SMIP!");
            errorHandled = true;
        }
    }
}

function deleteElements(className) {
    var elements = Array.from(document.getElementsByClassName(className))
    if (elements.length != 0) {
        elements.forEach((element) => {
            element.remove()
        })
    }
}

function populateUI(payload, query) {
    if (payload.data.equipments.length != 0) {
        payload.data.equipments.forEach (function(item, index, arr) {
            showElement("empty", false);
            machineId = "machine" + item.id;
            if (!document.getElementById(machineId)) {
                newMachine = new widgetFactory(machineId, item);
                document.getElementById("machines").appendChild(newMachine.build(newMachine));
            } else {
                //Machines don't really update, stations do
            }
            item.childEquipment.forEach (function(item, index, arr) {
                    stationId = "station" + item.id;
                    if (!document.getElementById(stationId)) {
                        newStation = new widgetFactory(stationId, item, config.stationType);
                        document.getElementById(machineId).appendChild(newStation.build(newStation));
                        document.getElementById(stationId).widget.statusId = item.attributes[0].id;
                    }
                    updateStation(document.getElementById(stationId).widget.statusId, item.id);
                    document.getElementById(machineId).widget.update(item);
                }
            );
        });
        document.getElementById("btnRefresh").innerHTML = "Refresh";
    } else {
        console.log("Empty payload for equipments query. Nothing to populate.");
        showElement("empty", true);
        deleteElements("fis_machine")
        //TODO Delete elements as they disappear from SMIP
    }
}

function updateUI(payload, stationId) {
    var faultedStates = ["BAD PROGRAM","POWER OFF","ESTOP","I/O FAULT","SAFETY TRIP","MOTOR OFF","FAULTED","ROBOT FAULTED","COMMUNICATION FAULT"];
    var runningStates = ["NORMAL OPERATION","RUNNING","BYPASS MODE","MANUAL MODE"];
    if (payload && payload.data && payload.data.getRawHistoryDataWithSampling && payload.data.getRawHistoryDataWithSampling[0] && payload.data.getRawHistoryDataWithSampling[0].stringvalue) {
        var newState = payload.data.getRawHistoryDataWithSampling[0].stringvalue;
        document.getElementById("status" + stationId).innerHTML = newState;
        if (faultedStates.indexOf(newState) != -1) {
            document.getElementById("station" + stationId).classList.add("faulted");
        } else {
            document.getElementById("station" + stationId).classList.remove("faulted");
        }
        if (runningStates.indexOf(newState) != -1) {
            document.getElementById("station" + stationId).classList.add("running");
        } else {
            document.getElementById("station" + stationId).classList.remove("running");
        }
    }
    else {
        console.log("Empty payload for timeseries query. Nothing to update.");
    }
}

function updateLoop() {
    setInterval(function () {
        loadMachines();
    }, 5000);
}