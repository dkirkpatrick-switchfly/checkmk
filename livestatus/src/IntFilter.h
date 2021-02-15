// Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
// This file is part of Checkmk (https://checkmk.com). It is subject to the
// terms and conditions defined in the file COPYING, which is part of this
// source code package.

#ifndef IntFilter_h
#define IntFilter_h

#include "config.h"  // IWYU pragma: keep

#include <bitset>
#include <chrono>
#include <cstdint>
#include <functional>
#include <memory>
#include <optional>
#include <string>

#include "ColumnFilter.h"
#include "Filter.h"
#include "contact_fwd.h"
#include "opids.h"
class Row;

class IntFilter : public ColumnFilter {
    using function_type = std::function<int(Row, const contact *)>;

public:
    IntFilter(Kind kind, std::string columnName, function_type,
              RelationalOperator relOp, const std::string &value);

    bool accepts(Row row, const contact *auth_user,
                 std::chrono::seconds timezone_offset) const override;

    [[nodiscard]] std::optional<int32_t> greatestLowerBoundFor(
        const std::string &column_name,
        std::chrono::seconds timezone_offset) const override;

    [[nodiscard]] std::optional<int32_t> leastUpperBoundFor(
        const std::string &column_name,
        std::chrono::seconds timezone_offset) const override;

    [[nodiscard]] std::optional<std::bitset<32>> valueSetLeastUpperBoundFor(
        const std::string &column_name,
        std::chrono::seconds timezone_offset) const override;

    [[nodiscard]] std::unique_ptr<Filter> copy() const override;
    [[nodiscard]] std::unique_ptr<Filter> negate() const override;

private:
    const function_type _get_value;
    const int32_t _ref_value;
};

#endif  // IntFilter_h
