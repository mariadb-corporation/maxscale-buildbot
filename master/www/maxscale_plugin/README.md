# README

## How use plugin?

1. Place plugin directory to the `master/www/` directory
2. Configure plugin in the `master/master.py` file:
    ```python
        c['www'] = dict(
            ...
            plugins=dict(
                ...
                maxscale_plugin={
                    "filters": [
                        {"name": "Only build", "tags": ["+build", "-test"]},
                        {"name": "Only test", "tags": ["-build", "+test"]}
                    ]
                }
            )
        )
    ```
3. Reconfigure BuildBot

## Developing

1. Place plugin directory to the `master/www/` directory
2. Place https://github.com/buildbot/buildbot/tree/master/www/build_common directory to the `master/www/` directory
3. Install dependencies via `yarn install`
4. Compile plugin via `pip3 install -e .`
5. Configure plugin in the `master/master.py` file:
    ```python
        c['www'] = dict(
            ...
            plugins=dict(
                ...
                maxscale_plugin={
                    "filters": [
                        {"name": "Only build", "tags": ["+build", "-test"]},
                        {"name": "Only test", "tags": ["-build", "+test"]}
                    ]
                }
            )
        )
    ```
6. Reconfigure BuildBot

After any changes to the plugin code, you need to run the `pip3 install -e .` command to recompile the plugin and apply the changes.
