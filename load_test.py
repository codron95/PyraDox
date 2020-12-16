import base64
import requests
import time
import threading

image_path_1 = "/Users/rohan/Downloads/sample.jpg"
image_path_2 = "/Users/rohan/Downloads/aadhaar_rohan.jpg"

URL = "http://aadharmaskimageautoscale-1-1850177578.ap-south-1.elb.amazonaws.com:8080/api/mask"

content = open(image_path_1, "rb").read()
base64_encoded_odd = base64.b64encode(content).decode("ascii")

content = open(image_path_2, "rb").read()
base64_encoded_even = base64.b64encode(content).decode("ascii")


def write_result(i):
    print("Thread {} invoked".format(i))
    if(i % 2 == 0):
        base64_encoded = base64_encoded_even
    else:
        base64_encoded = base64_encoded_odd

    response = requests.post(URL, headers={"Content-Type": "application/json"}, json={
        "doc_b64": base64_encoded,
        "aadhaar": ['342060864859']
    })
    base64_response = response.json()["doc_b64_masked"]

    print("iteration: " + str(i) + ": " + str(response.status_code))

    with open("/Users/rohan/Desktop/masked_{}.jpg".format(i), "wb") as f:
        f.write(base64.b64decode(base64_response))


for i in range(0, 20):
    t = threading.Thread(target=write_result, args=(i, ))
    t.start()

    time.sleep(0.2)
