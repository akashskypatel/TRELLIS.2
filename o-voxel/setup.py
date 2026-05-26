from setuptools import setup
from torch.utils.cpp_extension import CUDAExtension, BuildExtension, IS_HIP_EXTENSION
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_TARGET = os.environ.get("BUILD_TARGET", "auto")

if BUILD_TARGET == "auto":
    if IS_HIP_EXTENSION:
        IS_HIP = True
    else:
        IS_HIP = False
else:
    if BUILD_TARGET == "cuda":
        IS_HIP = False
    elif BUILD_TARGET == "rocm":
        IS_HIP = True

if not IS_HIP:
    cc_flag = []
else:
    archs = os.getenv("GPU_ARCHS", "native").split(";")
    cc_flag = [f"--offload-arch={arch}" for arch in archs]

setup(
    name="o_voxel",
    packages=[
        'o_voxel',
        'o_voxel.convert',
        'o_voxel.io',
    ],
    ext_modules=[
        CUDAExtension(
            name="o_voxel._C",
            sources=[
                # Hashmap functions
                "src/hash/hash.cu",
                # Convert functions
                "src/convert/flexible_dual_grid.cpp",
                "src/convert/volumetic_attr.cpp",
                ## Serialization functions
                "src/serialize/api.cu",
                "src/serialize/hilbert.cu",
                "src/serialize/z_order.cu",
                # IO functions
                "src/io/svo.cpp",
                "src/io/filter_parent.cpp",
                "src/io/filter_neighbor.cpp",
                # Rasterization functions
                "src/rasterize/rasterize.cu",
                
                # main
                "src/ext.cpp",
            ],
            include_dirs=[
                os.path.join(ROOT, "third_party/eigen"),
            ],
            extra_compile_args={
                "cxx": [
                    "/std:c++17",
                    "/EHsc", 
                    "/permissive-", 
                    "/Zc:__cplusplus", 
                    "/Zc:preprocessor",
                ],
                "nvcc": [
                    "-O3",
                    "--expt-relaxed-constexpr",
                    "--extended-lambda",
                    "-std=c++17",
                    "-Xcompiler=/std:c++17",
                    "-Xcompiler=/EHsc", 
                    "-Xcompiler=/permissive-", 
                    "-Xcompiler=/Zc:__cplusplus",
                    "-Xcompiler=/Zc:preprocessor",
                    "-allow-unsupported-compiler",
                ] + cc_flag,
            }
        )
    ],
    cmdclass={
        'build_ext': BuildExtension
    }
)
