L.CursorHandler = L.Handler.extend({

    addHooks: function () {
        this._popup = new L.Popup();
        this._map.on('mouseover', this._open, this);
        this._map.on('mousemove', this._update, this);
        this._map.on('mouseout', this._close, this);
    },

    removeHooks: function () {
        this._map.off('mouseover', this._open, this);
        this._map.off('mousemove', this._update, this);
        this._map.off('mouseout', this._close, this);
    },

    _open: function (e) {
        this._update(e);
        this._popup.openOn(this._map);
    },

    _close: function () {
        this._map.closePopup(this._popup);
    },

    _update: function (e) {
        this._popup.setLatLng(e.latlng)
            .setContent("<b>Latitude: " + e.latlng.lat + "</b><br><b>Longitude: " + e.latlng.lng + "</b>");
    }


});

L.Map.addInitHook('addHandler', 'cursor', L.CursorHandler);
var element = document.getElementById('osm-map');
var map = L.map(element, {zoomControl: false, cursor: true, doubleClickZoom:false});
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 10000
}).addTo(map);
L.control.zoom({
    position: 'bottomright'
}).addTo(map);

var markerArray = [];
fetchDrones();
var droneDisconnectedIcon = L.icon({
    iconUrl: '/static/images/black-silhouette-drone-against-white-background_1023514-2334-removebg-preview.png',
    iconSize:     [38, 38], // size of the icon
    shadowSize:   [0, 0], // size of the shadow
    iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
    shadowAnchor: [4, 62],  // the same for the shadow
    popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
});

var droneConnectedIcon = L.icon({
    iconUrl: '/static/images/drone_invert-removebg-preview.png',
    iconSize:     [38, 38], // size of the icon
    shadowSize:   [0, 0], // size of the shadow
    iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
    shadowAnchor: [4, 62],  // the same for the shadow
    popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
});




