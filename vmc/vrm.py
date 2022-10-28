#!/usr/bin/env python3

from gltflib import GLTF

class VRM(GLTF):
    def __init__(self, filename: str) -> None:
        gltf = super().load_glb(filename)
        super().__init__(gltf.model, gltf.resources)

    def export_to_glb(self, filename: str) -> None:
        super().export(filename)
    
    def export_to_gltf(self, filename: str) -> None:
        super().convert_to_file_resource(
            super().get_glb_resource(), 
            filename + ".resources.bin"
        )
        super().export(filename)

    def get_bones(self) -> list:
        return self.model.nodes
