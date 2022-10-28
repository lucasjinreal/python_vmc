#!/usr/bin/env python3

from osc import Client as OSCClient
from time import time
from math import radians, degrees, cos, sin, atan2, asin, pow, floor

class Bone:
    # 55 VRM bones
    valid_names = (
        "Hips",
        "LeftUpperLeg",
        "RightUpperLeg",
        "LeftLowerLeg",
        "RightLowerLeg",
        "LeftFoot",
        "RightFoot",
        "Spine",
        "Chest",
        "Neck",
        "Head",
        "LeftShoulder",
        "RightShoulder",
        "LeftUpperArm",
        "RightUpperArm",
        "LeftLowerArm",
        "RightLowerArm",
        "LeftHand",
        "RightHand",
        "LeftToes",
        "RightToes",
        "LeftEye",
        "RightEye",
        "Jaw",
        "LeftThumbProximal",
        "LeftThumbIntermediate",
        "LeftThumbDistal",
        "LeftIndexProximal",
        "LeftIndexIntermediate",
        "LeftIndexDistal",
        "LeftMiddleProximal",
        "LeftMiddleIntermediate",
        "LeftMiddleDistal",
        "LeftRingProximal",
        "LeftRingIntermediate",
        "LeftRingDistal",
        "LeftLittleProximal",
        "LeftLittleIntermediate",
        "LeftLittleDistal",
        "RightThumbProximal",
        "RightThumbIntermediate",
        "RightThumbDistal",
        "RightIndexProximal",
        "RightIndexIntermediate",
        "RightIndexDistal",
        "RightMiddleProximal",
        "RightMiddleIntermediate",
        "RightMiddleDistal",
        "RightRingProximal",
        "RightRingIntermediate",
        "RightRingDistal",
        "RightLittleProximal",
        "RightLittleIntermediate",
        "RightLittleDistal",
        "UpperChest"
    )

    def __init__(self, name: str) -> None:
        if name in self.valid_names:
            self.name = name
        else:
            raise ValueError("Invalid bone name.")
  
    def __str__(self) -> str:
        return self.name

class Position:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    @classmethod
    def identity(cls) -> 'Position':
        """Creates an identity position and returns it

        Returns:
            Position: Created identity position (x, y, z, w)

        >>> Position.identity()
        0.0, 0.0, 0.0

        """
        return cls(
            x = float(0.0),
            y = float(0.0),
            z = float(0.0)
        )

    def __str__(self) -> str:
        return ", ".join(
            (
                str(self.x), 
                str(self.y), 
                str(self.z)
            )
        )

