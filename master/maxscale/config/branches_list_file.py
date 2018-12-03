MAXSCALE_BRANCHES_LIST = [
    {
        "branch": "^develop$",
        "test_set": "-LE HEAVY"
    },
    {
        "branch": "MXS-.*",
        "test_set": "-LE HEAVY"
    },
    {
        "branch": r"^2\.2$",
        "test_set": "-LE HEAVY"
    },
    {
        "branch": r"^2\.3$",
        "test_set": "-LE UNSTABLE"
    }
]

MAXSCALE_PERF_BRANCHES_LIST = [
    {
        "branch": "^develop$"
    },
    {
        "branch": "MXS-.*"
    },
    {
        "branch": r"^2\.2$"
    },
    {
        "branch": r"^2\.3$"
    }
]
