class FiltersController {
    constructor(config, $window, $state) {
        const tagsParams = $state.current.data.tags.map(tag => `tags=${encodeURIComponent(tag)}`).join('&');
        $window.location.href = `/#/builders?${tagsParams}`;
    }
}

angular
    .module('maxscale_plugin')
    .controller('FiltersController', ['config', '$window', '$state', FiltersController]);