class Quaternion:
    def __init__(self, x: float, y: float, z: float, w: float) -> None:
        if round(pow(x, 2) + pow(y, 2) + pow(z, 2) + pow(w, 2), 1) == 1:
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)
            self.w = float(w)
        else:
            raise ValueError(
                "Invalid quaternion values: x={}, y={}, z={}, w={}".format(
                    x,
                    y,
                    z,
                    w
                )
            )

    @classmethod
    def identity(cls) -> 'Quaternion':
        """Creates an identity quaternion and returns it

        Returns:
            Quaternion: Created identity quaternion (x, y, z, w)

        >>> Quaternion.identity()
        0.0, 0.0, 0.0, 1.0

        """
        return cls(
            x = float(0.0),
            y = float(0.0),
            z = float(0.0),
            w = float(1.0)
        )
    
    @classmethod
    def from_euler(cls, 
                   phi: float, theta: float, psi: float,
                   precision: int) -> 'Quaternion':
        """Creates an quaternion by euler angles and returns it

        Args:
            phi (float): Rotation angle around the X axis
            theta (float): Rotation angle around the Y axis
            psi (float): Rotation angle around the Y axis
            precision (int): Round the results to 'precision' digits after the decimal point

        Returns:
            Quaternion: Created quaternion (x, y, z, w)

        >>> Quaternion.from_euler(-90, -180, 90, 12)
        0.5, -0.5, -0.5, 0.5

        .. _Source:
            https://www.meccanismocomplesso.org/en/hamiltons-quaternions-and-3d-rotation-with-python

        """
        # x axis rotation angle
        cos_phi_half = cos(radians(phi) / 2)
        sin_phi_half = sin(radians(phi) / 2)
        # y axis rotation angle
        cos_theta_half = cos(radians(theta) / 2)
        sin_theta_half = sin(radians(theta) / 2)
        # z axis rotation angle
        cos_psi_half = cos(radians(psi) / 2)
        sin_psi_half = sin(radians(psi) / 2)
        # Calculation
        return cls(
            x = float(round(sin_phi_half * cos_theta_half * cos_psi_half - cos_phi_half * sin_theta_half * sin_psi_half, precision)),
            y = float(round(cos_phi_half * sin_theta_half * cos_psi_half + sin_phi_half * cos_theta_half * sin_psi_half, precision)),
            z = float(round(cos_phi_half * cos_theta_half * sin_psi_half - sin_phi_half * sin_theta_half * cos_psi_half, precision)),
            w = float(round(cos_phi_half * cos_theta_half * cos_psi_half + sin_phi_half * sin_theta_half * sin_psi_half, precision))
        )

    def to_euler(self) -> tuple[float, float, float]:
        """Exports an quaternion as an euler angle tuple

        Returns:
            tuple[float, float, float]: (x, y, z)

        >>> Quaternion.from_euler(-90, -180, 90, 12).to_euler()
        90.0, 0.0, -90.0

        .. _Source:
            https://www.meccanismocomplesso.org/en/hamiltons-quaternions-and-3d-rotation-with-python

        """
        # x axis rotation angle
        t0 = 2 * (self.w * self.x + self.y * self.z)
        t1 = 1 - 2 * (self.x * self.x + self.y * self.y)
        x = atan2(t0, t1)
        # y axis rotation angle
        t2 = 2 * (self.w * self.y - self.z * self.x)
        t2 = 1 if t2 > 1 else t2
        t2 = -1 if t2 < -1 else t2
        y = asin(t2)
        # y axis rotation angle
        t3 = 2 * (self.w * self.z + self.x * self.y)
        t4 = 1 - 2 * (self.y * self.y + self.z * self.z)
        z = atan2(t3, t4)
        return degrees(x), degrees(y), degrees(z)

    def conjugate(self) -> 'Quaternion':
        """Quaternion conjugation

        Returns:
            Quaternion: Conjugated quaternion (x, y, z, w)

        >>> Quaternion.from_euler(90, -90, 90, 12).conjugate().to_euler()
        180.0, -90.0, 180.0

        .. _Source:
            https://www.meccanismocomplesso.org/en/hamiltons-quaternions-and-3d-rotation-with-python

        """
        # Calculation
        return Quaternion(
            x = -self.x, 
            y = -self.y, 
            z = -self.z, 
            w = self.w
        )

    def multiply_by(self, quaternion: 'Quaternion',  precision: int) -> 'Quaternion':
        """Quaternion multiplication

        Returns:
            Quaternion: Multiplication product quaternion (x, y, z, w)

        >>> Quaternion.identity().multiply_by(Quaternion.from_euler(90, 0, 0, 12), 12)
        0.707106781187, 0.0, 0.0, 0.707106781187

        .. _Source:
            https://www.meccanismocomplesso.org/en/hamiltons-quaternions-and-3d-rotation-with-python

        """
        # Calculation
        return Quaternion(
            x = float(round(self.w * quaternion.x + self.x * quaternion.w + self.y * quaternion.z - self.z * quaternion.y, precision)),
            y = float(round(self.w * quaternion.y + self.y * quaternion.w + self.z * quaternion.x - self.x * quaternion.z, precision)),
            z = float(round(self.w * quaternion.z + self.z * quaternion.w + self.x * quaternion.y - self.y * quaternion.x, precision)),
            w = float(round(self.w * quaternion.w - self.x * quaternion.x - self.y * quaternion.y - self.z * quaternion.z, precision))
        )

    def __str__(self) -> str:
        return ", ".join(
            (
                str(self.x), 
                str(self.y), 
                str(self.z), 
                str(self.w)
            )
        )

class Timestamp(float):
    def __new__(self) -> None:
        return super().__new__(self, time())

    def delta(self, offset: float = 0.0, precision: int = 6) -> float:
        """Returns time delta in seconds with it's fractions as float 

        Args:
            offset (float): Delta offset (Default: 0.0)
            precision (int): Round the results to 'precision' digits after the decimal point (Default: 6)

        Returns:
            float: Time delta in seconds with it's fractions

        >>> Timestamp().delta()
        0.0

        """
        return round(offset + time() - self, precision)

class Assistant(OSCClient):
    def __init__(self, host: str, port: int, name: str) -> None:
        super().__init__(host, port, name)

    def send_root_transform(self, position: Position, 
                            quaternion: Quaternion) -> None:
        # since VMC v2.0.0
        self.send(
            "/VMC/Ext/Root/Pos",
            None,
            [
                "root",
                position.x,
                position.y,
                position.z, 
                quaternion.x,
                quaternion.y,
                quaternion.z,
                quaternion.w
            ]
        )

    def send_bones_transform(self,
                             transform: list[list[Bone, Position, Quaternion]]
                            ) -> None:
        self.send_bundle(
            "/VMC/Ext/Bone/Pos",
            None,
            transform
        )

    def send_tracker_transform(self,
                             transform: list[list[str, Position, Quaternion]]
                            ) -> None:
        self.send_bundle(
            "/VMC/Ext/Tra/Pos",
            None,
            transform
        )

    def send_available_states(self, loaded: int, 
                              calibration_state: int = None,
                              calibration_mode: int = None,
                              tracking_status: int = None) -> None:
        if tracking_status == None:
            if calibration_state == None or calibration_mode == None:
                self.send(
                    "/VMC/Ext/OK",
                    None,
                    [
                        loaded
                    ]
                )
            else:
                # since VMC v2.5
                self.send(
                    "/VMC/Ext/OK",
                    None,
                    [
                        loaded,
                        calibration_state,
                        calibration_mode
                    ]
                )
        else:
            # since VMC v2.7
            self.send(
                "/VMC/Ext/OK",
                None,
                [
                    loaded,
                    calibration_state,
                    calibration_mode,
                    tracking_status
                ]
            )

    def send_relative_time(self, delta: float) -> None:
        self.send(
            "/VMC/Ext/T",
            None,
            [
                delta
            ]
        )
