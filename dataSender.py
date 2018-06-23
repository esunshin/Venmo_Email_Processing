import requests as r


def sendData(name, amount, note):

    params = {"name": name, "amount": amount, "note": note}
    resp = r.post('https://yourSite.com/resources/acceptPayment.php', data=params)
    print(resp)
    print(resp.text[:300])
