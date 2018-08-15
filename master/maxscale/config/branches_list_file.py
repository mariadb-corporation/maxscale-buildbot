MAXSCALE_BRANCHES_LIST = [
    {
        "branch": "^develop$",
        "test_set": "-LE HEAVY"
    },
    {
        "branch": "MXS-.*",
        "test_set": "-L LIGHT""
    },
    {
        "branch": r"^2\.2$",
        "test_set": "-LE HEAVY"
    }
]
