class FiltersState {
    constructor($stateProvider, glMenuServiceProvider, config) {
        const SECTION_NAME = 'maxscale_plugin_filters';

        glMenuServiceProvider.addGroup({
            name: SECTION_NAME,
            caption: 'Builders filters',
            icon: 'tags',
            order: 5
        });

        if (config.plugins.maxscale_plugin.filters == null) {
            return;
        }

        config.plugins.maxscale_plugin.filters.forEach((filter, index) => {
            const state = {
                controller: "FiltersController",
                name: `filter_${index}`,
                data: {
                    group: SECTION_NAME,
                    caption: filter.name,
                    tags: filter.tags,
                }
            };
            $stateProvider.state(state);
        });
    }
}

angular
    .module('maxscale_plugin', [
        'ui.router',
        'ngAnimate',
        'guanlecoja.ui',
        'bbData',
    ])
    .config(['$stateProvider', 'glMenuServiceProvider', 'config', FiltersState]);
