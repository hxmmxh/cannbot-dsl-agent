#!/usr/bin/env bash
# Usage: source /path/to/cannbot/env.sh
_CANNBOT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
_CANNBOT_CANN_ROOT="${CANNBOT_CANN_ROOT:-/usr/local/Ascend/cann-9.2.1}"

if [[ ! -f "${_CANNBOT_CANN_ROOT}/set_env.sh" ]]; then
    printf 'CANN environment script not found: %s\n' "${_CANNBOT_CANN_ROOT}/set_env.sh" >&2
    return 1
fi
if [[ ! -f "${_CANNBOT_ROOT}/.venv/bin/activate" ]]; then
    printf 'Create the root .venv with uv first; see docs/uv_setup.md.\n' >&2
    return 1
fi

export PATH="${HOME}/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export LD_LIBRARY_PATH="/usr/local/Ascend/driver/lib64:/usr/local/Ascend/driver/lib64/driver"
export PYTHONPATH=""
export CMAKE_PREFIX_PATH=""
unset PYTHONHOME ASCEND_HOME_PATH ASCEND_TOOLKIT_HOME ASCEND_TOOLKIT_LATEST_HOME
unset ASCEND_OPP_PATH ASCEND_AICPU_PATH ASCEND_LATEST_INSTALL_PATH TOOLCHAIN_HOME ATB_HOME_PATH
source "${_CANNBOT_CANN_ROOT}/set_env.sh" || return 1
source "${_CANNBOT_ROOT}/.venv/bin/activate" || return 1
export PYTHONNOUSERSITE=1
export UV_MANAGED_PYTHON=1
unset UV_PYTHON_DOWNLOADS
export CANNBOTDSL_CACHE_DIR="${_CANNBOT_ROOT}/build/dsl-cache"
export ADD_DEMO_DEVICE="${ADD_DEMO_DEVICE:-npu:0}"
unset _CANNBOT_ROOT _CANNBOT_CANN_ROOT
