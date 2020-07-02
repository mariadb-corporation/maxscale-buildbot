require('./ws_keepalive.state.js');
require('./ws_keepalive.controller.js');

class WsKeepAlive {
    constructor($interval, socketService) {
        const interval = $interval(function() {
            socketService.send({ msg: 'keepalive' });
        }, 30000);
    }
}

angular.module('ws_keepalive_plugin')
.run(['$interval', 'socketService', WsKeepAlive]);
