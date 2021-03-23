import requests

from segmind.utils import (
    check_if_instance_already_exists,
    create_instance,
    get_instance_info,
    terminate_instance,
)
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/create", methods=["POST"])
def create_instance_from_instance_type():
    args = request.json
    instance_type = args.get("instance_type")
    if not instance_type:
        return (
            jsonify(
                {
                    "result": "error",
                    "message": "instance_type is not provided in the request.",
                }
            ),
            200,
        )

    does_exist = check_if_instance_already_exists()
    if does_exist:
        instance_ip = does_exist["PublicIpAddress"]
        instance_id = does_exist["InstanceId"]
        return (
            jsonify(
                {
                    "result": "error",
                    "message": f"Instance {instance_id} is already running at {instance_ip} ",
                }
            ),
            200,
        )

    response = create_instance(instance_type)
    instance = response["Instances"][0]
    print(instance)

    return (
        jsonify(
            {
                "result": "success",
                "data": {
                    "instanceId": instance["InstanceId"],
                    "publicIp": instance.get("PublicIpAddress"),
                    "state": instance["State"],
                },
            }
        ),
        200,
    )


@app.route("/status", methods=["GET"])
def instance_status():
    instance_id = request.args.get("instance_id")
    if not instance_id:
        return (
            jsonify(
                {
                    "result": "error",
                    "message": "instance_id is not provided in the request.",
                }
            ),
            200,
        )

    status, instance = get_instance_info(instance_id=instance_id)
    if status != 200:
        return (
            jsonify(
                {
                    "result": "error",
                    "message": "Unable to fetch instance information.",
                }
            ),
            200,
        )

    state = instance["State"]
    service_available = False
    instance_available = False
    if state["Name"] == "running":
        instance_available = True
        url = f"http://{instance['PublicIpAddress']}"

        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                service_available = True
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            pass

    return (
        jsonify(
            {
                "result": "success",
                "data": {
                    "instance_state": {
                        "instanceId": instance["InstanceId"],
                        "publicIp": instance.get("PublicIpAddress"),
                        "state": state,
                        "available": instance_available,
                    },
                    "service_state": {"available": service_available},
                },
            }
        ),
        200,
    )


@app.route("/terminate", methods=["DELETE"])
def terminate():
    instance_id = request.args.get("instance_id")
    if not instance_id:
        return (
            jsonify(
                {
                    "result": "error",
                    "message": "instance_id is not provided in the request.",
                }
            ),
            200,
        )

    response = terminate_instance(instance_id=instance_id)

    return (
        jsonify(
            {
                "result": "success",
                "data": response,
            }
        ),
        200,
    )
