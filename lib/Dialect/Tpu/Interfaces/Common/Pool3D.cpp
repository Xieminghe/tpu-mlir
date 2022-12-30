//===----------------------------------------------------------------------===//
//
// Copyright (C) 2022 Sophgo Technologies Inc.  All rights reserved.
//
// TPU-MLIR is licensed under the 2-Clause BSD License except for the
// third-party components.
//
//===----------------------------------------------------------------------===//

#include "tpu_mlir/Dialect/Tpu/IR/TpuOps.h"
#include "tpu_mlir/Support/Dnnl/Dnnl.h"
#include "tpu_mlir/Support/Float16.h"
#include "tpu_mlir/Support/Helper/Module.h"
#include "tpu_mlir/Support/Helper/Quant.h"
#include "tpu_mlir/Support/MathUtils.h"

using namespace tpu_mlir;
using namespace tpu_mlir::helper;
using namespace mlir;

pool_attr_t tpu::Pool3DOp::parseParam() {
  pool_attr_t p = {0};
  assert(kernel_shape().size() == 3);
  auto ishape = input().getType().dyn_cast<RankedTensorType>().getShape();
  auto oshape = output().getType().dyn_cast<RankedTensorType>().getShape();
  auto kernel = Module::getI64Array(kernel_shape());
  auto stride = Module::getI64Array(strides());
  auto pad = Module::getI64Array(pads());

  p.n = ishape[0];
  p.c = ishape[1];
  p.id = ishape[2];
  p.ih = ishape[3];
  p.iw = ishape[4];
  p.od = oshape[2];
  p.oh = oshape[3];
  p.ow = oshape[4];
  p.kd = kernel->at(0);
  p.kh = kernel->at(1);
  p.kw = kernel->at(2);
  p.sd = stride->at(0);
  p.sh = stride->at(1);
  p.sw = stride->at(2);
  p.pad_d = pad->at(0);
  p.pad_h = pad->at(1);
  p.pad_w = pad->at(2);
  p.pad_d_after = pad->at(3);
  p.pad_h_after = pad->at(4);
  p.pad_w_after = pad->at(5);
  p.pad_value = pad_value();
  p.do_relu = do_relu();
  p.relu_limit = relu_limit().convertToDouble();
  p.is_global = p.id == p.kd && p.ih == p.kh && p.iw == p.kw && p.od == 1 &&
                p.oh == 1 && p.ow == 1;
  p.count_include_pad = count_include_pad();
  return p;
}

LogicalResult tpu::Pool3DOp::init(InferenceParameter &p) {
  auto pooling = new Pooling();
  auto attr = parseParam();

  int izp = 0;
  auto dtype = input().getType().cast<RankedTensorType>().getElementType();
  bool is_avg_pooling = pool_mode() == tpu::PoolMode::Avg;
  if (dtype.isa<quant::UniformQuantizedType>() && is_avg_pooling) {
    izp = dtype.cast<quant::UniformQuantizedType>().getZeroPoint();
  }
  pooling->setup(p.inputs[0], p.outputs[0], attr, is_avg_pooling, izp);
  p.handle = (void *)pooling;
  return success();
}

void tpu::Pool3DOp::deinit(InferenceParameter &p) {
  if (p.handle != nullptr) {
    auto pooling = (Pooling *)p.handle;
    delete pooling;
    p.handle = nullptr;
  }
  return;
}

LogicalResult tpu::Pool3DOp::inference(InferenceParameter &p) {
  if (p.handle == nullptr) {
    return failure();
  }
  auto pooling = (Pooling *)p.handle;
  pooling->run();

  if (pool_mode() == tpu::PoolMode::Max) {
    if (do_relu()) {
      auto limit = relu_limit().convertToDouble();
      function_relu(p.outputs[0], p.outputs[0],
                    Module::getNumElements(output()), limit,
                    Module::getStorageType(output()));
    }
    return success();
  }

  auto out_type = Module::getStorageType(output());
  auto num_elem = Module::getNumElements(output());
  if (out_type.isInteger(8)) {
#pragma omp parallel for schedule(static, omp_schedule(num_elem))
    for (int64_t i = 0; i < num_elem; ++i) {
      p.outputs[0][i] = p.outputs[0][i] * pooling->kd * pooling->kh *
                            pooling->kw * scale().value().convertToDouble() +
                        offset().value().convertToDouble();
      p.outputs[0][i] = out_type.isUnsignedInteger(8)
                            ? Quant::to_uint8(p.outputs[0][i])
                            : Quant::to_int8(p.outputs[0][i]);
    }
  } else if (out_type.isa<FloatType>()) {
    if (do_relu()) {
      auto limit = relu_limit().convertToDouble();
      function_relu(p.outputs[0], p.outputs[0], num_elem, limit);
    }
    if (out_type.isBF16()) {
      BF16(p.outputs[0], p.outputs[0], num_elem);
    } else if (out_type.isF16()) {
      F16(p.outputs[0], p.outputs[0], num_elem);
    }
  }

  return success();
}

LogicalResult tpu::Pool3DOp::LocalGenSupport() {
  auto attr = parseParam();
  if (attr.sd > 15 || attr.sh > 15 || attr.sw > 15) {
    return failure();
  }
  // do not support 3D local layer now
  return failure();
}

LogicalResult tpu::Pool3DOp::BackwardH(int64_t &in_idx, int64_t &in_slice,
                                       int64_t out_idx, int64_t out_slice) {
  auto attr = parseParam();
  in_slice = (out_slice - 1) * attr.sh + attr.kh;
  in_idx = out_idx * attr.sh - attr.pad_h;
  bool is_last = (out_idx + out_slice == attr.oh);
  LocalGenInterface::fixSlice(in_idx, in_slice, attr.ih, is_last);
  return success();
}
