#!/usr/bin/env python3
# Copyright (C) 2022 Sophgo Technologies Inc.  All rights reserved.
#
# TPU-MLIR is licensed under the 2-Clause BSD License except for the
# third-party components.
#
# ==============================================================================

import numpy as np
import os, sys
import transform.TpuLang as tpul
from typing import List

def rand_data(shape, dtype):
    if dtype == 'float32':
        return  np.random.random(shape).astype(np.float32)
    if dtype == 'int32' or 'uint32' or 'int16' or 'uint16' or 'int8' or 'uint8':
        return np.random.randint(0, 256, size=shape).astype(dtype)
    raise Exception("Not supported data type: {}!".format(dtype))

def tpulang(func):
    def wrapper(*args, **kwargs):
        tpul.init("BM1684X", True)
        func(*args, **kwargs)
        tpul.deinit()
    return wrapper

Failed_Cases = []

class TPULANG_IR_TESTER(object):
    # This class is built for testing single operator transform.
    def __init__(self):
        self.test_function = {
            #############################
            # TpuLang Test Case, Alphabetically
            #############################
            "Conv2d": self.test_Conv2d,
            "HModel": self.test_Model,
        }
        # no quantization when quant_mode == "f32"
        self.quant_modes = ["int8"]
        self.chip = self.get_chip_name()

    def get_chip_name(self):
        runchip = os.environ.get('SET_CHIP_NAME', None)
        if not runchip:
            print("no found SET_CHIP_NAME environment value, set bm1684x as default")
            runchip = "bm1684x"
        return runchip.lower()

    def test_single(self, case: str):
        if case in self.test_function:
            print("Test: {}".format(case))
            self.test_function[case](case)
            print("====== TEST {} Success ======".format(case))
        else:
            self.list()

    def test_all(self):
        for case in self.test_function:
            if case not in Failed_Cases:
                self.test_single(case)
        print("====== ALL TEST Success ======".format(case))

    def list(self):
        print("====== All Support Ops ======")
        for case in self.test_function:
            if case not in Failed_Cases:
                print(case)
        print("====== Error Ops ======")
        for case in self.test_function:
            if case in Failed_Cases:
                print(case)

    def coeff_tensor(self, shape, dtype, scale=1.0):
        data = rand_data(shape, dtype)
        data = data * scale if dtype == 'float32' else data
        return tpul.Tensor(dtype=dtype, shape=shape, data=data, is_const=True)

    #######################################################################
    # Convolution
    # ------------
    def conv_op(self, x, kshape, stride, pad=None, group=1, dilation=[1,1], zp=[None, None], dtype="float32"):
        oc = kshape[0]
        weight = self.coeff_tensor(kshape, dtype)
        out_dtype =  dtype if dtype == 'float32' else 'int32'
        bias = self.coeff_tensor(oc, out_dtype)
        conv = tpul.conv_v2(x, weight, bias=bias, stride=stride, pad=pad,
                            dilation=dilation, group=group, input_zp=zp[0],
                            weight_zp=zp[1], out_dtype=out_dtype)
        return conv
    def test_Conv2d(self, case_name):
        """Conv 2D"""
        @tpulang
        def _test_convolution(
            input_shape:List[int], kernel_shape:List[int], stride:List[int]=[1,1],
            dilation:List[int]=[1,1], pad:List[int]=None, group=1, dtype="float32",
            zp:List[int]=[None,None]
        ):
            x_data = rand_data(input_shape, dtype)
            x = tpul.Tensor(dtype=dtype, shape=input_shape, data=x_data)
            conv = self.conv_op(x, kernel_shape, stride, pad, group=group, dilation=dilation,
                    zp=zp, dtype=dtype)
            tpul.compile(case_name, [x], [conv], False, 2)

        _test_convolution([1, 3, 28, 28], [12, 3, 1, 1], group=3)
        _test_convolution([1, 3, 32, 32], [12, 3, 3, 3], stride=[2,2], pad=[1,1,1,1])
        _test_convolution([1, 3, 32, 32], [12, 3 , 3, 3], stride=[2,2], pad=[1,1,1,1], dtype="int8", zp=[5, -8])

    #######################################################################
    # HModel
    # ------------
    def test_Model(self, case_name):
        def model_def(x):
            rq0 = tpul.requant_fp_to_int(x, 1.0, 0, 0, 'int8')
            conv1 = self.conv_op(rq0, [64,1,7,7],[2,2], None, zp=[0,0], dtype='int8')
            # rq2 = tpul.requant_int(conv1, 2030043136, -13, 0, 0, 'int8', round_mode='half_away_from_zero')
            # relu3 = tpul.relu(rq2)
            # conv4 = conv_op(relu3, [96,64,3,3], [2,2], None, zp=[0,0], dtype='int8')
            # rq5 = tpul.requant_int(conv4, 1748893696, -10, 0, 0, 'int8', round_mode='half_away_from_zero')
            # relu6 = tpul.relu(rq5)
            # dq7 = tpul.dequant_int_to_fp(relu6, 0.25, 0)
            # coeff8 = coeff_tensor([1,96,1,1], 'float32', 10.0)
            # tpul.constdata(coeff8)
            # mul9 = tpul.mul(dq7, coeff8)
            # coeff10 = coeff_tensor([1,96,1,1], 'float32', -2.0)
            # tpul.constdata(coeff10)
            # add11 = tpul.add(mul9, coeff10)
            # relu12 = tpul.relu(add11)
            # rq13 = tpul.requant_fp_to_int(relu12, 4.0, 0, 0, 'int8')
            # conv14 = conv_op(rq13, [96,96,3,3], [1,1], [1,1,1,1], zp=[0,0], dtype='int8')
            # rq15 = tpul.requant_int(conv14, 1623457792, -8, 0, 0, 'int8', round_mode='half_away_from_zero')
            # relu16 = tpul.relu(rq15)
            # conv17 = conv_op(relu16, [96,96,3,3], [1,1], [1,1,1,1], zp=[0,0], dtype='int8')
            # rq18 = tpul.requant_int(conv17, 1623457792, -10, 0, 0, 'int8', round_mode='half_away_from_zero')
            # dq19 = tpul.dequant_int_to_fp(rq18, 0.0625, 0)
            # add20 = tpul.add(dq19, dq7)
            # coeff21 = coeff_tensor([1,96,1,1], 'float32', 2.0)
            # tpul.constdata(coeff21)
            # mul22 = tpul.mul(add20, coeff21)
            # coeff23 = coeff_tensor([1,96,1,1], 'float32', -2.0)
            # tpul.constdata(coeff23)
            # add24 = tpul.add(mul22, coeff23)
            # relu25 = tpul.relu(add24)
            # rq26 = tpul.requant_fp_to_int(relu25, 8.0, 0, 0, 'int8')
            # conv27 = conv_op(rq26, [96,96,3,3], [1,1], [1,1,1,1], zp=[0,0], dtype='int8')
            # rq28 = tpul.requant_int(conv27, 1712717824, -7, 0, 0, 'int8', round_mode='half_away_from_zero')
            # dq29 = tpul.dequant_int_to_fp(rq28, 0.0625, 0)
            return conv1

        @tpulang
        def _test_model_def(in_shape):
            x_data = (rand_data(in_shape, 'float32') - 0.5) * 256
            x = tpul.Tensor(dtype='float32', shape=in_shape, data=x_data)
            out = model_def(x=x)
            tpul.compile(case_name, [x], [out], False, 2)

        _test_model_def([1, 3, 28, 28])

if __name__ == "__main__":
    tester = TPULANG_IR_TESTER()
    os.makedirs("tpulang_test", exist_ok=True)
    os.chdir("tpulang_test")
    if len(sys.argv) == 2:
        tester.test_single(sys.argv[1])
    else:
        tester.test_all()