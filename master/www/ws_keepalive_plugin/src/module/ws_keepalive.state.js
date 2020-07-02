class WsKeepaliveState {
    constructor($stateProvider) {
        const state = {
            controller: "WsKeepaliveController",
            name: 'WsKeepaliveState',
            data: {},
        };
        $stateProvider.state(state);
    }
}

angular
    .module('ws_keepalive_plugin', [])
    .config(['$stateProvider', WsKeepaliveState]);
