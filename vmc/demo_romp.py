#!/usr/bin/env python3

from log import Log
import sys
from configuration import Configuration
from vmc import Assistant as VMCAssistant, Bone, Position, Quaternion, Timestamp
import numpy as np
import romp, cv2, argparse, os
from scipy.spatial.transform import Rotation as R
from alfred.utils.file_io import ImageSourceIter

# Configuration
configuration: dict = {
    "host"  : "127.0.0.1",
    "port"  : 39539,
    "name"  : "example",
    "delta" : 0.0
}

# Logging
sys.stdout = Log(filename = "vmc.log", is_error = False)
sys.stderr = Log(filename = "vmc.log", is_error = True)

# ROMP
settings = romp.main.default_settings
subject_id = 0
root_position_offset = Position(0.0, 1.5, 0.0) # Align how you like
#hips_bone_position = Position(0, 0.939207, 0.003576) # Initial position in model
hips_bone_position = Position(0.0, 0.0, 0.0)
romp_model = romp.ROMP(settings)

# Input

iter = ImageSourceIter(sys.argv[1])

while iter.ok:
    itm = next(iter)
    if isinstance(itm, str):
        itm = cv2.imread(itm)
        
    outputs = romp_model(itm) # Test1
    #outputs = romp_model(cv2.imread('00000215.png')) # Test2
    #outputs = romp_model(cv2.imread('test2.png')) # Test3
    #outputs = romp_model(cv2.imread('00000119.png')) # Test4

    smpl_root_rotation = outputs["cam"][subject_id]
    smpl_root_rotation = R.from_rotvec(smpl_root_rotation).as_quat()
    smpl_root_rotation = Quaternion(-smpl_root_rotation[0], smpl_root_rotation[1], smpl_root_rotation[2], smpl_root_rotation[3]).conjugate()

    smpl_root_position = outputs["cam_trans"][subject_id]

    smpl_rotations_by_axis = outputs["smpl_thetas"][subject_id].reshape(24, 3)

    # VRM
    # (Just the logical bone names. Not the actual ones [nodes] in the rig)
    vrm_bone_names = {
        0 : "Hips", # Pelvis
        1 : "LeftUpperLeg", # L_Hip
        2 : "RightUpperLeg", # R_Hip
        3 : "Spine", # Spine1
        4 : "LeftLowerLeg", # L_Knee
        5 : "RightLowerLeg", # R_Knee
        6 : "Chest", # Spine2
        7 : "LeftFoot", # L_Ankle
        8 : "RightFoot", # R_Ankle
        9 : "UpperChest", # Spine3
        10 : "LeftToes", # L_Foot
        11 : "RightToes", # R_Foot
        12 : "Neck", # Neck
        13 : "LeftShoulder", # L_Collar
        14 : "RightShoulder", # R_Collar
        15 : "Head", # Head
        16 : "LeftUpperArm", # L_Shoulder
        17 : "RightUpperArm", # R_Shoulder
        18 : "LeftLowerArm", # L_Elbow
        19 : "RightLowerArm", # R_Elbow
        20 : "LeftHand", # L_Wrist
        21 : "RightHand", # R_Wrist
        22 : "LeftMiddleProximal", # L_Hand
        23 : "RightMiddleProximal" # R_hand
    }

    # VMC
    configuration = Configuration("vmc.yml", configuration)
    vmc = VMCAssistant(
        configuration['host'], 
        configuration["port"], 
        configuration["name"]
    )
    started_at = Timestamp()
    bones = []
    for index, rot in enumerate(smpl_rotations_by_axis):
        bone_name = vrm_bone_names[index]
        rot = R.from_rotvec(rot).as_quat()
        rotation = Quaternion(-rot[0], rot[1], rot[2], rot[3])
        bones.append(
            [
                Bone(bone_name),
                Position.identity(),
                rotation.conjugate()
            ]
        )

    # Sending
    vmc.send_root_transform(
        Position(
            -smpl_root_position[0] - hips_bone_position.x + root_position_offset.x,
            -smpl_root_position[1] - hips_bone_position.y + root_position_offset.y,
            -smpl_root_position[2] - hips_bone_position.z + root_position_offset.z
        ), 
        Quaternion.identity().multiply_by(Quaternion.from_euler(-180, 0, 0, 12), 12)
    )
    vmc.send_bones_transform(bones)
    vmc.send_available_states(1)
    delta = started_at.delta(configuration["delta"])
    vmc.send_relative_time(delta)
    configuration["delta"] = delta

