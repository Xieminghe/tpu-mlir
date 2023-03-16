//===----------------------------------------------------------------------===//
//
// Copyright (C) 2022 Sophgo Technologies Inc.  All rights reserved.
//
// TPU-MLIR is licensed under the 2-Clause BSD License except for the
// third-party components.
//
//===----------------------------------------------------------------------===//

#include "tpu_mlir/Conversion/ExtraConversion/ExtraConvertCV18XX.h"

namespace tpu_mlir {

namespace cv18xx {

void populateDoExtraConversionPatterns(RewritePatternSet *patterns) {
  // clang-format off
  patterns->add<
      ConvertAddConstOp,
      ConvertDivOp,
      ConvertGatherOp,
      ConvertMaskedFillOp,
      ConvertMaxPoolWithMaskOp,
      ConvertMaxUnpoolOp,
      ConvertScaleOp,
      ConvertUpsampleOp,
      ConvertWhereOp,
      ConvertMatMulWithRightTranspose
  >(patterns->getContext());
  // clang-format on
}
} // namespace cv18xx
} // namespace tpu_mlir