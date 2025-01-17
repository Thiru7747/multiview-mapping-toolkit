import xml.etree.ElementTree as ET

import numpy as np


def make_4x4_transform(rotation_str: str, translation_str: str, scale_str: str = "1"):
    """Convenience function to make a 4x4 matrix from the string format used by Metashape

    Args:
        rotation_str (str): Row major with 9 entries
        translation_str (str): 3 entries
        scale_str (str, optional): single value. Defaults to "1".

    Returns:
        np.ndarray: (4, 4) A homogenous transform mapping from cam to world
    """
    rotation_np = np.fromstring(rotation_str, sep=" ")
    rotation_np = np.reshape(rotation_np, (3, 3))

    if not np.isclose(np.linalg.det(rotation_np), 1.0, atol=1e-8, rtol=0):
        raise ValueError(
            f"Inproper rotation matrix with determinant {np.linalg.det(rotation_np)}"
        )

    translation_np = np.fromstring(translation_str, sep=" ")
    scale = float(scale_str)
    transform = np.eye(4)
    transform[:3, :3] = rotation_np * scale
    transform[:3, 3] = translation_np
    return transform


def parse_transform_metashape(camera_file):
    tree = ET.parse(camera_file)
    root = tree.getroot()
    # first level
    components = root.find("chunk").find("components")

    assert len(components) == 1
    transform = components.find("component").find("transform")

    rotation = transform.find("rotation").text
    translation = transform.find("translation").text
    scale = transform.find("scale").text

    local_to_epgs_4978_transform = make_4x4_transform(rotation, translation, scale)

    return local_to_epgs_4978_transform


def parse_sensors(sensors):
    sensors_dict = {}

    for sensor in sensors:
        sensor_dict = {}

        sensor_dict["image_width"] = int(sensor[0].get("width"))
        sensor_dict["image_height"] = int(sensor[0].get("height"))

        calibration = sensor.find("calibration")
        if calibration is None:
            raise ValueError("No calibration provided")

        sensor_dict["f"] = float(calibration.find("f").text)
        sensor_dict["cx"] = float(calibration.find("cx").text)
        sensor_dict["cy"] = float(calibration.find("cy").text)
        if None in (sensor_dict["f"], sensor_dict["cx"], sensor_dict["cy"]):
            ValueError("Incomplete calibration provided")

        # Get potentially-empty dict of distortion parameters
        sensor_dict["distortion_params"] = {
            calibration[i].tag: float(calibration[i].text)
            for i in range(3, len(calibration))
        }
        sensor_ID = int(sensor.get("id"))
        sensors_dict[sensor_ID] = sensor_dict
    return sensors_dict
