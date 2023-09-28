import argparse

from semantic_mesh_pytorch3d.config import (
    DEFAULT_CAM_FILE,
    DEFAULT_IMAGES_FOLDER,
    DEFAULT_LOCAL_MESH,
    PATH_TYPE,
)
from semantic_mesh_pytorch3d.meshes import Pytorch3DMesh


def parse_args():
    """_summary_

    Returns:
        _type_: _description_
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--mesh-file", default=DEFAULT_LOCAL_MESH)
    parser.add_argument("--camera-file", default=DEFAULT_CAM_FILE)
    parser.add_argument("--image-folder", default=DEFAULT_IMAGES_FOLDER)
    parser.add_argument(
        "--texture-type",
        default=0,
        type=int,
        help="Enum for texture. 0: default texture, 1: dummy texture, 2: geofile texture",
    )
    parser.add_argument(
        "--run-vis", action="store_true", help="Run mesh and cameras visualization"
    )
    parser.add_argument(
        "--run-aggregation",
        action="store_true",
        help="Aggregate color from multiple viewpoints",
    )
    parser.add_argument(
        "--run-render", action="store_true", help="Render out viewpoints"
    )
    args = parser.parse_args()
    return args


def main(
    mesh_file: PATH_TYPE,
    camera_file: PATH_TYPE,
    image_folder: PATH_TYPE,
    run_vis: bool,
    run_aggregation: bool,
    run_render: bool,
    texture_type: int,
):
    """Entrypoint

    Args:
        mesh_file (PATH_TYPE): Path to mesh in local metashape coordinates, with .ply extension
        camera_file (PATH_TYPE): Path to camera file from metashape with .xml extension
        image_folder (PATH_TYPE): Path to image folder
        run_vis (bool): Should the mesh be visualized
        run_aggregation (bool): Should data from different viewpoints be aggregated onto the mesh
        run_render (bool): Should images from the camera poses be rendered
        texture_type (int): How should the mesh be textured
    """
    mesh = Pytorch3DMesh(
        mesh_file, camera_file, image_folder=image_folder, texture_enum=texture_type
    )
    if run_vis:
        mesh.vis_pv()
    if run_aggregation:
        mesh.aggregate_viepoints_pytorch3d()
    if run_render:
        mesh.render_pytorch3d()


if __name__ == "__main__":
    args = parse_args()
    main(
        args.mesh_file,
        args.camera_file,
        args.image_folder,
        args.run_vis,
        args.run_aggregation,
        args.run_render,
        args.texture_type,
    )
