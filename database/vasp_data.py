VASP_DATABASE = {
    "0xVASP001": {
        "name": "Demo Exchange",
        "type": "Centralized Exchange",
        "country": "India"
    },
    "0xVASP002": {
        "name": "Demo Crypto Exchange",
        "type": "Centralized Exchange",
        "country": "Singapore"
    }
}


def identify_vasp(wallet_address):
    return VASP_DATABASE.get(wallet_address)
