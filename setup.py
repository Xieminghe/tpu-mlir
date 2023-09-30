import re
import sys
import os
from setuptools import setup, find_packages
from glob import glob
import codecs
import subprocess

def collect_caffe_dependence():


    os.system("cp /usr/lib/x86_64-linux-gnu/libpython3.10.so.1.0 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libboost_thread.so.1.74.0 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libboost_filesystem.so.1.74.0 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libboost_regex.so.1.74.0 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libglog.so.0 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libgflags.so.2.2 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libprotobuf.so.23 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libm.so.6 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libboost_python310.so.1.74.0 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libstdc++.so.6 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libgomp.so.1 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libz.so.1 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libicui18n.so.70 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libicuuc.so.70 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libunwind.so.8 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libpthread.so.0  /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libgfortran.so.5  /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/liblzma.so.5 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libquadmath.so.0 /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libopenblas.so.0  /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libgcc_s.so.1  /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libicudata.so.70  /workspace/install/lib")
    os.system("cp /usr/lib/x86_64-linux-gnu/libc.so.6 /workspace/install/lib")
    os.system("cp -r /usr/local/python_packages/caffe /workspace/install")
    print("caffe dependence cllect Done")

def collect_oneDNN_dependence():
    os.system("cp /usr/local/lib/libdnnl.so /workspace/install/lib")
    os.system("cp /usr/local/lib/libdnnl.so.3 /workspace/install/lib")
    os.system("cp /usr/local/lib/libdnnl.so.3.1 /workspace/install/lib")
    print("oneDNN dependence cllect Done")


def release_packages_merge():
    os.system("mkdir tpu_mlir_release")
    os.system("mkdir /workspace/tpu_mlir_release/lib")

    #os.system("cp -r /workspace/install/lib  /workspace/tpu_mlir_release")
    os.system("find /workspace/ -type f -name '*.so*' -exec cp {}  /workspace/tpu_mlir_release/lib \;")
    os.system("find /workspace/ -type f -name '*.so.*' -exec cp {}  /workspace/tpu_mlir_release/lib \;")
    os.system("cp -r /workspace/install/python  /workspace/tpu_mlir_release")
   # os.system("cp -r /workspace/install/docs  /workspace/tpu_mlir_release")
    os.system("cp -r /workspace/install/src   /workspace/tpu_mlir_release")
    os.system("cp -r /workspace/install/bin  /workspace/tpu_mlir_release")
    os.system("cp -r /workspace/regression  /workspace/tpu_mlir_release")
    os.system("cp -r /workspace/third_party/customlayer  /workspace/tpu_mlir_release")
    os.system("cp -r /workspace/install/caffe   /workspace/tpu_mlir_release")
    print("release packages merge Done")


# def iter_shared_objects():
#     cur_dir = os.path.abspath(os.path.dirname(sys.argv[0]) or '.')
#     for dirpath, dirnames, filenames in os.walk(cur_dir):
#         for fn in filenames:
#             if fn.endswith('.so'):
#                 yield os.path.join(dirpath, fn)

# #packages = ['tpu_perf']
# so_list = list(iter_shared_objects())

def show_readmefile():

    here = os.path.abspath(os.path.dirname("/workspace/"))
    with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
        long_description = "\n" + fh.read()
    print("show README file Done")

def search_files(dir_path):
    """
    Get all files
    :param dir_path:files path
    :return: List of all files in this folder
    """
    result = []
    file_list = os.listdir(dir_path)
    for file_name in file_list:
        complete_file_name = os.path.join(dir_path, file_name)
        if os.path.isdir(complete_file_name):
            result.extend(search_files(complete_file_name))
        if os.path.isfile(complete_file_name):
            result.append(complete_file_name)
            print(complete_file_name)
    return result



def tpu_mlir_setup():

    list1 = list(search_files("/workspace/tpu_mlir_release/"))
    # list2 = list(search_files("/workspace/tpu_mlir_release/regression"))
    # list3 = list(search_files("/workspace/tpu_mlir_release/lib"))
    # list4 = list(search_files("/workspace/tpu_mlir_release/docs"))
    # list5 = list(search_files("/workspace/tpu_mlir_release/src"))
    # list6 = list(search_files("/workspace/tpu_mlir_release/bin"))
    # list7 = list(search_files("/workspace/tpu_mlir_release/customlayer"))
    # list8 = list(search_files("/workspace/tpu_mlir_release/caffe"))


    setup(


        name='tpu_mlir_release',
        version='1.3',
        author='sophgo',
        description='tpu-mlir release pip',
        author_email='dev@sophgo.com',
        license='Apache',
        platforms = 'any',
        url='https://github.com/sophgo/tpu-mlir',
       # install_requires=['numpy'],
        include_package_data=True,

        packages=['tpu_mlir_release'],

        keywords=['python3.10', 'unbuntu22.04', 'linux','tpu-mlir'],
        package_data={'': list1},
        long_description_content_type="text/markdown",
        classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development'
        ],
      #  python_requires='==3.10',
    )
    print("release packages setup Done")


def remove_tpu_mlir_release():
    os.system("rm -r /workspace/tpu_mlir_release")

def workflow():
  #  show_readmefile()
    # collect_caffe_dependence()
    # collect_oneDNN_dependence()
    release_packages_merge()
    tpu_mlir_setup()
   # remove_tpu_mlir_release()

workflow()
