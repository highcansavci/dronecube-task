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
var map = L.map(element, {zoomControl:false, cursor: true});
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19
}).addTo(map);
L.control.zoom({
    position: 'bottomright'
}).addTo(map);
var target = L.latLng('39', '35');
map.setView(target, 1);
map.flyTo(target, 7);