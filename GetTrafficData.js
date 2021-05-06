
function GetMap() {
    //Initialize a map instance.
    map = new atlas.Map('myMap', {
        center: [34.8246, 32.05414],
        zoom: 22,
        view: 'Auto',

        //Add authentication details for connecting to Azure Maps.
        authOptions: {
            //Use Azure Active Directory authentication.
/*            authType: 'anonymous',
            clientId: "04ec075f-3827-4aed-9975-d56301a2d663", //Your Azure Active Directory client id for accessing your Azure Maps account.
            getToken: function (resolve, reject, map) {
                //URL to your authentication service that retrieves an Azure Active Directory Token.
                var tokenServiceUrl = "https://azuremapscodesamples.azurewebsites.net/Common/TokenService.ashx";

                fetch(tokenServiceUrl).then(r => r.text()).then(token => resolve(token));
            }*/

            // Alternatively, use an Azure Maps key. Get an Azure Maps key at https://azure.com/maps. NOTE: The primary key should be used as the key.
            authType: atlas.AuthenticationType.subscriptionKey,
            subscriptionKey: 'EKpxrbgAeS0563m__gkw-554yTMJZy8A1F-H-c5FQ0A'
        }
    });
    //Wait until the map resources have fully loaded are ready, then load the traffic overlay.
    map.events.add('ready', function () {
        //Create a style control and add it to the map.
        map.controls.add(new atlas.control.StyleControl(), {
            position: 'top-right'
        });

        UpdateTrafficOverlay();
    });
}

function UpdateTrafficOverlay() {
    //Retrieve the options from the input fields.
    var incidentOption = document.getElementById('incidentOption').checked;

    var elm = document.getElementById('flowOptions');
    var selectedFlowOption = elm.options[elm.selectedIndex].value;

    //Set the trafficv overlay options.
    map.setTraffic({
        incidents: incidentOption,
        flow: selectedFlowOption
    });

    console.log(new View({
        projection: 'EPSG:4326',
        center: [34.8246, 32.05414],
        zoom: 22
    }))
}