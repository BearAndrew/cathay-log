import requests

# 查詢 IP 資訊
def get_ip_info(ip_address: str) -> dict:
    # ipinfo.io API URL
    url = f'https://ipinfo.io/{ip_address}/json'

    response = requests.get(url)

    data = response.json()
    data.pop('readme', None)

    print(f"IP Info: {data}")
    return data