function fetchDrones() {
  const apiUrl = '/api/drones';
  const myHeaders = new Headers({
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            });

  fetch(apiUrl, {
      method: "get",
      headers: myHeaders
  }).then(response => {
      if (!response.ok) {
        throw new Error(`Network response was not ok (status ${response.status})`);
      }
      return response.json();
    })
    .then(data => {
      console.log(data);
      if (data.length > 0) {
        data.forEach(pinpointDrones);
        var group = L.featureGroup(markerArray).addTo(map);
        map.flyToBounds(group.getBounds().pad(0.5));
      } else {
          var target = L.latLng('39', '35');
          map.setView(target, 1);
          map.flyTo(target, 7);
      }
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
};


function pinpointDrones(drone) {
    var target = L.latLng(drone.latitude, drone.longitude);
    map.setView(target, 1);
    var myPopup = L.DomUtil.create('div', 'infoWindow');
    myPopup.innerHTML = '<div class="popup-box">' +
            '<i class="fa fas fa-rocket"></i>' +
            '<span>Drone Information</span>' +
            '<ul>' +
                '<li>ID: ' + drone.id + '</li>' +
                '<li>Name: ' + drone.name + '</li>' +
                '<li>Altitude: ' + drone.altitude + '</li>' +
                '<li>Connected: ' + connected(drone.connected) + '</li>' +
            '</ul>' +
            '</div>'
    const droneIcon = drone.connected ? droneConnectedIcon : droneDisconnectedIcon;
    var DronecubeMarker = L.Marker.extend({
       options: {
            id: drone.id,
            name: drone.name,
            latitude: drone.latitude,
            longitude: drone.longitude,
            altitude: drone.altitude,
            connected: drone.connected,
       }
    });
    const marker = new DronecubeMarker(target,  {
            id: drone.id,
            name: drone.name,
            latitude: drone.latitude,
            longitude: drone.longitude,
            altitude: drone.altitude,
            connected: drone.connected,
       }).setIcon(droneIcon).on('click', onMarkerClick).on('dblclick', connectionStatus).bindPopup(myPopup);
    markerArray.push(marker);
};


var popup = L.popup({ maxWidth: "auto" });

function connected(connected) {
    return connected ? "True" : "False";
};

function connectionStatus(e) {
   map.closePopup();
  const apiUrl = '/api/drones/' + e.target.options.id;
  const myHeaders = new Headers({
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            });

  fetch(apiUrl, {
      method: "post",
      headers: myHeaders
  }).then(response => {
      if (!response.ok) {
        throw new Error(`Network response was not ok (status ${response.status})`);
      }
      return response.json();
    })
    .then(data => {
      e.target.options.connected = data.connected;
      const droneIcon = data.connected ? droneConnectedIcon : droneDisconnectedIcon;
      e.target.setIcon(droneIcon);
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
};

async function onMapClick(e) {
    console.log(e);
    var drone = L.latLng(e.latlng.lat, e.latlng.lng);
    map.setView(drone, 1);
    const apiUrl = '/api/drones';

      await fetch(apiUrl, {
          method: "post",
          headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({
              name: 'Drone Cube',
              latitude: e.latlng.lat,
              longitude: e.latlng.lng,
              altitude: 35,
              home_latitude: 35,
              home_longitude: 35,
              home_altitude: 35,
              velocity_x: 35,
              velocity_y: 35,
              velocity_z: 35,
              connected: "Connected"
          })
      }).then(response => {
          console.log(response);
          if (!response.ok) {
            throw new Error(`Network response was not ok (status ${response.status})`);
          }
          return response.json();
        })
        .then(data => {
          var myPopup = L.DomUtil.create('div', 'infoWindow');
            myPopup.innerHTML = '<div class="popup-box">' +
                    '<i class="fa fas fa-rocket"></i>' +
                    '<span>Drone Information</span>' +
                    '<ul>' +
                        '<li>ID: ' + data.id + '</li>' +
                        '<li>Name: ' + data.name + '</li>' +
                        '<li>Altitude: ' + data.altitude + '</li>' +
                        '<li>Connected: ' + connected(data.connected) + '</li>' +
                    '</ul>' +
                    '</div>'
            const droneIcon = data.connected ? droneConnectedIcon : droneDisconnectedIcon;
            var DronecubeMarker = L.Marker.extend({
               options: {
                    id: data.id,
                    name: data.name,
                    latitude: data.latitude,
                    longitude: data.longitude,
                    altitude: data.altitude,
                    connected: data.connected,
               }
            });
            const marker = new DronecubeMarker(drone,  {
                    id: data.id,
                    name: data.name,
                    latitude: data.latitude,
                    longitude: data.longitude,
                    altitude: data.altitude,
                    connected: data.connected,
               }).setIcon(droneIcon).on('click', onMarkerClick).on('dblclick', connectionStatus).bindPopup(myPopup);
            marker.addTo(map);
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });
};

function onMarkerClick(e) {
    var popup = e.target.getPopup();
  const apiUrl = '/api/drones/' + e.target.options.id;
  const myHeaders = new Headers({
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            });

  fetch(apiUrl, {
      method: "get",
      headers: myHeaders
  }).then(response => {
      if (!response.ok) {
        throw new Error(`Network response was not ok (status ${response.status})`);
      }
      return response.json();
    })
    .then(data => {
      var content = '<div class="popup-box">' +
            '<i class="fa fas fa-rocket"></i>' +
            '<span>Drone Information</span>' +
            '<ul>' +
                '<li>ID: ' + data.id + '</li>' +
                '<li>Name: ' + data.name + '</li>' +
                '<li>Altitude: ' + data.altitude + '</li>' +
                '<li>Connected: ' + connected(data.connected) + '</li>' +
            '</ul>' +
            '</div>';
      e.target.options.id = data.id;
      e.target.options.name = data.name;
      e.target.options.latitude = data.latitude;
      e.target.options.longitude = data.longitude;
      e.target.options.altitude = data.altitude;
      e.target.options.connected = data.connected;
      popup.setContent(content);
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
}

map.on('dblclick', onMapClick);